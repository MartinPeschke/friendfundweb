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
	def currency(self, verb):
		c.verb = verb
		if verb not in ['e','d']:
			return abort(403)
		elif verb == 'e':
			c.currency = request.params.get('value')
			c.currencies = sorted(g.country_choices.currencies)
			return {'html':render('/widgets/currency_selector.html').strip()}
		elif verb == 'd':
			c.currency = request.params.get('value')
			if c.currency in g.country_choices.currencies:
				c.pool = websession.get('pool', Pool())
				c.pool.currency = c.currency
				websession['pool'] = c.pool
			return {'html':render('/widgets/currency_selector.html').strip()}
	
	@jsonify
	def prodname(self, verb):
		c.verb = verb
		if verb not in ['e','d']:
			return abort(403)
		elif verb == 'e':
			c.ptitle = request.params.get('value')
			return {'html':render('/widgets/product_title_editor.html').strip()}
		elif verb == 'd':
			c.ptitle = request.params.get('value')
			c.pool = websession.get('pool', Pool())
			c.pool.product = c.pool.product or Product()
			c.pool.product.title = c.ptitle
			websession['pool'] = c.pool
			return {'html':render('/widgets/product_title_editor.html').strip()}

	@jsonify
	def proddesc(self, verb):
		c.verb = verb
		if verb not in ['e','d']:
			return abort(403)
		elif verb == 'e':
			c.pdesc = request.params.get('value')
			return {'html':render('/widgets/product_description_editor.html').strip()}
		elif verb == 'd':
			pdesc = request.params.get('value')
			c.pool = websession.get('pool', Pool())
			c.pool.product = c.pool.product or Product()
			c.pool.product.description = pdesc
			c.pdesc = c.pool.product.get_display_description()
			websession['pool'] = c.pool
			return {'html':render('/widgets/product_description_editor.html').strip()}