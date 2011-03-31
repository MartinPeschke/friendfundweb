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
from friendfund.model.authuser import User, WebLoginUserByTokenProc, DBRequestPWProc, SetNewPasswordForUser, VerifyAdminEmailProc, OtherUserData, WebLoginUserByEmail, SetUserEmailProc, SetUserLocaleProc
from friendfund.model.common import SProcWarningMessage
from friendfund.model.forms.user import EmailRequestForm, PasswordResetForm, SignupForm, LoginForm, MyProfileForm
from friendfund.model.myprofile import GetMyProfileProc, SetDefaultProfileProc
from friendfund.tasks.twitter import remote_persist_user as tw_remote_persist_user

log = logging.getLogger(__name__)

class MyprofileController(BaseController):
	@logged_in(ajax=False)
	def account(self):
		c.values = {"name":"",
					"email":""}
		c.errors = {}
		c.myprofiles = g.dbm.get(GetMyProfileProc, u_id = c.user.u_id).profiles
		defaults = map(lambda x: x.network, filter(lambda x: x.is_default, c.myprofiles.values()))
		if len(defaults):
			default = defaults[0]
			c.values["is_default"] = default
		else:
			c.values["is_default"] = "email"
		if 'email' in c.myprofiles:
			c.values['name'] = c.myprofiles['email'].name
			c.values['email'] = c.myprofiles['email'].email
		return self.render('/myprofile/account.html')
		
	@logged_in(ajax=False)
	@default_domain_only()
	def save(self):
		c.errors = {}
		if request.method != 'POST':
			return redirect(url(controller='myprofile', action="account"))
		c.values = formencode.variabledecode.variable_decode(request.params)
		schema = MyProfileForm()
		g.dbm.set(SetDefaultProfileProc(u_id=c.user.u_id, network=c.values['is_default']))
		
		c.myprofiles = g.dbm.get(GetMyProfileProc, u_id = c.user.u_id).profiles
		defaults = map(lambda x: x.network, filter(lambda x: x.is_default, c.myprofiles.values()))
		if len(defaults):
			default = defaults[0]
			c.user.name = c.myprofiles[default].name
			c.user.profile_picture_url = c.myprofiles[default].profile_picture_url
		
		if h.contains_one_ne(c.values, ['email', 'name']):
			try:
				form_result = schema.to_python(c.values, state = FriendFundFormEncodeState)
				c.values = form_result
				c.values['network'] = 'email'
				c.values['u_id'] = c.user.u_id
				
				if ('profile_pic' in c.values and isinstance(c.values['profile_pic'], FieldStorage)):
					g.user_service.save_email_user_picture(c.values, c.values['profile_pic'])
				
				suppl_user = OtherUserData(**c.values)
				additional_user_data = g.dbm.call(suppl_user, User)
				
				c.user.set_network('email', 
								network_id =  c.user.default_email,
								access_token = None,
								access_token_secret = None
							)
			except formencode.validators.Invalid, error:
				c.values = error.value
				c.errors = error.error_dict or {}
				return self.render('/myprofile/account.html')
		c.messages.append(SuccessMessage(_("FF_ACCOUNT_Your changes have been changed.")))
		return redirect(url(controller='myprofile', action="account"))
	
	@logged_in(ajax=False)
	@default_domain_only()
	def notifications(self):
		return self.render('/myprofile/notifications.html')
	
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
		schema = LoginForm()
		try:
			form_result = schema.to_python(login, state = FriendFundFormEncodeState)
			c.login_values = form_result
			c.login_values['network'] = 'email'
			c.user = g.dbm.call(WebLoginUserByEmail(**c.login_values), User)
			c.user.set_network('email', 
							network_id = c.user.default_email,
							access_token = None,
							access_token_secret = None
						)
			c.user.network = 'email'
			return {"data":{"success":True}, 'login_panel':render('/myprofile/login_panel.html').strip()}
		except formencode.validators.Invalid, error:
			c.login_values = error.value
			c.login_errors = error.error_dict or {}
			return {'html':render_def('/myprofile/login_panel.html', 'renderPanel').strip()}
		except SProcWarningMessage, e:
			c.login_errors = {'email':_("USER_LOGIN_UNKNOWN_EMAIL_OR_PASSWORD")}
			return {'html':render_def('/myprofile/login_panel.html', 'renderPanel').strip()}
	@jsonify
	def loginpopup(self):
		c.login_values = {}
		c.login_errors = {}
		login = formencode.variabledecode.variable_decode(request.params).get('login', None)
		if not login:
			return {'popup':render('/myprofile/login_popup.html').strip()}
		schema = LoginForm()
		try:
			form_result = schema.to_python(login, state = FriendFundFormEncodeState)
			c.login_values = form_result
			c.login_values['network'] = 'email'
			c.user = g.dbm.call(WebLoginUserByEmail(**c.login_values), User)
			c.user.set_network('email', 
							network_id = c.user.default_email,
							access_token = None,
							access_token_secret = None
						)
			c.user.network = 'email'
			return {"data":{"success":True}, 'login_panel':render('/myprofile/login_panel.html').strip()}
		except formencode.validators.Invalid, error:
			c.login_values = error.value
			c.login_errors = error.error_dict or {}
			return {'popup':render('/myprofile/login_popup.html').strip()}
		except SProcWarningMessage, e:
			c.login_errors = {'email':_("USER_LOGIN_UNKNOWN_EMAIL_OR_PASSWORD")}
			return {'popup':render('/myprofile/login_popup.html').strip()}
	@jsonify
	def signuppopup(self):
		if not c.user.is_anon:
			return {"data":{"success":True}, 'login_panel':render('/myprofile/login_panel.html').strip()}
		c.signup_values = {}
		c.signup_errors = {}
		signup = formencode.variabledecode.variable_decode(request.params).get('signup', None)
		if not signup:
			return {'popup':render('/myprofile/signup_popup.html').strip()}
		try:
			c.user = g.user_service.signup_email_user(signup)
			return {"data":{"success":True}, 'login_panel':render('/myprofile/login_panel.html').strip()}
		except formencode.validators.Invalid, error:
			c.signup_values = error.value
			c.signup_errors = error.error_dict or {}
			return {'popup':render('/myprofile/signup_popup.html').strip()}
		except SProcWarningMessage, e:
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
			return {"data":{"success":True}, 'login_panel':render('/myprofile/login_panel.html').strip()}
		except formencode.validators.Invalid, error:
			c.values = error.value
			c.errors = error.error_dict or {}
			return {'popup':render('/myprofile/addemail_popup.html').strip()}
		except SProcWarningMessage, e:
			c.values = form_result
			c.errors = {"email":_("FF_RESETPASSWORD_Email is already owned by another user.")}
			return {'popup':render('/myprofile/addemail_popup.html').strip()}
	
	
	def password(self):
		c.pwd_values ={}
		c.pwd_errors ={}
		if request.method != 'POST':
			return self.render('/myprofile/password_request.html')
		pwd = formencode.variabledecode.variable_decode(request.params).get('pwd', None)
		schema = EmailRequestForm()
		try:
			form_result = schema.to_python(pwd, state = FriendFundFormEncodeState)
			email = form_result['email']
			g.dbm.set(DBRequestPWProc(email=email))
			c.messages.append(_(u"PROFILE_PASSWORD_A Password Email has been sent to: %s, please check Your Mailbox!") % email)
			return self.render('/myprofile/password_request.html')
		except formencode.validators.Invalid, error:
			c.pwd_values = error.value
			c.pwd_errors = error.error_dict or {}
			return self.render('/myprofile/password_request.html')
		except SProcWarningMessage, e:
			if str(e) == 'USER_DOESNT_EXIST':
				c.pwd_values = form_result
				c.pwd_errors = {'email':_(u"PROFILE_PASSWORD_Unknown Email Address")}
			elif str(e) == 'TOKEN_ALREADY_SENT_IN_LAST_24_HOURS':
				c.pwd_values = form_result
				c.pwd_errors = {'email':_(u"PROFILE_PASSWORD_Token Already Sent")}
			else:
				c.pwd_values = form_result
				c.pwd_errors = {'email':_(u"PROFILE_PASSWORD_Unknown Error Occured")}
			return self.render('/myprofile/password_request.html')
	
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
		lang = request.params.get('lang')
		if websession['lang'] == lang:
			return redirect(request.referer)
		if lang not in g.locales:
			abort(404)
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