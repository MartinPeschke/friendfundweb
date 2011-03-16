import logging, urllib, urllib2, simplejson, formencode, datetime, types
from collections import deque
from ordereddict import OrderedDict

from pylons import request, response, tmpl_context as c, url, app_globals as g, cache, session as websession
from pylons.controllers.util import abort, redirect
from pylons.decorators import jsonify, PylonsFormEncodeState
from friendfund.lib import fb_helper, tw_helper, helpers as h
from friendfund.lib.auth.decorators import logged_in, enforce_blocks, checkadd_block, remove_block, post_only
from friendfund.lib.base import BaseController, render, render_def, _, ExtBaseController
from friendfund.lib.i18n import FriendFundFormEncodeState
from friendfund.lib.notifications.messages import Message, ErrorMessage, SuccessMessage
from friendfund.model.authuser import UserNotLoggedInWithMethod
from friendfund.model.forms.pool import PoolEmailInviteeForm
from friendfund.model.pool import Pool, PoolInvitee, AddInviteesProc, GetPoolInviteesProc
from friendfund.tasks import fb as fbservice, twitter as twservice
from friendfund.tasks.photo_renderer import remote_profile_picture_render, remote_pool_picture_render

from formencode.variabledecode import variable_decode
strbool = formencode.validators.StringBoolean(if_missing=False, if_empty=False)
from celery.task.sets import TaskSet
log = logging.getLogger(__name__)

class InviteController(ExtBaseController):
	
	def display(self, pool_url):
		if c.user.is_anon or not c.pool.am_i_member(c.user):
			return redirect(url('get_pool', pool_url=pool_url))
		locals = {"closing_date":h.format_date(c.pool.expiry_date, format="full"), "pool_url":url("get_pool", pool_url=pool_url, protocol="http"), "title":c.pool.title}
		c.errors = {}
		c.values = {"subject":c.pool.title, \
			"message":_("FF_INVITE_PAGE_Hey guys,\n\nI've created a Pool using friendfund to collect money for %(title)s.\nYou've been invited to chip in and help fund this Pool by %(closing_date)s.\n\n%(pool_url)s")%locals
			}
		return self._display_invites()
	
	def _display_invites(self, invitees = {}):
		c.workflow = request.params.get("v") or "1"
		c.method = c.user.get_current_network() or 'facebook'
		c.invitees = invitees
		return self.render('/invite/invite.html')
	
	@jsonify
	@logged_in(ajax=True)
	def method(self, pool_url, method):
		c.method = str(method)
		if method in ['facebook', 'twitter']:
			pv =  request.params.getall('pv')
			already_invited = g.dbm.get(GetPoolInviteesProc, p_url = pool_url, network=c.method)
			already_invited.idset = already_invited.idset.union(pv)
			
			try:
				receiver_id = already_invited.receiver.network_id
			except:
				receiver_id = None
			
			is_complete = True
			offset = 0
			try:
				friends, is_complete, offset = c.user.get_friends(c.method, getattr(c.pool.receiver.networks.get(method), 'network_id', receiver_id))
			except UserNotLoggedInWithMethod, e:
				if c.method == 'facebook':
					return {'data':{'is_complete': True, 'success':False, 'html':render('/receiver/fb_login.html').strip()}}
				else: 
					return {'data':{'is_complete': True, 'success':False, 'html':render('/receiver/tw_login.html').strip()}}
			else:
				c.friends = OrderedDict([(id, friends[id]) for id in sorted(friends, key=lambda x: friends[x]['name']) if id not in already_invited.idset])
				return {'data':{'is_complete':is_complete, 'success':True, 'offset':offset, 'html':render('/invite/inviter.html').strip()}}
		else:
			c.friends = {}
			c.email_errors = {}
			c.email_values = {}
		return {'html':render('/invite/inviter.html').strip()}
	
	@jsonify
	def get_extension(self, pool_url, method):
		if method in ['twitter']:
			c.method = str(method)
			pv =  request.params.getall('pv')
			already_invited = g.dbm.get(GetPoolInviteesProc, p_url = pool_url, network=c.method).idset
			already_invited = already_invited.union(pv)
			offset = int(request.params['offset'])
			friends, is_complete, offset = c.user.get_friends(c.method, offset = offset)
			c.friends = OrderedDict([(id, friends[id]) for id in sorted(friends, key=lambda x: friends[x]['name']) if id not in already_invited])
			return {'data':{'is_complete':is_complete, 'offset':offset, 'html':render('/invite/networkfriends.html').strip()}}
		return {'success':False}
	
	def _return_to_input(self, invitees):
		c.enforce_blocks = True
		c.invitees = {}
		c.messages.append(ErrorMessage(_("FF_INVITE_PAGE_ERRORBAND_Please fill in below values correctly.")))
		for inv in invitees:
			netw = inv['network'].lower()
			invs = c.invitees.get(netw,{})
			invs[str(inv['network_id'])] = inv
			c.invitees[netw] = invs
		return self._display_invites(c.invitees)
	
	
	
	@logged_in(ajax=False)
	def friends(self, pool_url):
		data = simplejson.loads(request.params.get('invitees') or '{}')
		invitees = data.get("invitees")
		c.workflow = request.params.get("v") or "1"
		c.errors = {}
		c.values = {}
		
		c.pool.is_secret = request.params.get("is_secret", False)
		if invitees:
			if not request.params.get('message'):
				c.errors['message']=_("Please input an Invite Message")
			if not request.params.get('subject'):
				c.errors['subject']=_("Please input an Invite Subject")
			if c.errors:
				c.values['subject'] = request.params.get('subject')
				c.values['message'] = request.params.get('message')
				return self._return_to_input(invitees)
		
		
		#determine state of permissions and require missing ones
		perms_required = checkadd_block('email') # true if email is required and missing
		if invitees is not None:
			has_stream_publish_invitees = False
			has_create_event_invitees = False
			has_fb_invites = len(filter(lambda x: x.get('network') == 'facebook', invitees or []))
			if has_fb_invites:
				if c.pool.am_i_admin(c.user):
					has_create_event_invitees = True
				else:
					has_stream_publish_invitees = True
				perms_required = (has_create_event_invitees and checkadd_block('create_event') or remove_block('create_event'))
				perms_required = (has_stream_publish_invitees and checkadd_block('fb_streampub') or remove_block('fb_streampub')) or perms_required 
		if perms_required:
			log.error("PERMS_REQUIRED, ###TODO: deprecated!!!")
			return self._return_to_input(invitees)
		
		if invitees:
			invittes_proc_result = g.dbm.set(AddInviteesProc(p_url = c.pool.p_url
							, event_id = c.pool.event_id
							, inviter_user_id = c.user.u_id
							, users=[PoolInvitee.fromMap(el) for el in invitees]
							, subject = request.params.get('subject')
							, message = request.params.get('message')
							, is_secret = c.pool.is_secret))
			g.dbm.expire(Pool(p_url = c.pool.p_url))
			tasks = deque()
			for i in invitees:
				if i['network'] != 'email':
					tasks.append(remote_profile_picture_render.subtask(args=[[(i['network'], i['network_id'],i['large_profile_picture_url'])]]))
			job = TaskSet(tasks=tasks)
			job.apply_async()
			
			remote_pool_picture_render.apply_async(args=[c.pool.p_url])
		return redirect(url('ctrlpoolindex', controller='pool', pool_url = c.pool.p_url, v=c.workflow))
	
	
	@jsonify
	def preview(self, pool_url):
		c.method = request.params.get("method") or "facebook"
		c.subject = request.params.get("subject")
		c.message = request.params.get("message")
		if c.method=="email":
			return  {"popup":self.render("/invite/preview/preview_email.html").strip()}
		elif c.method=="twitter":
			return  {"popup":self.render("/invite/preview/preview_twitter.html").strip()}
		else:
			return  {"popup":self.render("/invite/preview/preview_facebook.html").strip()}
	

	@jsonify
	@post_only(ajax=True)
	def validate(self):
		params = variable_decode(request.params)
		invitee = params.get("invitee")
		network = invitee['network']
		if network == 'email':
			c.email_values = c.email_errors = {}
			try:
				form_result = PoolEmailInviteeForm().to_python(invitee, state=FriendFundFormEncodeState)
			except formencode.validators.Invalid, error:
				c.email_errors = error.error_dict or {}
				c.email_values = error.value
				return {"data":{'success':False, 'html':render_def('/invite/inviter.html', 'mailinviter').strip()}}
			else:
				c.method = 'email'
				invitee['success'] = True
				invitee['profile_picture_url'] = invitee.get('profile_picture_url', h.get_user_picture(None, "PROFILE_S", ext="png", site_root=request.qualified_host))
				invitee['large_profile_picture_url'] = invitee.get('large_profile_picture_url', h.get_user_picture(None, "POOL", ext="png", site_root=request.qualified_host))
				invitee['html'] = render_def('/invite/inviter.html', 'render_email_friends', friends = {invitee['network_id']:invitee}, active = True, class_='selectable').strip()
				invitee['input_html'] = render_def('/invite/inviter.html', 'mailinviter').strip()
				return {'clearmessage':True, 'data':invitee}
		else:
			return self.ajax_messages(_(u"RECEIVER_ADD_Unknown Network or Method"))