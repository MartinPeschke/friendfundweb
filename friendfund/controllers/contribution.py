from __future__ import with_statement
import logging, formencode, urllib, datetime
from copy import copy
from pylons import request, response, session as websession, tmpl_context as c, url, app_globals as g, cache, config
from pylons.controllers.util import abort, redirect
from pylons.decorators import jsonify

from friendfund.lib import helpers as h
from friendfund.lib.auth.decorators import logged_in, no_blocks, enforce_blocks, checkadd_block
from friendfund.lib.base import BaseController, render, _
from friendfund.lib.i18n import FriendFundFormEncodeState
from friendfund.lib.payment.adyen import UnsupportedPaymentMethod, UnsupportedOperation, DBErrorAfterPayment, DBErrorDuringSetup
from friendfund.lib.synclock import TokenNotExistsException
from friendfund.model.pool import Pool
from friendfund.model.db_access import SProcException
from friendfund.model.contribution import Contribution, CreditCard, DBPaymentNotice
from friendfund.model.forms.contribution import PaymentConfForm, CreditCardForm, MonetaryValidator
from friendfund.services.payment_service import NotAllowedToPayException

paymentlog = logging.getLogger('payment.service')

from friendfund.services.pool_service import MissingPermissionsException

class ContributionController(BaseController):
	navposition=g.globalnav[1][2]
	
	@logged_in(ajax=False)
	def chipin_current(self):
		paymentlog.info( 'PAYMENT RETURN from External: %s' , request.params )
		if not g.payment_service.verify_result(request.params):
			return abort(404)
		elif not c.user.current_pool:
			return abort(404)
		c.pool = g.dbm.get(Pool, p_url = c.user.current_pool.p_url)
		if c.pool is None:
			return abort(404)
		c.contrib = websession.get('contribution')
		try:
			c.paymentpage = g.payment_service.get_payment_settings(c.pool.region, c.pool.product.is_virtual, c.user, c.pool)
			c.has_fees = c.paymentpage.has_fees
		except NotAllowedToPayException, e:
			c.messages.append(_(u"CONTRIBUTION_Payment Not Allowed."))
			return redirect(url('ctrlpoolindex', controller='pool', pool_url=c.pool.p_url, protocol='http'))
		if c.contrib:
			c.chipin_values = {"amount": h.format_number(c.contrib.get_amount())
								, 'payment_method':c.contrib.paymentmethod
								, 'is_secret':c.contrib.is_secret
								, 'anonymous':c.contrib.anonymous and 'yes' or 'no'
								, 'message':c.contrib.message
							}
		c.show_delay = c.contrib.paymentmethod in ['paypal','directEbanking']
		if request.params.get('authResult') == 'AUTHORISED':
			return self.render('/contribution/contribution_result_success.html')
		else:
			return self.render('/contribution/contribution_result_fail.html')
	
	@logged_in(ajax=False)
	def chipin_fixed(self, pool_url):
		c.pool = g.dbm.get(Pool, p_url = pool_url)
		if c.pool is None:
			return abort(404)
		try:
			c.paymentpage = g.payment_service.get_payment_settings(c.pool.region, c.pool.product.is_virtual, c.user, c.pool)
		except NotAllowedToPayException, e:
			c.messages.append(_(u"CONTRIBUTION_Payment Not Allowed."))
			return redirect(url('ctrlpoolindex', controller='pool', pool_url=c.pool.p_url, protocol='http'))
		c.action = 'chipin_fixed'
		c.chipin_values = {"amount": h.format_number(c.pool.get_amount_left())}
		c.chipin_errors = {}
		c.amount_fixed = True
		c.back_to_admin = True
		if request.method != 'POST':
			return self.render('/contribution/contrib_screen.html')
		return self._check_chip_in_details(c.pool)
	
	@logged_in(ajax=False)
	def virtual(self, pool_url):
		c.pool = g.dbm.get(Pool, p_url = pool_url)
		if c.pool is None:
			return abort(404)
		c.action = 'chipin'
		if not c.pool.is_contributable():
			c.messages.append(_(u"CONTRIBUTION_You cannot contribute to this pool at this time, this pool is closed."))
			return redirect(url('ctrlpoolindex', controller='pool', pool_url=pool_url, protocol='http'))
		try:
			c.paymentpage = g.payment_service.get_payment_settings(c.pool.region, c.pool.product.is_virtual, c.user, c.pool)
		except NotAllowedToPayException, e:
			c.messages.append(_(u"CONTRIBUTION_Payment Not Allowed."))
			return redirect(url('ctrlpoolindex', controller='pool', pool_url=pool_url, protocol='http'))
		
		contrib = Contribution(agreedToS=True, is_secret=False,anonymous=False, message="")
		contrib.currency = c.pool.currency
		contrib.set_amount(1)
		contrib.set_total(1)
		contrib.paymentmethod = c.paymentpage.methods[0].code
		return g.payment_service.process_payment(c, contrib, c.pool, render, redirect)
	
	@logged_in(ajax=False)
	def chipin(self, pool_url):
		c.pool = g.dbm.get(Pool, p_url = pool_url)
		if c.pool is None:
			return abort(404)
		c.action = 'chipin'
		if not c.pool.is_contributable():
			c.messages.append(_(u"CONTRIBUTION_You cannot contribute to this pool at this time, this pool is closed."))
			return redirect(url('ctrlpoolindex', controller='pool', pool_url=pool_url, protocol='http'))
		try:
			c.paymentpage = g.payment_service.get_payment_settings(c.pool.region, c.pool.product.is_virtual, c.user, c.pool)
		except NotAllowedToPayException, e:
			c.messages.append(_(u"CONTRIBUTION_Payment Not Allowed."))
			return redirect(url('ctrlpoolindex', controller='pool', pool_url=pool_url, protocol='http'))
		c.chipin_values = getattr(c, 'chipin_values', {})
		c.chipin_errors = getattr(c, 'chipin_errors', {})
		c.amount_fixed = False
		c.back_to_admin = False
		if request.method != 'POST':
			return self.render('/contribution/contrib_screen.html')
		return self._check_chip_in_details(c.pool)
	
	def _check_chip_in_details(self, pool):
		chipin = formencode.variabledecode.variable_decode(request.params).get('chipin', None)
		if not g.payment_service.check_payment_method(chipin.get('payment_method'), pool.region, pool.product.is_virtual):
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
			#ugly hack, but otherwise i cant set selected or not not correctly, as template gets "yes" and True alternatively on error and on permission
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
			websession['contribution'] = contrib
			try:
				return g.payment_service.process_payment(c, contrib, pool, render, redirect)
			except UnsupportedPaymentMethod, e:
				tmpl_context.messages.append(_("CONTRIBUTION_PAGE_Unknown Payment Method"))
				return redirect(url('chipin', pool_url=pool.p_url, protocol='g.SSL_PROTOCOL'))
			except DBErrorDuringSetup, e:
				return self.ajax_messages(_(u"CONTRIBUTION_CREDITCARD_DETAILS_An error has occured, please try again later. Your payment has not been processed."))
			except DBErrorAfterPayment, e:
				return self.ajax_messages(_(u"CONTRIBUTION_CREDITCARD_DETAILS_A serious error occured, please try again later"))
	
	@logged_in(ajax=False)
	@no_blocks(ajax=False)
	def details(self, pool_url):
		c.pool = g.dbm.get(Pool, p_url = pool_url)
		if c.pool is None:
			return abort(404)
		try:
			c.paymentpage = g.payment_service.get_payment_settings(c.pool.region, c.pool.product.is_virtual, c.user, c.pool)
		except NotAllowedToPayException, e:
			c.messages.append(_(u"CONTRIBUTION_Payment Not Allowed."))
			return redirect(url('ctrlpoolindex', controller='pool', pool_url=pool_url, protocol='http'))
		c.form_secret = request.params.get('token')
		if g.test:
			c.creditcard_values = {"ccHolder":"Test User", "ccNumber":"4111111111111111", "ccCode":"737", "ccExpiresMonth":"12", "ccExpiresYear":"2012"}
		else:
			c.creditcard_values = {}
		if 'contribution' not in websession:
			c.messages.append(_(u"CONTRIBUTION_CREDITCARD_DETAILS_Form already submitted."))
			return redirect(url('chipin', pool_url=pool_url, protocol='g.SSL_PROTOCOL'))
		c.contrib = websession['contribution']
		return self.render('/contribution/payment_details.html')
	
	@logged_in(ajax=True)
	@no_blocks(ajax=True)
	@jsonify
	def creditcard(self, pool_url):
		c.pool = g.dbm.get(Pool, p_url = pool_url)
		if c.pool is None or c.pool.product.is_virtual:
			return abort(404)
		c.creditcard_values = {}
		c.creditcard_errors = {}
		
		if 'contribution' not in websession:
			c.messages.append(_(u"CONTRIBUTION_CREDITCARD_DETAILS_Form already submitted."))
			return {'redirect':url('chipin', pool_url=pool_url, protocol='g.SSL_PROTOCOL')}
		if request.method != 'POST':
			return self.ajax_messages(_(u"CONTRIBUTION_CREDITCARD_DETAILS_Method Not Allowed"))
		
		c.form_secret = request.POST.get('formtoken')
		if not c.form_secret:
			return self.ajax_messages(_(u"CONTRIBUTION_CREDITCARD_DETAILS_Incorrect Payment Form Data, Token missing. Your payment has not been processed."))
		
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
				return {'redirect':url('chipin', pool_url=pool_url, protocol='g.SSL_PROTOCOL')}
		try:
			return g.payment_service.post_process_payment(c, websession['contribution'], c.pool, render, redirect)
		except TokenNotExistsException, e:
			return self.ajax_messages(_(u"CONTRIBUTION_CREDITCARD_DETAILS_Form Already Submitted, please standby!"))
		except UnsupportedPaymentMethod, e:
			tmpl_context.messages.append(_("CONTRIBUTION_PAGE_Unknown Payment Method"))
			return redirect(url('chipin', pool_url=pool_url, protocol='g.SSL_PROTOCOL'))
		except DBErrorDuringSetup, e:
			return self.ajax_messages(_(u"CONTRIBUTION_CREDITCARD_DETAILS_An error has occured, please try again later. Your payment has not been processed."))
		except DBErrorAfterPayment, e: # DISABLED since this is irrelevant with async notifications coming in
			return self.ajax_messages(_(u"CONTRIBUTION_CREDITCARD_DETAILS_A serious error occured, please try again later"))
	
	def success(self, pool_url):
		c.contrib = websession.get('contribution', None)
		if not c.contrib:
			return redirect(url("get_pool", pool_url=pool_url))
		c.pool = g.dbm.get(Pool, p_url = pool_url)
		if c.pool is None:
			return abort(404)
		c.has_fees = c.contrib.amount < c.contrib.total
		return render('/contribution/contribution_result_success.html')	
	def fail(self, pool_url):
		c.contrib = websession.get('contribution')
		if not c.contrib:
			return redirect(url("get_pool", pool_url=pool_url))
		c.pool = g.dbm.get(Pool, p_url = pool_url)
		if c.pool is None:
			return abort(404)
		c.has_fees = c.contrib.amount < c.contrib.total
		return render('/contribution/contribution_result_fail.html')
	
	
	
	
	
	
	
	
	
	
	
	def service(self):
		"""basic auth: adyen/4epayeguka7ew43frEst5b4u"""
		if request.method != 'POST':
			return ['rejected']
		params = request.POST
		if str(params['eventCode']) in ['AUTHORISATION', 'REFUND', 'CANCELLATION', 'CAPTURE', 'CHARGEBACK', 'CHARGEBACK_REVERSED']:
			paymentlog.info( 'headers=%s', request.headers )
			paymentlog.info( 'post_params=%s', request.params )
			paymentlog.info( '-'*40 )
		else:
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
			g.dbm.set(notice)
		except SProcException, e:
			log.error(e)
		finally:
			return '[accepted]'