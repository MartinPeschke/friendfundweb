import logging, formencode, datetime

from pylons import request, response, session as websession, tmpl_context as c, url, app_globals as g
from pylons.controllers.util import abort, redirect
from pylons.decorators import jsonify
from friendfund.lib.base import BaseController, render, _
from friendfund.model.pool import Pool
from friendfund.model.product import Product

from friendfund.lib.base import _
log = logging.getLogger(__name__)

class DataEditorController(BaseController):
	@jsonify
	def currency(self):
		if request.method == "GET":
			c.currency = request.params.get('value')
			c.currencies = sorted(g.country_choices.currencies)
			return {'html':render('/widgets/currency_selector.html').strip()}
		else:
			c.currency = request.params.get('value')
			if c.currency in g.country_choices.currencies:
				c.pool = websession.get('pool', Pool())
				c.pool.currency = c.currency
				websession['pool'] = c.pool
			return {'html':render('/widgets/currency_selector.html').strip()}