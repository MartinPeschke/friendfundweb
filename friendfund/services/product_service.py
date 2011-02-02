import logging, urlparse, uuid, urllib2

from lxml import etree
from datetime import datetime

from BeautifulSoup import BeautifulSoup
from pylons import app_globals, tmpl_context, session as websession
from pylons.controllers.util import abort
from friendfund.model.mapper import DBMapper
from friendfund.model.pool import Pool
from friendfund.model.product import ProductRetrieval, ProductSuggestionSearch, PendingProduct, Product
from friendfund.model.product_search import CombinedSearchResult
from friendfund.model.virtual_product import ProductPager

log = logging.getLogger(__name__)

class AmazonWrongRegionException(Exception):pass
class AmazonUnsupportedRegionException(Exception):pass

_ = lambda x:x
SORTEES = [("RANK",_("PRODUCT_SORT_ORDER_Relevancy")),
			("PRICE_UP",_("PRODUCT_SORT_ORDER_Price up")),
			("PRICE_DOWN",_("PRODUCT_SORT_ORDER_Price down")),
			("MERCHANT",_("PRODUCT_SORT_ORDER_Merchant"))]
PAGESIZE = 5

GIFT_PANEL_TABS = [("search_tab", _("PRODUCT_SEARCH_PANEL_Gift Search"))]
from pylons.i18n import ugettext as _

class ProductService(object):
	"""
		This is shared between all threads, do not stick state in here!
	"""
	SCROLLER_PAGE_SIZE = 5
	
	def __init__(self, amazon_services, top_sellers, country_choices):
		if not isinstance(amazon_services, dict) or len(amazon_services) < 3:
			raise Exception("Insufficient Amazon Services")
		self.amazon_services = amazon_services
		
		self.top_sellers = {}
		for k,v in top_sellers.map.items():
			if len(v)%self.SCROLLER_PAGE_SIZE != 0:
				top_sellers.map[k] = v + v[:self.SCROLLER_PAGE_SIZE-len(v)%self.SCROLLER_PAGE_SIZE]
		
		for region, countries  in country_choices.r2c_map.iteritems():
			for country in countries:
				self.top_sellers[country] = top_sellers.map[region.upper()]
		
	def setup_region(self, request):
		tmpl_context.region = request.params.get('region', websession['region'])
		return tmpl_context
		
	def request_setup(self, request, minimal = False):
		tmpl_context = self.setup_region(request)
		if request.params.get('minimal', minimal):
			tmpl_context.gift_panel_tabs = GIFT_PANEL_TABS[:-1]
		else:
			tmpl_context.gift_panel_tabs = GIFT_PANEL_TABS
		tmpl_context.sortees = SORTEES
		tmpl_context.sort = SORTEES[0][0]
		tmpl_context.search_keys = {}
		tmpl_context.panelcloser = request.params.get('panelcloser', True)
		return tmpl_context
	def request_search_setup(self, request):
		tmpl_context.page = int(request.params.get('page', 1))
		tmpl_context.search_keys = dict(request.params.iteritems())
		tmpl_context.search_keys['page'] = tmpl_context.page
		tmpl_context.sort = request.params.get('sort', "RANK")
		tmpl_context.page_size = 6
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
		tmpl_context.SCROLLER_PAGE_SIZE = self.SCROLLER_PAGE_SIZE
		tmpl_context.top_sellers = self.top_sellers[tmpl_context.region]
		return tmpl_context
	
	def search_tab_search(self, request):
		tmpl_context = self.search_tab_setup(request)
		tmpl_context = self.request_search_setup(request)
		tmpl_context.search_base_url='search_tab_search'
		
		if tmpl_context.searchterm.startswith("http://") and tmpl_context.amazon_available:
				return self._amazon_fallback(request, tmpl_context.searchterm)
		else:
			tmpl_context.searchresult = self.amazon_services[tmpl_context.region].get_products_from_search(tmpl_context.searchterm)
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
		product = self.amazon_services[region].get_product_from_guid(product['guid'])
		return product
	
	def set_product(self, pool, product, request):
		tmpl_context = self.setup_region(request)
		product = self.amazon_services[tmpl_context.region].get_product_from_guid(product['guid'])
		product.fromDB(None)
		if not product:
			return self.ajax_messages(_("POOL_CREATE_Product not Found"))
		pool.product = product
		pool.region = tmpl_context.region
		return pool
	
	def set_product_from_open_graph(self, pool, request):
		transl = {  "og:description":(["description_long","description"], lambda x:x),
					"description":(["description"], lambda x:x),
					"og:name":(["name"], lambda x:x),
					"og:price":(["amount"], lambda x:int(x)),
					"og:shipping_handling":(["shipping_cost"], lambda x:int(x)),
					"og:image":(["picture_small", "picture_large"], lambda x:x),
					"og:currency":(["currency"], lambda x:x)}
		query=request.params.get("referer")
		if not query:
			log.error("Query not found")
			abort(404)
		try:
			scheme, domain, path, query_str, fragment = urlparse.urlsplit(query)
			product_page = urllib2.urlopen(query)
		except Exception, e:
			log.error("Query could not opened or not wellformed: %s", e)
			abort(404)
		
		soup = BeautifulSoup(product_page.read())
		params = dict((t.get('name'), t.get('content')) for t in soup.findAll('meta') if t.get('name'))
		if params.get("og:type") != 'product':
			log.error("Markup not OKAY")
			abort(404)
		products = {}
		for k in params:
			parts = k.rsplit('-',1)
			if parts[0] in transl:
				if len(parts) == 1:
					no = u'0'
				else:
					no = unicode(parts[1])
				if no not in products:
					products[no] = Product(aff_id=query, 
							aff_program_id="-1", 
							aff_program_name=domain, 
							aff_net=domain,
							guid=uuid.uuid4(),
							category="170000", 
							is_virtual=False,
							aff_program_logo_url="",
							aff_program_delivery_time=5,
							tracking_link=query)
				attr_names, transf = transl.get(parts[0])
				for attr in attr_names:
					if not getattr(products[no], attr, None):
						setattr(products[no], attr, transf(params.get(k)))
		product = products.get(sorted(products)[0])
		for key in products:
			products[key].fromDB(None)
		pool.product = product
		pool.region = params.get('og:location') or params.get('lang') or params.get('language') or 'de'
		return pool, products
		
	
	