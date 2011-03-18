import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons.decorators import jsonify
from friendfund.lib.auth.decorators import default_domain_only

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
	@jsonify
	def amazonhowto(self):
		return {"popup":render("/content/popups/amazon.html").strip()}
	
	@jsonify
	def pool_too_little_money(self):
		c.faq_items = FAQ_KEYS[1:2]
		c.faq_item_header = _("POOL_PAGE_What happens if we raise less money?")
		return {"popup":render("/content/popups/faq_popup.html").strip()}
	@jsonify
	def why_transaction_costs(self):
		c.faq_items = FAQ_KEYS[2:3]
		c.faq_item_header = c.faq_items[0][0]
		return {"popup":render("/content/popups/faq_popup.html").strip()}
	
	@jsonify
	def what_is_cvc(self):
		return {"popup":render("/content/popups/what_is_cvc.html").strip()}
	@jsonify
	def pledging_faq(self):
		return {"popup":render("/content/popups/pledging_faq.html").strip()}
	
	@jsonify
	def profile_help(self):
		c.faq_items = FAQ_KEYS[9:12]
		c.faq_item_header = c.faq_items[0][0]
		return {"popup":render("/content/popups/faq_popup.html").strip()}
	
	@jsonify
	def invite_info(self):
		return {"popup":render("/content/popups/how_friends_invited_popup.html").strip()}	
	
	@default_domain_only()
	def contact(self):
		return render("/content/contact.html")
	@default_domain_only()
	def aboutus(self):
		return render("/content/aboutus.html")
	
	@default_domain_only()
	def tos(self, lang = None):
		if lang:
			try:
				return render("/content/tos_%s.html" % lang)
			except:
				return render("/content/tos.html")
		else:
			return render("/content/tos.html")
	
	@default_domain_only()
	def jobs(self):
		return render("/content/jobs.html")
	@default_domain_only()
	def privacy(self, lang):
		if lang:
			try:
				return render("/content/privacy_%s.html" % lang)
			except:
				return render("/content/privacy.html")
		else:
			return render("/content/privacy.html")
	@default_domain_only()
	def impressum(self):
		return render("/content/impressum.html")
	def merchant_explain(self):
		return render("/content/merchant_explain.html")
	@default_domain_only()
	def learn_more(self):
		return render("/content/learnmore.html")
	@default_domain_only()
	def become_partner(self):
		return render("/content/become_partner.html")
	@default_domain_only()
	def faq(self):
		c.faq_items = FAQ_KEYS
		return render("/content/faq.html")
