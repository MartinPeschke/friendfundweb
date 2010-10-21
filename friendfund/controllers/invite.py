import logging, urllib, urllib2, simplejson, formencode
from collections import deque

from pylons import request, response, session as websession, tmpl_context as c, url, app_globals as g, cache
from pylons.controllers.util import abort, redirect
from pylons.decorators import jsonify, PylonsFormEncodeState
from friendfund.lib import fb_helper, tw_helper
from friendfund.lib.auth.decorators import logged_in, enforce_blocks, checkadd_block, remove_block
from friendfund.lib.base import BaseController, render, _
from friendfund.model.authuser import UserNotLoggedInWithMethod
from friendfund.model.pool import Pool, PoolUser, AddInviteesProc
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
	
	def _display_invites(self, pool):
		c.pool = pool
		c.method = c.user.get_current_network() or 'facebook'
		c.furl = '/invite/%s' % pool.p_url
		c.pool_url = pool.p_url
		#Find all people that have been selected as to-be-invited but not added to pool yet
		c.invitees = websession.get('invitees', {})
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
		c.invitees = websession.get('invitees', {})
		
		il = c.pool.get_invitees(c.method)
		if method in ['facebook', 'twitter']:
			try:
				friends = c.user.get_friends(c.method, getattr(c.pool.receiver.networks.get(method), 'network_id', None))
			except UserNotLoggedInWithMethod, e:
				if c.method == 'facebook':
					return {'html':render('/receiver/fb_login.html').strip()}
				else: 
					return {'html':render('/receiver/tw_login.html').strip()}
			else:
				c.already_invited = dict([(i, friends[i]) for i in il if i in friends])
				pre_invited = [str(k) for k in c.invitees.get(method, {})]
				c.friends = dict([(id, friends[id]) for id in friends if not (str(id) in pre_invited or str(id) in c.already_invited)])
		else:
			c.friends = c.invitees.get(method, {})
			# print method, c.friends
		return {'html':render('/invite/inviter.html').strip()}
	
	@logged_in(ajax=False)
	def friends(self, pool_url):
		params = variable_decode(request.params)
		c.furl = '/invite/%s' % pool_url
		c.pool_url = pool_url
		pool = g.dbm.get(Pool, p_url = pool_url)
		pool.is_secret = params.get("is_secret", False)
		
		invitees = params.get('invitees')
		
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
			return self._display_invites(pool)
		
		
		if invitees is not None:
			c.pool = g.dbm.set(AddInviteesProc(p_id = pool.p_id
							, p_url = pool.p_url
							, inviter_user_id = c.user.u_id
							, users=[PoolUser(**el) for el in invitees]
							, description = params['description']
							, is_secret = params.get("is_secret", False)))
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
	def addall(self, pool_url):
		if request.method != 'POST':
			return self.ajax_messages("Not Allowed")
		params = variable_decode(request.params)
		network = params['network']
		if network not in ['facebook', 'twitter']:
			return self.ajax_messages("Network Not Allowed")
		if 'userlist' not in params:
			return self.ajax_messages("No Users Found")
		invitees = websession.get('invitees', {})
		network_invitees = invitees.get(network, {})
		for user in params['userlist']:
			network_id = user.pop('networkid')
			networkname = user.get('networkname')
			if networkname and network_id:
				network_invitees[str(network_id)] = user
		invitees[network] = network_invitees
		websession['invitees'] = invitees
		log.debug('added: %s/%s to websession' % (network, network_invitees))
		return {'clearmessage':True}
	
	@jsonify
	@logged_in(ajax=True)
	def add(self, pool_url):
		if request.method != 'POST':
			return self.ajax_messages("Not Allowed")
		params = variable_decode(request.params)
		invitee = params.get("invitee")
		network = invitee['network']
		try:
			if network == 'email':
				valid = formencode.validators.Email(min=5, max = 255, not_empty = True, resolve_domain=True)
				try:
					network_id = valid.to_python(invitee.pop('networkid'))
				except formencode.validators.Invalid, error:
					return {'data':{'success':False, 'message':'<span>%s</span>' % error}}
			else:
				network_id = invitee.pop('networkid')
			
			invitees = websession.get('invitees', {})
			network_invitees = invitees.get(network, {})
			network_invitees[str(network_id)] = invitee
			invitees[network] = network_invitees
			websession['invitees'] = invitees
			log.debug('add: %s' % websession['invitees'])
		except Exception, e:
			log.warning("Something wonky happened in /invite/add")
			return self.ajax_messages("An error occured, please try again!")
		else:
			if network == 'email':
				c.pool = g.dbm.get(Pool, p_url = c.user.current_pool.p_url)
				c.method = 'email'
				c.invitees = invitees
				return {'clearmessage':True, 'data':{'success':True, 'html':self.render('/invite/invited.html').strip()}}
			else:
				return {'clearmessage':True, 'data':{'initial':len(network_invitees) == 1, 'len': len(network_invitees)}}
	
	@jsonify
	@logged_in(ajax=False)
	def rem(self, pool_url):
		if request.method != 'POST':
			return redirect(url('home'))
		try:
			network = request.params.get('network', None)
			network_id = request.params.get('networkid', None)
			
			invitees = websession.get('invitees', {})
			network_invitees = invitees.get(network, {})
			if network_id in network_invitees:
				del network_invitees[str(network_id)]
			invitees[network] = network_invitees
			websession['invitees'] = invitees
			log.debug('rem: %s' % websession['invitees'])
		except:
			log.warning("Something wonky happened in /invite/rem")
		if network != 'email':
			return {'clearmessage':True, 'data':{'last':len(network_invitees) == 1, 'len': len(network_invitees)}}
		else:
			return {}