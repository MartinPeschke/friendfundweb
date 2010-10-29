import logging, formencode, uuid, md5, os, simplejson

from pylons import request, response, session as websession, tmpl_context as c, url, config, app_globals as g, cache
from pylons.decorators import jsonify
from pylons.controllers.util import abort, redirect
from cgi import FieldStorage
from formencode.variabledecode import variable_decode

from friendfund.lib import fb_helper, tools, tw_helper
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
		params = formencode.variabledecode.variable_decode(request.params)
		receiver = params.get('receiver', None)
		
		if not (tools.dict_contains(receiver, ['name', 'network', 'network_id'])
				or receiver.get('network', '').lower() == 'email'
				and tools.dict_contains(receiver, ['name', 'network', 'email'])):
			return self.ajax_messages(_("POOL_CREATE_No Known ReceiverFound"))
		
		receiver = dict([(k, receiver[k]) for k in receiver if receiver[k]])
		receiver = PoolUser(**receiver)
		receiver.is_receiver = True
		c.pool = websession.get('pool') or Pool()
		c.pool.participants = [receiver]
		c.pool.receiver = receiver
		websession['pool'] = c.pool
		return {'clearmessage':True, 'html':render('/receiver/button.html').strip()}
	
	@jsonify
	def method(self, method):
		c.furl = url('home') # TODO: this might break shit, fix
		c.method = str(method)
		if method in ['facebook', 'twitter']:
			try:
				c.friends, is_complete, offset = c.user.get_friends(c.method)
			except UserNotLoggedInWithMethod, e:
				if c.method == 'facebook':
					return {'html':render('/receiver/fb_login.html').strip()}
				else: 
					return {'html':render('/receiver/tw_login.html').strip()}
		return {'data':{'is_complete':is_complete, 'offset':offset, 'html':render('/receiver/inviter.html').strip()}}

	@jsonify
	def get_extension(self, method):
		if method in ['twitter']:
			c.method = method
			offset = request.params['offset']
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
				network_id = valid.to_python(invitee.get('networkid'), state = FriendFundFormEncodeState)
			except formencode.validators.Invalid, error:
				return {'data':{'success':False, 'message':'<span>%s</span>' % error}}
			else:
				network_id = invitee.get('networkid')
			imgurl = "/static/imgs/default_m.png"
			return {'clearmessage':True, 
					'data':{'success':True, 
							'email':network_id, 
							'network':network, 
							'name':invitee.get('networkname'), 
							'imgurl' : imgurl
						}
					}
		elif network == 'yourself' and not c.user.is_anon:
			network = c.user.network.lower()
			if network == 'email':
				network_id_name = 'email'
				network_id = c.user.email
			else:
				network_id_name = 'network_id'
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
							network_id_name:network_id, 
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

	# @tools.iframe_jsonify
	# def set(self):
		# TODO: this surely doesnt work anymore
		# c.receiver_values = {}
		# c.receiver_errors = {}
		# receiver = formencode.variabledecode.variable_decode(request.params).get('receiver', None)
		# schema = user.ReceiverForm()
		# try:
			# form_result = schema.to_python(receiver, state = FriendFundFormEncodeState)
		# except formencode.validators.Invalid, error:
			# c.receiver_values = error.value
			# c.receiver_errors = error.error_dict or {}
			# return {'type':'content', 'success':False, 'html':render('/receiver/panel.html').strip()}
		# else:
			# profile_picture_url = None
			# if ('profile_pic' in receiver and isinstance(receiver['profile_pic'], FieldStorage)):
				# profile_picture_url = get_upload_pic_name(str(uuid.uuid4()))
				# if not os.path.exists(ulpath):
					# os.makedirs(ulpath)
				# fname, ext = os.path.splitext(receiver['profile_pic'].filename)
				# fname = os.path.join(ulpath \
					# , '%s%s' % (md5.new(profile_picture_url).hexdigest(), ext))
				# outf = open(fname, 'wb')
				# outf.write(receiver['profile_pic'].file.read())
				# outf.close()
				# photo_renderer.remote_save_image.delay(fname, profile_picture_url)
			# c.receiver = PoolUser(name=receiver['name'], \
						# network = 'EMAIL', \
						# profile_picture_url = profile_picture_url,\
						# email=receiver['email'], sex=receiver['gender'])
		# return {'html':render('/receiver/button.html').strip()}
