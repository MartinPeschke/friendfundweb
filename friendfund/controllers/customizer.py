import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from friendfund.lib.base import BaseController, render

log = logging.getLogger(__name__)

class CustomizerController(BaseController):
	def css(self):
		response.content_type = "text/css"
		return render('/customization/custom.css')
	def js(self):
		response.content_type = "application/x-javascript"
		return render('/customization/custom.js')