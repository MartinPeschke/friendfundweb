import logging

from pylons import request, response, session as websession, tmpl_context as c, config, app_globals, url
from pylons.controllers.util import abort, redirect

from friendfund.lib.base import BaseController, render, _

log = logging.getLogger(__name__)

class FacebookStaticController(BaseController):
	def index(self):
		return render("/facebook_static/like_page.html")