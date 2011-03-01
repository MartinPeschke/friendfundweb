import formencode
from friendfund.model.forms.common import DecimalValidator, CurrencyValidator, DateValidator#, SettlementValidator

class PoolHomePageForm(formencode.Schema):
	allow_extra_fields = True
	amount = DecimalValidator(not_empty=True, min=0.01, max=9999999)
	title = formencode.validators.String(not_empty=True, max=1024)


class PoolCreateForm(formencode.Schema):
	allow_extra_fields = True
	
	date = DateValidator(not_empty=True)
	amount = DecimalValidator(not_empty=True, min=0.01, max=9999999)
	currency = CurrencyValidator(not_empty=True)
	title = formencode.validators.String(not_empty=True, max=1024)
	description = formencode.validators.String(not_empty=True, max=4096)
	tracking_link = formencode.validators.String(if_missing=None, max=1024, if_empty=None)
	product_picture = formencode.validators.String(if_missing=None, max=1024)
	product_name = formencode.validators.String(if_missing=None, max=1024)
	product_description = formencode.validators.String(if_missing=None, max=4096)
	settlementOption = formencode.validators.String(not_empty=True) #SettlementValidator() #TODO: DO