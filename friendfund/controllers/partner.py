from __future__ import with_statement
import logging, formencode, datetime, uuid, socket, urllib2, urlparse
from BeautifulSoup import BeautifulSoup
from ordereddict import OrderedDict

from pylons import request, response, tmpl_context as c, url, app_globals, session as websession
from pylons.controllers.util import abort, redirect
from friendfund.lib import helpers as h
from friendfund.lib.auth.decorators import logged_in, post_only, workflow_available
from friendfund.lib.base import BaseController, render, _, render_def
from friendfund.lib.i18n import FriendFundFormEncodeState
from friendfund.model.common import SProcWarningMessage
from friendfund.model.forms.pool import PoolCreateForm
from friendfund.model.pool import OccasionSearch, PoolUser, FeaturedPool
from friendfund.model.product import DisplayProduct
from friendfund.tasks.cache_refresher import get_mfp_key
log = logging.getLogger(__name__)

class PartnerController(BaseController):
	def _get_run_time(self):
		return app_globals.pool_service.pool_run_time
	def _get_featured_pools(self, merchant):
		with app_globals.cache_pool.reserve() as mc:
			featured_pools = mc.get(get_mfp_key(merchant.key))
		if featured_pools is None:
			log.warning("NO_MERCHANT_FEATURED_POOLS_FOUND_IN_CACHE_REVERTING_TO_LOCAL_GET")
			featured_pools = []
			for p in merchant.featured_pools:
				 featured_pools.append(app_globals.dbm.get(FeaturedPool, p_url = p.p_url))
		return featured_pools



	def bounce(self):
		c.backup_values = request.params
		query=request.params.get("referer")
		key=request.params.get("key")
		host=request.params.get("host")
		real_host=request.params.get("real_host")
		
		total_param_set = formencode.variabledecode.variable_decode(request.params, dict_char='.', list_char='?')
		params = total_param_set.get("ff", {}).get("names", {})
		params.update(total_param_set.get("ff", {}).get("props", {}))
		
		c.pool_run_time = self._get_run_time()
		c.is_default = False
		c.product_list = app_globals.product_service.get_products_from_open_graph(params, query)
		if not len(c.product_list):
			c.get_featured_pools = self._get_featured_pools
			return self.render('/partner/iframe_home.html')
		
		c.product = c.product_list[0]
		c.method = c.user.get_current_network() or 'facebook'
		c.olist = app_globals.dbm.get(OccasionSearch, date = h.format_date_internal(datetime.date.today()), country = websession['region']).occasions
		c.values = {"occasion_name":c.olist[0].get_display_name(), "date":h.format_date(datetime.datetime.now()+datetime.timedelta(10), format="long")}
		c.errors = {}
		return self.render('/partner/iframe_product.html')
	
	@workflow_available()
	def preset(self):
		c._workflow['query']=request.params.get("referer")
		c._workflow['key']=request.params.get("key")
		c._workflow['host']=request.params.get("host")
		c._workflow['real_host']=request.params.get("real_host")
		total_param_set = formencode.variabledecode.variable_decode(request.params, dict_char='.', list_char='?')
		params = total_param_set.get("ff", {}).get("names", {})
		params.update(total_param_set.get("ff", {}).get("props", {}))
		c._workflow['product_list'] = app_globals.product_service.get_products_from_open_graph(params, c._workflow['query'])
		return redirect(url(controller="partner", action="set", ck = c._workflow._key))
		
	@workflow_available(presence_required = True)
	def set(self):
		c.product_list = c._workflow['product_list']
		c.pool_run_time = self._get_run_time()
		if not len(c.product_list):
			c.get_featured_pools = self._get_featured_pools
			return self.render('/partner/iframe_home.html')
		
		c.product = c.product_list[0]
		c.method = c.user.get_current_network() or 'facebook'
		c.olist = app_globals.dbm.get(OccasionSearch, date = h.format_date_internal(datetime.date.today()), country = websession['region']).occasions
		c.values = {"occasion_name":c.olist[0].get_display_name(), "date":h.format_date(datetime.datetime.now()+datetime.timedelta(10), format="long")}
		c.errors = {}
		return self.render('/partner/iframe_product.html')
	
	
	
	
	
	@logged_in(ajax=False)
	@post_only(ajax=False)
	def validate(self):
		c.method = c.user.get_current_network() or 'facebook'
		product = request.params.get("productMap")
		c.product = DisplayProduct.from_minimal_repr(product)
		try:
			c.pool = app_globals.pool_service.create_group_gift_from_iframe(c.product)
			return redirect(url("invite_index", pool_url = c.pool.p_url))
		except formencode.validators.Invalid, error:
			c.olist = app_globals.dbm.get(OccasionSearch, date = h.format_date_internal(datetime.date.today()), country = websession['region']).occasions
			c.errors = error.error_dict or {}
			c.values = error.value
			return self.render('/partner/create.html')
	
	@workflow_available()
	def prepare(self):
		product = request.params.get("productMap")
		c._workflow['product'] = DisplayProduct.from_minimal_repr(product)
		c.furl = url(controller="partner", action="get_started", ck = c._workflow._key)
		return render("/widgets/bust_iframe.html")
	
	@workflow_available(presence_required = True)
	def get_started(self):
		c.furl = url(controller="partner", action="details", ck = c._workflow._key)
		if not c.user.is_anon:
			return redirect(c.furl)
		c.product = c._workflow['product']
		c.method = c.user.get_current_network() or 'facebook'
		c.signup_values = {}
		c.signup_errors = {}
		if request.method != 'POST':
			return self.render('/partner/signup.html')
		signup = formencode.variabledecode.variable_decode(request.params).get('signup', None)
		try:
			c.user = app_globals.user_service.signup_email_user(signup)
			return redirect(c.furl)
		except formencode.validators.Invalid, error:
			c.signup_values = error.value
			c.signup_errors = error.error_dict or {}
			return self.render('/partner/signup.html')
		except SProcWarningMessage, e:
			c.signup_values = signup
			c.signup_errors = {'email':_("USER_SIGNUP_EMAIL_ALREADY_EXISTS")}
			c.messages.append(_(u"USER_SIGNUP_If this is you, please try logging in with your email address and password or %(link_open)srequest a password change!%(link_close)s") \
							% {'link_open':"<a onclick=\"window.__auth__.forgotPassword('%s')\">" %url(controller='myprofile', action='rppopup'), 'link_close':'</a>'})
			return self.render('/partner/signup.html')
		
	@workflow_available(presence_required = True)
	def details(self):
		if c.user.is_anon:
			return redirect(url(controller="partner", action="get_started", ck = c._workflow._key))

		c.product = c._workflow['product']
		c.method = c.user.get_current_network() or 'facebook'
		
		c.olist = app_globals.dbm.get(OccasionSearch, date = h.format_date_internal(datetime.date.today()), country = websession['region']).occasions
		c.values = {"occasion_name":c.olist[0].get_display_name()
					, "date":h.format_date(datetime.datetime.now()+datetime.timedelta(10), format="long")
					, "title":c.product.get_iframe_display_label(words = 8)
					, "description":c.product.description
					}
		c.errors = {}
		return self.render('/partner/create.html')