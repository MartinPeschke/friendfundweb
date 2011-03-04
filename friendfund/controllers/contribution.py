import logging, formencode, urllib, datetime
from copy import copy
from pylons import request, response, session as websession, tmpl_context as c, url, app_globals as g
from pylons.controllers.util import abort, redirect
from pylons.decorators import jsonify

from friendfund.lib import helpers as h
from friendfund.lib.auth.decorators import logged_in, no_blocks, enforce_blocks, checkadd_block
from friendfund.lib.base import ExtBaseController, render, _
from friendfund.lib.i18n import FriendFundFormEncodeState
from friendfund.lib.payment.adyen import UnsupportedPaymentMethod, UnsupportedOperation, DBErrorAfterPayment, DBErrorDuringSetup
from friendfund.lib.synclock import TokenNotExistsException
from friendfund.model.pool import Pool
from friendfund.model.db_access import SProcException
from friendfund.model.contribution import Contribution, CreditCard, GetPoolURLFromContribRef
from friendfund.model.forms.contribution import PaymentConfForm, CreditCardForm, MonetaryValidator

paymentlog = logging.getLogger('payment.service')
log = logging.getLogger(__name__)

from friendfund.services.pool_service import MissingPermissionsException

class ContributionController(ExtBaseController):
	navposition=g.globalnav[1][2]
	
	@logged_in(ajax=False)
	def chipin_current(self):
		paymentlog.info( 'PAYMENT RETURN from External: %s' , request.params )
		merchantReference = request.params.get('merchantReference')
		merchant_domain = g.payment_service.verify_result(request.params)
		if not merchant_domain:
			log.warning("Payment Provider Signature could not be verified: %s", request.params)
			return abort(404)
		elif merchant_domain != request.merchant.domain:
			log.info("REDIRECTED, found:%s(%s), expected: %s(%s)", merchant_domain, type(merchant_domain), request.merchant.domain, type(request.merchant.domain))
			return redirect(url.current(host=merchant_domain.encode("latin-1"), **dict(request.params.items())))
		pool_base_info = g.dbm.get(GetPoolURLFromContribRef, contribution_ref = merchantReference)
		c.pool = g.dbm.get(Pool, p_url = pool_base_info.p_url)
		if c.pool is None:
			log.warning("Pool from Payment Provider Signature not found: %s", request.params)
			return abort(404)
		c.contrib = websession.get('contribution')
		
		if c.contrib:
			c.chipin_values = {"amount": h.format_number(c.contrib.get_amount())
								, 'payment_method':c.contrib.paymentmethod
								, 'is_secret':c.contrib.is_secret
								, 'message':c.contrib.message
							}
		c.show_delay = hasattr(c, 'contrib') and c.contrib.paymentmethod in ['paypal','directEbanking']
		if request.params.get('authResult') == 'AUTHORISED':
			return self.render('/contribution/contribution_result_success.html')
		else:
			return self.render('/contribution/contribution_result_fail.html')
	
	@logged_in(ajax=False)
	def chipin_fixed(self, pool_url):
		c.action = 'chipin_fixed'
		c.chipin_values = {"amount":h.format_number(c.pool.get_amount_left())}
		c.chipin_errors = {}
		if request.method != 'POST':
			return self.render('/contribution/contrib_screen.html')
		return self._check_chip_in_details(c.pool)
	
	@logged_in(ajax=False)
	def chipin(self, pool_url):
		c.action = 'chipin'
		suggested_amount = request.params.get('amount')
		if not c.pool.is_contributable():
			c.messages.append(_(u"CONTRIBUTION_You cannot contribute to this pool at this time, this pool is closed."))
			return redirect(url('ctrlpoolindex', controller='pool', pool_url=pool_url, protocol='http'))

		c.chipin_values = getattr(c, 'chipin_values', {})
		if suggested_amount: 
			try:
				suggested_amount = (float(suggested_amount)/100)
			except:
				pass
			c.chipin_values['amount'] = h.format_number(suggested_amount)
		c.chipin_errors = getattr(c, 'chipin_errors', {})
		if request.method != 'POST':
			return self.render('/contribution/contrib_screen.html')
		return self._check_chip_in_details(c.pool)
	
	def _check_chip_in_details(self, pool):
		chipin = formencode.variabledecode.variable_decode(request.params).get('chipin', None)
		if not g.payment_service.check_payment_method(chipin.get('payment_method'), pool.currency):
			c.messages.append(_("CONTRIBUTION_PAGE_Unknown Payment Method"))
			return redirect(url('chipin', pool_url=pool.p_url, protocol=g.SSL_PROTOCOL))
		schema = PaymentConfForm()
		try:
			schema.fields['amount'].max = round(pool.get_amount_left(), 2)
			chipin['agreedToS'] = chipin.get('agreedToS', 'no')
			state = copy(pool)
			state.__dict__["_"] = FriendFundFormEncodeState._
			state.__dict__["payment_method"] = g.payment_service.get_payment_method(chipin['payment_method'])
			state.__dict__["payment_currency"] = g.payment_service.get_payment_method(chipin['payment_method'])
			form_result = schema.to_python(chipin, state)
			
		except formencode.validators.Invalid, error:
			c.chipin_values = error.value
			c.chipin_values['is_secret'] = formencode.validators.StringBool(if_missing=False).to_python(c.chipin_values.get('is_secret'))
			c.chipin_errors = error.error_dict or {}
			return self.render('/contribution/contrib_screen.html')
		else:
			c.chipin_values = form_result
			if checkadd_block('email'):
				c.messages.append(_('CONTRIBUTION_EMAILBLOCK_We do need an Email address when you want to chip in!'))
				c.enforce_blocks = True
				c.page = 'contrib'
				return self.render('/contribution/contrib_screen.html')
			else:
				g.pool_service.invite_myself(c.pool, c.user)
			
			contrib = Contribution(**form_result)
			contrib.currency = pool.currency
			contrib.set_amount(form_result['amount'])
			contrib.set_total(form_result['total'])
			contrib.paymentmethod = chipin.get('payment_method')
			try:
				return g.payment_service.process_payment(c, contrib, pool, render, redirect)
			except UnsupportedPaymentMethod, e:
				tmpl_context.messages.append(_("CONTRIBUTION_PAGE_Unknown Payment Method"))
				return redirect(url('chipin', pool_url=pool.p_url, protocol=g.SSL_PROTOCOL))
			except DBErrorDuringSetup, e:
				return self.ajax_messages(_(u"CONTRIBUTION_CREDITCARD_DETAILS_An error has occured, please try again later. Your payment has not been processed."))
			except DBErrorAfterPayment, e:
				return self.ajax_messages(_(u"CONTRIBUTION_CREDITCARD_DETAILS_A serious error occured, please try again later"))
	
	@logged_in(ajax=False)
	def payment(self, pool_url):
		return self.render('/contribution/payment_details.html')
	@logged_in(ajax=False)
	def payment_success(self, pool_url):
		return self.render('/contribution/payment_success.html')
	
	
	
	@logged_in(ajax=False)
	@no_blocks(ajax=False)
	def details(self, pool_url):
		c.form_secret = request.params.get('token')
		if g.test:
			c.creditcard_values = {"ccHolder":"Test User", "ccNumber":"4111111111111111", "ccCode":"737", "ccExpiresMonth":"12", "ccExpiresYear":"2012"}
		else:
			c.creditcard_values = {}
		if 'contribution' not in websession:
			c.messages.append(_(u"CONTRIBUTION_CREDITCARD_DETAILS_Form already submitted."))
			return redirect(url('chipin', pool_url=pool_url, protocol=g.SSL_PROTOCOL))
		c.contrib = websession['contribution']
		return self.render('/contribution/payment_details.html')
	
	@logged_in(ajax=True)
	@no_blocks(ajax=True)
	@jsonify
	def creditcard(self, pool_url):
		c.creditcard_values = {}
		c.creditcard_errors = {}
		
		if 'contribution' not in websession:
			c.messages.append(_(u"CONTRIBUTION_CREDITCARD_DETAILS_Form already submitted."))
			return {'redirect':url('chipin', pool_url=pool_url, protocol=g.SSL_PROTOCOL)}

		


		cc = formencode.variabledecode.variable_decode(request.params).get('creditcard', None)
		schema = CreditCardForm()
		try:
			form_result = schema.to_python(cc, state = FriendFundFormEncodeState)
		except formencode.validators.Invalid, error:
			c.creditcard_values = error.value
			c.creditcard_errors = error.error_dict or {}
			return {'data':{'html':render('/contribution/payment_details_form.html').strip()}}
		except AssertionError, error:
			c.creditcard_values = error.value
			c.creditcard_errors = error.error_dict or {}
			return {'data':{'html':render('/contribution/payment_details_form.html').strip()}}
		else:
			c.creditcard_values = form_result
			try:
				websession['contribution'].methoddetails = CreditCard(**form_result)
			except AttributeError, e:
				self.messages.append(_(u"CONTRIBUTION_CREDITCARD_DETAILS_Some Error Occured. Your payment has not been processed."))
				return {'redirect':url('chipin', pool_url=pool_url, protocol=g.SSL_PROTOCOL)}

				
				
				
		try:
			return g.payment_service.post_process_payment(c, c.pool, render, redirect)
		except TokenNotExistsException, e:
			c.messages.append(_(u"CONTRIBUTION_CREDITCARD_DETAILS_Form Already Submitted, please standby!"))
			return {'redirect':url('chipin', pool_url=pool_url, protocol=g.SSL_PROTOCOL)}
		except UnsupportedPaymentMethod, e:
			tmpl_context.messages.append(_("CONTRIBUTION_PAGE_Unknown Payment Method"))
			return {'redirect':url('chipin', pool_url=pool_url, protocol=g.SSL_PROTOCOL)}
		except DBErrorDuringSetup, e:
			return self.ajax_messages(_(u"CONTRIBUTION_CREDITCARD_DETAILS_An error has occured, please try again later. Your payment has not been processed."))
		except DBErrorAfterPayment, e: # DISABLED since this is irrelevant with async notifications coming in
			return self.ajax_messages(_(u"CONTRIBUTION_CREDITCARD_DETAILS_A serious error occured, please try again later"))
	
	def success(self, pool_url):
		c.contrib = websession.get('contribution', None)
		if not c.contrib:
			return redirect(url("get_pool", pool_url=pool_url))
		c.has_fees = c.contrib.amount < c.contrib.total
		return render('/contribution/contribution_result_success.html')	
	def fail(self, pool_url):
		c.contrib = websession.get('contribution')
		if not c.contrib:
			return redirect(url("get_pool", pool_url=pool_url))
		c.has_fees = c.contrib.amount < c.contrib.total
		return render('/contribution/contribution_result_fail.html')
	
	
	
	
	
	
	
	
	