import logging, formencode, uuid, md5, os, simplejson

from pylons import request, response, session as websession, tmpl_context as c, url, config, app_globals as g, cache
from pylons.decorators import jsonify
from pylons.controllers.util import abort, redirect
from cgi import FieldStorage
from formencode.variabledecode import variable_decode

from friendfund.lib import fb_helper, tw_helper
from friendfund.lib.auth.decorators import post_only
from friendfund.lib.base import BaseController, render, _
from friendfund.lib.helpers import get_upload_pic_name
from friendfund.lib.i18n import FriendFundFormEncodeState
from friendfund.model.forms import user, common
from friendfund.model.pool import PoolUser, Pool
from friendfund.model.authuser import UserNotLoggedInWithMethod
from friendfund.tasks import photo_renderer, fb as fbservice, twitter as twservice

log = logging.getLogger(__name__)
ulpath = config['pylons.paths']['uploads']

class ReceiverController(BaseController):
	navposition=g.globalnav[1][2]
	
	@jsonify
	def panel(self):
		c.method = c.user.get_current_network() or 'facebook'
		c.furl = url('home') # TODO: this might break shit, fix
		return {'data':{'html':render('/receiver/panel.html').strip(), 'method':c.method}}
	
	@jsonify
	def unset(self):
		c.pool = websession.get('pool') or Pool()
		del pool.receiver
		websession['pool'] = c.pool
		return {'clearmessage':True, 'html':render('/receiver/button.html').strip()}
	
	@jsonify
	def set(self):
		receiver = formencode.variabledecode.variable_decode(request.params)
		try:
			receiver = PoolUser.fromMap(receiver)
		except InsufficientParamsException, e:
			log.warning(str(e))
			return self.ajax_messages(_("POOL_CREATE_No Known ReceiverFound"))
		receiver.is_receiver = True
		c.pool = websession.get('pool') or Pool()
		receiver.profile_picture_url = receiver.large_profile_picture_url
		c.pool.participants = [receiver]
		c.pool.receiver = receiver
		websession['pool'] = c.pool
		return {'clearmessage':True, 'html':render('/receiver/button.html').strip()}
	
	@jsonify
	def method(self, method):
		c.furl = url('home') # TODO: this might break shit, fix
		c.method = str(method)
		if method in ['facebook', 'twitter']:
			is_complete = True
			offset = 0
			try:
				c.friends, is_complete, offset = c.user.get_friends(c.method)
			except UserNotLoggedInWithMethod, e:
				if c.method == 'facebook':
					result = self.ajax_messages()
					result['data'] = {'is_complete': True, 'html':render('/receiver/fb_login.html').strip()}
					return result
				else: 
					result = self.ajax_messages()
					result['data'] = {'is_complete': True, 'html':render('/receiver/tw_login.html').strip()}
					return result
			return {'data':{'is_complete':is_complete, 'offset':offset, 'html':render('/receiver/inviter.html').strip()}}
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
	def add(self):
		invitee = variable_decode(request.params).get('invitee', {})
		network = invitee.get('network')
		if network == 'email':
			valid = formencode.validators.Email(not_empty=True, min=5, max = 255, resolve_domain=True)
			try:
				network_id = valid.to_python(invitee.get('network_id'), state = FriendFundFormEncodeState)
			except formencode.validators.Invalid, error:
				return {'data':{'success':False, 'message':'<span>%s</span>' % error}}
			else:
				network_id = invitee.get('network_id')
			imgurl = "/static/imgs/default_m.png"
			return {'clearmessage':True, 
					'data':{'success':True, 
							'network_id':network_id, 
							'network':network, 
							'name':invitee.get('name'), 
							'imgurl' : imgurl
						}
					}
		elif network == 'yourself' and not c.user.is_anon:
			network = c.user.network.lower()
			if network == 'email':
				network_id = c.user.email
			else:
				network_id = c.user.network_id
			network_name = c.user.name
			imgurl = c.user.get_profile_pic('RA')
			
			if imgurl == c.user.profile_picture_url:
				if network == 'twitter':
					imgurl = tw_helper.get_profile_picture_url(c.user.profile_picture_url)
				elif network == 'facebook':
					imgurl = fb_helper.get_large_pic_url(c.user.network_id)
			return {'clearmessage':True, 
					'data':{'success':True, 
							'network_id':network_id, 
							'network':network, 
							'name':network_name, 
							'imgurl' : imgurl
						}
					}
		elif(c.user.is_anon):
			return {'data':
					{'success':False, 
					 'html':self.render('/receiver/login_required.html').strip()
					}
				}
		else:
			return self.ajax_messages(_(u"RECEIVER_ADD_Unknown Network or Method"))
