import logging

from pylons import request, response, tmpl_context as c, app_globals, url
from pylons.controllers.util import redirect

from pylons.templating import render_mako as render
from pylons.i18n import ugettext as _
from pylons.decorators import jsonify

from friendfund.lib.auth.decorators import logged_in
from friendfund.lib.base import BaseController
from friendfund.lib import fb_helper
from friendfund.model import db_access
from friendfund.model.authuser import NetworkUserPermissions
from friendfund.tasks.fb import remote_persist_user

log = logging.getLogger(__name__)

class FbController(BaseController):
    @jsonify
    def login(self):
        if "error" in request.params:
            return {'login':{'success': False}}
        try:
            user_data = fb_helper.extract_user_data(request, app_globals, c, response)
        except (fb_helper.FBNoCookiesFoundException, fb_helper.FBNotLoggedInException), e:
            log.error(e)
            return {'login':{'success': False}}
        except fb_helper.FBLoggedInWithIncorrectUser, e:
            log.error(e)
            return {'login':{'success': False},'message':_("FB_LOGIN_TRY_This User cannot be consolidated with your current Account.")}
        #Save and Persist, render profile
        success, msg = app_globals.user_service.login_or_consolidate(user_data, remote_persist_user)
        scope = request.params.get("scope")
        if scope:
            perms = c.user.get_perm_network(network='facebook', network_id=user_data['network_id'])
            if perms.add_perms_from_scope(scope, user_data['email']):
                try:
                    app_globals.dbm.set(perms)
                except (db_access.SProcWarningMessage,db_access.SProcException), e:
                    pass
        if success:
            return {"login":{"success": True, "has_activity":c.user.has_activity,'panel':render('/myprofile/login_panel.html').strip()}}
        else:
            return {'login':{'success': False},'message': msg}

    @jsonify
    def failed_login(self):
        try:
            fb_data = fb_helper.get_user_from_cookie(request.cookies, app_globals.FbApiKey, app_globals.FbApiSecret.__call__(), c.user)
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
                           )
        return {"login":{"success":False}}

    def remove(self):
        try:
            user_id = fb_helper.get_user_from_signed_request(request.params, app_globals.FbApiSecret.__call__())
        except fb_helper.FBIncorrectlySignedRequest, e:
            log.error("DEAUTHORIZE with %s, %s", request.params, request.cookies)
            return '1'
        perms = NetworkUserPermissions(network='facebook', network_id=user_id, stream_publish = False, has_email = False, permanent = False, create_event = False)
        try:
            app_globals.dbm.set(perms)
        # user =  app_globals.dbm.get(User, network = "facebook",network_id = user_id)
        # app_globals.user_service.disconnect(user, 'facebook', user_id)
        except (db_access.SProcException, db_access.SProcWarningMessage), e:
            pass
        return '1'

    @logged_in()
    def disconnect(self):
        app_globals.user_service.disconnect(c.user, 'facebook', request.params.get("network_id"))
        return redirect(url(controller="myprofile", action="connections"))
