import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons.decorators import jsonify

from friendfund.lib.base import BaseController, render, _

log = logging.getLogger(__name__)

class ContentController(BaseController):
	@jsonify
	def amazonhowto(self):
		return {"popup":self.render("/messages/popups/amazon.html").strip()}	
	@jsonify
	def pool_too_little_money(self):
		return {"popup":self.render("/messages/popups/pool_too_little_money.html").strip()}
	
	def contact(self):
		return self.render("/content/contact.html")
	def tos(self):
		return self.render("/content/tos.html")
	def privacy(self):
		return self.render("/content/privacy.html")
	def impressum(self):
		return self.render("/content/impressum.html")
	def faq(self):
		return self.render("/content/faq.html")
