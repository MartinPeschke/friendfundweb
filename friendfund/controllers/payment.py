import logging, formencode, uuid
from copy import copy
from pylons import request, response, session as websession, tmpl_context as c, url, app_globals as g
from pylons.controllers.util import abort, redirect
from pylons.decorators import jsonify


from friendfund.lib import helpers as h, synclock
from friendfund.lib.auth.decorators import logged_in
from friendfund.lib.base import ExtBaseController, render, _, ErrorMessage
from friendfund.lib.i18n import FriendFundFormEncodeState
from friendfund.lib.payment.adyen import UnsupportedOperation, UnsupportedPaymentMethod, DBErrorDuringSetup, DBErrorAfterPayment
from friendfund.model.contribution import Contribution, GetDetailsFromContributionRefProc, CreditCard
from friendfund.model.forms.contribution import PaymentIndexForm, PaymentConfForm
from friendfund.model.forms.creditcard import CreditCardForm
from friendfund.model.db_access import SProcException

paymentlog = logging.getLogger('payment.controller')
log = logging.getLogger(__name__)

class PaymentController(ExtBaseController):
	@jsonify
	def transaction_fees(self, pool_url):
		return {"popup":render("/contribution/popups/transaction_fees.html").strip()}

	@logged_in(ajax=False)
	def index(self, pool_url):
		if c.user.is_anon or not c.pool.am_i_member(c.user):
			return redirect(url('get_pool', pool_url=pool_url))
		c.values = getattr(c, 'values', {})
		c.errors = getattr(c, 'errors', {})
		suggested_amount = request.params.get('amount')
		try:suggested_amount = (float(suggested_amount)/100)
		except: pass
		else: c.values['amount'] = h.format_number(suggested_amount)
		c.payment_methods = g.payment_methods
		return self.render('/contribution/contrib_screen.html')
	@logged_in(ajax=False)
	def details(self, pool_url):
		if c.user.is_anon or not c.pool.am_i_member(c.user):
			return redirect(url('get_pool', pool_url=pool_url))
		c.payment_methods = g.payment_methods
		details = formencode.variabledecode.variable_decode(request.params).get('payment', {})
		details['agreedToS'] = details.get('agreedToS', False)  #if_missing wouldnt evaluate, and if_empty returns MISSING VALUE error message, both suck bad
		schema = PaymentConfForm()
		schema.fields['amount'].max = round(c.pool.get_amount_left(), 2)
		c.values = {}
		c.errors = {}
		try:
			state = copy(c.pool)
			state.__dict__["_"] = FriendFundFormEncodeState._
			state.__dict__["payment_methods"] = g.payment_methods_map
			form_result = schema.to_python(details, state)
		except formencode.validators.Invalid, error:
			c.values = error.value
			c.errors = error.error_dict or {}
			c.messages.append(ErrorMessage(_("FF_CONTRIBUTION_PAGE_ERRORBAND_Please correct the Errors below")))
			return self.render('/contribution/contrib_screen.html')
		else:
			contrib = Contribution(**form_result)
			contrib.currency = c.pool.currency
			contrib.set_amount(form_result['amount'])
			contrib.set_total(form_result['total'])
			contrib.paymentmethod_code = form_result.get('method')
			
			try:
				return g.payment_methods_map[contrib.paymentmethod_code].process(c, contrib, c.pool, self.render, redirect)
			except (UnsupportedPaymentMethod, KeyError), e:
				c.messages.append(ErrorMessage(_("CONTRIBUTION_PAGE_Unknown Payment Method")))
				return redirect(url("payment", pool_url=c.pool.p_url, protocol="http"))
			except DBErrorDuringSetup, e:
				c.messages.append(ErrorMessage(_(u"CONTRIBUTION_CREDITCARD_DETAILS_An error has occured, please try again later. Your payment has not been processed.")))
				return redirect(url("payment", pool_url=c.pool.p_url, protocol="http"))
			except DBErrorAfterPayment, e:
				c.messages.append(ErrorMessage(_(u"CONTRIBUTION_CREDITCARD_DETAILS_A serious error occured, please try again later")))
				return redirect(url("payment", pool_url=c.pool.p_url, protocol="http"))
	
	@logged_in(ajax=False)
	def creditcard(self, pool_url):
		if c.user.is_anon or not c.pool.am_i_member(c.user):
			return redirect(url('get_pool', pool_url=pool_url))
		### Establishing correctnes of Flow and getting colateral Info
		c.token = request.params.get('token')
		if not c.token:
			log.error("PAYMENT_FORM_WITHOUT_TOKEN")
			c.messages.append(ErrorMessage(_(u"CONTRIBUTION_CREDITCARD_DETAILS_Incorrect Payment Form Data, Token missing. Your payment has not been processed.")))
			return redirect(url("payment", pool_url=c.pool.p_url, protocol="http"))
		try:
			c.contrib_view = synclock.get_contribution(c.token, c.user) # raises TokenIncorrectException
		except synclock.TokenIncorrectException, e:
			log.error("PAYMENT_FORM_WITH_INCORRECT_TOKEN %s", c.token)
			c.messages.append(ErrorMessage(_(u"CONTRIBUTION_CREDITCARD_DETAILS_Incorrect Payment Form Data, Token missing. Your payment has not been processed.")))
			return redirect(url("payment", pool_url=c.pool.p_url, protocol="http"))
		
		
		### Making colaterals available
		c.values = {}
		c.errors = {}
		c.values.update({"amount": c.contrib_view.get_amount()
					, "payment_method":c.contrib_view.paymentmethod_code
					, "is_secret":c.contrib_view.is_secret
					, "message":c.contrib_view.message
					})
		c.payment_method = g.payment_methods_map[c.contrib_view.paymentmethod_code]
		if g.test:
			c.values.update({"ccHolder":"Test User", "ccNumber":"4111111111111111", "ccCode":"737", "ccExpiresMonth":"12", "ccExpiresYear":"2012"})
		if request.method != 'POST':
			return self.render('/contribution/payment_details.html')
		else:
			### Validating creditcard details
			cc = formencode.variabledecode.variable_decode(request.params).get('creditcard', None)
			schema = CreditCardForm()
			try:
				cc_values = schema.to_python(cc, state = FriendFundFormEncodeState)
			except formencode.validators.Invalid, error:
				c.values.update(error.value)
				c.errors = error.error_dict or {}
				c.messages.append(ErrorMessage(_("FF_CONTRIBUTION_VALIDATION_ERRORBAND_Please fill in all fields correctly!")))
				return self.render('/contribution/payment_details.html')
			except AssertionError, e:
				c.values = cc
				c.errors = {"ccType":_("Unknown Card Type")}
				return self.render('/contribution/payment_details.html')
			else:
				ccard = CreditCard(**cc_values)
				try:
					synclock.rem_contribution(c.token) # raises TokenIncorrectException
				except synclock.TokenIncorrectException, e:
					c.messages.append(_(u"CONTRIBUTION_CREDITCARD_DETAILS_Incorrect Payment Form Data, Token missing."))
					return redirect(url("payment", pool_url=pool.p_url, protocol=app_globals.SSL_PROTOCOL))
			
			### Handing control over to the specific creditcard method implementation for processing
			try:
				return g.payment_methods_map[c.contrib_view.paymentmethod_code].post_process(c, ccard, c.pool, self.render, redirect)
			except (UnsupportedPaymentMethod, KeyError), e:
				c.messages.append(_("CONTRIBUTION_PAGE_Unknown Payment Method"))
				return redirect(url("payment", pool_url=c.pool.p_url, protocol="http"))
			except DBErrorDuringSetup, e:
				c.messages.append(_(u"CONTRIBUTION_CREDITCARD_DETAILS_An error has occured, please try again later. Your payment has not been processed."))
				return redirect(url("payment", pool_url=c.pool.p_url, protocol="http"))
			except DBErrorAfterPayment, e:
				c.messages.append(_(u"CONTRIBUTION_CREDITCARD_DETAILS_A serious error occured, please try again later"))
				return redirect(url("payment", pool_url=c.pool.p_url, protocol="http"))
	
	
	
	
	@logged_in(ajax=False)
	def success(self, pool_url):
		ref = request.params.get('ref')
		if not ref:
			c.messages.append(_("CONTRIBUTION_PAGE_Unknown Payment Method"))
			return redirect(url("payment", pool_url=c.pool.p_url, protocol="http"))
		c.contrib = g.dbm.get(GetDetailsFromContributionRefProc, contribution_ref = ref)
		c.values = {"amount": h.format_currency(c.contrib.get_amount(), c.pool.currency)
					, "baseUnits" : c.contrib.amount
					, "is_secret":c.contrib.is_secret
					, "message":c.contrib.message
					}
		c.show_delay = False
		return self.render('/contribution/payment_success.html')
	
	@logged_in(ajax=False)
	def fail(self, pool_url):
		ref = request.params.get('ref')
		if not ref:
			c.messages.append(_("CONTRIBUTION_PAGE_Unknown Payment Method"))
			return redirect(url("payment", pool_url=c.pool.p_url, protocol="http"))
		c.contrib = g.dbm.get(GetDetailsFromContributionRefProc, contribution_ref = ref)
		c.values = {"amount": h.format_currency(c.contrib.get_amount(), c.pool.currency)
					, "baseUnits" : c.contrib.amount
					, "is_secret":c.contrib.is_secret
					, "message":c.contrib.message
					}
		c.show_delay = False
		return self.render('/contribution/payment_fail.html')
	
	@logged_in(ajax=False)
	def ret(self, pool_url):
		paymentlog.info( 'PAYMENT RETURN from External: %s' , request.params )
		merchantReference = request.params.get('merchantReference')
		try:
			paymentmethod =  g.payment_methods_map[request.params.get('paymentMethod')]
			merchant_domain = paymentmethod.verify_signature(request.params)
		except KeyError, e:
			merchant_domain = None
		if not merchant_domain:
			c.messages.append(_(u"Invalid payment data found, possibly some hiccup?"))
			return redirect(url("payment", pool_url=c.pool.p_url, protocol=g.SSL_PROTOCOL))
		elif merchant_domain != request.merchant.domain:
			log.info("REDIRECTED, found:%s(%s), expected: %s(%s)", merchant_domain, type(merchant_domain), request.merchant.domain, type(request.merchant.domain))
			return redirect(url.current(host=merchant_domain.encode("latin-1"), **dict(request.params.items())))
		
		c.contrib = g.dbm.get(GetDetailsFromContributionRefProc, contribution_ref = merchantReference)
		
		c.show_delay = paymentmethod.has_result_delay
		
		if c.contrib:
			c.values = {"amount": h.format_currency(c.contrib.get_amount(), c.pool.currency)
						, "baseUnits" : c.contrib.amount
						, "payment_method":paymentmethod.code
						, "is_secret":c.contrib.is_secret
						, "message":c.contrib.message
						}
		if request.params.get('authResult') == 'AUTHORISED':
			return self.render('/contribution/payment_success.html')
		else:
			return self.render('/contribution/payment_fail.html')
		return self.render('/contribution/payment_details.html')