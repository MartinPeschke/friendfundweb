import logging, formencode
from datetime import datetime
from friendfund.model.contribution import DBPaymentNotice
from pylons import request, app_globals
log = logging.getLogger(__name__)

class NotAllowedToPayException(Exception):pass

class PaymentPageSettings(object):
	def __init__(self, currency, user, pool):
		self.methods = filter(lambda x: x.can_i_contribute(pool, user) and currency in x.currencies, PaymentService.payment_methods)
		self.has_fees = len(filter(lambda x: x.has_fees, self.methods)) > 0
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
	def get_payment_settings(self, currency, user, pool):
		return PaymentPageSettings(currency, user, pool)
	def check_payment_method(self, method_code, currency):
		return str(method_code) in self.payment_methods_map
	def get_payment_method(self, method_code):
		return self.payment_methods_map[method_code]
	def process_payment(self, tmpl_context, contribution, pool, renderer, redirecter):
		return self.payment_methods_map[contribution.paymentmethod].process(tmpl_context, contribution, pool, renderer, redirecter)
	def post_process_payment(self, tmpl_context, contribution, pool, renderer, redirecter):
		return self.payment_methods_map[contribution.paymentmethod].post_process(tmpl_context, contribution, pool, renderer, redirecter)
	
	
	
	
	def receive_notification(self, paymentlog, params):
		strbool = formencode.validators.StringBoolean(if_missing=False)
		if str(params['eventCode']) in ['AUTHORISATION', 'REFUND', 'CANCELLATION', 'CAPTURE', 'CHARGEBACK', 'CHARGEBACK_REVERSED']:
			paymentlog.info( '-'*40 )
			paymentlog.info( 'headers=%s', request.headers )
			paymentlog.info( 'post_params=%s', request.params )
			paymentlog.info( '-'*40 )
		else:
			paymentlog.info( '-'*40 )
			paymentlog.warning( request.headers )
			paymentlog.warning( request.params )
			paymentlog.info( '-'*40 )
			return '[accepted]'
		if str(params['eventCode']) in ['AUTHORISATION']:
			transl = {  'merchantReference':'ref'\
						,'pspReference':'tx_id'\
						,'eventCode':'type'\
						,'success':'success'
					}
		else:
			transl = {  'merchantReference':'ref'\
						,'originalReference':'tx_id'\
						,'pspReference':'msg_id'\
						,'eventCode':'type'\
						,'success':'success'
					}
		noticeparams = dict([k for k in filter(lambda x: x[1], [(transl[k],v) for k,v in params.iteritems() if k in transl])])
		noticeparams['success'] = strbool.to_python(noticeparams.get('success', False))
		try:
			notice = DBPaymentNotice(**noticeparams)
			app_globals.dbm.set(notice)
		except SProcException, e:
			paymentlog.error(e)
		except Exception, e:
			paymentlog.error(e)
		finally:
			paymentlog.info( '-'*40 )
			return '[accepted]'