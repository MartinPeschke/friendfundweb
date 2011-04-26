import logging, formencode,  simplejson, urlparse
from cgi import FieldStorage

from pylons import request, response, session as websession, tmpl_context as c, url, app_globals as g, config
from pylons.controllers.util import abort, redirect
from pylons.decorators import jsonify
from pylons.i18n.translation import set_lang

from friendfund.lib.auth.decorators import logged_in, default_domain_only
from friendfund.lib.base import BaseController, render, _, render_def, SuccessMessage, ErrorMessage
from friendfund.lib.i18n import FriendFundFormEncodeState
from friendfund.lib import helpers as h
from friendfund.model.authuser import User, WebLoginUserByTokenProc, DBRequestPWProc, SetNewPasswordForUser, VerifyAdminEmailProc, OtherUserData, SetUserEmailProc, SetUserLocaleProc
from friendfund.model.common import SProcWarningMessage
from friendfund.model.forms.user import EmailRequestForm, PasswordResetForm, SignupForm, LoginForm, MyProfileForm, NotificationsForm
from friendfund.model.myprofile import GetMyProfileProc, SetDefaultProfileProc, OptOutNotificationsProc, OptOutTemplateType, GetMyPictureProc, ResetPasswordProc
from friendfund.tasks.twitter import remote_persist_user as tw_remote_persist_user
from friendfund.services import static_service as statics
log = logging.getLogger(__name__)

class MyprofileController(BaseController):
	@logged_in(ajax=False)
	@default_domain_only()
	def account(self):
		c.errors = {}
		c.myprofiles_result = g.dbm.get(GetMyPictureProc, u_id = c.user.u_id)
		c.mypictures = c.myprofiles_result.pictures
		if request.method != 'POST':
			c.values = c.myprofiles_result.to_map()
			return self.render('/myprofile/account.html')
		else:
			try:
				form_result = MyProfileForm().to_python(request.params, state = FriendFundFormEncodeState)
				c.values = form_result
				c.values['u_id'] = c.user.u_id
				if ('profile_pic' in c.values and isinstance(c.values['profile_pic'], FieldStorage)):
					c.values['profile_picture_url'] = g.user_service.save_email_user_picture(c.values, c.values['profile_pic'])
					c.values['is_uploaded'] = True
				
				c.values['is_rendered'] = statics.url_is_local(c.values['profile_picture_url'])
				g.dbm.set(GetMyPictureProc(**c.values))
				c.user.profile_picture_url = c.values['profile_picture_url']
				c.user.name = c.values['name']
				c.messages.append(SuccessMessage(_("FF_ACCOUNT_Your changes have been changed.")))
				return redirect(url.current())
			except formencode.validators.Invalid, error:
				c.values = error.value
				c.errors = error.error_dict or {}
				c.messages.append(ErrorMessage(_("FF_ADDRESS_Please correct the Errors below")))
				return self.render('/myprofile/account.html')
			except SProcWarningMessage, e:
				c.values = request.params
				c.errors = {'email':_("USER_SIGNUP_EMAIL_ALREADY_EXISTS")}
				c.messages.append(ErrorMessage(_("FF_ADDRESS_Please correct the Errors below")))
				return self.render('/myprofile/account.html')
	
	@logged_in(ajax=False)
	@default_domain_only()
	def notifications(self):
		c.values = {}
		c.errors = {}
		c.templatetypes = g.dbm.get(OptOutNotificationsProc, u_id = c.user.u_id).types
		if request.method != 'POST':
			return self.render('/myprofile/notifications.html')
		
		notifs = formencode.variabledecode.variable_decode(request.params).get("optout", {})
		try:
			schema = NotificationsForm()
			values = schema.to_python(notifs, state = FriendFundFormEncodeState)
			options = []
			for k,v in values.items():
				options.append(OptOutTemplateType(name = k, opt_out = v))
			c.templatetypes = g.dbm.set(OptOutNotificationsProc(u_id = c.user.u_id, types = options)).types
		except formencode.validators.Invalid, error:
			c.values = error.value
			c.errors = error.error_dict or {}
			return self.render('/myprofile/notifications.html')
		c.messages.append(SuccessMessage(_("FF_ACCOUNT_Your changes have been changed.")))
		return redirect(url(controller='myprofile', action="notifications"))
	
	@logged_in(ajax=False)
	@default_domain_only()
	def connections(self):
		c.myprofiles = g.dbm.get(GetMyProfileProc, u_id = c.user.u_id).profiles
		return self.render('/myprofile/connections.html')
	
	@logged_in(ajax=False)
	@default_domain_only()
	def password(self):
		c.accounts = g.dbm.get(GetMyProfileProc, u_id = c.user.u_id)
		c.is_pwd_create = "email" not in c.accounts.profiles
		c.values ={}
		c.errors ={}
		if request.method != 'POST':
			return self.render('/myprofile/account_password.html')
		pwd_data = formencode.variabledecode.variable_decode(request.params)
		try:
			form_result = PasswordResetForm().to_python(pwd_data, state = FriendFundFormEncodeState)
			g.dbm.set(ResetPasswordProc(u_id=c.user.u_id, **form_result))
			c.messages.append(SuccessMessage(_("FF_ACCOUNT_Your changes have been changed.")))
			return redirect(url(controller='myprofile', action="password"))
		except formencode.validators.Invalid, error:
			c.values = error.value
			c.errors = error.error_dict or {}
			c.messages.append(ErrorMessage(_("FF_ADDRESS_Please correct the Errors below")))
			return self.render('/myprofile/account_password.html')
		except SProcWarningMessage, e:
			if "CONSOLIDATION_FAILED_USERS_SHARE_OTHER_NETWORK_TYPE" in str(e) or "DONT_CONSOLIDATE" in str(e):
				c.messages.append(ErrorMessage(_("FF_ADDRESS_Your email address has already been claimed by another user, please choose a new one in your profile settings!")))
			elif "CURRENT_PASSWORD_WRONG" in str(e):
				c.messages.append(ErrorMessage(_("FF_ADDRESS_Please correct the Errors below")))
				c.errors = {'current_pwd':_(u"FF_PWD_PAGE_Current password incorrect!")}
			else:
				raise e
			c.values = form_result
			return self.render('/myprofile/account_password.html')
	
	def login(self):
		if not c.user.is_anon:
			response.headers['Content-Type'] = 'application/json'
			return simplejson.dumps({"data":{"success":True}, 'login_panel':render('/myprofile/login_panel.html').strip()})
		if c.user.is_anon and bool(c.user.user_data_temp):
			return self.addemailpopup()
		else:
			return self.loginpopup()
	
	@jsonify
	def loginpanel(self):
		if not c.user.is_anon:
			return {"data":{"success":True}, 'login_panel':render('/myprofile/login_panel.html').strip()}
		c.login_values = {}
		c.login_errors = {}
		c.expanded = True
		login = formencode.variabledecode.variable_decode(request.params).get('login', None)
		if not login:
			return {'popup':render('/myprofile/login_popup.html').strip()}
		try:
			c.user = g.user_service.login_email_user(login)
			return {"data":{"success":True, "has_activity":c.user.has_activity}, 'login_panel':render('/myprofile/login_panel.html').strip()}
		except formencode.validators.Invalid, error:
			c.login_values = error.value
			c.login_errors = error.error_dict or {}
			return {'html':render_def('/myprofile/login_panel.html', 'renderPanel').strip()}
		except SProcWarningMessage, e:
			c.login_values = login
			c.login_errors = {'email':_("USER_LOGIN_UNKNOWN_EMAIL_OR_PASSWORD")}
			return {'html':render_def('/myprofile/login_panel.html', 'renderPanel').strip()}
	@jsonify
	def loginpopup(self):
		c.login_values = {}
		c.login_errors = {}
		login = formencode.variabledecode.variable_decode(request.params).get('login', None)
		if not login:
			return {'popup':render('/myprofile/login_popup.html').strip()}
		try:
			c.user = g.user_service.login_email_user(login)
			return {"data":{"success":True, "has_activity":c.user.has_activity}, 'login_panel':render('/myprofile/login_panel.html').strip()}
		except formencode.validators.Invalid, error:
			c.login_values = error.value
			c.login_errors = error.error_dict or {}
			return {'popup':render('/myprofile/login_popup.html').strip()}
		except SProcWarningMessage, e:
			c.login_values = login
			c.login_errors = {'email':_("USER_LOGIN_UNKNOWN_EMAIL_OR_PASSWORD")}
			return {'popup':render('/myprofile/login_popup.html').strip()}
	@jsonify
	def signuppopup(self):
		if not c.user.is_anon:
			return {"data":{"success":True, "has_activity":c.user.has_activity}, 'login_panel':render('/myprofile/login_panel.html').strip()}
		c.signup_values = {}
		c.signup_errors = {}
		signup = formencode.variabledecode.variable_decode(request.params).get('signup', None)
		if not signup:
			return {'popup':render('/myprofile/signup_popup.html').strip()}
		try:
			c.user = g.user_service.signup_email_user(signup)
			return {"data":{"success":True, "has_activity":c.user.has_activity}, 'login_panel':render('/myprofile/login_panel.html').strip()}
		except formencode.validators.Invalid, error:
			c.signup_values = error.value
			c.signup_errors = error.error_dict or {}
			return {'popup':render('/myprofile/signup_popup.html').strip()}
		except SProcWarningMessage, e:
			c.signup_values = signup
			c.signup_errors = {'email':_("USER_SIGNUP_EMAIL_ALREADY_EXISTS")}
			return {'popup':render('/myprofile/signup_popup.html').strip()}
	##########################################################################################
	#Forgot Password Cycle
	
	@jsonify
	def rppopup(self):
		c.pwd_values ={}
		c.pwd_errors ={}
		pwd = formencode.variabledecode.variable_decode(request.params).get('pwd', None)
		if not pwd:
			return {'popup':render('/myprofile/forgotpassword_popup.html').strip()}
		schema = EmailRequestForm()
		try:
			form_result = schema.to_python(pwd, state = FriendFundFormEncodeState)
			email = form_result['email']
			g.dbm.set(DBRequestPWProc(email=email))
			c.messages.append(SuccessMessage(_("FF_An email with your new password has been sent to %(email)s.") % form_result))
			return {"reload":True}
		except formencode.validators.Invalid, error:
			c.pwd_values = error.value
			c.pwd_errors = error.error_dict or {}
			return {'popup':render('/myprofile/forgotpassword_popup.html').strip()}
		except SProcWarningMessage, e:
			c.pwd_values = pwd
			c.pwd_errors = {"email":_("FF_RESETPASSWORD_Email does not exist.")}
			return {'popup':render('/myprofile/forgotpassword_popup.html').strip()}	
	
	@jsonify
	def addemailpopup(self):
		c.values ={}
		c.errors ={}
		form = formencode.variabledecode.variable_decode(request.params).get('form', None)
		if not form:
			return {'popup':render('/myprofile/addemail_popup.html').strip()}
		schema = EmailRequestForm()
		try:
			form_result = schema.to_python(form, state = FriendFundFormEncodeState)
			
			c.user.user_data_temp['email'] = form_result['email']
			success, msg = g.user_service.login_or_consolidate(c.user.user_data_temp, tw_remote_persist_user)
			if not success:
				c.values = form_result
				c.errors = {"email":_("FF_RESETPASSWORD_Email is already owned by another user.")}
				return {'popup':render('/myprofile/addemail_popup.html').strip()}
			c.user.default_email = form_result['email']
			return {"data":{"success":True, "has_activity":c.user.has_activity}, 'login_panel':render('/myprofile/login_panel.html').strip()}
		except formencode.validators.Invalid, error:
			c.values = error.value
			c.errors = error.error_dict or {}
			return {'popup':render('/myprofile/addemail_popup.html').strip()}
		except SProcWarningMessage, e:
			c.values = form_result
			c.errors = {"email":_("FF_RESETPASSWORD_Email is already owned by another user.")}
			return {'popup':render('/myprofile/addemail_popup.html').strip()}
	
	def tlogin(self, token):
		c.messages.append(_("PROFILE_RESETPASSWORD_TOKEN_This link is no longer valid, please request a new password <a %s>here </a>") %\
					('onclick="xhrPost(\'%s\', {});closeLoginPanel();")'%url(controller='myprofile', action='rppopup')))
		return redirect(url("home"))
	
	def setpassword(self, token):
		"""
			/myprofile/setpassword/TOKENSTRING
			app.[web_login_token] '<LOGIN token = "sfgsdfvdfgwefgere"/>' 
		"""
		try:
			c.user = g.dbm.get(WebLoginUserByTokenProc, token=token)
			c.user.set_network('email', network_id = '1', access_token=None, access_token_secret=None) ###TODO: email is not returned by proc, would be needed to prevent fuckups
			return self.render('/myprofile/password_reset.html')
		except SProcWarningMessage, e:
			c.messages.append(_("PROFILE_RESETPASSWORD_TOKEN_Token expired or invalid"))
			return redirect(url(controller='myprofile', action='password'))
	
	@logged_in(ajax=False)
	def resetpwd(self):
		pwdreset = formencode.variabledecode.variable_decode(request.params).get('pwdreset', None)
		schema = PasswordResetForm()
		try:
			form_result = schema.to_python(pwdreset, state = FriendFundFormEncodeState)
			pwd = form_result['pwd']
			g.dbm.set(SetNewPasswordForUser(u_id = c.user.u_id, pwd=pwd))
			c.messages.append(_(u"PROFILE_RESETPASSWORD_Your password has been reset!"))
			return redirect(c.furl)
		except formencode.validators.Invalid, error:
			c.pwdreset_values = error.value
			c.pwdreset_errors = error.error_dict or {}
			return self.render('/myprofile/password_reset.html')
		except SProcWarningMessage, e:
			c.pwdreset_values = form_result
			c.pwdreset_errors = {'pwd':str(e)}
			return self.render('/myprofile/password_reset.html')
	
	def verify_email(self, token):
		try:
			g.dbm.set(VerifyAdminEmailProc(token=token))
		except SProcWarningMessage, e:
			c.messages.append(_(u"PROFILE_VERIFY_EMAIL_TOKEN_Token expired or invalid"))
		else:
			c.messages.append(_(u"PROFILE_VERIFY_EMAIL_TOKEN_Your Email Address has been verified. Thank You!"))
		return redirect(url('home'))

	def set_lang(self):
		if not isinstance(request.referer, basestring):
			abort(404)
		lang = h.negotiate_locale([request.params.get('lang', '')], g.LANGUAGES)
		if websession['lang'] == lang:
			return redirect(request.referer)
		else:
			websession['lang'] = lang
			set_lang(lang)
			if not c.user.is_anon:
				g.dbm.set(SetUserLocaleProc(locale=lang, u_id=c.user.u_id))
			
			scheme, domain, path, params, query_str, fragment = urlparse.urlparse(request.referer)
			if domain in request.qualified_host:
				match = config['routes.map'].match(path)
				if "lang" in match:
					match['lang'] = lang
					return redirect(urlparse.urlunparse((scheme, domain, url(**match), params, query_str, fragment)))
			return redirect(request.referer)