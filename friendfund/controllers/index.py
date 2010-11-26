import logging, formencode, uuid, md5, os
from cgi import FieldStorage

from pylons import request, response, session as websession, tmpl_context as c, config, app_globals as g, url
from pylons.controllers.util import abort, redirect
from pylons.decorators import jsonify

from friendfund.lib.i18n import FriendFundFormEncodeState
from friendfund.lib.auth.decorators import logged_in, remove_block, enforce_blocks, clear_blocks
from friendfund.lib.base import BaseController, render, _
from friendfund.lib.helpers import get_upload_pic_name
from friendfund.lib import fb_helper
from friendfund.model.forms.user import LoginForm, SignupForm
from friendfund.model.common import SProcWarningMessage
from friendfund.model.authuser import User, SetUserEmailProc, DBRequestPWProc, ANONUSER
from friendfund.model.pool import Product
from friendfund.model.recent_activity import RecentActivityStream
from friendfund.tasks.photo_renderer import remote_save_image

log = logging.getLogger(__name__)
ulpath = config['pylons.paths']['uploads']

class IndexController(BaseController):
	navposition=g.globalnav[0][2]
	ra_total_page_size = 50
	ra_page_size = 5
	
	def index(self):
		c.recent_activity = g.dbm.get(RecentActivityStream)
		c.ra_offset = self.ra_page_size
		c.uuid = str(uuid.uuid4())
		if 'pool' in websession:
			c.pool = websession['pool']
		return self.render('/index.html')
	
	def test_error(self):
		return abort(500, "TEST")
	
	@jsonify
	def stream(self):
		c.recent_activity = g.dbm.get(RecentActivityStream)
		c.uuid = str(uuid.uuid4())
		return {"data":{"html":render("/widgets/ra_stream.html").strip()}}
	
	@jsonify
	def login_panel(self):
		return {'html':render('/myprofile/login_panel.html').strip()}
	
	
	@jsonify
	def logout(self):
		c.furl = request.params.get('furl', url('home'))
		c.user = ANONUSER
		c.settings = {}
		c.messages = []
		if 'invitees' in websession:
			del websession['invitees']
		if 'pool' in websession:
			del websession['pool']
		result = {'redirect':c.furl}
		clear_blocks()
		return result
	
	def login(self):
		c.furl = request.params.get('furl', url('home'))
		if not c.user.is_anon:
			c.messages.append(_(u"USER_LOGIN_ALREADY_LOGGEDIN_WARNING!"))
			return redirect(furl)
		c.login_values = {}
		c.login_errors = {}
		if request.method != 'POST':
			return self.render('/myprofile/login_screen.html')
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
			return redirect(c.furl)
		except formencode.validators.Invalid, error:
			c.login_values = error.value
			c.login_errors = error.error_dict or {}
			return self.render('/myprofile/login_screen.html')
		except SProcWarningMessage, e:
			c.login_errors = {'email':_("USER_LOGIN_UNKNOWN_EMAIL_OR_PASSWORD")}
			return self.render('/myprofile/login_screen.html')
	
	def signup(self):
		c.furl = request.params.get('furl', '')
		c.signup_values = {}
		c.signup_errors = {}
		if request.method != 'POST':
			return self.render('/myprofile/login_screen.html')
		signup = formencode.variabledecode.variable_decode(request.params).get('signup', None)
		schema = SignupForm()
		try:
			form_result = schema.to_python(signup, state = FriendFundFormEncodeState)
			c.signup_values = form_result
			c.signup_values['network'] = 'EMAIL'
			if ('profile_pic' in signup and isinstance(signup['profile_pic'], FieldStorage)):
				g.user_service.save_email_user_picture(c.signup_values, signup['profile_pic'])

			c.user = g.dbm.call(User(**c.signup_values), User)
			c.user.set_network('email', 
							network_id = None,
							access_token = None,
							access_token_secret = None
						)
			c.user.network = 'email'
			c.user.email = c.signup_values['email']
			return redirect(url('home'))
		except formencode.validators.Invalid, error:
			c.signup_values = error.value
			c.signup_errors = error.error_dict or {}
			return self.render('/myprofile/login_screen.html')
		except SProcWarningMessage, e:
			c.signup_errors = {'email':_("USER_SIGNUP_EMAIL_ALREADY_EXISTS")}
			c.messages.append(_(u"USER_SIGNUP_If this is you, please try logging in with your email address and password or %(link_open)srequest a password change!%(link_close)s") \
							% {'link_open':'<a href="/myprofile/password">', 'link_close':'</a>'})
			return self.render('/myprofile/login_screen.html')
	
	@jsonify
	@enforce_blocks('email')
	@logged_in(ajax=True)
	def set_email(self):
		if request.method != 'POST':
			return {'message':'Not allowed!'}
		elif not c.user.u_id:
			return {'message':'Not authorized!'}
		valid = formencode.validators.Email(not_empty=True, min=5, max = 255, resolve_domain=True)
		c.email = request.params.get('email', None)
		try:
			c.email = valid.to_python(c.email, state = FriendFundFormEncodeState)
			suep = SetUserEmailProc(u_id = c.user.u_id, name = c.user.name, email = c.email)
			g.dbm.set(suep)
			
			remove_block('email')
			c.user.email = c.email
			c.user.has_email = True
			c.messages.append(_(u'USER_SETEMAILBLOCK_Email Updated!'))
			return {'data':{'success':True}}
		except formencode.validators.Invalid, error:
			return {'data':{'success':False, 'message':'<span>%s</span>' % error}}
		except SProcWarningMessage, e:
			log.warning(str(e))
			return {'data':{'success':False, 'message':'<span>%s</span>' % _(u'USER_SETEMAILBLOCK_Email_Email Address already taken!')}}
