import logging
from datetime import datetime

from pylons import app_globals, tmpl_context, session as websession

from friendfund.model.product import ProductRetrieval, ProductSuggestionSearch, ProductSearch
from friendfund.model.product_search import ProductSearchByCategory

log = logging.getLogger(__name__)

_ = lambda x:x
SORTEES = [("RANK",_("PRODUCT_SORT_ORDER_Relevancy")),
			("PRICE_UP",_("PRODUCT_SORT_ORDER_Price up")),
			("PRICE_DOWN",_("PRODUCT_SORT_ORDER_Price down")),
			("MERCHANT",_("PRODUCT_SORT_ORDER_Merchant"))]
PAGESIZE = 5

GIFT_PANEL_TABS = [("recommended_tab", _("PRODUCT_SEARCH_PANEL_Recommended Gifts")),
					("virtual_tab", _("PRODUCT_SEARCH_PANEL_Virtual Gifts")),
					("search_tab", _("PRODUCT_SEARCH_PANEL_Gift Search"))
				]

from pylons.i18n import ugettext as _

class ProductService(object):
	"""
		This is shared between all threads, do not stick state in here!
	"""
	
	def __init__(self, amazon_services, product_categories):
		if not isinstance(amazon_services, dict) or len(amazon_services) < 3:
			raise Exception("Insufficient Amazon Services")
		self.amazon_services = amazon_services
		self.product_categories = product_categories
		self.category_map = dict([(cat.name,cat) for cat in self.product_categories.list])
	
	def request_setup(self, request):
		tmpl_context.region = request.params.get('region', websession['region'])
		tmpl_context.gift_panel_tabs = GIFT_PANEL_TABS
		tmpl_context.sortees = SORTEES
		tmpl_context.sort = SORTEES[0][0]
		return tmpl_context
	def request_search_setup(self, request):
		tmpl_context.page = request.params.get('page', 1)
		tmpl_context.sort = request.params.get('sort', "RANK")
		tmpl_context.page_size = 6
		return tmpl_context
	
	def recommended_tab(self, request):
		tmpl_context = self.request_setup(request)
		tmpl_context.panel = 'recommended_tab'
		tmpl_context.search_base_url='recommended_tab_search'
		tmpl_context.categories = self.product_categories.list
		tmpl_context.category = request.params.get('category')
		if tmpl_context.category and tmpl_context.category not in self.category_map:
			abort(404)
		tmpl_context.category = self.category_map.get(tmpl_context.category)
		return tmpl_context
	def recommended_tab_search(self, request):
		tmpl_context = self.recommended_tab(request)
		tmpl_context = self.request_search_setup(request)
		tmpl_context.search_keys = [('category', tmpl_context.category.name),
									('sort', tmpl_context.sort)]
		tmpl_context.searchresult = app_globals.dbsearch.call(ProductSearchByCategory(
							region=tmpl_context.region,
							category=tmpl_context.category.name,
							page_no = tmpl_context.page,
							page_size = tmpl_context.page_size,
							sort = tmpl_context.sort
							), ProductSearchByCategory)
		return tmpl_context
	
	
	
	def virtual_tab(self, request):
		tmpl_context = self.request_setup(request)
		tmpl_context.panel = 'virtual_tab'
		return tmpl_context
	
	def search_tab(self, request):
		tmpl_context = self.request_setup(request)
		tmpl_context.panel = 'search_tab'
		tmpl_context.q = None
		tmpl_context.back_q = None
		tmpl_context.amazon_available = bool(self.amazon_services.get(tmpl_context.region))
		tmpl_context.psuggestions = app_globals.dbsearch.get(ProductSuggestionSearch\
									, country = tmpl_context.region\
									, occasion = request.params.get('occasion_key', None)\
									, receiver_sex = request.params.get('sex', None)).suggestions
		return tmpl_context