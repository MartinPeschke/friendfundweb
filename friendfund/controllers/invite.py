import logging, urllib, urllib2, simplejson, formencode, datetime
from collections import deque
from ordereddict import OrderedDict

from pylons import request, response, tmpl_context as c, url, app_globals as g, cache, session as websession
from pylons.controllers.util import abort, redirect
from pylons.decorators import jsonify, PylonsFormEncodeState
from friendfund.lib import fb_helper, tw_helper
from friendfund.lib.auth.decorators import logged_in, enforce_blocks, checkadd_block, remove_block
from friendfund.lib.base import BaseController, render, _
from friendfund.lib.i18n import FriendFundFormEncodeState
from friendfund.model.authuser import UserNotLoggedInWithMethod
from friendfund.model.pool import Pool, PoolInvitee, AddInviteesProc
from friendfund.tasks import fb as fbservice, twitter as twservice
from friendfund.tasks.photo_renderer import remote_profile_picture_render, remote_pool_picture_render


from formencode.variabledecode import variable_decode
strbool = formencode.validators.StringBoolean(if_missing=False, if_empty=False)
from celery.task.sets import TaskSet
log = logging.getLogger(__name__)

class InviteController(BaseController):
	navposition=g.globalnav[1][2]
	
	@logged_in(ajax=False)
	def display(self, pool_url):
		if not pool_url:
			return redirect(url('home'))
		if not c.user.set_pool_url(pool_url):
			return redirect(url('home'))
		pool = g.dbm.get(Pool, p_url = c.user.current_pool.p_url)
		if pool is None:
			return abort(404)
		if 'invitees' in websession:
			del websession['invitees']
		return self._display_invites(pool)
	
	def _display_invites(self, pool, invitees = {}):
		c.pool = pool
		c.method = c.user.get_current_network() or 'facebook'
		c.furl = '/invite/%s' % pool.p_url
		c.pool_url = pool.p_url
		#Find all people that have been selected as to-be-invited but not added to pool yet
		c.invitees = invitees
		for network, invitees in c.invitees.iteritems():
			if network and invitees:
				il = c.pool.get_invitees(network)
				c.invitees[network] = dict([(k,v) for k,v in invitees.iteritems() if k not in il])
			else:
				del c.invitees[network]
		return self.render('/invite/invite.html')
	
	@jsonify
	@logged_in(ajax=True)
	def method(self, pool_url, method):
		c.pool = g.dbm.get(Pool, p_url = c.user.current_pool.p_url)
		if c.pool is None:
			return abort(404)
		c.method = str(method)
		c.furl = '/invite/%s' % (pool_url)
		
		il = c.pool.get_invitees(c.method)
		already_invited = (websession.get('invitees',{}).get(c.method, {}).keys())
		if method in ['facebook', 'twitter']:
			is_complete = True
			offset = 0
			try:
				friends, is_complete, offset = c.user.get_friends(c.method, getattr(c.pool.receiver.networks.get(method), 'network_id', None))
			except UserNotLoggedInWithMethod, e:
				if c.method == 'facebook':
					return {'data':{'is_complete': True, 'html':render('/receiver/fb_login.html').strip()}}
				else: 
					return {'data':{'is_complete': True, 'html':render('/receiver/tw_login.html').strip()}}
			else:
				c.already_invited = dict([(i, friends[i]) for i in il if i in friends])
				c.friends = OrderedDict([(id, friends[id]) for id in sorted(friends, key=lambda x: friends[x]['name']) if str(id) not in c.already_invited and str(id) not in already_invited])
				return {'data':{'is_complete':is_complete, 'offset':offset, 'html':render('/invite/inviter.html').strip()}}
		else:
			c.friends = {}
		return {'html':render('/invite/inviter.html').strip()}
	
	@jsonify
	def get_extension(self, method):
		if method in ['twitter']:
			offset = int(request.params['offset'])
			c.pool = g.dbm.get(Pool, p_url = c.user.current_pool.p_url)
			if c.pool is None:
				return abort(404)
			c.method = str(method)
			il = c.pool.get_invitees(c.method)
			c.method = method
			friends, is_complete, offset = c.user.get_friends(c.method, offset = offset)
			
			already_invited = (websession.get('invitees',{}).get(c.method, {}).keys())
			c.already_invited = dict([(i, friends[i]) for i in il if i in friends])
			c.friends = OrderedDict([(id, friends[id]) for id in sorted(friends, key=lambda x: friends[x]['name']) if not str(id) in c.already_invited and str(id) not in already_invited])
			return {'data':{'is_complete':is_complete, 'offset':offset, 'html':render('/invite/networkfriends.html').strip()}}
		return {'success':False}
	
	@logged_in(ajax=False)
	def friends(self, pool_url):
		data = simplejson.loads(request.params.get('invitees') or '{}')
		invitees = data.get("invitees")
		c.furl = '/invite/%s' % pool_url
		c.pool_url = pool_url
		pool = g.dbm.get(Pool, p_url = pool_url)
		pool.is_secret = request.params.get("is_secret", False)
		pool.description = request.params['description']
		
		#determine state of permissions and require missing ones
		perms_required = False
		if checkadd_block('email'):
			perms_required = True
		if invitees is not None:
			has_fb_invitees = False
			for inv in invitees or []:
				if isinstance(inv, dict) and 'network' in inv:
					if inv['network'].lower() == 'facebook': 
						has_fb_invitees = True
						break
				else:
					log.warn("ADDINVITEES: found non dict invitee: %s", unicode(inv).encode("latin-1","xmlcharrefreplace"))
			if (has_fb_invitees and checkadd_block('create_event')):
				perms_required = True
			else:
				remove_block('create_event')
		if perms_required:
			c.enforce_blocks = True
			c.invitees = {}
			for inv in invitees:
				netw = inv['network'].lower()
				invs = c.invitees.get(netw,{})
				invs[str(inv['network_id'])] = inv
				c.invitees[netw] = invs
				if strbool.to_python(inv.get('is_selector')): pool.selector=PoolInvitee.fromMap(inv)
				websession['invitees'] = c.invitees
			return self._display_invites(pool, c.invitees)
		
		if invitees is not None:
			self.create_event(pool, invitees)
			c.pool = g.dbm.set(AddInviteesProc(p_id = pool.p_id
							, p_url = pool.p_url
							, inviter_user_id = c.user.u_id
							, users=[PoolInvitee.fromMap(el) for el in invitees]
							, description = pool.description
							, is_secret = pool.is_secret))

			g.dbm.expire(Pool(p_url = pool.p_url))
			
			
			tasks = deque()
			for i in invitees:
				if i['network'] != 'email':
					tasks.append(remote_profile_picture_render.subtask(args=[[(i['network'], i['network_id'],i['large_profile_picture_url'])]]))
			job = TaskSet(tasks=tasks)
			job.apply_async()
			
			remote_pool_picture_render.apply_async(args=[c.pool.p_url])
			if 'invitees' in websession:
				del websession['invitees']
		return redirect(url('ctrlpoolindex', controller='pool', pool_url = pool_url))
	
	
	
	
	def create_event(self, pool, invitees):
		try:
			fb_data = fb_helper.get_user_from_cookie(request.cookies, g.FbApiKey, g.FbApiSecret.__call__(), c.user)
		except fb_helper.FBIncorrectlySignedRequest, e: 
			log.error("DEAUTHORIZE with %s, %s", request.params, request.cookies)
			return '1'
		
		fb_invitees = {}
		for inv in invitees:
				netw = inv['network'].lower()
				if netw == 'facebook':
					fb_invitees[str(inv['network_id'])] = inv
				from poster.encode import multipart_encode
		
		from poster.streaminghttp import register_openers
		import urllib2, simplejson
		register_openers()
		datagen, headers = multipart_encode({
				"event_info": simplejson.dumps({"name":pool.occasion.get_display_label().encode("utf-8"), 
												"start_time" : (pool.occasion.date - datetime.timedelta(0,3600)).strftime("%Y-%m-%d"), 
												"end_time":pool.occasion.date.strftime("%Y-%m-%d"),
												"description":"%s\n\n%s" % (pool.description, '%s/pool/%s'%(g.SITE_ROOT_URL,pool.p_url)),
												"tagline":"Friendfund, group gifting",
												"host":"Me",
												"link" : "http://dev.friendfund.de"}),
				"access_token":fb_data['access_token'],"format":"json",
				"[no name]":open("/opt/www/friendfund/data%s" % pool.receiver.get_profile_pic("RA"), "rb"),
				"link" : "http://dev.friendfund.de", "name":"Friendfund"})
		req = urllib2.Request('https://api.facebook.com/method/events.create', datagen, headers)
		try: 
			event_id = urllib2.urlopen(req).read()
		except Exception, e:
			event_id = e.fp.read()
		else:
			msg = {"eid":str(event_id),
					"uids" : '[%s,1707117978]'%(','.join(fb_invitees.keys())),
					"personal_message":pool.description or 'Description', "format":"json",
					"access_token":fb_data['access_token']}
			msg = dict((k,v.encode("utf-8")) for k,v in msg.iteritems())
			print msg
			try:
				resp = urllib2.urlopen('https://api.facebook.com/method/events.invite', urllib.urlencode(msg))
			except urllib2.HTTPError, e:
				resp = e.fp
			post = resp.read()
			print post
		print event_id
		
		
		# msg = {'access_token':fb_data['access_token'],
				# 'link':'%s/pool/%s'%(g.SITE_ROOT_URL,pool.p_url),
				# 'message':'Merry %s' % (pool.occasion.get_display_label()).encode("utf-8"),
				# 'picture':'%s%s'%(g.SITE_ROOT_URL,pool.receiver.get_profile_pic("RA")),
				# 'name':("Friendfund for %s's %s"%(pool.receiver.name, pool.occasion.get_display_label())).encode("utf-8"),
				# 'caption':"Friendfund",
				# 'description':("Friendfund for %s's %s"%(pool.receiver.name, pool.occasion.get_display_label())).encode("utf-8")}
		
		# print msg, 'https://graph.facebook.com/%s/feed'%str(event_id)
		# try:
			# resp = urllib2.urlopen('https://graph.facebook.com/%s/feed'%str(event_id), urllib.urlencode(msg))
		# except urllib2.HTTPError, e:
			# resp = e.fp
		# post = resp.read()
		# print post
		
		return event_id
	
	
	
	@jsonify
	@logged_in(ajax=True)
	def add(self, pool_url):
		params = variable_decode(request.params)
		invitee = params.get("invitee")
		network = invitee['network']
		if request.method != 'POST' or network!= 'email':
			return self.ajax_messages("Not Allowed")
		valid = formencode.validators.Email(min=5, max = 255, not_empty = True, resolve_domain=True)
		try:
			network_id = valid.to_python(invitee.get('network_id'), state=FriendFundFormEncodeState)
		except formencode.validators.Invalid, error:
			return {'data':{'success':False, 'message':'<span>%s</span>' % error}}
		else:
			c.method = 'email'
			c.invitees = {network_id:invitee}
			return {'clearmessage':True, 'data':{'success':True, 'html':self.render('/invite/email_invitee.html').strip()}}