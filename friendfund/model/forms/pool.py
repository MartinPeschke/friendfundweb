import formencode
from friendfund.model.forms.common import DecimalValidator, CurrencyValidator, SettlementValidator, DecimalStringValidator, SanitizedHTMLString, ReceiverValidator

_ = lambda x:x

class PoolHomePageForm(formencode.Schema):
	allow_extra_fields = True
	amount = DecimalStringValidator(min=1, max=9999999, if_missing="")
	title = formencode.validators.String(max=100, if_missing="")

class PoolPartnerIFrameForm(formencode.Schema):
	allow_extra_fields = True
	occasion_name = formencode.validators.String(not_empty=True, max=140, messages={'empty': _('FF_PARTNERIFRAME_ERROR_TITLE_Please enter some event name!')})
	occasion_key = formencode.validators.String(not_empty=True, max=140, messages={'empty': _('FF_PARTNERIFRAME_ERROR_TITLE_Please enter some event key!')})
	receiver = ReceiverValidator(not_empty=True,messages={'empty': _('FF_PARTNERIFRAME_ERROR_TITLE_Please select a recipient!')})
	
class PoolCreateForm(formencode.Schema):
	allow_extra_fields = True
	
	amount = DecimalValidator(not_empty=True, min=1, max=9999999, messages={'empty': _('FF_POOLETAILS_ERROR_AMOUNT_Please enter some amount value!')})
	currency = CurrencyValidator(not_empty=True)
	title = formencode.validators.String(not_empty=True, max=100, messages={'empty': _('FF_POOLETAILS_ERROR_TITLE_Please enter some title text!')})
	description = SanitizedHTMLString(not_empty=True, messages={'empty': _('FF_POOLETAILS_ERROR_DESCR_Please enter some descriptive text!')})
	tracking_link = formencode.validators.String(if_missing=None, max=1024, if_empty=None)
	product_picture = formencode.validators.String(if_missing=None, max=1024)
	product_name = formencode.validators.String(if_missing=None, max=1024)
	product_description = formencode.validators.String(if_missing=None, max=4096)
	settlementOption = formencode.validators.String(not_empty = True, max=4096)
	chained_validators = [ 
					SettlementValidator() 
				]

class PoolEditPageForm(formencode.Schema):
	allow_extra_fields = True
	title = formencode.validators.String(not_empty=True, max=100, messages={'empty': _('FF_POOLETAILS_ERROR_TITLE_Please enter some title text!')})
	description = SanitizedHTMLString(not_empty=True, max=4096, messages={'empty': _('FF_POOLETAILS_ERROR_DESCR_Please enter some descriptive text!')})
	product_name = formencode.validators.String(max=1024, if_missing=None, if_empty=None)
	product_description = formencode.validators.String(max=10000, if_missing=None, if_empty=None)
	product_picture = formencode.validators.String(max=1000, if_missing=None, if_empty=None)

class PoolEmailInviteeForm(formencode.Schema):
	allow_extra_fields = True
	name = formencode.validators.String(not_empty=True, min=1, max = 255, messages={'empty': _('FF_INVITEE_ERROR_NAME_Please enter a name text!')})
	network_id = formencode.validators.Email(resolve_domain=False, messages={'empty': _('FF_INVITEE_ERROR_EMAIL_Please enter some email!')})

class PoolAddressForm(formencode.Schema):
	allow_extra_fields = True
	
	first_name = formencode.validators.String(not_empty=True, min=1, max = 255)
	last_name = formencode.validators.String(not_empty=True, min=1, max = 255)
	line1 = formencode.validators.String(not_empty=True, min=1, max = 255)
	line2 = formencode.validators.String(not_empty=True, min=1, max = 255)
	line3 = formencode.validators.String(not_empty=True, min=1, max = 255)
	zipcode = formencode.validators.String(not_empty=True, min=1, max = 10)
	country = formencode.validators.String(not_empty=True, min=2, max = 2)
	shipping_note = formencode.validators.String(max = 255)