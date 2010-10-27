import logging
from datetime import datetime
from friendfund.lib.payment.adyen import VirtualPayment
log = logging.getLogger(__name__)

class NotAllowedToPayException(Exception):pass

class PaymentPageSettings(object):
	def __init__(self, region, is_virtual, user, pool):
		self.amount_fixed = is_virtual
		self.amount = is_virtual and 1 or None
		self.methods = filter(lambda x: x.can_i_contribute(pool, user) and region in x.regions and is_virtual == x.virtual , PaymentService.payment_methods)
		self.has_fees = len(filter(lambda x: x.has_fees, self.methods)) > 0
		self.is_virtual = len(filter(lambda x: isinstance(x, VirtualPayment), self.methods)) == len(self.methods)
		if self.methods:
			self.methods[0].default = True
			self.default = self.methods[0]
		else:
			raise NotAllowedToPayException('NoMethodsAvailableToUser')

class PaymentService(object):
	"""
		This is shared between all threads, do not stick state in here!
	"""
	payment_methods = []
	creditcard_types = [('visa', 'Visa'), ('amex', 'American Express'), ('mastercard', 'MasterCard')]
	cc_validity_years = zip(range(datetime.today().year, datetime.today().year + 50), range(datetime.today().year, datetime.today().year + 100))
	cc_validity_months = zip(range(1,13), range(1,13))
	
	def __init__(self, payment_methods):
		self.__class__.payment_methods = payment_methods
		self.payment_methods_map = dict([(pm.code, pm) for pm in self.payment_methods])
	def verify_result(self, params):
		method = params['paymentMethod']
		return self.payment_methods_map[method].verify_signature(params)
	def get_payment_settings(self, region, is_virtual, user, pool):
		return PaymentPageSettings(region, is_virtual, user, pool)
	def check_payment_method(self, method_code, region, is_virtual):
		return str(method_code) in self.payment_methods_map
	def get_payment_method(self, method_code):
		return self.payment_methods_map[method_code]
	def process_payment(self, tmpl_context, contribution, pool_url, renderer, redirecter):
		return self.payment_methods_map[contribution.paymentmethod].process(tmpl_context, contribution, pool_url, renderer, redirecter)
	def post_process_payment(self, tmpl_context, contribution, pool_url, renderer, redirecter):
		return self.payment_methods_map[contribution.paymentmethod].post_process(tmpl_context, contribution, pool_url, renderer, redirecter)