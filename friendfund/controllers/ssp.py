import logging, formencode

from pylons import request, response, session, tmpl_context as c, url, app_globals as g, session as websession
from pylons.controllers.util import abort, redirect
from friendfund.model.common import SProcWarningMessage
from friendfund.model.ssp import SSPUserLogin, ANONUSER
from friendfund.model.forms.user import LoginForm
from friendfund.lib.auth.decorators import is_ssp_admin
from friendfund.lib.base import BaseController, render, _
from friendfund.lib.i18n import FriendFundFormEncodeState

log = logging.getLogger(__name__)

class SspController(BaseController):
	PAGES = [('Current Orders', 'orderoverview'), ('Order History', 'orderhistory')]
	def __before__(self, action, environ):
		c.furl = request.params.get("furl") or request.path_info
		c.user = websession.get('user', ANONUSER)
		c.pages = self.PAGES
		c.page = environ['wsgiorg.routing_args'][1]['action']
		if not g.isMerchantSite:
			return abort(404)
	def __after__(self, action, environ):
		websession['user'] = c.user
		websession.save()
	
	def index(self):
		c.login_values = {}
		return render("/ssp/login.html")
	def logout(self):
		c.user = ANONUSER
		return redirect(url(controller="ssp", action="index"))
	
	
	def login(self):
		c.login_values = {}
		c.login_errors = {}
		login = formencode.variabledecode.variable_decode(request.params).get('login', None)
		schema = LoginForm()
		try:
			form_result = schema.to_python(login, state = FriendFundFormEncodeState)
			c.login_values = form_result
			g.dbadmin.get(SSPUserLogin, **c.login_values)
			c.user = SSPUserLogin(**c.login_values)
		except formencode.validators.Invalid, error:
			c.login_values = error.value
			c.login_errors = error.error_dict or {}
			return render("/ssp/login.html")
		except SProcWarningMessage, e:
			c.login_errors = {'email':_("USER_LOGIN_UNKNOWN_EMAIL_OR_PASSWORD")}
			return render("/ssp/login.html")
		else:
			return redirect(url(controller='ssp', action='orderoverview'))
	
	@is_ssp_admin(ajax = False)
	def orderoverview(self):
		c.orders = []
		return render("/ssp/order_overview.html")
	@is_ssp_admin(ajax = False)
	def orderhistory(self):
		c.orders = []
		return render("/ssp/order_history.html")