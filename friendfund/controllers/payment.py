import logging, formencode
from copy import copy
from pylons import request, response, session as websession, tmpl_context as c, url, app_globals as g
from pylons.controllers.util import abort, redirect
from pylons.decorators import jsonify

from friendfund.lib import helpers as h
from friendfund.lib.auth.decorators import logged_in, no_blocks, enforce_blocks, checkadd_block
from friendfund.lib.base import ExtBaseController, render, _
from friendfund.lib.i18n import FriendFundFormEncodeState

from friendfund.model.forms.contribution import PaymentIndexForm
from friendfund.model.db_access import SProcException
from friendfund.services.payment_service import NotAllowedToPayException

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
		
		if request.method != 'POST':
			return self.render('/contribution/contrib_screen.html')
		return self._check_contrib_details(c.pool)
	
	def _check_contrib_details(self, pool):
		pass
	def details(self, pool_url):
		details = formencode.variabledecode.variable_decode(request.params).get('payment', None)
		details['agreedToS'] = details.get('agreedToS', False)  #if_missing wouldnt evaluate, and if_empty returns MISSING VALUE error message, both suck bad
		schema = PaymentIndexForm()
		schema.fields['amount'].max = round(c.pool.get_amount_left(), 2)
		state = copy(c.pool)
		state.__dict__["_"] = FriendFundFormEncodeState._
		try:
			form_result = schema.to_python(details, state)
		except formencode.validators.Invalid, error:
			c.values = error.value
			c.errors = error.error_dict or {}
			print c.errors
			return self.render('/contribution/contrib_screen.html')
		return self.render('/contribution/payment_details.html')
	
	@logged_in(ajax=False)
	def payment_success(self, pool_url):
		return self.render('/contribution/payment_success.html')