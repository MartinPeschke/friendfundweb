from ZSI import TC
from ZSI.client import Binding
from ZSI.auth import AUTH
import Payment_services, Payment_services_types


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
		preq = parse_dict_into_request(preq, dict(
			merchantAccount=self.merchantAccount,
			reference=txid,
			shopperEmail=shopperEmail,
			shopperReference=shopperReference,
			amount=dict(value=amount,currency=currency),
			card = dict(cvc=cvc,expiryMonth=expiryMonth,expiryYear=expiryYear,holderName=holderName,number=number),
			recurring = dict(contract = 'ONECLICK', recurringDetailName = recurringDetailName)
			))
		req.set_element_paymentRequest(preq)
		result = service.authorise(req)
		payment_result = result.get_element_paymentResult()
		return dict([(k.replace("get_element_",""), getattr(payment_result, k)()) for k in dir(payment_result) if k.startswith('get_element')])
	
	
	def submit_recurring(self, txid, amount, currency, shopperEmail, shopperReference, selectedRecurringDetailReference):
		"""Send an authorise request"""
		if len(filter(None, [txid, amount, currency, shopperEmail, shopperReference, selectedRecurringDetailReference])) < 6:
			raise ValueError("Received Empty Value for at least field:%s", [txid, amount, currency, shopperEmail, shopperReference, selectedRecurringDetailReference])
		service = Payment_services.PaymentHttpBindingSOAP(url=self.url, auth=(AUTH.httpbasic, self.user, self.password))
		req = Payment_services.authoriseRequest()
		preq = req.new_paymentRequest() ###additionalData, amount, card, merchantAccount, recurring, reference, shopperEmail, shopperIP, shopperReference, 
		preq = parse_dict_into_request(preq, dict(
			merchantAccount=self.merchantAccount,
			reference=txid,
			shopperEmail=shopperEmail,
			shopperReference=shopperReference,
			selectedRecurringDetailReference = selectedRecurringDetailReference,
			amount=dict(value=amount,currency=currency),
			recurring = dict(contract = 'ONECLICK')
			))
		req.set_element_paymentRequest(preq)
		result = service.authorise(req)
		payment_result = result.get_element_paymentResult()
		return dict([(k.replace("get_element_",""), getattr(payment_result, k)()) for k in dir(payment_result) if k.startswith('get_element')])
	
	
	

	def authorise3d(self, md, paResponse, ipAddress=None, browserInfo=None):
		"""Send an authorise3d request"""
		gw = Binding(url=self.url, auth=(AUTH.httpbasic, self.user, self.password))
		request = PaymentRequest3d(
			md,
			self.merchantAccount,
			paResponse,
			browserInfo,
			ipAddress,
		)
		result = gw.RPC(None, 'authorise3d', (request,), replytype=Authorise3dResponse.typecode)
		return {
			'authCode': result.paymentResult.authCode,
			'pspReference': result.paymentResult.pspReference,
			'issuerUrl': result.paymentResult.issuerUrl,
			'md': result.paymentResult.md,
			'paRequest': result.paymentResult.paRequest,
			'refusalReason': result.paymentResult.refusalReason,
			'fraudResult': result.paymentResult.fraudResult and \
				result.paymentResult.fraudResult.accountScore or None,
		}

	def cancel(self, txid):
		"""Send a cancel request"""
		gw = Binding(url=self.url, auth=(AUTH.httpbasic, self.user, self.password))
		request = CancelRequest(self.merchantAccount, txid)
		result = gw.RPC(None, 'cancel', (request,), replytype=CancelResponse.typecode)
		return result.cancelResult.response == '[cancel-received]'

	def capture(self, txid, amount, currency):
		"""Send a capture request"""
		gw = Binding(url=self.url, auth=(AUTH.httpbasic, self.user, self.password))
		request = CaptureRequest(self.merchantAccount, txid, ModificationAmount(currency, amount))
		result = gw.RPC(None, 'capture', (request,), replytype=CaptureResponse.typecode)
		return result.captureResult.response == '[capture-received]'

	def refund(self, txid, amount, currency):
		"""Send a refund request"""
		gw = Binding(url=self.url, auth=(AUTH.httpbasic, self.user, self.password))
		request = RefundRequest(self.merchantAccount, txid, ModificationAmount(currency, amount))
		result = gw.RPC(None, 'refund', (request,), replytype=RefundResponse.typecode)
		return result.refundResult.response == '[refund-received]'
