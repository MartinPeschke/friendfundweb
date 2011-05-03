import logging, formencode, md5
from pylons import request, response, session as websession, tmpl_context as c, url, app_globals as g
from pylons.controllers.util import abort, redirect
from pylons.decorators import jsonify
from webhelpers.html import escape

from friendfund.lib.auth.decorators import default_domain_only, provide_lang
from friendfund.lib.base import BaseController, render, _, SuccessMessage, set_lang
from friendfund.lib.i18n import FriendFundFormEncodeState
from friendfund.model.forms.contact import ContactForm
from friendfund.tasks.notifiers.email import send_email
log = logging.getLogger(__name__)

class ContentController(BaseController):
	@jsonify
	def amazonhowto(self):
		return {"popup":render("/content/popups/amazon.html").strip()}
	
	@jsonify
	def what_is_cvc(self):
		return {"popup":render("/content/popups/what_is_cvc.html").strip()}
		
	@jsonify
	def all_or_nothing(self, lang = None):
		return {"popup":render("/content/popups/all_or_nothing.html").strip()}
		
		
	@jsonify
	def pledging_faq(self):
		return {"popup":render("/content/popups/pledging_faq.html").strip()}
	
	@jsonify
	def invite_info(self):
		return {"popup":render("/content/popups/how_friends_invited_popup.html").strip()}
	@default_domain_only()
	def jobs(self):
		return self.render("/content/jobs.html")


	def impressum(self):
		return redirect(url(controller="content", action="aboutus"))
	def merchant_explain(self):
		return self.render("/content/merchant_explain.html")
		
		
	@provide_lang()
	def contact(self):
		c.errors = {}
		c.values = {}
		if request.method!="POST":
			return self.render("/content/contact.html")
		else:
			schema = ContactForm()
			c.values = formencode.variabledecode.variable_decode(request.params)
			try:
				c.data = schema.to_python(c.values, state = FriendFundFormEncodeState)
				msg = {}
				msg['email'] = g.SUPPORT_EMAIL
				msg['subject'] = "[CONTACT_FORM_REQUEST] %s" % c.data['email']
				msg['text'] = render("/messaging/internal/contact_form.html")
				log.info("SENT_CONTACT_REQUEST, %s", send_email(msg))
			except formencode.validators.Invalid, error:
				c.values = error.value
				c.errors = error.error_dict or {}
				return self.render("/content/contact.html")
		c.messages.append(SuccessMessage(_("FF_CONTACT_EMAIL_SENT_Your message has been sent to us, thank you for your time!")))
		return redirect(url.current())
	
	######LOCALIZED
		

	@provide_lang()
	def faq(self, lang = None):
		if lang:
			try:
				return self.render("/content/localized/faq_%s.html" % lang)
			except:
				return self.render("/content/localized/faq.html")
		else:
			return self.render("/content/localized/faq.html")
	
	@provide_lang()
	def become_partner(self, lang = None):
		return self.what_you_get(lang)
	
	@provide_lang()
	def what_you_get(self, lang = None):
		if lang:
			try:
				return self.render("/content/localized/partner/what_you_get_%s.html" % lang)
			except:
				return self.render("/content/localized/partner/what_you_get.html")
		else:
			return self.render("/content/localized/partner/what_you_get.html")
	
	@provide_lang()
	def how_it_works(self, lang = None):
		if lang:
			try:
				return self.render("/content/localized/partner/how_it_works_%s.html" % lang)
			except:
				return self.render("/content/localized/partner/how_it_works.html")
		else:
			return self.render("/content/localized/partner/how_it_works.html")
	
	@provide_lang()
	def pricing(self, lang = None):
		if lang:
			try:
				return self.render("/content/localized/partner/pricing_%s.html" % lang)
			except:
				return self.render("/content/localized/partner/pricing.html")
		else:
			return self.render("/content/localized/partner/pricing.html")
	
	@provide_lang()
	def set_it_up(self, lang = None):
		if lang:
			try:
				return self.render("/content/localized/partner/set_it_up_%s.html" % lang)
			except:
				return self.render("/content/localized/partner/set_it_up.html")
		else:
			return self.render("/content/localized/partner/set_it_up.html")
	





	
	@provide_lang()
	def aboutus(self, lang = None):
		if lang:
			try:
				return self.render("/content/localized/aboutus_%s.html" % lang)
			except:
				return self.render("/content/localized/aboutus.html")
		else:
			return self.render("/content/localized/aboutus.html")
	

	@provide_lang()
	def tips(self, lang = None):
		if lang:
			try:
				return self.render("/content/localized/pool_tips_%s.html" % lang)
			except:
				return self.render("/content/localized/pool_tips.html")
		else:
			return self.render("/content/localized/pool_tips.html")

	@provide_lang()
	def learn_more(self, lang = None):
		if lang:
			try:
				return self.render("/content/localized/learnmore_%s.html" % lang)
			except:
				return self.render("/content/localized/learnmore.html")
		else:
			return self.render("/content/localized/learnmore.html")
		

	@provide_lang()
	def tos(self, lang = None):
		if lang:
			try:
				return self.render("/content/localized/tos_%s.html" % lang)
			except:
				return self.render("/content/localized/tos.html")
		else:
			return self.render("/content/localized/tos.html")

	@provide_lang()
	def confidence(self, lang = None):
		if lang:
			try:
				return self.render("/content/localized/confidence_%s.html" % lang)
			except:
				return self.render("/content/localized/confidence.html")
		else:
			return self.render("/content/localized/confidence.html")

	@provide_lang()
	def privacy(self, lang = None):
		if lang:
			try:
				return self.render("/content/localized/privacy_%s.html" % lang)
			except:
				return self.render("/content/localized/privacy.html")
		else:
			return self.render("/content/localized/privacy.html")