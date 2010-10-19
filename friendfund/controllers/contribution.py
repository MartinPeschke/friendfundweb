import logging, formencode, uuid, urllib, datetime

from pylons import request, response, session as websession, tmpl_context as c, url, app_globals as g, cache, config
from pylons.controllers.util import abort, redirect
from pylons.decorators import jsonify

from friendfund.lib import helpers as h
from friendfund.lib.auth.decorators import logged_in, no_blocks, enforce_blocks, checkadd_block
from friendfund.lib.base import BaseController, render, _
from friendfund.lib.i18n import FriendFundFormEncodeState
from friendfund.lib.payment.adyen import PaymentService
from friendfund.lib.synclock import add_token, rem_token, TokenNotExistsException
from friendfund.model.pool import Pool
from friendfund.model.db_access import SProcException
from friendfund.model.contribution import Contribution, CreditCard, DBContribution, DBPaymentInitialization, DBPaymentNotice
from friendfund.model.forms.contribution import PaymentConfForm, CreditCardForm, MonetaryValidator
from friendfund.tasks.photo_renderer import remote_pool_picture_render


paymentlog = logging.getLogger('payment.service')
strbool = formencode.validators.StringBoolean()

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
		c.contrib = websession.get('contribution')
		if c.contrib:
			c.chipin_values = {"amount": h.format_number(c.contrib.get_amount())
								, 'payment_method':c.contrib.paymentmethod
								, 'is_secret':c.contrib.is_secret
								, 'anonymous':c.contrib.anonymous and 'yes' or 'no'
								, 'message':c.contrib.message
							}
		c.success = request.params.get('authResult') == 'AUTHORISED'
		c.pool_fulfilled = False
		c.show_delay = c.contrib.paymentmethod in ['paypal','directEbanking']
		return self.render('/contribution/payment_details.html')
	
	@logged_in(ajax=False)
	def chipin_fixed(self, pool_url):
		c.pool = g.dbm.get(Pool, p_url = pool_url)
		if c.pool is None:
			return abort(404)
		c.action = 'chipin_fixed'
		c.chipin_values = {"amount": h.format_number(c.pool.get_amount_left())}
		c.chipin_errors = {}
		c.amount_fixed = True
		if request.method != 'POST':
			return self.render('/contribution/contrib_screen.html')
		return self._check_chip_in_details(pool_url)
		
	@logged_in(ajax=False)
	def chipin(self, pool_url):
		c.pool = g.dbm.get(Pool, p_url = pool_url)
		if c.pool is None:
			return abort(404)
		c.action = 'chipin'
		if not c.pool.is_contributable():
			c.messages.append(_(u"CONTRIBUTION_You cannot contribute to this pool at this time, this pool is closed."))
			return redirect(url('ctrlpoolindex', controller='pool', pool_url=pool_url, protocol='http'))
		c.chipin_values = getattr(c, 'chipin_values', {})
		c.chipin_errors = getattr(c, 'chipin_errors', {})
		c.amount_fixed = False
		if request.method != 'POST':
			return self.render('/contribution/contrib_screen.html')
		return self._check_chip_in_details(pool_url)
	
	def _check_chip_in_details(self, pool_url):
		chipin = formencode.variabledecode.variable_decode(request.params).get('chipin', None)
		if chipin.get('payment_method') not in ['credit_card', 'paypal','directEbanking']:
			c.messages.append(_("CONTRIBUTION_PAGE_Unknown Payment Method"))
			return redirect(url('chipin', pool_url=pool_url, protocol='https'))
		schema = PaymentConfForm()
		try:
			schema.fields['amount'].max = round(c.pool.get_amount_left(), 2)
			c.user.__dict__["_"] = FriendFundFormEncodeState._
			form_result = schema.to_python(chipin, c.user)
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
				return self.render('/contribution/contrib_screen.html')
			
			contrib = Contribution(**form_result)
			contrib.currency = c.pool.currency
			contrib.set_amount(form_result['amount'])
			contrib.set_total(form_result['total'])
			contrib.paymentmethod = chipin.get('payment_method')
			websession['contribution'] = contrib
		c.form_secret = str(uuid.uuid4())
		add_token(c.form_secret, c.action)
		
		if chipin.get('payment_method') in ['paypal','directEbanking']:
			contrib = websession['contribution']
			try:
				g.payment_service.get_request(c.user, contrib, pool_url, chipin.get('payment_method'))
			except SProcException, e:
				c.messages.append(_(u"CONTRIBUTION_CREDITCARD_DETAILS_An error has occured, please try again later. Your payment has not been processed."))
				return redirect(url('chipin', pool_url=pool_url, protocol='https'))
		elif chipin.get('payment_method') == 'credit_card':
			return redirect(url(controller='contribution', pool_url=pool_url, action='details', token=c.form_secret, protocol='https'))
		else:
			c.messages.append(_("CONTRIBUTION_PAGE_Unknown Payment Method"))
			return redirect(url('chipin', pool_url=pool_url, protocol='https'))
	
	@logged_in(ajax=False)
	@no_blocks(ajax=False)
	def details(self, pool_url):
		c.pool = g.dbm.get(Pool, p_url = pool_url)
		if c.pool is None:
			return abort(404)
		c.form_secret = request.params.get('token')
		if g.debug:
			c.creditcard_values = {"ccHolder":"Test User", "ccNumber":"4111111111111111", "ccCode":"737", "ccExpiresMonth":"12", "ccExpiresYear":"2012"}
		else:
			c.creditcard_values = {}
		if 'contribution' not in websession:
			c.messages.append(_(u"CONTRIBUTION_CREDITCARD_DETAILS_Form already submitted."))
			return redirect(url('chipin', pool_url=pool_url, protocol='https'))
		c.contrib = websession['contribution']
		return self.render('/contribution/payment_details.html')
	
	@logged_in(ajax=True)
	@no_blocks(ajax=True)
	@jsonify
	def creditcard(self, pool_url):
		c.pool = g.dbm.get(Pool, p_url = pool_url)
		if c.pool is None:
			return abort(404)
		c.creditcard_values = {}
		c.creditcard_errors = {}
		if 'contribution' not in websession:
			c.messages.append(_(u"CONTRIBUTION_CREDITCARD_DETAILS_Form already submitted."))
			return {'redirect':url('chipin', pool_url=pool_url, protocol='https')}
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
				return {'redirect':url('chipin', pool_url=pool_url, protocol='https')}
		try:
			action = rem_token(c.form_secret)
			c.pool_fulfilled = action == 'chipin_fixed'
		except TokenNotExistsException, e:
			return self.ajax_messages(_(u"CONTRIBUTION_CREDITCARD_DETAILS_Form Already Submitted, please standby!"))
		contrib = websession['contribution']
		contrib = DBContribution(amount = contrib.amount
								,total = contrib.total
								,is_secret = contrib.is_secret
								,anonymous = contrib.anonymous
								,message = contrib.message
								,paymentmethod = contrib.paymentmethod
								,u_id = c.user.u_id
								,network = c.user.network
								,network_id = c.user.network_id
								,email = c.user.email
								,p_url = pool_url)
		try:
			contrib = g.dbm.set(contrib, merge = True)
		except SProcException, e:
			return self.ajax_messages(_(u"CONTRIBUTION_CREDITCARD_DETAILS_An error has occured, please try again later. Your payment has not been processed."))
		
		websession['contribution'].ref = contrib.ref
		paymentresult = PaymentService.authorize(websession['contribution'])
		del websession['contribution']
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
			return self.ajax_messages(_(u"CONTRIBUTION_CREDITCARD_DETAILS_A serious error occured, please try again later"))
		c.success = (paymentresult['resultCode'] == 'Authorised')
		if c.success : remote_pool_picture_render.delay(pool_url)
		return {'data':{'html':render('/contribution/payment_success.html').strip()}}
	
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