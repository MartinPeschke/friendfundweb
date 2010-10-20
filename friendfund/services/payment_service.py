import base64, hmac, hashlib, urllib, datetime, logging
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

class PaymentService(object):
	"""
		This is shared between all threads, do not stick state in here!
	"""
	def __init__(self, base_url, skincode, merchantaccount, secret):
		self.base_url = base_url
		self.secret = secret
		self.standard_params = {"merchantAccount":merchantaccount, "skinCode":skincode}
	def get_request_parameters(self, params, payment_method):
		sign_base = self.standard_params.copy()
		sign_base["shipBeforeDate"] = (datetime.datetime.now() + datetime.timedelta(1)).strftime("%Y-%m-%d")
		sign_base["sessionValidity"] = (datetime.datetime.now() + datetime.timedelta(0, 1800)).strftime("%Y-%m-%dT%H:%M:%SZ")
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