import logging, cgi, simplejson, urllib, urllib2, datetime

from pylons import request, tmpl_context as c, app_globals as g
from pylons.controllers.util import abort, redirect
from pylons.decorators import jsonify
from friendfund.lib.base import BaseController, render, _
from friendfund.lib import fb_helper
from friendfund.model import db_access
from friendfund.model.authuser import FBUserPermissions
from friendfund.model.pool import Pool
from friendfund.tasks.fb import get_email_from_permissions, remote_persist_user

log = logging.getLogger(__name__)

class FbController(BaseController):
	
	@jsonify
	def login(self):
		try:
			fb_data = fb_helper.get_user_from_cookie(request.cookies, g.FbApiKey, g.FbApiSecret.__call__(), c.user)
		except fb_helper.FBNotLoggedInException, e: 
			return {'reload':True}
			return {'message':_(u'FB_LOGIN_NOT_LOGGED_INTO_FACEBOOK_WARNING')}
		except fb_helper.FBLoggedInWithIncorrectUser, e: 
			return {'message':_("FB_LOGIN_TRY_This User cannot be consolidated with your current Account.")}
		user_data = dict([(k,v) for k,v in request.params.iteritems()])
		user_data.update(fb_data)
		user_data['network'] = 'facebook'
		try:
			user_data['birthday'] = datetime.datetime.strptime(user_data['birthday'], "%m/%d/%Y")
		except Exception, e:
			log.info("%s ----- %s", e, user_data)
			pass
		user_data['network_id'] = user_data.pop('id')
		user_data['profile_picture_url'] = fb_helper.get_large_pic_url(user_data['network_id'])
		user_data['access_token_secret'] = user_data.pop('secret')
		#Save and Persist, render profile
		success, msg = g.user_service.login_or_consolidate(user_data, remote_persist_user)
		if not success:
			return {'message':_("FB_LOGIN_TRY_This User cannot be consolidated with your current Account.")}
		else:
			if not c.user.has_perm('facebook', 'stream_publish'):
				perms = FBUserPermissions(network='facebook', network_id=user_data['network_id'], stream_publish = True)
				try:
					g.dbm.set(perms)
				except db_access.SProcException, e:
					log.error(str(e))
				c.user.set_perm('facebook', 'stream_publish', True)
			if not c.user.has_perm('facebook', 'create_event'):
				perms = FBUserPermissions(network='facebook', network_id=user_data['network_id'], create_event = True)
				try:
					g.dbm.set(perms)
				except db_access.SProcException, e:
					log.error(str(e))
				c.user.set_perm('facebook', 'create_event', True)
		return {"data":{"success":True, "has_activity":c.user.has_activity}, 'login_panel':render('/myprofile/login_panel.html').strip()}
	
	@jsonify
	def failed_login(self):
		try:
			fb_data = fb_helper.get_user_from_cookie(request.cookies, g.FbApiKey, g.FbApiSecret.__call__(), c.user)
		except fb_helper.FBNotLoggedInException, e: 
			return {'message':_(u'FB_LOGIN_NOT_LOGGED_INTO_FACEBOOK_WARNING')}
		except fb_helper.FBLoggedInWithIncorrectUser, e: 
			return {'message':_("FB_LOGIN_TRY_This User cannot be consolidated with your current Account.")}
		user_data = dict([(k,v) for k,v in request.params.iteritems()])
		user_data.update(fb_data)
		log.info("MISSINGPERMISSIONS:%s (%s)", request.params.get("missing_scope"), user_data)
		c.user.set_network('facebook',
			network_id = user_data.get('id'),
			access_token = user_data['access_token'],
			access_token_secret = user_data.get('secret')
		)
		return {"data":{"success":False}, 'login_panel':render('/myprofile/login_panel.html').strip()}
	
	def remove(self):
		try:
			user_id = fb_helper.get_user_from_signed_request(request.params, g.FbApiSecret.__call__())
		except fb_helper.FBIncorrectlySignedRequest, e: 
			log.error("DEAUTHORIZE with %s, %s", request.params, request.cookies)
			return '1'
		perms = FBUserPermissions(network='facebook', network_id=user_id, stream_publish = False, has_email = False, permanent = False, create_event = False)
		try:
			g.dbm.set(perms)
		except db_access.SProcException, e:
			log.error(str(e))
		return '1'
	def disconnect(self):
		self.remove()
		fb_data = fb_helper.get_user_from_cookie(request.cookies, g.FbApiKey, g.FbApiSecret.__call__(), c.user)
		try:
			g.user_service.disconnect(c.user, 'facebook', fb_data['uid'])
		except:
			pass
		print urllib2.urlopen("https://api.facebook.com/method/auth.revokeAuthorization?access_token=%s&format=json"%fb_data['access_token']).read()
		
		return {"data":{"success":True}}
		