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
	
class NotificationsForm(formencode.Schema):
	allow_extra_fields = True
	filter_extra_fields = True
	
	COMMENT_NOTIFICATION = formencode.validators.StringBool(if_empty=True, if_missing=True)
	CONTRIBUTION_NOTIFICATION = formencode.validators.StringBool(if_empty=True, if_missing=True)
	INVITE = formencode.validators.StringBool(if_empty=True, if_missing=True)
	NEWSLETTER = formencode.validators.StringBool(if_empty=True, if_missing=True)
	REMINDER = formencode.validators.StringBool(if_empty=True, if_missing=True)


class PasswordResetForm(formencode.Schema):
	allow_extra_fields = True
	filter_extra_fields = True
	
	is_create = formencode.validators.StringBool(if_empty=False, if_missing=False)
	current_pwd = PWDValidator(not_empty=False, if_empty=None, if_missing=None, min=5, max = 255)
	new_pwd = PWDValidator(not_empty=True, min=5, max = 255, messages={'empty': _('FF_PWD_PAGE_ERROR_Please enter your new password !')})
	new_pwd_confirm = PWDValidator(not_empty=True, min=5, max = 255, messages={'empty': _('FF_PWD_PAGE_ERROR_Please re-enter your new password !')})
	chained_validators = [formencode.validators.FieldsMatch('new_pwd','new_pwd_confirm')]
