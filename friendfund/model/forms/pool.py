import formencode
from friendfund.model.forms.common import DecimalValidator, CurrencyValidator, DateValidator

class ProductForm(formencode.Schema):
	tracking_link = formencode.validators.String(max=255)
	name = formencode.validators.String(max=255)
	description = formencode.validators.String(max=4096)
	
class OccasionForm(formencode.Schema):
	date = DateValidator(not_empty=True)
	
class PoolCreateForm(formencode.Schema):
	allow_extra_fields = True
	filter_extra_fields = True
	
	amount = DecimalValidator(not_empty=True, min=0.01, max=9999999)
	currency = CurrencyValidator(not_empty=True)
	title = formencode.validators.String(not_empty=True, max=255)
	description = formencode.validators.String(not_empty=True, max=4096)