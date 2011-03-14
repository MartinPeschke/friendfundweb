import logging, urllib, urllib2, formencode, base64, hmac, hashlib, uuid
from datetime import datetime, timedelta

from pylons import session as websession, url, app_globals, request
from friendfund.lib import helpers as h, synclock
from friendfund.lib.i18n import FriendFundFormEncodeState
from friendfund.lib.payment.adyengateway import AdyenPaymentGateway, get_contribution_from_adyen_result
from friendfund.model.contribution import Contribution, DBContribution, DBPaymentInitialization
from friendfund.model.db_access import SProcException
from friendfund.model.pool import Pool
from friendfund.tasks.photo_renderer import remote_pool_picture_render


log = logging.getLogger(__name__)
class UnsupportedOperation(Exception):pass
class UnsupportedPaymentMethod(Exception):pass
class DBErrorDuringSetup(Exception):pass
class DBErrorAfterPayment(Exception):pass

_ = lambda x:x

LOCALIZATIONS = {"mastercard":_("FF_mastercard"), "amex":_("FF_amex"),"visa":_("FF_visa"), "paypal":_("FF_paypal")}

from pylons.i18n import _

class PaymentGateway(object):
	def __init__(self, gtw_location, gtw_username, gtw_password, gtw_account):
		self.gateway = AdyenPaymentGateway(gtw_location, gtw_username, gtw_password, gtw_account)
	def authorize(self, contrib_model, contrib_view):
		args = [contrib_view.ref 
					,contrib_model.total  #### This is supposed to be Database configured total for the whole transaction, i.e. what the user input plus transaction costs
					,contrib_view.currency
					,contrib_view.methoddetails.ccHolder
					,contrib_view.methoddetails.ccNumber
					,contrib_view.methoddetails.ccExpiresMonth
					,contrib_view.methoddetails.ccExpiresYear
					,contrib_view.methoddetails.ccCode]
		return self.gateway.authorise(*args)
	
	def authorize_recurring(self, contrib_model, contrib_view):
		args = [contrib_model.ref 
					,contrib_model.total  #### This is the Database configured total
					,contrib_view.currency
					,contrib_view.methoddetails.ccHolder
					,contrib_view.methoddetails.ccNumber
					,contrib_view.methoddetails.ccExpiresMonth
					,contrib_view.methoddetails.ccExpiresYear
					,contrib_view.methoddetails.ccCode
					,contrib_model.shopper_email
					,contrib_model.shopper_ref
					,contrib_model.shopper_ref 
					]
		return self.gateway.authorise_recurring_contract(*args)


class PaymentMethod(object):
	_method_translation = {"master_card":"mastercard", "amex":"amex","visa":"visa", "paypal":"paypal"}
	def __init__(self, logo_url, code, currencies, fee_absolute, fee_relative):
		self.logo_url = logo_url
		self.code = self._method_translation[code]
		self.currencies = currencies
		self.fee_absolute = fee_absolute # in base units
		self._fee_absolute = float(fee_absolute)/100
		self.fee_relative = fee_relative # in percent
		self._fee_relative = fee_relative
		self.has_fees = bool(fee_absolute or fee_relative)
		self.default = False
	def check_totals(self, base, total):
		return -0.01 < total - (base*(1 + self._fee_relative) + self._fee_absolute) < 0.01
	def __repr__(self):
		return '<%s: %s (%s/%s)>' % (self.__class__.__name__, self.code, self.fee_absolute, self.fee_relative)
	def process(self, tmpl_context, contribution, pool, renderer, redirecter):
		raise UnsupportedPaymentMethod('process')
	def post_process(self, tmpl_context, token, contrib_view, pool, renderer, redirecter):
		raise UnsupportedPaymentMethod('process')
	def verify_signature(self, params):
		raise Exception('NotImplemented')
	def calculate_costs(self, amount, currency):
		amount = h.parse_number(amount)
		return (amount*(1 + self._fee_relative) + self._fee_absolute)
	def get_display_name(self):
		return _(LOCALIZATIONS[self.code])
	
class CreditCardPayment(PaymentMethod):
	has_result_delay = False
	cc_validity_years = zip(range(datetime.today().year, datetime.today().year + 50), range(datetime.today().year, datetime.today().year + 100))
	cc_validity_months = zip(range(1,13), range(1,13))
	
	def __init__(self, logo_url, code, currencies, fee_absolute, fee_relative, gtw_location, gtw_username, gtw_password, gtw_account):
		super(self.__class__, self).__init__(logo_url, code, currencies, fee_absolute, fee_relative)
		self.paymentGateway = PaymentGateway(gtw_location, gtw_username, gtw_password, gtw_account)

	def process(self, tmpl_context, contrib_view, pool, renderer, redirecter):
		tmpl_context.form_secret = str(uuid.uuid4())
		synclock.set_contribution(tmpl_context.form_secret, tmpl_context.user, contrib_view)
		return redirecter(url(controller="payment", action="creditcard", pool_url=pool.p_url, protocol=app_globals.SSL_PROTOCOL, token=tmpl_context.form_secret))
	
	
	def post_process(self, tmpl_context, ccard, pool, renderer, redirecter):
		contrib_model = DBContribution(amount = tmpl_context.contrib_view.amount
								,total = tmpl_context.contrib_view.total
								,is_secret = tmpl_context.contrib_view.is_secret
								,message = tmpl_context.contrib_view.message
								,paymentmethod = ccard.ccType
								,u_id = tmpl_context.user.u_id
								,network = tmpl_context.user.network
								,network_id = tmpl_context.user.network_id
								,shopper_email = tmpl_context.user.default_email
								,p_url = pool.p_url)
		try:
			contrib_model = app_globals.dbm.set(contrib_model, merge = True)
		except SProcException, e:
			log.error(e)
			tmpl_context.messages.append(_(u"CONTRIBUTION_CREDITCARD_DETAILS_An error has occured, please try again later. Your payment has not been processed."))
			return redirecter(url("payment", pool_url=c.pool.p_url, protocol="http"))
		else:
			tmpl_context.contrib_view.ref = contrib_model.ref
			
			### Adding and immediately removing credit cards details, dont want it bleeding anywhere
			tmpl_context.contrib_view.methoddetails = ccard
			if contrib_model.is_recurring:
				log.info("AUTHORIZING_RECURRING %s", tmpl_context.contrib_view.ref)
				paymentresult = self.paymentGateway.authorize_recurring(contrib_model, tmpl_context.contrib_view)
			else:
				log.info("AUTHORIZING_NORMAL %s", tmpl_context.contrib_view.ref)
				paymentresult = self.paymentGateway.authorize(contrib_model, tmpl_context.contrib_view)
			del tmpl_context.contrib_view.methoddetails
			
			notice = get_contribution_from_adyen_result(contrib_model.ref, paymentresult)
			try:
				app_globals.dbm.set(notice)
			except SProcException, e:
				log.error(e)
			app_globals.dbm.expire(Pool(p_url = pool.p_url))
			tmpl_context.success = (paymentresult['resultCode'] == 'Authorised')
			if tmpl_context.success : 
				remote_pool_picture_render.delay(pool.p_url)
				return redirecter(url(controller='payment', pool_url=pool.p_url, action='success', protocol="http", ref=contrib_model.ref))
			else:
				return redirecter(url(controller='payment', pool_url=pool.p_url, action='fail', protocol="http", ref=contrib_model.ref))


class RedirectPayment(PaymentMethod):
	request_order = ["paymentAmount","currencyCode","shipBeforeDate","merchantReference"
						,"skinCode","merchantAccount","sessionValidity","shopperEmail"
						,"shopperReference","recurringContract","allowedMethods","blockedMethods"
						,"shopperStatement","merchantReturnData","billingAddressType","offset"]
	result_order = ["authResult", "pspReference", "merchantReference", "skinCode", "merchantReturnData"]
	has_result_delay = True
	
	def __init__(self, logo_url, code, currencies, fee_absolute, fee_relative, base_url, skincode, merchantaccount, secret):
		super(self.__class__, self).__init__(logo_url, code, currencies, fee_absolute, fee_relative)
		self.base_url = base_url
		self.secret = secret
		self.standard_params = {"merchantAccount":merchantaccount, "skinCode":skincode}
	
	def verify_signature(self, params):
		merchantSig = params.get('merchantSig')
		if self.get_signature(params, signorder = self.result_order) == merchantSig:
			return params['merchantReturnData']
		else:
			return None
	
	def get_request_parameters(self, params):
		sign_base = self.standard_params.copy()
		sign_base["shipBeforeDate"] = (datetime.now() + timedelta(1)).strftime("%Y-%m-%d")
		sign_base["sessionValidity"] = (datetime.now() + timedelta(0, 1800)).strftime("%Y-%m-%dT%H:%M:%SZ")
		sign_base["allowedMethods"] = self.code
		sign_base["brandCode"] = self.code
		sign_base.update(params)
		return sign_base
	
	def get_signature(self, params, signorder = None):
		signorder = signorder or self.request_order
		sign_base = ''.join([unicode(params.get(k, "")) for k in signorder])
		hm = hmac.new(self.secret, sign_base, hashlib.sha1)
		return base64.encodestring(hm.digest()).strip()
	
	def process(self, tmpl_context, contribution, pool, renderer, redirecter):
		dbcontrib = DBContribution(amount = contribution.amount
								,total = contribution.total
								,is_secret = contribution.is_secret
								,message = contribution.message
								,paymentmethod = self.code
								,u_id = tmpl_context.user.u_id
								,network = tmpl_context.user.network
								,network_id = tmpl_context.user.network_id
								,shopper_email = tmpl_context.user.default_email
								,p_url = pool.p_url)
		try:
			dbcontrib = app_globals.dbm.set(dbcontrib, merge = True)
		except SProcException, e:
			log.error(e)
			raise DBErrorDuringSetup(e)
		
		redirect_params = {
				"paymentAmount":'%s'%contribution.total,
				"currencyCode":contribution.currency,
				"shopperLocale":websession['lang'],
				"merchantReference" : dbcontrib.ref,
				"merchantReturnData" : request.merchant.domain,
				"resURL":"%s"%(url("payment_current", pool_url = ''.join(pool.p_url.rpartition(".")[:2]), protocol="http"))
				}
		params = self.get_request_parameters(redirect_params)
		urlparams = '&'.join(['%s=%s' % (k, urllib.quote(v)) for k,v in params.iteritems()])
		return redirecter("%s?%s&merchantSig=%s" % (self.base_url, urlparams, urllib.quote(self.get_signature(params))))