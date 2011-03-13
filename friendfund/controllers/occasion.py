import logging, formencode, datetime


from pylons import request, response, session as websession, tmpl_context as c, url, app_globals as g
from friendfund.lib import helpers as h
from pylons.decorators import jsonify
from pylons.controllers.util import abort, redirect

from friendfund.lib.base import BaseController, render, _
from friendfund.lib.tools import dict_contains
from friendfund.model.pool import Occasion, OccasionSearch, Pool
from friendfund.model.forms.common import DateValidator

log = logging.getLogger(__name__)

class OccasionController(BaseController):
	
	@jsonify
	def panel(self):
		c.lower_limit_date = h.format_date_internal(datetime.date.today() + datetime.timedelta(1))
		try:
			dob = datetime.datetime.strptime(request.params.get('dob', "").split()[0], '%Y-%m-%d').date()
		except:
			dob = None
		try:
			c.date = datetime.datetime.strptime(request.params.get('date', None), '%Y-%m-%d').date()
		except:
			c.date = ""
		c.key = request.params.get('key')
		c.name = request.params.get('name')
		c.olist = g.dbm.get(OccasionSearch, date = h.format_date_internal(datetime.date.today()), country = websession['region']).occasions
		bday = filter(lambda x:x.key == 'EVENT_BIRTHDAY', c.olist)
		if dob and len(bday):
			bday[0].date = dob
		result = {'clearmessage':True, 'html':render('/occasion/panel.html').strip()}
		return result
	
	@jsonify
	def unset(self):
		c.pool = websession.get('pool') or Pool()
		del pool.occasion
		websession['pool'] = c.pool
		return {'clearmessage':True, 'html':render('/occasion/button.html').strip()}
	
	@jsonify
	def set(self):
		params = formencode.variabledecode.variable_decode(request.params)
		occasion = params.get('occasion', None)
		if not occasion or not dict_contains(occasion, ['date', 'key']):
			return self.ajax_messages(_("INDEX_PAGE_No Occasion Found"))
		
		dv = DateValidator()
		try:
			occasion['date'] = dv.to_python(occasion['date'])
			occasion['custom'] = formencode.validators.StringBool().to_python(occasion['custom'])
		except formencode.validators.Invalid, error:
			return self.ajax_messages(_("INDEX_PAGE_Invalid Format - Occasion"))
		c.pool = websession.get('pool') or Pool()
		c.pool.occasion = Occasion(**occasion)
		websession['pool'] = c.pool
		return {'clearmessage':True, 'html':render('/occasion/button.html').strip()}