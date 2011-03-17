import formencode
from friendfund.model.forms.common import CurrencyValidator, PWDValidator

_ = lambda x:x

class LoginForm(formencode.Schema):
	allow_extra_fields = True
	filter_extra_fields = True
	email = formencode.validators.Email(not_empty=True, min=5, max = 255, resolve_domain=False, messages={'empty': _('FF_SIGNUP_ERROR_EMAIL_Please enter an email !')})
	pwd = PWDValidator(not_empty=True, messages={'empty': _('FF_SIGNUP_ERROR_PWD_Please enter a password !')})

class EmailRequestForm(formencode.Schema):
	allow_extra_fields = True
	filter_extra_fields = True
	email = formencode.validators.Email(not_empty=True, min=5, max = 255, resolve_domain=True, messages={'empty': _('FF_SIGNUP_ERROR_EMAIL_Please enter an email !')})

class PasswordResetForm(formencode.Schema):
	allow_extra_fields = True
	filter_extra_fields = True
	pwd = PWDValidator(not_empty=True, min=5, max = 255)
	pwd_confirm = PWDValidator(not_empty=True, min=5, max = 255)
	chained_validators = [formencode.validators.FieldsMatch('pwd','pwd_confirm')]


class ReceiverForm(formencode.Schema):
	allow_extra_fields = True
	filter_extra_fields = True
	name = formencode.validators.String(not_empty=True, min=1, max = 255)
	email =  formencode.validators.Email(not_empty=True, min=5, max = 255, resolve_domain=True)
	gender = formencode.validators.String(not_empty=True, min=1, max = 1)

class SignupForm(formencode.Schema):
	allow_extra_fields = True
	filter_extra_fields = True
	
	name = formencode.validators.String(not_empty=True, messages={'empty': _('FF_SIGNUP_ERROR_NAME_Please enter a name!')})
	email = formencode.validators.Email(not_empty=True, min=5, max = 255, resolve_domain=True, messages={'empty': _('FF_SIGNUP_ERROR_EMAIL_Please enter an email !')})
	pwd = PWDValidator(not_empty=True, min=5, max = 255, messages={'empty': _('FF_SIGNUP_ERROR_PWD_Please enter a password !')})

class MyProfileForm(formencode.Schema):
	allow_extra_fields = True
	
	is_default = formencode.validators.String()
	
	name = formencode.validators.String(not_empty=True)
	email =  formencode.validators.Email(not_empty=True, min=5, max = 255, resolve_domain=True)
	
class ShippingAddressForm(formencode.Schema):
	allow_extra_fields = True
	filter_extra_fields = True
	
	line1 = formencode.validators.String(not_empty=True, min=1, max = 255)
	line2 = formencode.validators.String(not_empty=True, min=1, max = 255)
	line3 = formencode.validators.String(not_empty=True, min=1, max = 255)
	zipcode = formencode.validators.String(not_empty=True, min=1, max = 10)
	country = formencode.validators.String(not_empty=True, min=1, max = 255)

class BillingAddressForm(formencode.Schema):
	allow_extra_fields = True
	filter_extra_fields = True
	
	line1 = formencode.validators.String(not_empty=True, min=1, max = 255)
	line2 = formencode.validators.String(not_empty=True, min=1, max = 255)
	line3 = formencode.validators.String(not_empty=True, min=1, max = 255)
	zipcode = formencode.validators.String(not_empty=True, min=1, max = 10)
	country = formencode.validators.String(not_empty=True, min=1, max = 255)