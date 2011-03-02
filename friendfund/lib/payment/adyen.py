from __future__ import with_statement

import logging, urllib, urllib2
import base64, hmac, hashlib, uuid
from datetime import datetime, timedelta

from pylons import session as websession, url, app_globals, request

from friendfund.lib import helpers as h
from friendfund.lib.payment.adyengateway import AdyenPaymentGateway, get_contribution_from_adyen_result

from friendfund.lib.synclock import add_token, rem_token
from friendfund.model.contribution import Contribution, DBContribution, DBPaymentInitialization
from friendfund.model.db_access import SProcException
from friendfund.model.pool import Pool
from friendfund.tasks.photo_renderer import remote_pool_picture_render

log = logging.getLogger(__name__)
class UnsupportedOperation(Exception):pass
class UnsupportedPaymentMethod(Exception):pass
class DBErrorDuringSetup(Exception):pass
class DBErrorAfterPayment(Exception):pass


class PaymentGateway(object):
	def __init__(self, gtw_location, gtw_username, gtw_password, gtw_account):
		self.gateway = AdyenPaymentGateway(gtw_location, gtw_username, gtw_password, gtw_account)
	def authorize(self, contrib_view):
		args = [contrib_view.ref 
					,contrib_view.total
					,contrib_view.currency
					,contrib_view.methoddetails.ccHolder
					,contrib_view.methoddetails.ccNumber
					,contrib_view.methoddetails.ccExpiresMonth
					,contrib_view.methoddetails.ccExpiresYear
					,contrib_view.methoddetails.ccCode]
		return self.gateway.authorise(*args)
	
	def authorize_recurring(self, contrib_model, contrib_view):
		args = [contrib_model.ref 
					,contrib_model.initial_transaction_total
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
	def __init__(self, logo_url, code, currencies, fee_absolute, fee_relative):
		self.logo_url = logo_url
		self.code = code
		self.currencies = currencies
		self.fee_absolute = fee_absolute # in base units
		self._fee_absolute = float(fee_absolute)/100
		self.fee_relative = fee_relative # in percent
		self._fee_relative = float(fee_relative)/100
		self.has_fees = bool(fee_absolute or fee_relative)
		self.default = False
		
	def check_totals(self, base, total):
		return -0.01 < total - (base*(1 + self._fee_relative) + self._fee_absolute) < 0.01
	def __repr__(self):
		return '<%s: %s (%s/%s)>' % (self.__class__.__name__, self.code, self.fee_absolute, self.fee_relative)
	def process(self, tmpl_context, contribution, pool, renderer, redirecter):
		raise UnsupportedPaymentMethod('process')
	def post_process(self, tmpl_context, pool, renderer, redirecter):
		raise UnsupportedPaymentMethod('process')
	def verify_signature(self, params):
		raise Exception('NotImplemented')
	def calculate_costs(self, amount, currency):
		amount = h.parse_number(amount)
		print currency in self.currencies
		return (amount*(1 + self._fee_relative) + self._fee_absolute)
	
class CreditCardPayment(PaymentMethod):
	def __init__(self, logo_url, code, currencies, fee_absolute, fee_relative, gtw_location, gtw_username, gtw_password, gtw_account):
		super(self.__class__, self).__init__(logo_url, code, currencies, fee_absolute, fee_relative)
		self.paymentGateway = PaymentGateway(gtw_location, gtw_username, gtw_password, gtw_account)
	
	def process(self, tmpl_context, contrib_view, pool, renderer, redirecter):
		tmpl_context.form_secret = str(uuid.uuid4())
		with app_globals.cache_pool.reserve() as mc:
			add_token(mc, tmpl_context.form_secret, contrib_view)
		if app_globals.test:
			tmpl_context.creditcard_values = {"ccHolder":"Test User", "ccNumber":"4111111111111111", "ccCode":"737", "ccExpiresMonth":"12", "ccExpiresYear":"2012"}
		else:
			tmpl_context.creditcard_values = {}
		tmpl_context.contrib_view = contrib_view
		return renderer('/contribution/payment_details.html')
	
	def post_process(self, tmpl_context, pool, renderer, redirecter):
		with app_globals.cache_pool.reserve() as client:
			contrib_view = rem_token(client, tmpl_context.form_secret) # raises TokenNotExistsException
		
		contrib_model = DBContribution(amount = contrib_view.amount
								,total = contrib_view.total
								,is_secret = contrib_view.is_secret
								,message = contrib_view.message
								,paymentmethod = ccType
								,u_id = tmpl_context.user.u_id
								,network = tmpl_context.user.network
								,network_id = tmpl_context.user.network_id
								,shopper_email = tmpl_context.user.default_email
								,p_url = pool.p_url)
		try:
			contrib_model = app_globals.dbm.set(contrib_model, merge = True)
		except SProcException, e:
			log.error(e)
			raise DBErrorDuringSetup(e)
		
		contrib_view.ref = contrib_model.ref
		if contrib_model.is_recurring:
			log.info("AUTHORIZING_RECURRING %s", contrib_view.ref)
			paymentresult = self.paymentGateway.authorize_recurring(contrib_model, contrib_view)
		else:
			log.info("AUTHORIZING_NORMAL %s", contrib_view.ref)
			paymentresult = self.paymentGateway.authorize(contrib_view)
		notice = get_contribution_from_adyen_result(contrib_model.ref, paymentresult)
		try:
			app_globals.dbm.set(notice)
		except SProcException, e:
			log.error(e)
		app_globals.dbm.expire(Pool(p_url = pool.p_url))
		tmpl_context.success = (paymentresult['resultCode'] == 'Authorised')
		if tmpl_context.success : 
			remote_pool_picture_render.delay(pool.p_url)
			return redirecter(url('contribution', pool_url=pool.p_url, action='success', token=tmpl_context.form_secret))
		else:
			return redirecter(url('contribution', pool_url=pool.p_url, action='fail', token=tmpl_context.form_secret))


class RedirectPayment(PaymentMethod):
	request_order = ["paymentAmount","currencyCode","shipBeforeDate","merchantReference"
						,"skinCode","merchantAccount","sessionValidity","shopperEmail"
						,"shopperReference","recurringContract","allowedMethods","blockedMethods"
						,"shopperStatement","merchantReturnData","billingAddressType","offset"]
	result_order = ["authResult", "pspReference", "merchantReference", "skinCode", "merchantReturnData"]
	
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
				"resURL":"http://dev.friendfund.de/mypools" # can be used to redirect user to correct paymentResult Page
				}
		params = self.get_request_parameters(redirect_params)
		urlparams = '&'.join(['%s=%s' % (k, urllib.quote(v)) for k,v in params.iteritems()])
		url = "%s?%s&merchantSig=%s" % (self.base_url, urlparams, urllib.quote(self.get_signature(params)))
		return redirecter(url)