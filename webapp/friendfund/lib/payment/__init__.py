from friendfund.lib.payment.adyen import CreditCardPayment, RedirectPayment

class PaymentFactory(object):
    def __init__(self
                 ,gtw_location
                 ,gtw_username
                 ,gtw_password
                 ,gtw_account
                 ,hosted_base_url
                 ,hosted_skincode
                 ,merchantaccount
                 ,hosted_sign_secret):

        self.gtw_location       = gtw_location
        self.gtw_username       = gtw_username
        self.gtw_password       = gtw_password
        self.gtw_account        = gtw_account
        self.hosted_base_url    = hosted_base_url
        self.hosted_skincode    = hosted_skincode
        self.merchantaccount    = merchantaccount
        self.hosted_sign_secret = hosted_sign_secret


    def get(self, pm):
        if pm.name == "paypal":
            return RedirectPayment('icon-%s.png' % pm.name, pm.name, ['EUR','GBP','USD'], pm.absolute_fee, pm.relative_fee
                                   ,base_url = self.hosted_base_url
                                   ,skincode = self.hosted_skincode
                                   ,merchantaccount = self.merchantaccount
                                   ,secret = self.hosted_sign_secret
            )
        else:
            return CreditCardPayment('icon-%s.png' % pm.name,  pm.name, ['EUR','GBP','USD'], pm.absolute_fee, pm.relative_fee
                                     ,gtw_location = self.gtw_location
                                     ,gtw_username = self.gtw_username
                                     ,gtw_password = self.gtw_password
                                     ,gtw_account = self.gtw_account
            )