import base64, hmac, hashlib, urllib, logging
from decimal import Decimal
from datetime import datetime, timedelta
from pylons.controllers.util import abort, redirect

from pylons import app_globals as g, session as websession
from friendfund.model.contribution import Contribution, DBContribution
from friendfund.model.db_access import SProcException

log = logging.getLogger(__name__)

request_order = ["paymentAmount","currencyCode","shipBeforeDate","merchantReference"
					,"skinCode","merchantAccount","sessionValidity","shopperEmail"
					,"shopperReference","recurringContract","allowedMethods","blockedMethods"
					,"shopperStatement","merchantReturnData","billingAddressType","offset"]
result_order = ["authResult", "pspReference", "merchantReference", "skinCode", "merchantReturnData"]



class PaymentMethod(object):
	def __init__(self, logo_url, code, name, regions, virtual, fee_absolute, fee_relative):
		self.logo_url = logo_url
		self.code = code
		self.name = name
		self.regions = regions
		self.virtual = virtual
		self.fee_absolute = fee_absolute # in base units
		self._fee_absolute = float(fee_absolute)/100
		self.fee_relative = fee_relative # in percent
		self._fee_relative = float(fee_relative)/100
		self.has_fees = bool(fee_absolute or fee_relative)
		self.default = False
	def check_totals(self, base, total):
		return -0.01 < total - (base*(1 + self._fee_relative) + self._fee_absolute) < 0.01
	
	def __repr__(self):
		return '<%s: %s>' % (self.__class__.__name__, self.name)
		
class PaymentPageSettings(object):
	all_payment_methods = [
				PaymentMethod('/static/imgs/icon-visa-mastercard.png', 'credit_card', "CONTRIBUTION_PAGE_Creditcard", ['de','gb','us','ie','ca','ch','at'], False, 10, 2),
				PaymentMethod('/static/imgs/icon-paypal.png', 'paypal', "CONTRIBUTION_PAGE_Paypal", ['de','gb','us','ie','ca','ch','at'], False, 10, 2),
				PaymentMethod('/static/imgs/icon_directebanking.png', 'directEbanking', "CONTRIBUTION_PAGE_Direct eBanking", ['de','at'], False, 10, 2),
				PaymentMethod('/static/imgs/currencies/pog.png', 'virtual', "CONTRIBUTION_PAGE_Virtual Pot of Gold", ['de','gb','us','ie','ca','ch','at'], True, 0, 0),
		]
	def __init__(self, region, is_virtual):
		self.amount_fixed = is_virtual
		self.amount = is_virtual and 1 or None
		self.methods = filter(lambda x: region in x.regions and is_virtual == x.virtual , self.all_payment_methods)
		
		self.has_fees = len(filter(lambda x: x.has_fees, self.methods)) > 0
		if self.methods:
			self.methods[0].default = True
			self.default = self.methods[0]
	
	
class PaymentService(object):
	"""
		This is shared between all threads, do not stick state in here!
	"""
	creditcard_types = [('visa', 'Visa'), ('amex', 'American Express'), ('mastercard', 'MasterCard')]
	cc_validity_years = zip(range(datetime.today().year, datetime.today().year + 100), range(datetime.today().year, datetime.today().year + 100))
	cc_validity_months = zip(range(1,13), range(1,13))
	
	def __init__(self, base_url, skincode, merchantaccount, secret):
		self.base_url = base_url
		self.secret = secret
		self.standard_params = {"merchantAccount":merchantaccount, "skinCode":skincode}
		
	def get_request_parameters(self, params, payment_method):
		sign_base = self.standard_params.copy()
		sign_base["shipBeforeDate"] = (datetime.now() + timedelta(1)).strftime("%Y-%m-%d")
		sign_base["sessionValidity"] = (datetime.now() + timedelta(0, 1800)).strftime("%Y-%m-%dT%H:%M:%SZ")
		sign_base["allowedMethods"] = payment_method
		sign_base["brandCode"] = payment_method
		sign_base.update(params)
		return sign_base
	def get_signature(self, params, signorder = None):
		signorder = signorder or request_order
		sign_base = ''.join([unicode(params.get(k, "")) for k in signorder])
		hm = hmac.new(self.secret, sign_base, hashlib.sha1)
		return base64.encodestring(hm.digest()).strip()
	def get_request(self, user, contrib, pool_url, payment_method):
		dbcontrib = DBContribution(amount = contrib.amount
								,total = contrib.total
								,is_secret = contrib.is_secret
								,anonymous = contrib.anonymous
								,message = contrib.message
								,paymentmethod = contrib.paymentmethod
								,u_id = user.u_id
								,network = user.network
								,network_id = user.network_id
								,email = user.email
								,p_url = pool_url)
		dbcontrib = g.dbm.set(dbcontrib, merge = True)
		paypal_params = {
				"paymentAmount":'%s'%contrib.total,
				"currencyCode":contrib.currency,
				"shopperLocale":websession['lang'],
				"merchantReference" : dbcontrib.ref,
				"merchantReturnData" : dbcontrib.ref
				}
		
		params = self.get_request_parameters(paypal_params, payment_method)
		urlparams = '&'.join(['%s=%s' % (k, urllib.quote(v)) for k,v in params.iteritems()])
		url = "%s?%s&merchantSig=%s" % (self.base_url, urlparams, urllib.quote(self.get_signature(params)))
		return redirect(url)
	def verify_result(self, params):
		merchantSig = params.get('merchantSig')
		return self.get_signature(params, signorder = result_order) == merchantSig
	
	
	def get_available_payment_methods(self, region, is_virtual):
		return PaymentPageSettings(region, is_virtual)
	def check_payment_method(self, method_code, region, is_virtual):
		return str(method_code) in map(lambda x: x.code, PaymentPageSettings(region, is_virtual).methods)
	def get_payment_method(self, method_code):
		return filter(lambda x: method_code == x.code , PaymentPageSettings.all_payment_methods)[0]