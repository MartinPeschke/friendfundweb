import logging, formencode, uuid, os, md5
from cgi import FieldStorage

from pylons import request, response, session as websession, tmpl_context as c, url, app_globals as g, config
from pylons.controllers.util import abort, redirect
from pylons.decorators import jsonify
from pylons.i18n.translation import set_lang

from friendfund.lib.auth.decorators import logged_in
from friendfund.lib.base import BaseController, render, _
from friendfund.lib.i18n import FriendFundFormEncodeState
from friendfund.model.authuser import User, WebLoginUserByTokenProc, DBRequestPWProc, SetNewPasswordForUser, VerifyAdminEmailProc, OtherUserData, UserNotLoggedInWithMethod
from friendfund.model.common import SProcWarningMessage
from friendfund.model.forms.user import PasswordRequestForm, PasswordResetForm, SignupForm, LoginForm, MyProfileForm
from friendfund.model.myprofile import GetMyProfileProc, SetDefaultProfileProc

log = logging.getLogger(__name__)

class MyprofileController(BaseController):
	navposition=g.globalnav[2][2]
	@logged_in(ajax=False)
	def index(self):
		c.myprofiles = g.dbm.get(GetMyProfileProc, u_id = c.user.u_id)
		c.myprofile_values = {'name' :getattr(c.myprofiles.profiles.get('email'), 'name', ''), 'email':getattr(c.myprofiles.profiles.get('email'), 'email', '')}
		return self.render('/myprofile/index.html')
	
	@jsonify
	def loginpanel(self):
		c.furl = request.params.get('furl', url('home'))
		if not c.user.is_anon:
			return {}
		c.login_values = {}
		c.login_errors = {}
		c.expanded = True
		login = formencode.variabledecode.variable_decode(request.params).get('login', None)
		schema = LoginForm()
		try:
			form_result = schema.to_python(login, state = FriendFundFormEncodeState)
			c.login_values = form_result
			c.login_values['network'] = 'email'
			c.user = g.dbm.get(User, **c.login_values)
			c.user.set_network('email', 
							network_id = None,
							access_token = None,
							access_token_secret = None
						)
			c.user.network = 'email'
			c.user.email = c.login_values['email']
			return {"redirect":c.furl}
		except formencode.validators.Invalid, error:
			c.login_values = error.value
			c.login_errors = error.error_dict or {}
			return {'html':render('/myprofile/login_panel.html').strip()}
		except SProcWarningMessage, e:
			c.login_errors = {'email':_("USER_LOGIN_UNKNOWN_EMAIL_OR_PASSWORD")}
			return {'html':render('/myprofile/login_panel.html').strip()}
	
	
	
	@logged_in(ajax=False)
	def save(self):
		c.myprofile_values = {}
		c.myprofile_errors = {}
		if request.method != 'POST':
			return redirect(url('controller', controller='myprofile'))
		myprofile = formencode.variabledecode.variable_decode(request.params).get('myprofile', None)
		schema = MyProfileForm()
		
		if 'is_default' in myprofile:
			g.dbm.set(SetDefaultProfileProc(u_id=c.user.u_id, network=myprofile['is_default']))
		
		c.myprofiles = g.dbm.get(GetMyProfileProc, u_id = c.user.u_id)
		try:
			myprofile['email'] = getattr(c.myprofiles.profiles.get('email'), 'email', '')
			form_result = schema.to_python(myprofile, state = FriendFundFormEncodeState)
			c.myprofile_values = form_result
			c.myprofile_values['network'] = 'email'
			c.myprofile_values['u_id'] = c.user.u_id
			
			if ('profile_pic' in myprofile and isinstance(myprofile['profile_pic'], FieldStorage)):
				g.user_service.save_email_user_picture(c.myprofile_values, myprofile['profile_pic'])
			
			if not c.myprofile_values.get("pwd"):
				del c.myprofile_values["pwd"]
				del c.myprofile_values["pwd_confirm"]
			
			suppl_user = OtherUserData(**c.myprofile_values)
			additional_user_data = g.dbm.call(suppl_user, User)
			
			c.user.set_network('email', 
							network_id = c.myprofile_values['email'],
							access_token = None,
							access_token_secret = None
						)
			c.messages.append(_("MYPROFILE_EMAILSEIGNUP_Changes saved!"))
			
			return redirect(url('controller', controller='myprofile'))
		except formencode.validators.Invalid, error:
			c.myprofile_values = error.value
			c.myprofile_errors = error.error_dict or {}
			# print c.myprofile_errors
			return self.render('/myprofile/index.html')
		except SProcWarningMessage, e:
			c.myprofile_errors = {'email':e}
			c.messages.append(_(u"USER_SIGNUP_If this is you, please try logging in with your email address and password or %(link_open)srequest a password change!%(link_close)s") \
							% {'link_open':'<a href="/myprofile/password">', 'link_close':'</a>'})
			return self.render('/myprofile/index.html')
	
	@logged_in(ajax=False)
	def add_email(self):
		c.signup_values = {}
		c.signup_errors = {}
		if request.method != 'POST':
			return redirect(url('controller', controller='myprofile'))
		signup = formencode.variabledecode.variable_decode(request.params).get('signup', None)
		schema = SignupForm()
		try:
			form_result = schema.to_python(signup, state = FriendFundFormEncodeState)
			c.signup_values = form_result
			c.signup_values['network'] = 'email'
			c.signup_values['u_id'] = c.user.u_id
			if ('profile_pic' in signup and isinstance(signup['profile_pic'], FieldStorage)):
				g.user_service.save_email_user_picture(c.signup_values, signup['profile_pic'])
			
			suppl_user = OtherUserData(**c.signup_values)
			additional_user_data = g.dbm.call(suppl_user, User)
				
			c.user.set_network('email', 
							network_id = c.signup_values['email'],
							access_token = None,
							access_token_secret = None
						)
			c.user.has_email = True
			c.user.email = c.signup_values['email']
			c.messages.append(_("MYPROFILE_EMAILSEIGNUP_Details saved!"))
			return redirect(url('controller', controller='myprofile'))
		except formencode.validators.Invalid, error:
			c.signup_values = error.value
			c.signup_errors = error.error_dict or {}
			c.myprofiles = g.dbm.get(GetMyProfileProc, u_id = c.user.u_id)
			return self.render('/myprofile/index.html')
		except SProcWarningMessage, e:
			c.signup_errors = {'email':e}
			c.messages.append(_(u"USER_SIGNUP_If this is you, please try logging in with your email address and password or %(link_open)srequest a password change!%(link_close)s") \
							% {'link_open':'<a href="/myprofile/password">', 'link_close':'</a>'})
			c.myprofiles = g.dbm.get(GetMyProfileProc, u_id = c.user.u_id)
			return self.render('/myprofile/index.html')
		
		
	##########################################################################################
	#Forgot Password Cycle
	def password(self):
		c.furl = request.referer
		c.pwd_values ={}
		c.pwd_errors ={}
		if request.method != 'POST':
			return self.render('/myprofile/password_request.html')
		pwd = formencode.variabledecode.variable_decode(request.params).get('pwd', None)
		schema = PasswordRequestForm()
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
		furl = request.params.get('furl', url('home'))
		if not c.user.is_anon:
			c.messages.append(_(u"USER_LOGIN_ALREADY_LOGGEDIN_WARNING!"))
			return redirect(furl)
		try:
			c.user = g.dbm.get(WebLoginUserByTokenProc, token=token)
		except SProcWarningMessage, e:
			c.messages.append(_("PROFILE_RESETPASSWORD_TOKEN_Token expired or invalid"))
		return redirect(furl)
	
	def setpassword(self, token):
		"""
			/myprofile/setpassword/TOKENSTRING
			app.[web_login_token] '<LOGIN token = "sfgsdfvdfgwefgere"/>' 
		"""
		c.furl = request.params.get('furl', url('home'))
		try:
			c.user = g.dbm.get(WebLoginUserByTokenProc, token=token)
			c.user.set_network('email', network_id = '1', access_token=None, access_token_secret=None) ###TODO: email is not returned by proc, would be needed to prevent fuckups
			return self.render('/myprofile/password_reset.html')
		except SProcWarningMessage, e:
			c.messages.append(_("PROFILE_RESETPASSWORD_TOKEN_Token expired or invalid"))
			return redirect(url(controller='myprofile', action='password'))
	
	@logged_in(ajax=False)
	def resetpwd(self):
		c.furl = request.params.get('furl', url('home'))
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
		if lang not in g.locale_lookup:
			abort(404)
		else:
			websession['lang'] = lang
			set_lang(lang)
			return redirect(request.referer)