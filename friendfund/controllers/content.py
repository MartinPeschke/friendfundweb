import logging, formencode, md5
from pylons import request, response, session as websession, tmpl_context as c, url, app_globals as g
from pylons.controllers.util import abort, redirect
from pylons.decorators import jsonify
from webhelpers.html import escape

from friendfund.lib.auth.decorators import default_domain_only
from friendfund.lib.base import BaseController, render, _, SuccessMessage, set_lang
from friendfund.lib.i18n import FriendFundFormEncodeState
from friendfund.lib.helpers import negotiate_locale_from_header
from friendfund.model.forms.contact import ContactForm
from friendfund.tasks.notifiers.email import send_email
log = logging.getLogger(__name__)

class ContentController(BaseController):
	
	def __before__(self, action, environ):
		super(ContentController, self).__before__(action, environ)
		routing = environ['wsgiorg.routing_args'][1]
		lang = routing.get('lang')
		if not lang or lang not in g.locales:
			lang = negotiate_locale_from_header(request.accept_language.best_matches(), g.locales)
			return redirect(url(routing['controller'], action = routing['action'], lang = lang))
		else:
			set_lang(lang)
		
	@jsonify
	def amazonhowto(self):
		return {"popup":render("/content/popups/amazon.html").strip()}
	
	@jsonify
	def what_is_cvc(self):
		return {"popup":render("/content/popups/what_is_cvc.html").strip()}
	@jsonify
	def pledging_faq(self):
		return {"popup":render("/content/popups/pledging_faq.html").strip()}
	
	@jsonify
	def invite_info(self):
		return {"popup":render("/content/popups/how_friends_invited_popup.html").strip()}
	@default_domain_only()
	def jobs(self):
		return self.render("/content/jobs.html")

	@default_domain_only()
	def impressum(self):
		return redirect(url(controller="content", action="aboutus"))
	def merchant_explain(self):
		return self.render("/content/merchant_explain.html")
		
		
	@default_domain_only()
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
	
	@default_domain_only()
	def faq(self, lang = None):
		if lang:
			try:
				return self.render("/content/localized/faq_%s.html" % lang)
			except:
				return self.render("/content/localized/faq.html")
		else:
			return self.render("/content/localized/faq.html")
	
	@default_domain_only()
	def become_partner(self, lang = None):
		if lang:
			try:
				return self.render("/content/localized/become_partner_%s.html" % lang)
			except:
				return self.render("/content/localized/become_partner.html")
		else:
			return self.render("/content/localized/become_partner.html")
		
	# @default_domain_only()
	def aboutus(self, lang = None):
		if lang:
			try:
				return self.render("/content/localized/aboutus_%s.html" % lang)
			except:
				return self.render("/content/localized/aboutus.html")
		else:
			return self.render("/content/localized/aboutus.html")
	
	# @default_domain_only()
	def learn_more(self, lang = None):
		if lang:
			try:
				return self.render("/content/localized/learnmore_%s.html" % lang)
			except:
				return self.render("/content/localized/learnmore.html")
		else:
			return self.render("/content/localized/learnmore.html")
		
	@default_domain_only()
	def tos(self, lang = None):
		if lang:
			try:
				return self.render("/content/localized/tos_%s.html" % lang)
			except:
				return self.render("/content/localized/tos.html")
		else:
			return self.render("/content/localized/tos.html")
	
	@default_domain_only()
	def privacy(self, lang = None):
		if lang:
			try:
				return self.render("/content/localized/privacy_%s.html" % lang)
			except:
				return self.render("/content/localized/privacy.html")
		else:
			return self.render("/content/localized/privacy.html")