from __future__ import with_statement

import logging, urllib, urllib2
import base64, hmac, hashlib, uuid
from datetime import datetime, timedelta

from pylons import session as websession, url, app_globals as g

from friendfund.lib.payment.adyengateway import AdyenPaymentGateway
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
	def authorize(self, contribution):
		args = [contribution.ref 
					,contribution.total
					,contribution.currency
					,contribution.methoddetails.ccHolder
					,contribution.methoddetails.ccNumber
					,contribution.methoddetails.ccExpiresMonth
					,contribution.methoddetails.ccExpiresYear
					,contribution.methoddetails.ccCode]
		result = self.gateway.authorise(*args)
		return result

class PaymentMethod(object):
	def __init__(self, logo_url, code, name, regions, virtual, fee_absolute, fee_relative, multi_contributions):
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
		self.multi_contributions = multi_contributions
		
	def can_i_contribute(self, pool, user):
		return self.multi_contributions or (not pool.am_i_contributor(user))
	def check_totals(self, base, total):
		return -0.01 < total - (base*(1 + self._fee_relative) + self._fee_absolute) < 0.01
	def __repr__(self):
		return '<%s: %s>' % (self.__class__.__name__, self.code)
	def process(self, tmpl_context, contribution, pool_url, renderer, redirecter):
		raise UnsupportedPaymentMethod('process')
	def post_process(self, tmpl_context, contribution, pool_url, renderer, redirecter):
		raise UnsupportedPaymentMethod('process')
	def verify_signature(self, params):
		raise Exception('NotImplemented')
	def setup(self):
		return None
	
class CreditCardPayment(PaymentMethod):
	def __init__(self, logo_url, code, name, regions, virtual, fee_absolute, fee_relative, multi_contributions, gtw_location, gtw_username, gtw_password, gtw_account):
		super(self.__class__, self).__init__(logo_url, code, name, regions, virtual, fee_absolute, fee_relative, multi_contributions)
		self.paymentGateway = PaymentGateway(gtw_location, gtw_username, gtw_password, gtw_account)
	
	def process(self, tmpl_context, contribution, pool_url, renderer, redirecter):
		tmpl_context.form_secret = str(uuid.uuid4())
		with g.cache_pool.reserve() as mc:
			add_token(mc, tmpl_context.form_secret, tmpl_context.action)
		return redirecter(url(controller='contribution', pool_url=pool_url, action='details', token=tmpl_context.form_secret, protocol=g.SSL_PROTOCOL))
	
	def post_process(self, tmpl_context, contribution, pool_url, renderer, redirecter):
		with g.cache_pool.reserve() as client:
			action = rem_token(client, tmpl_context.form_secret) # raises TokenNotExistsException
		tmpl_context.pool_fulfilled = action == 'chipin_fixed'
		
		contrib = DBContribution(amount = contribution.amount
								,total = contribution.total
								,is_secret = contribution.is_secret
								,anonymous = contribution.anonymous
								,message = contribution.message
								,paymentmethod = contribution.paymentmethod
								,u_id = tmpl_context.user.u_id
								,network = tmpl_context.user.network
								,network_id = tmpl_context.user.network_id
								,email = tmpl_context.user.email
								,p_url = pool_url)
		try:
			contrib = g.dbm.set(contrib, merge = True)
		except SProcException, e:
			log.error(e)
			raise DBErrorDuringSetup(e)
		
		contribution.ref = contrib.ref
		paymentresult = self.paymentGateway.authorize(contribution)
		payment_transl = {'Authorised':'AUTHORISATION', 'Refused':'REFUSED'}
		notice = DBPaymentInitialization(\
					ref = contrib.ref\
					, tx_id=paymentresult['pspReference']\
					, msg_id=None\
					, type=payment_transl[paymentresult['resultCode']]\
					, success = True\
					, reason=paymentresult['refusalReason']\
					, fraud_result = paymentresult['fraudResult'])
		try:
			g.dbm.set(notice)
		except SProcException, e:
			log.error(e)
			raise DBErrorAfterPayment(e)
		g.dbm.expire(Pool(p_url = pool_url))
		tmpl_context.success = (paymentresult['resultCode'] == 'Authorised')
		if tmpl_context.success : 
			remote_pool_picture_render.delay(pool_url)
			return {'redirect':url('contribution', pool_url=pool_url, action='success', token=tmpl_context.form_secret)}
		else:
			return {'redirect':url('contribution', pool_url=pool_url, action='fail', token=tmpl_context.form_secret)}


class RedirectPayment(PaymentMethod):
	request_order = ["paymentAmount","currencyCode","shipBeforeDate","merchantReference"
						,"skinCode","merchantAccount","sessionValidity","shopperEmail"
						,"shopperReference","recurringContract","allowedMethods","blockedMethods"
						,"shopperStatement","merchantReturnData","billingAddressType","offset"]
	result_order = ["authResult", "pspReference", "merchantReference", "skinCode", "merchantReturnData"]
	
	def __init__(self, logo_url, code, name, regions, virtual, fee_absolute, fee_relative, multi_contributions, base_url, skincode, merchantaccount, secret):
		super(self.__class__, self).__init__(logo_url, code, name, regions, virtual, fee_absolute, fee_relative, multi_contributions)
		self.base_url = base_url
		self.secret = secret
		self.standard_params = {"merchantAccount":merchantaccount, "skinCode":skincode}
	
	def verify_signature(self, params):
		merchantSig = params.get('merchantSig')
		return self.get_signature(params, signorder = self.result_order) == merchantSig
	
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
	
	def process(self, tmpl_context, contribution, pool_url, renderer, redirecter):
		dbcontrib = DBContribution(amount = contribution.amount
								,total = contribution.total
								,is_secret = contribution.is_secret
								,anonymous = contribution.anonymous
								,message = contribution.message
								,paymentmethod = self.code
								,u_id = tmpl_context.user.u_id
								,network = tmpl_context.user.network
								,network_id = tmpl_context.user.network_id
								,email = tmpl_context.user.email
								,p_url = pool_url)
		try:
			dbcontrib = g.dbm.set(dbcontrib, merge = True)
		except SProcException, e:
			log.error(e)
			raise DBErrorDuringSetup(e)
		paypal_params = {
				"paymentAmount":'%s'%contribution.total,
				"currencyCode":contribution.currency,
				"shopperLocale":websession['lang'],
				"merchantReference" : dbcontrib.ref,
				"merchantReturnData" : dbcontrib.ref
				}
		params = self.get_request_parameters(paypal_params)
		urlparams = '&'.join(['%s=%s' % (k, urllib.quote(v)) for k,v in params.iteritems()])
		url = "%s?%s&merchantSig=%s" % (self.base_url, urlparams, urllib.quote(self.get_signature(params)))
		return redirecter(url)
		
class VirtualPayment(PaymentMethod):
	def process(self, tmpl_context, contribution, pool_url, renderer, redirecter):
		dbcontrib = DBContribution(amount = contribution.amount
								,total = contribution.total
								,is_secret = contribution.is_secret
								,anonymous = contribution.anonymous
								,message = contribution.message
								,paymentmethod = self.code
								,u_id = tmpl_context.user.u_id
								,network = tmpl_context.user.network
								,network_id = tmpl_context.user.network_id
								,email = tmpl_context.user.email
								,p_url = pool_url)
		try:
			dbcontrib = g.dbm.set(dbcontrib, merge = True)
		except SProcException, e:
			log.error(e)
			raise DBErrorDuringSetup(e)
		
		notice = DBPaymentInitialization(ref = dbcontrib.ref, tx_id='1', msg_id=None, type='AUTHORISATION', success = True, reason='VIRTUAL', fraud_result = '')
		try:
			g.dbm.set(notice)
		except SProcException, e:
			log.error(e)
			raise DBErrorAfterPayment(e)
		
		g.dbm.expire(Pool(p_url = pool_url))
		
		tmpl_context.success = True
		tmpl_context.pool_fulfilled = False
		tmpl_context.show_delay = False
		tmpl_context.contrib = contribution
		return renderer('/contribution/contribution_result_success.html')
	def check_totals(self, base, total):
		return True
