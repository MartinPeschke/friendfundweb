import formencode
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