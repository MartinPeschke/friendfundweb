import logging, formencode, datetime, uuid
from ordereddict import OrderedDict

from pylons import request, response, tmpl_context as c, url, app_globals as g, session as websession
from friendfund.lib import helpers as h
from friendfund.lib.auth.decorators import logged_in, post_only
from friendfund.lib.base import BaseController, render, _, render_def
from friendfund.lib.i18n import FriendFundFormEncodeState
from friendfund.model.forms.pool import PoolCreateForm
from friendfund.model.pool import OccasionSearch, PoolUser
from friendfund.model.product import DisplayProduct
log = logging.getLogger(__name__)

class PartnerController(BaseController):
	def simplebounce(self):
		query=request.params.get("referer")
		params = formencode.variabledecode.variable_decode(request.params, dict_char='.', list_char='?')
		c.product_list = g.product_service.get_products_from_open_graph(params.get("meta", {}), query)
		c.product = c.product_list[0]
		
		c.method = c.user.get_current_network() or 'facebook'
		c.olist = g.dbm.get(OccasionSearch, date = h.format_date_internal(datetime.date.today()), country = websession['region']).occasions
		
		c.values = {}
		c.errors = {}
		return self.render('/partner/iframe.html')
	
	@logged_in(ajax=False)
	@post_only(ajax=False)
	def validate(self):
		c.method = c.user.get_current_network() or 'facebook'
		product = request.params.get("productMap")
		c.product = DisplayProduct.from_minimal_repr(product)
		c.product_list = [c.product]
		receiver = request.params.get("invitees")
		c.receiver_data = h.decode_minimal_repr(receiver)
		receiver = PoolUser.fromMap(c.receiver_data)
		
		try:
			c.pool = g.pool_service.create_group_gift_from_iframe(c.product, receiver)
			c.furl = url("invite_index", pool_url = c.pool.p_url)
			return render("/widgets/bust_iframe.html")
		except formencode.validators.Invalid, error:
			c.olist = g.dbm.get(OccasionSearch, date = h.format_date_internal(datetime.date.today()), country = websession['region']).occasions
			c.errors = error.error_dict or {}
			c.values = error.value
			return self.render('/partner/iframe.html')
