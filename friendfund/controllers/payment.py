import logging, formencode
from copy import copy
from pylons import request, response, session as websession, tmpl_context as c, url, app_globals as g
from pylons.controllers.util import abort, redirect
from pylons.decorators import jsonify

from friendfund.lib import helpers as h
from friendfund.lib.auth.decorators import logged_in, no_blocks, enforce_blocks, checkadd_block
from friendfund.lib.base import ExtBaseController, render, _
from friendfund.lib.i18n import FriendFundFormEncodeState

from friendfund.model.forms.contribution import PaymentIndexForm, PaymentConfForm
from friendfund.model.db_access import SProcException

paymentlog = logging.getLogger('payment.controller')
log = logging.getLogger(__name__)

class PaymentController(ExtBaseController):
	navposition=g.globalnav[1][2]
	
	@logged_in(ajax=False)
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
			contrib.paymentmethod = form_result.get('payment_method')
			
			try:
				return g.payment_methods_map[contrib.paymentmethod].process(c, contrib, pool, render, redirect)
			except UnsupportedPaymentMethod, e:
				tmpl_context.messages.append(_("CONTRIBUTION_PAGE_Unknown Payment Method"))
				return redirect(url("payment", pool_url=pool.p_url, protocol=g.SSL_PROTOCOL))
			except DBErrorDuringSetup, e:
				return self.ajax_messages(_(u"CONTRIBUTION_CREDITCARD_DETAILS_An error has occured, please try again later. Your payment has not been processed."))
			except DBErrorAfterPayment, e:
				return self.ajax_messages(_(u"CONTRIBUTION_CREDITCARD_DETAILS_A serious error occured, please try again later"))
	
	@logged_in(ajax=True)
	@no_blocks(ajax=True)
	@jsonify
	def creditcard(self, pool_url):
		c.values = {}
		c.errors = {}
		if request.method != 'POST':
			return self.ajax_messages(_(u"CONTRIBUTION_CREDITCARD_DETAILS_Method Not Allowed"))
		
	
	@logged_in(ajax=False)
	def payment_success(self, pool_url):
		return self.render('/contribution/payment_success.html')

	@logged_in(ajax=False)
	def det(self, pool_url):
		return self.render('/contribution/payment_details.html')