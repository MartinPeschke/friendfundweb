import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from friendfund.lib.base import BaseController, render

log = logging.getLogger(__name__)

class SspController(BaseController):
	def index(self):
		c.ssp_login = {}
		return render("/ssp/login.html")
	def login(self):
		return redirect(url(controller='ssp', action='orderhistory'))
	def orderhistory(self):
		c.orders = []
		return render("/ssp/order_history.html")