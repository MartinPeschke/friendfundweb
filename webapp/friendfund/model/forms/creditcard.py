import formencode

_ = lambda x:x

class CreditCardForm(formencode.Schema):
	allow_extra_fields = True
	
	ccType = formencode.validators.String(not_empty=True)
	ccHolder = formencode.validators.String(not_empty=True, messages={'empty': _("FF_CONTRIBPAGE_ERROR_Your full name as it appears on the card")})
	ccNumber = formencode.validators.String(not_empty=True, messages={'empty': _('FF_CONTRIBPAGE_ERROR_ccNumber_Please enter your credit card number!')})
	ccCode = formencode.validators.String(not_empty=True, messages={'empty': _('FF_CONTRIBPAGE_ERROR_ccCVC_Please enter your CVC number!')})
	ccExpiresMonth = formencode.validators.Int(not_empty=True, min=1, max = 12)
	ccExpiresYear = formencode.validators.Int(not_empty=True, min=2010, max = 2100)
	
	chained_validators = [
		formencode.validators.CreditCardValidator("ccType", "ccNumber"),
		formencode.validators.CreditCardExpires("ccExpiresMonth", "ccExpiresYear"),
		formencode.validators.CreditCardSecurityCode("ccType", "ccCode")
	]