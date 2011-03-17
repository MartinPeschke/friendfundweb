import formencode
from friendfund.model.forms.common import DecimalValidator, CurrencyValidator, DateValidator, SettlementValidator, DecimalStringValidator

_ = lambda x:x

class PoolHomePageForm(formencode.Schema):
	allow_extra_fields = True
	amount = DecimalStringValidator(min=0.01, max=9999999, if_missing="")
	title = formencode.validators.String(max=1024, if_missing="")


class PoolCreateForm(formencode.Schema):
	allow_extra_fields = True
	
	date = DateValidator(not_empty=True, messages={'empty': _('FF_POOLETAILS_ERROR_DATE_Please enter some date value!')})
	amount = DecimalValidator(not_empty=True, min=0.01, max=9999999, messages={'empty': _('FF_POOLETAILS_ERROR_AMOUNT_Please enter some amount value!')})
	currency = CurrencyValidator(not_empty=True)
	title = formencode.validators.String(not_empty=True, max=140, messages={'empty': _('FF_POOLETAILS_ERROR_TITLE_Please enter some title text!')})
	description = formencode.validators.String(not_empty=True, max=4096, messages={'empty': _('FF_POOLETAILS_ERROR_DESCR_Please enter some descriptive text!')})
	tracking_link = formencode.validators.String(if_missing=None, max=1024, if_empty=None)
	product_picture = formencode.validators.String(if_missing=None, max=1024)
	product_name = formencode.validators.String(if_missing=None, max=1024)
	product_description = formencode.validators.String(if_missing=None, max=4096)
	settlementOption = formencode.validators.String(not_empty = True, max=4096)
	chained_validators = [ 
					SettlementValidator() 
				]

class PoolEmailInviteeForm(formencode.Schema):
	allow_extra_fields = True
	name = formencode.validators.String(not_empty=True, min=1, max = 255, messages={'empty': _('FF_INVITEE_ERROR_NAME_Please enter a name text!')})
	network_id =  formencode.validators.Email(not_empty=True, min=5, max = 255, resolve_domain=True, messages={'empty': _('FF_INVITEE_ERROR_EMAIL_Please enter some email!')})