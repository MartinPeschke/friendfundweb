import logging, urllib, urllib2, simplejson, formencode
from collections import deque
from ordereddict import OrderedDict

from pylons import request, response, session as websession, tmpl_context as c, url, app_globals as g, cache
from pylons.controllers.util import abort, redirect
from pylons.decorators import jsonify, PylonsFormEncodeState
from friendfund.lib import fb_helper, tw_helper
from friendfund.lib.auth.decorators import logged_in, enforce_blocks, checkadd_block, remove_block
from friendfund.lib.base import BaseController, render, _
from friendfund.model.authuser import UserNotLoggedInWithMethod
from friendfund.model.pool import Pool, PoolInvitee, AddInviteesProc
from friendfund.tasks import fb as fbservice, twitter as twservice
from friendfund.tasks.photo_renderer import remote_profile_picture_render, remote_pool_picture_render

from formencode.variabledecode import variable_decode

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
		return self._display_invites(pool)
	
	def _display_invites(self, pool, invitees = {}):
		c.pool = pool
		c.method = c.user.get_current_network() or 'facebook'
		c.furl = '/invite/%s' % pool.p_url
		c.pool_url = pool.p_url
		#Find all people that have been selected as to-be-invited but not added to pool yet
		c.invitees = invitees
		for network, invitees in c.invitees.items():
			if network and invitees:
				il = c.pool.get_invitees(network)
				c.invitees[network] = dict([(k,v) for k,v in invitees.iteritems() if k not in il])
			else:
				del c.invitees[network]
		websession['invitees'] = c.invitees
		
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
				c.friends = OrderedDict([(id, friends[id]) for id in sorted(friends, key=lambda x: friends[x]['name']) if str(id) not in c.already_invited])
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
			c.already_invited = dict([(i, friends[i]) for i in il if i in friends])
			c.friends = OrderedDict([(id, friends[id]) for id in sorted(friends, key=lambda x: friends[x]['name']) if not str(id) in c.already_invited])
			return {'data':{'is_complete':is_complete, 'offset':offset, 'html':render('/invite/networkfriends.html').strip()}}
		return {'success':False}
	
	
	@logged_in(ajax=False)
	def friends(self, pool_url):
		invitees = simplejson.loads(request.params.get('invitees'))
		print invitees
		invitees = invitees.get("invitees")
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
			if (has_fb_invitees and checkadd_block('fb_streampub')):
				perms_required = True
			else:
				remove_block('fb_streampub')
		if perms_required:
			c.enforce_blocks = True
			c.invitees = {}
			for inv in invitees:
				netw = inv['network'].lower()
				invs = c.invitees.get(netw,{})
				invs[str(inv['network_id'])] = inv
				c.invitees[netw] = invs
			return self._display_invites(pool, c.invitees)
		
		if invitees is not None:
			print invitees
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
	
	@jsonify
	@logged_in(ajax=True)
	def add(self, pool_url):
		params = variable_decode(request.params)
		invitee = params.get("invitee")
		print invitee
		network = invitee['network']
		if request.method != 'POST' or network!= 'email':
			return self.ajax_messages("Not Allowed")
		valid = formencode.validators.Email(min=5, max = 255, not_empty = True, resolve_domain=True)
		try:
			network_id = valid.to_python(invitee.get('network_id'))
		except formencode.validators.Invalid, error:
			return {'data':{'success':False, 'message':'<span>%s</span>' % error}}
		else:
			c.method = 'email'
			c.invitees = {network_id:invitee}
			print invitee
			return {'clearmessage':True, 'data':{'success':True, 'html':self.render('/invite/email_invitee.html').strip()}}