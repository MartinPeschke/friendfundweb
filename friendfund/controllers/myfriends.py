import logging, formencode, random, itertools
from cgi import FieldStorage
from formencode.variabledecode import variable_decode
from ordereddict import OrderedDict

from pylons import request, response, session as websession, tmpl_context as c, url, config, app_globals as g, cache
from pylons.decorators import jsonify
from pylons.controllers.util import abort, redirect

from friendfund.lib import fb_helper, tw_helper, helpers as h
from friendfund.lib.auth.decorators import post_only, logged_in
from friendfund.lib.i18n import FriendFundFormEncodeState
from friendfund.lib.base import BaseController, render, _, render_def
from friendfund.model.authuser import UserNotLoggedInWithMethod
from friendfund.model.forms.pool import PoolEmailInviteeForm
from friendfund.tasks import photo_renderer, fb as fbservice, twitter as twservice

log = logging.getLogger(__name__)

class MyfriendsController(BaseController):
	@jsonify
	def method(self, method):
		c.method = str(method)
		if method in ['facebook', 'twitter']:
			is_complete = True
			offset = 0
			try:
				c.friends, is_complete, offset = c.user.get_friends(c.method)
			except UserNotLoggedInWithMethod, e:
				if c.method == 'facebook':
					result = self.ajax_messages()
					result['data'] = {'is_complete': True, 'success':False, 'html':render('/receiver/fb_login.html').strip()}
					return result
				else: 
					result = self.ajax_messages()
					result['data'] = {'is_complete': True, 'success':False, 'html':render('/receiver/tw_login.html').strip()}
					return result
			return {'data':{'is_complete':is_complete, 'success':True, 'offset':offset, 'html':render('/receiver/inviter.html').strip()}}
		else:
			return {'html':render('/receiver/inviter.html').strip()}
	
	@logged_in(ajax=False)
	@jsonify
	def get(self, pmethod):
		c.method = str(pmethod)
		if c.method in ['facebook', 'twitter']:
			is_complete = True
			offset = 0
			try:
				c.friends, is_complete, offset = c.user.get_friends(c.method)
				if c.method in ['facebook']:
					c.friends = OrderedDict(((k,v) for k,v in itertools.islice(c.friends.iteritems(), 0, 12)))
				else:
					c.friends = OrderedDict([(k,c.friends[k]) for k in random.sample(c.friends, len(c.friends)>12 and 12 or len(c.friends))])
			except UserNotLoggedInWithMethod, e:
				if c.method == 'facebook':
					result = self.ajax_messages()
					result['data'] = {'is_complete': True, 'success':False, 'html':render('/receiver/fb_login.html').strip()}
					return result
				else: 
					result = self.ajax_messages()
					result['data'] = {'is_complete': True, 'success':False, 'html':render('/receiver/tw_login.html').strip()}
					return result
			return {'data':{'is_complete':True, 'success':True, 'offset':0, 'html':render('/receiver/networkfriends.html').strip()}}
		else:
			return {'html':render('/receiver/inviter.html').strip()}
	
	@jsonify
	def get_extension(self, method):
		if method in ['twitter']:
			c.method = method
			offset = int(request.params['offset'])
			c.friends, is_complete, offset = c.user.get_friends(c.method, offset = offset)
			return {'data':{'is_complete':is_complete, 'offset':offset, 'html':render('/receiver/networkfriends.html').strip()}}
		return {'success':False}

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
		elif network == 'yourself' and not c.user.is_anon:
			data = invitee
			data['success'] = True
			data['network'] = c.user.get_current_network()
			data['network_id'] = (data['network'] == 'email' and c.user.default_email or c.user.network_id)
			data['name'] = c.user.name
			data['large_profile_picture_url'] = data['profile_picture_url'] = c.user.get_profile_pic('POOL')
			return {'clearmessage':True,'data':data}
		elif(c.user.is_anon):
			return {'data':
					{'success':False, 
					 'html':self.render('/receiver/login_required.html').strip()
					}
				}
		else:
			return self.ajax_messages(_(u"RECEIVER_ADD_Unknown Network or Method"))
