import logging, urlparse
from datetime import datetime

from pylons import app_globals, tmpl_context, session as websession
from pylons.controllers.util import abort
from friendfund.model.product import ProductRetrieval, ProductSuggestionSearch, ProductSearch
from friendfund.model.product_search import ProductSearchByCategory
from friendfund.model.virtual_product import ProductPager
from friendfund.model.pool import Pool

log = logging.getLogger(__name__)

class AmazonWrongRegionException(Exception):pass
class AmazonUnsupportedRegionException(Exception):pass


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
	SCROLLER_PAGE_SIZE = 5
	
	def __init__(self, amazon_services, product_categories, virtual_gifts, top_sellers, country_choices):
		if not isinstance(amazon_services, dict) or len(amazon_services) < 3:
			raise Exception("Insufficient Amazon Services")
		self.amazon_services = amazon_services
		self.product_categories = product_categories
		self.category_map = dict([(cat.name,cat) for cat in self.product_categories.list])
		
		
		self.top_sellers = {}
		self.virtual_gifts = {}
		for k,v in top_sellers.map.items():
			if len(v)%self.SCROLLER_PAGE_SIZE != 0:
				top_sellers.map[k] = v + v[:self.SCROLLER_PAGE_SIZE-len(v)%self.SCROLLER_PAGE_SIZE]
		
		for region, countries  in country_choices.r2c_map.iteritems():
			for country in countries:
				self.top_sellers[country] = top_sellers.map[region.upper()]
				self.virtual_gifts[country] = virtual_gifts.map[region.upper()]

		self.virtual_gift_map = dict([(gift.guid, gift) for region, gifts in self.virtual_gifts.iteritems() for gift in gifts])

		
	
	def setup_region(self, request):
		tmpl_context.region = request.params.get('region', websession['region'])
		return tmpl_context
		
	def request_setup(self, request):
		tmpl_context = self.setup_region(request)
		tmpl_context.gift_panel_tabs = GIFT_PANEL_TABS
		tmpl_context.sortees = SORTEES
		tmpl_context.sort = SORTEES[0][0]
		tmpl_context.search_keys = {}
		return tmpl_context
	def request_search_setup(self, request):
		tmpl_context.page = int(request.params.get('page', 1))
		tmpl_context.search_keys = dict(request.params.iteritems())
		tmpl_context.search_keys['page'] = tmpl_context.page
		tmpl_context.sort = request.params.get('sort', "RANK")
		tmpl_context.page_size = 6
		return tmpl_context
	
	def recommended_tab(self, request):
		tmpl_context = self.request_setup(request)
		tmpl_context.panel = 'recommended_tab'
		tmpl_context.search_base_url='recommended_tab_search'
		tmpl_context.categories = self.product_categories.list
		tmpl_context.SCROLLER_PAGE_SIZE = self.SCROLLER_PAGE_SIZE
		tmpl_context.category = request.params.get('category')
		
		tmpl_context.top_sellers = self.top_sellers[tmpl_context.region]
		
		if tmpl_context.category and tmpl_context.category not in self.category_map:
			abort(404)
		tmpl_context.category = self.category_map.get(tmpl_context.category)
		return tmpl_context
	def recommended_tab_search(self, request):
		tmpl_context = self.recommended_tab(request)
		tmpl_context = self.request_search_setup(request)
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
		tmpl_context = self.request_search_setup(request)
		tmpl_context.panel = 'virtual_tab'
		tmpl_context.search_base_url='virtual_tab_search'
		tmpl_context.sort = request.params.get('sort', "PRICE_UP")
		tmpl_context.searchresult = ProductPager(
				region = tmpl_context.region
				,page_no = tmpl_context.page
				,page_size = tmpl_context.page_size
				,sort = tmpl_context.sort
				,products = self.virtual_gifts[tmpl_context.region]
			)
		return tmpl_context
	
	
	
	def search_tab_setup(self, request):
		tmpl_context = self.request_setup(request)
		tmpl_context.panel = 'search_tab'
		tmpl_context.aff_net = request.params.get('aff_net', None)
		tmpl_context.aff_net_ref = request.params.get('aff_net_ref', None)
		tmpl_context.searchterm = request.params.get('searchterm', '')
		tmpl_context.max_price = request.params.get('price', None)
		tmpl_context.currency = request.params.get('currency', None)
		tmpl_context.amazon_available = bool(self.amazon_services.get(tmpl_context.region))
		return tmpl_context
	
	def search_tab(self, request):
		tmpl_context = self.search_tab_setup(request)
		tmpl_context.search_base_url='search_tab_search'
		tmpl_context.psuggestions = app_globals.dbsearch.get(ProductSuggestionSearch\
									, country = tmpl_context.region\
									, occasion = request.params.get('occasion_key', None)\
									, receiver_sex = request.params.get('sex', None)).suggestions
		return tmpl_context
	
	def search_tab_search(self, request):
		tmpl_context = self.search_tab_setup(request)
		tmpl_context = self.request_search_setup(request)
		tmpl_context.search_base_url='search_tab_search'
		
		if tmpl_context.searchterm.startswith("http://") and tmpl_context.amazon_available:
				return self._amazon_fallback(request, tmpl_context.searchterm)
		else:
			tmpl_context.searchresult = app_globals.dbsearch.call(ProductSearch( 
										sort = tmpl_context.sort,
										page_size = tmpl_context.page_size,
										program_id = tmpl_context.aff_net_ref, 
										search=tmpl_context.searchterm, 
										page_no=tmpl_context.page,
										region=tmpl_context.region,
										max_price = tmpl_context.max_price), ProductSearch)
			tmpl_context.searchterm = request.params.get("catname", tmpl_context.searchterm)
		return tmpl_context
	
	def _amazon_fallback(self, request, url):
		scheme, domain, path, query, fragment = urlparse.urlsplit(url)
		tmpl_context.searchterm = "Amazon Link"
		if domain not in self.amazon_services:
			raise AmazonUnsupportedRegionException()
		elif self.amazon_services[domain] != self.amazon_services[tmpl_context.region]:
			raise AmazonWrongRegionException()
		else:
			tmpl_context.searchresult = self.amazon_services[domain].get_product_from_url(url)
		return tmpl_context
	
	
	def getaltproduct(self, product, region):
		if product['is_amazon']:
			product = self.amazon_services[region].get_product_from_guid(product['guid'])
		elif product['is_virtual']:
			product = self.virtual_gift_map[product['guid']]
		else:
			productresult = app_globals.dbsearch.get(ProductRetrieval
											, guid = product['guid']
											, region = region
											, is_curated = product['is_curated']
										)
			if not productresult.product:
				return self.ajax_messages(_("POOL_CREATE_Product not Found"))
			product = productresult.product
		return product
	
	def set_product(self, product, request):
		tmpl_context = self.setup_region(request)
		
		if product['is_amazon']:
			product = self.amazon_services[tmpl_context.region].get_product_from_guid(product['guid'])
		elif product['is_virtual']:
			product = self.virtual_gift_map[product['guid']]
		else:
			productresult = app_globals.dbsearch.get(ProductRetrieval
											, guid = product['guid']
											, region = tmpl_context.region
											, is_curated = product['is_curated']
										)
			if not productresult.product:
				return self.ajax_messages(_("POOL_CREATE_Product not Found"))
			product = productresult.product
		
		tmpl_context.pool = websession.get('pool') or Pool()
		tmpl_context.pool.product = product
		tmpl_context.pool.region = tmpl_context.region
		websession['pool'] = tmpl_context.pool
		return tmpl_context
	