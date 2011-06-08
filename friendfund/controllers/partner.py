import logging, formencode, datetime, uuid, socket, urllib2, urlparse
from BeautifulSoup import BeautifulSoup
from ordereddict import OrderedDict

from pylons import request, response, tmpl_context as c, url, app_globals as g, session as websession
from pylons.controllers.util import abort, redirect
from friendfund.controllers.index import IndexController
from friendfund.lib import helpers as h
from friendfund.lib.auth.decorators import logged_in, post_only
from friendfund.lib.base import BaseController, render, _, render_def
from friendfund.lib.i18n import FriendFundFormEncodeState
from friendfund.model.forms.pool import PoolCreateForm
from friendfund.model.pool import OccasionSearch, PoolUser
from friendfund.model.product import DisplayProduct
log = logging.getLogger(__name__)

class PartnerController(BaseController):
	def bounce(self):
		c.backup_values = request.params
		query=request.params.get("referer")
		key=request.params.get("key")
		host=request.params.get("host")
		real_host=request.params.get("real_host")
		
		total_param_set = formencode.variabledecode.variable_decode(request.params, dict_char='.', list_char='?')
		params = total_param_set.get("ff", {}).get("names", {})
		params.update(total_param_set.get("ff", {}).get("props", {}))
		
		c.is_default = False
		c.product_list = g.product_service.get_products_from_open_graph(params, query)
		if not len(c.product_list):
			index = IndexController()
			c.suggested_pools = index._get_featured_pools()
			return self.render('/partner/iframe_home.html')
		
		c.product = c.product_list[0]
		c.method = c.user.get_current_network() or 'facebook'
		c.olist = g.dbm.get(OccasionSearch, date = h.format_date_internal(datetime.date.today()), country = websession['region']).occasions
		c.values = {"occasion_name":c.olist[0].get_display_name(), "date":h.format_date(datetime.datetime.now()+datetime.timedelta(10), format="long")}
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
		receiver = PoolUser.from_map(c.receiver_data)
		
		try:
			c.pool = g.pool_service.create_group_gift_from_iframe(c.product, receiver)
			c.furl = url("invite_index", pool_url = c.pool.p_url)
			return render("/widgets/bust_iframe.html")
		except formencode.validators.Invalid, error:
			c.olist = g.dbm.get(OccasionSearch, date = h.format_date_internal(datetime.date.today()), country = websession['region']).occasions
			c.errors = error.error_dict or {}
			c.values = error.value
			return self.render('/partner/iframe.html')
