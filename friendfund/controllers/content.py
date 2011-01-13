import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons.decorators import jsonify

_ = lambda x:x
FAQ_KEYS = [(_("STATIC_Frequently Asked Questions_Question1" ), _("STATIC_Frequently Asked Questions_Answer1" )),
			(_("STATIC_Frequently Asked Questions_Question2" ), _("STATIC_Frequently Asked Questions_Answer2" )),
			(_("STATIC_Frequently Asked Questions_Question3" ), _("STATIC_Frequently Asked Questions_Answer3" )),
			(_("STATIC_Frequently Asked Questions_Question4" ), _("STATIC_Frequently Asked Questions_Answer4" )),
			(_("STATIC_Frequently Asked Questions_Question5" ), _("STATIC_Frequently Asked Questions_Answer5" )),
			(_("STATIC_Frequently Asked Questions_Question6" ), _("STATIC_Frequently Asked Questions_Answer6" )),
			(_("STATIC_Frequently Asked Questions_Question7" ), _("STATIC_Frequently Asked Questions_Answer7" )),
			(_("STATIC_Frequently Asked Questions_Question8" ), _("STATIC_Frequently Asked Questions_Answer8" )),
			(_("STATIC_Frequently Asked Questions_Question9" ), _("STATIC_Frequently Asked Questions_Answer9" )),
			(_("STATIC_Frequently Asked Questions_Question10"), _("STATIC_Frequently Asked Questions_Answer10")),
			(_("STATIC_Frequently Asked Questions_Question11"), _("STATIC_Frequently Asked Questions_Answer11")),
			(_("STATIC_Frequently Asked Questions_Question12"), _("STATIC_Frequently Asked Questions_Answer12")),
			(_("STATIC_Frequently Asked Questions_Question13"), _("STATIC_Frequently Asked Questions_Answer13")),
			(_("STATIC_Frequently Asked Questions_Question14"), _("STATIC_Frequently Asked Questions_Answer14")),
			(_("STATIC_Frequently Asked Questions_Question15"), _("STATIC_Frequently Asked Questions_Answer15"))
		]

from friendfund.lib.base import BaseController, render, _
log = logging.getLogger(__name__)
class ContentController(BaseController):
	def __before__(self, action, environ):
		pass
	def __after__(self, action, environ):
		pass
	@jsonify
	def amazonhowto(self):
		return {"popup":self.render("/messages/popups/amazon.html").strip()}	
	@jsonify
	def pool_too_little_money(self):
		c.faq_items = FAQ_KEYS[1:2]
		c.faq_item_header = _("POOL_PAGE_What happens if we raise less money?")
		return {"popup":self.render("/messages/popups/faq_popup.html").strip()}
	@jsonify
	def why_transaction_costs(self):
		c.faq_items = FAQ_KEYS[2:3]
		c.faq_item_header = c.faq_items[0][0]
		return {"popup":self.render("/messages/popups/faq_popup.html").strip()}
	
	@jsonify
	def our_virtual_gifts_help(self):
		c.faq_items = FAQ_KEYS[12:15]
		c.faq_item_header = c.faq_items[0][0]
		return {"popup":self.render("/messages/popups/faq_popup.html").strip()}	
	
	@jsonify
	def invite_preview(self):
		return {"popup":self.render("/messages/popups/invite_preview.html").strip()}
	
	def contact(self):
		return self.render("/content/contact.html")
	def tos(self):
		return self.render("/content/tos.html")
	def privacy(self):
		return self.render("/content/privacy.html")
	def impressum(self):
		return self.render("/content/impressum.html")
	def faq(self):
		c.faq_items = FAQ_KEYS
		return self.render("/content/faq.html")
