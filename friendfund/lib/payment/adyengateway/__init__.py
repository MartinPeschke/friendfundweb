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
    
	def authorise(self, txid, amount, currency, holderName, number,
			expiryMonth, expiryYear, cvc, shopperEmail = None, shopperReference=None):
		"""Send an authorise request"""
		
		service = Payment_services.PaymentHttpBindingSOAP(url=self.url, auth=(AUTH.httpbasic, self.user, self.password))
		req = Payment_services.authoriseRequest()
		preq = req.new_paymentRequest() ###additionalData, amount, card, merchantAccount, recurring, reference, shopperEmail, shopperIP, shopperReference, 
		preq = parse_dict_into_request(preq, dict(
			merchantAccount=self.merchantAccount,
			reference=txid,
			shopperEmail=shopperEmail,
			shopperReference=shopperReference,
			amount=dict(value=amount,currency=currency),
			card = dict(cvc=cvc,expiryMonth=expiryMonth,expiryYear=expiryYear,holderName=holderName,number=number)
			))
		req.set_element_paymentRequest(preq)
		result = service.authorise(req)
		payment_result = result.get_element_paymentResult()
		return dict([(k.replace("get_element_",""), getattr(payment_result, k)()) for k in dir(payment_result) if k.startswith('get_element')])    
	
	def authorise_recurring_contract(self, txid, amount, currency, holderName, number,
			expiryMonth, expiryYear, cvc, shopperEmail, shopperReference, recurringDetailName):
		"""Send an authorise request"""
		
		service = Payment_services.PaymentHttpBindingSOAP(url=self.url, auth=(AUTH.httpbasic, self.user, self.password))
		req = Payment_services.authoriseRequest()
		preq = req.new_paymentRequest() ###additionalData, amount, card, merchantAccount, recurring, reference, shopperEmail, shopperIP, shopperReference, 
		
		preq_params = dict(
			merchantAccount=self.merchantAccount,
			reference=txid,
			shopperEmail=shopperEmail,
			shopperReference=shopperReference,
			amount=dict(value=amount,currency=currency),
			card = dict(cvc=cvc,expiryMonth=expiryMonth,expiryYear=expiryYear,holderName=holderName,number=number),
			recurring = dict(contract = 'RECURRING', recurringDetailName = recurringDetailName)
			)
		log.info(preq_params)
		preq = parse_dict_into_request(preq, preq_params)
		req.set_element_paymentRequest(preq)
		result = service.authorise(req)
		payment_result = result.get_element_paymentResult()
		return dict([(k.replace("get_element_",""), getattr(payment_result, k)()) for k in dir(payment_result) if k.startswith('get_element')])
	
	
	def use_last_recurring(self, original_txid, amount, currency, shopperEmail, shopperReference, selectedRecurringDetailReference = 'LATEST'):
		"""Send an authorise request"""
		if len(filter(None, [txid, amount, currency, shopperEmail, shopperReference, selectedRecurringDetailReference])) < 6:
			raise ValueError("Received Empty Value for at least field:%s", [txid, amount, currency, shopperEmail, shopperReference, selectedRecurringDetailReference])
		service = Payment_services.PaymentHttpBindingSOAP(url=self.url, auth=(AUTH.httpbasic, self.user, self.password))
		req = Payment_services.authoriseRequest()
		preq = req.new_paymentRequest() ###additionalData, amount, card, merchantAccount, recurring, reference, shopperEmail, shopperIP, shopperReference, 
		
		preq_params = dict(
			merchantAccount=self.merchantAccount,
			reference=original_txid,
			shopperEmail=shopperEmail,
			shopperReference=shopperReference,
			amount=dict(value=amount,currency=currency),
			shopperInteraction="ContAuth",
			selectedRecurringDetailReference = 'LATEST',
			recurring = dict(contract = 'RECURRING')
			)
		log.info(preq_params)
		preq = parse_dict_into_request(preq, preq_params)
		req.set_element_paymentRequest(preq)
		result = service.authorise(req)
		payment_result = result.get_element_paymentResult()
		return dict([(k.replace("get_element_",""), getattr(payment_result, k)()) for k in dir(payment_result) if k.startswith('get_element')])
	
	def cancel(self, txid):
		pass
	def capture(self, txid, amount, currency):
		pass
	def refund(self, txid, amount, currency):
		pass
	