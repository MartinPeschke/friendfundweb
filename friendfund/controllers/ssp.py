import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from friendfund.lib.base import BaseController, render

log = logging.getLogger(__name__)

class SspController(BaseController):	
	PAGES = [('Current Orders', 'orderoverview'), ('Order History', 'orderhistory')]
	def __before__(self, action, environ):
		c.pages = self.PAGES
		c.page = environ['wsgiorg.routing_args'][1]['action']
	def __after__(self, action, environ):
		pass
	def index(self):
		c.ssp_login = {}
		return render("/ssp/login.html")
	def login(self):
		return redirect(url(controller='ssp', action='orderoverview'))
	def orderoverview(self):
		c.orders = []
		return render("/ssp/order_overview.html")
	def orderhistory(self):
		c.orders = []
		return render("/ssp/order_history.html")