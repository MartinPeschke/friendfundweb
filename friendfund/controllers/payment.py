import logging, formencode
from copy import copy
from pylons import request, response, session as websession, tmpl_context as c, url, app_globals as g
from pylons.controllers.util import abort, redirect
from pylons.decorators import jsonify


from friendfund.lib import helpers as h, synclock
from friendfund.lib.auth.decorators import logged_in, no_blocks, enforce_blocks, checkadd_block
from friendfund.lib.base import ExtBaseController, render, _
from friendfund.lib.i18n import FriendFundFormEncodeState
from friendfund.lib.payment.adyen import UnsupportedOperation, UnsupportedPaymentMethod, DBErrorDuringSetup, DBErrorAfterPayment

from friendfund.model.contribution import Contribution, GetDetailsFromContributionRefProc
from friendfund.model.forms.contribution import PaymentIndexForm, PaymentConfForm
from friendfund.model.db_access import SProcException

paymentlog = logging.getLogger('payment.controller')
log = logging.getLogger(__name__)

class PaymentController(ExtBaseController):
	navposition=g.globalnav[1][2]
	
	def index(self, pool_url):
		c.values = getattr(c, 'values', {})
		c.errors = getattr(c, 'errors', {})
		suggested_amount = request.params.get('amount')
		try:suggested_amount = (float(suggested_amount)/100)
		except: pass
		else: c.values['amount'] = h.format_number(suggested_amount)
		c.payment_methods = g.payment_methods
		return self.render('/contribution/contrib_screen.html')
	
	def details(self, pool_url):
		c.payment_methods = g.payment_methods
		details = formencode.variabledecode.variable_decode(request.params).get('payment', None)
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
			return self.render('/contribution/contrib_screen.html')
		else:
			c.values = form_result
			if checkadd_block('email'):
				c.messages.append(_('CONTRIBUTION_EMAILBLOCK_We do need an Email address when you want to chip in!'))
				c.enforce_blocks = True
				return self.render('/contribution/contrib_screen.html')
			else:
				g.pool_service.invite_myself(c.pool, c.user)
			
			contrib = Contribution(**form_result)
			contrib.currency = c.pool.currency
			contrib.set_amount(form_result['amount'])
			contrib.set_total(form_result['total'])
			contrib.paymentmethod_code = form_result.get('method')
			
			tmpl_context.form_secret = str(uuid.uuid4())
			synclock.set_contribution(tmpl_context.form_secret, c.user, contrib)
			
			try:
				return g.payment_methods_map[contrib.paymentmethod_code].process(c, contrib, c.pool, self.render, redirect)
			except (UnsupportedPaymentMethod, KeyError), e:
				c.messages.append(_("CONTRIBUTION_PAGE_Unknown Payment Method"))
				return redirect(url("payment", pool_url=c.pool.p_url, protocol=g.SSL_PROTOCOL))
			except DBErrorDuringSetup, e:
				c.messages.append(_(u"CONTRIBUTION_CREDITCARD_DETAILS_An error has occured, please try again later. Your payment has not been processed."))
				return redirect(url("payment", pool_url=c.pool.p_url, protocol=g.SSL_PROTOCOL))
			except DBErrorAfterPayment, e:
				c.messages.append(_(u"CONTRIBUTION_CREDITCARD_DETAILS_A serious error occured, please try again later"))
				return redirect(url("payment", pool_url=c.pool.p_url, protocol=g.SSL_PROTOCOL))
	
	@logged_in(ajax=True)
	@no_blocks(ajax=True)
	def creditcard(self, pool_url):
		c.values = {}
		c.errors = {}
		if request.method != 'POST':
			c.messages.append(_(u"CONTRIBUTION_CREDITCARD_DETAILS_Method Not Allowed"))
		method_code = request.params.get("creditcard.ccType")
		try:
			return g.payment_methods_map[method_code].post_process(c, c.pool, self.render, redirect)
		except (UnsupportedPaymentMethod, KeyError), e:
			c.messages.append(_("CONTRIBUTION_PAGE_Unknown Payment Method"))
			return redirect(url("payment", pool_url=c.pool.p_url, protocol=g.SSL_PROTOCOL))
		except DBErrorDuringSetup, e:
			c.messages.append(_(u"CONTRIBUTION_CREDITCARD_DETAILS_An error has occured, please try again later. Your payment has not been processed."))
			return redirect(url("payment", pool_url=c.pool.p_url, protocol=g.SSL_PROTOCOL))
		except DBErrorAfterPayment, e:
			c.messages.append(_(u"CONTRIBUTION_CREDITCARD_DETAILS_A serious error occured, please try again later"))
			return redirect(url("payment", pool_url=c.pool.p_url, protocol=g.SSL_PROTOCOL))
		
	
	@logged_in(ajax=False)
	def success(self, pool_url):
		c.values = {"amount": h.format_currency(c.contrib.get_amount(), c.pool.currency)
					, "payment_method":paymentmethod.code
					, "is_secret":c.contrib.is_secret
					, "message":c.contrib.message
					}
		return self.render('/contribution/payment_success.html')
	@logged_in(ajax=False)
	def fail(self, pool_url):
		c.values = {"amount": h.format_currency(c.contrib.get_amount(), c.pool.currency)
					, "payment_method":paymentmethod.code
					, "is_secret":c.contrib.is_secret
					, "message":c.contrib.message
					}
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
		
		if c.contrib:
			c.values = {"amount": h.format_currency(c.contrib.get_amount(), c.pool.currency)
						, "payment_method":paymentmethod.code
						, "is_secret":c.contrib.is_secret
						, "message":c.contrib.message
						}
		c.show_delay = paymentmethod.has_result_delay
		if request.params.get('authResult') == 'AUTHORISED':
			return self.render('/contribution/payment_success.html')
		else:
			return self.render('/contribution/payment_fail.html')
		return self.render('/contribution/payment_details.html')