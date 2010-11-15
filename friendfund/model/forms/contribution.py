import formencode
from friendfund.model.forms.common import MonetaryValidator, TotalTransactionCostValidator

class PaymentConfForm(formencode.Schema):
	allow_extra_fields = True
	filter_extra_fields = True
	
	amount = MonetaryValidator(not_empty=True, min=0.01, max=9999)
	total = MonetaryValidator(not_empty=False, min=0.01, max=9999)
	agreedToS = formencode.validators.StringBool(not_empty=True)
	is_secret = formencode.validators.StringBool(not_empty=False, if_missing=False)
	anonymous = formencode.validators.StringBool(if_missing=False)
	message = formencode.validators.String(max=140)
	payment_method = formencode.validators.String(not_empty=True)
	chained_validators = [
		TotalTransactionCostValidator("amount", "total")
	]

class CreditCardForm(formencode.Schema):
	allow_extra_fields = True
	filter_extra_fields = True
	
	ccType = formencode.validators.String(not_empty=True)
	ccHolder = formencode.validators.String(not_empty=True)
	ccNumber = formencode.validators.String(not_empty=True)
	ccCode = formencode.validators.String(not_empty=True)
	ccExpiresMonth = formencode.validators.Int(not_empty=True, min=1, max = 12)
	ccExpiresYear = formencode.validators.Int(not_empty=True, min=2010, max = 2100)
	
	chained_validators = [
		formencode.validators.CreditCardValidator("ccType", "ccNumber"),
		formencode.validators.CreditCardExpires("ccExpiresMonth", "ccExpiresYear"),
		formencode.validators.CreditCardSecurityCode("ccType", "ccCode")
	]