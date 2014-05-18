import formencode
from friendfund.model.forms.common import MonetaryValidator, TotalTransactionCostValidator, TOSValidator, PaymentMethodValidator

_ = lambda x:x

class PaymentConfForm(formencode.Schema):
    allow_extra_fields = True
    filter_extra_fields = True

    amount = MonetaryValidator(not_empty=True, min=0.01, max=9999)
    total = MonetaryValidator(not_empty=False, min=0.01, max=9999)
    agreedToS = TOSValidator(not_empty=False, if_missing=False)
    is_secret = formencode.validators.StringBool(not_empty=False, if_missing=False)
    do_notify = formencode.validators.StringBool(if_empty=False, if_missing=False)
    message = formencode.validators.String(max=140)
    method = PaymentMethodValidator(not_empty=True)
    chained_validators = [
        TotalTransactionCostValidator("amount", "total")
    ]