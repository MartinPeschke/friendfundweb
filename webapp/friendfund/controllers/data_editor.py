import logging

from pylons.templating import render_mako as render

from pylons import request, session as websession, tmpl_context as c, app_globals as g
from pylons.decorators import jsonify

from friendfund.lib.base import BaseController

from friendfund.model.pool import Pool

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