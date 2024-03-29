import logging

import formencode
from pylons import request, tmpl_context as c, url, app_globals as g
from pylons.decorators import jsonify
from pylons.i18n import ugettext as _
from pylons.templating import render_mako as render

from friendfund.lib.notifications.messages import SuccessMessage
from friendfund.lib.auth.decorators import default_domain_only, provide_lang
from friendfund.lib.base import BaseController
from friendfund.lib.i18n import FriendFundFormEncodeState
from friendfund.lib.routes_middleware import redirect
from friendfund.model.forms.contact import ContactForm, PartnerForm
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

    @provide_lang()
    def become_partner(self, lang = None):
        return redirect(url("short_content", action="what_you_get", lang=lang))
    @provide_lang()
    def set_it_up(self, lang = None):
        c.errors = {}
        c.values = {}
        if request.method!="POST":
            return self.render("/content/localized/partner/set_it_up.html")
        else:
            schema = PartnerForm()
            c.values.update(request.params)
            c.values = formencode.variabledecode.variable_decode(c.values)
            try:
                c.data = schema.to_python(c.values, state = FriendFundFormEncodeState)
                msg = {'email': g.SALES_EMAIL,
                       'subject': "[PARTNER_REQUEST] %s" % c.data['company'],
                       'text': render("/messaging/internal/partner_form.html")}
                log.info("SENT_PARTNER_REQUEST, %s", send_email(msg))
            except formencode.validators.Invalid, error:
                c.values = error.value
                c.errors = error.error_dict or {}
                return self.render("/content/localized/partner/set_it_up.html")
        c.messages.append(SuccessMessage(_("FF_CONTACT_EMAIL_SENT_Your message has been sent to us, thank you for your time!")))
        return redirect(url.current())

    def _localized_content(self, template, lang):
        if lang:
            try:
                return self.render("/content/localized/%s_%s.html" % (template, lang))
            except:
                return self.render("/content/localized/%s.html" % template)
        else:
            return self.render("/content/localized/%s.html" % template)
    @provide_lang()
    def aboutus(self, lang = None):
        return self._localized_content("aboutus", lang)
    @provide_lang()
    def imprint(self, lang = None):
        return self._localized_content("imprint", lang)
    @provide_lang()
    def learn_more(self, lang = None):
        return self._localized_content("pool_tips", lang)
    @provide_lang()
    def tos(self, lang = None):
        return self._localized_content("tos", lang)
    @provide_lang()
    def confidence(self, lang = None):
        return self._localized_content("confidence", lang)
    @provide_lang()
    def privacy(self, lang = None):
        return self._localized_content("privacy", lang)
    @provide_lang()
    def what_you_get(self, lang = None):
        return self._localized_content("partner/what_you_get", lang)
    @provide_lang()
    def how_it_works(self, lang = None):
        return self._localized_content("partner/how_it_works", lang)
    @provide_lang()
    def pricing(self, lang = None):
        return self._localized_content("partner/pricing", lang)
    @provide_lang()
    def faq(self, lang = None):
        return self._localized_content("faq", lang)