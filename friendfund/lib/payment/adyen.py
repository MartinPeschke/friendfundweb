from pylons import config
import logging, urllib, urllib2

from friendfund.lib.payment.adyengateway import AdyenPaymentGateway

log = logging.getLogger(__name__)

USERNAME = config['app_conf']['adyen.user']
PASSWORD = config['app_conf']['adyen.password']
LOCATION = config['app_conf']['adyen.location']
ACCOUNT = config['app_conf']['adyen.merchantAccount']

gateway = AdyenPaymentGateway(LOCATION, USERNAME, PASSWORD, ACCOUNT)

class PaymentService(object):
	@classmethod
	def authorize(cls, contribution):
		args = [contribution.ref 
					,contribution.total
					,contribution.currency
					,contribution.methoddetails.ccHolder
					,contribution.methoddetails.ccNumber
					,contribution.methoddetails.ccExpiresMonth
					,contribution.methoddetails.ccExpiresYear
					,contribution.methoddetails.ccCode]
		result = gateway.authorise(*args)
		return result