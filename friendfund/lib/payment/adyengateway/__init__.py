from ZSI import TC
from ZSI.client import Binding
from ZSI.auth import AUTH
import Payment_services, Payment_services_types, logging

log = logging.getLogger("friendfund.lib.payment.adyengateway.AdyenPaymentGateway")

def parse_dict_into_request(obj, map):
	for k,v in map.iteritems():
		if v is None:
			continue
		elif isinstance(v, dict):
			newobj = getattr(obj, 'new_%s'%k)()
			newobj = parse_dict_into_request(newobj, v)
			getattr(obj, 'set_element_%s'%k)(newobj)
		else:
			getattr(obj, 'set_element_%s'%k)(v)
	return obj


class AdyenPaymentGateway(object):
	"""Payment Gateway utility for Adyen"""

	def __init__(self, url, user, password, merchantAccount):
		self.url = url
		self.user = user
		self.password = password
		self.merchantAccount = merchantAccount

	### AUTHORIZE PAYMENTS / RECURRINGs
	def _send_authorize(self, preq_params):
		service = Payment_services.PaymentHttpBindingSOAP(url=self.url, auth=(AUTH.httpbasic, self.user, self.password))
		req = Payment_services.authoriseRequest()
		preq = req.new_paymentRequest() ###additionalData, amount, card, merchantAccount, recurring, reference, shopperEmail, shopperIP, shopperReference, 
		preq = parse_dict_into_request(preq, preq_params)
		req.set_element_paymentRequest(preq)
		result = service.authorise(req)
		payment_result = result.get_element_paymentResult()
		result_data = dict([(k.replace("get_element_",""), getattr(payment_result, k)()) for k in dir(payment_result) if k.startswith('get_element')])
		log.debug("RECEIVED_PAYMENT_RESPONSE: %s", result_data)
		return result_data
		
	def authorise(self, txid, amount, currency, holderName, number, expiryMonth, expiryYear, cvc, shopperEmail = None, shopperReference=None):
		"""Send an authorise request"""
		preq_params = dict(
			merchantAccount=self.merchantAccount,
			reference=txid,
			shopperEmail=shopperEmail,
			shopperReference=shopperReference,
			amount=dict(value=amount,currency=currency),
			card = dict(cvc=cvc,expiryMonth=expiryMonth,expiryYear=expiryYear,holderName=holderName,number=number)
			)
		return self._send_authorize(preq_params)
	
	def authorise_recurring_contract(self, txid, amount, currency, holderName, number, expiryMonth, expiryYear, cvc, shopperEmail, shopperReference, recurringDetailName):
		preq_params = dict(
				merchantAccount=self.merchantAccount,
				reference=txid,
				shopperEmail=shopperEmail,
				shopperReference=shopperReference,
				amount=dict(value=amount,currency=currency),
				card = dict(cvc=cvc,expiryMonth=expiryMonth,expiryYear=expiryYear,holderName=holderName,number=number),
				recurring = dict(contract = 'RECURRING', recurringDetailName = recurringDetailName)
			)
		return self._send_authorize(preq_params)
	
	
	def use_last_recurring(self, txid, amount, currency, shopperEmail, shopperReference, selectedRecurringDetailReference = 'LATEST'):
		preq_params = dict(
			merchantAccount=self.merchantAccount,
			reference=txid,
			shopperEmail=shopperEmail,
			shopperReference=shopperReference,
			amount=dict(value=amount,currency=currency),
			shopperInteraction="ContAuth",
			selectedRecurringDetailReference = 'LATEST',
			recurring = dict(contract = 'RECURRING')
			)
		return self._send_authorize(preq_params)
	
	###### MODIFICATIONS
		
	def _send_modification(self, req, preq_params):
		log.debug("SENDING_MODIFICATION_REQUEST: %s", preq_params)
		preq = req.new_modificationRequest() ###merchantAccount, modificationAmount, originalReference
		preq = parse_dict_into_request(preq, preq_params)
		req.set_element_modificationRequest(preq)
		service = Payment_services.PaymentHttpBindingSOAP(url=self.url, auth=(AUTH.httpbasic, self.user, self.password))
		result = service.authorise(req)
		payment_result = result.get_element_paymentResult()
		result_data = dict([(k.replace("get_element_",""), getattr(payment_result, k)()) for k in dir(payment_result) if k.startswith('get_element')])
		log.debug("RECEIVED_MODIFICATION_RESPONSE: %s", preq_params)
		return result_data
	
	def cancel_or_refund(self, original_txid):
		req = Payment_services.cancelOrRefundRequest()
		preq_params = dict(
			merchantAccount=self.merchantAccount,
			originalReference=original_txid,
			)
		return self._send_modification(req, preq_params)
	
	def capture(self, original_txid, amount, currency):
		req = Payment_services.captureRequest()
		preq_params = dict(
			merchantAccount=self.merchantAccount,
			originalReference=original_txid,
			modificationAmount=dict(value = amount, currency = currency)
			)
		return self._send_modification(req, preq_params)
		
		
	def refund(self, original_txid, amount, currency):
		req = Payment_services.refundRequest()
		preq_params = dict(
			merchantAccount=self.merchantAccount,
			originalReference=original_txid,
			modificationAmount=dict(value = amount, currency = currency)
			)
		return self._send_modification(req, preq_params)
		
	def cancel(self, original_txid):
		req = Payment_services.cancelRequest()
		preq_params = dict(
			merchantAccount=self.merchantAccount,
			originalReference=original_txid
			)
		return self._send_modification(req, preq_params)
	