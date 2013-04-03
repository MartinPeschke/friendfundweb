import formencode
from friendfund.model.forms.common import CurrencyValidator, PWDValidator

_ = lambda x:x

class ContactForm(formencode.Schema):
	allow_extra_fields = True
	filter_extra_fields = True
	
	subject = formencode.validators.String(not_empty=True, min=5, max = 255, messages={'empty': _('FF_CONTACT_ERROR_SUBJECT_Please enter a subject!')})
	message = formencode.validators.String(not_empty=True, messages={'empty': _('FF_CONTACT_ERROR_MESSAGE_Please enter a message!')})
	name = formencode.validators.String(not_empty=True, messages={'empty': _('FF_CONTACT_ERROR_NAME_Please enter a name!')})
	email = formencode.validators.Email(not_empty=True, min=5, max = 255, resolve_domain=True, messages={'empty': _('FF_CONTACT_ERROR_EMAIL_Please enter an email !')})
class PartnerForm(formencode.Schema):
	allow_extra_fields = True
	filter_extra_fields = True
	
	message = formencode.validators.String(not_empty=True, messages={'empty': _('FF_CONTACT_ERROR_MESSAGE_Please enter a message!')})
	name = formencode.validators.String(not_empty=True, messages={'empty': _('FF_CONTACT_ERROR_NAME_Please enter a name!')})
	company = formencode.validators.String(not_empty=True, messages={'empty': _('FF_CONTACT_ERROR_NAME_Please enter a name!')})
	email = formencode.validators.Email(not_empty=True, min=5, max = 255, resolve_domain=True, messages={'empty': _('FF_CONTACT_ERROR_EMAIL_Please enter an email !')})