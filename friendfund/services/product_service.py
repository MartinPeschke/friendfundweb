import logging, urlparse, uuid, urllib2, socket
from ordereddict import OrderedDict

from lxml import etree
from datetime import datetime

from pylons import app_globals, tmpl_context, session as websession
from pylons.controllers.util import abort
from friendfund.lib import helpers as h, url_parser
from friendfund.model.mapper import DBMapper
from friendfund.model.pool import Pool
from friendfund.model.product import DisplayProduct, Product

log = logging.getLogger(__name__)

class AmazonWrongRegionException(Exception):pass
class AmazonUnsupportedRegionException(Exception):pass
class QueryMalformedException(Exception):pass


_ = lambda x:x
SORTEES = [("RANK",_("PRODUCT_SORT_ORDER_Relevancy")),
			("PRICE_UP",_("PRODUCT_SORT_ORDER_Price up")),
			("PRICE_DOWN",_("PRODUCT_SORT_ORDER_Price down"))]
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
		
		for k,v in top_sellers.map.items():
			if len(v)%self.SCROLLER_PAGE_SIZE != 0:
				top_sellers.map[k] = v + v[:self.SCROLLER_PAGE_SIZE-len(v)%self.SCROLLER_PAGE_SIZE]
		
		self.top_sellers = {}
		self.amazon_region_map = {}
		self.amazon_domain_map = {}
		self.default_region = country_choices.fallback
		
		
		for country_code, amazon_service in amazon_services.items():
			self.amazon_domain_map[amazon_service.domain] = amazon_service
			topsellers = top_sellers.map.get(country_code)
			if topsellers:
				self.top_sellers[country_code] = topsellers
			self.amazon_region_map[country_code] = amazon_service
		
	def setup_region(self, request):
		tmpl_context.region = request.params.get('region', websession['region'])
		if tmpl_context.region not in self.amazon_region_map:
			tmpl_context.region = self.default_region.code
		tmpl_context.amazon_region_map = self.amazon_region_map
		tmpl_context.merchant_logo_url = h.get_merchant_logo_url(request)
		return tmpl_context
	
	def request_setup(self, request, minimal = False):
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
	
	def search_tab_setup(self, request):
		tmpl_context = self.request_setup(request)
		tmpl_context.panel = 'search_tab'
		tmpl_context.searchterm = request.params.get('searchterm', '')
		tmpl_context.currency = request.params.get('currency', None)
		tmpl_context.amazon_available = bool(self.amazon_region_map.get(tmpl_context.region))
		return tmpl_context
	
	def search_tab(self, request):
		tmpl_context = self.search_tab_setup(request)
		tmpl_context.search_base_url='search_tab_search'
		tmpl_context.SCROLLER_PAGE_SIZE = self.SCROLLER_PAGE_SIZE
		tmpl_context.top_sellers = self.top_sellers.get(tmpl_context.region, [])
		return tmpl_context
	
	def search_tab_search(self, request):
		tmpl_context = self.search_tab_setup(request)
		tmpl_context = self.request_search_setup(request)
		tmpl_context.search_base_url='search_tab_extension'
		tmpl_context.searchterm = tmpl_context.searchterm.strip()
		if tmpl_context.searchterm.startswith("http://") and tmpl_context.amazon_available:
			return self._amazon_fallback(request, tmpl_context.searchterm)
		else:
			tmpl_context.searchresult = self.amazon_region_map[tmpl_context.region].get_products_from_search(tmpl_context.searchterm, page_no = tmpl_context.page, sorting=tmpl_context.sort)
		return tmpl_context
	
	def search_tab_extension(self, request):
		tmpl_context = self.search_tab_setup(request)
		tmpl_context = self.request_search_setup(request)
		tmpl_context.search_base_url='search_tab_extension'
		tmpl_context.searchterm = tmpl_context.searchterm.strip()
		if tmpl_context.searchterm.startswith("http://") and tmpl_context.amazon_available:
			return self._amazon_fallback(request, tmpl_context.searchterm)
		else:
			tmpl_context.searchresult = self.amazon_region_map[tmpl_context.region].get_products_from_search(tmpl_context.searchterm, page_no = tmpl_context.page, sorting=tmpl_context.sort)
		return tmpl_context
	
	def _amazon_fallback(self, request, url):
		scheme, domain, path, query, fragment = urlparse.urlsplit(url)
		tmpl_context.searchterm = "Amazon Link"
		if domain not in self.amazon_domain_map:
			raise AmazonUnsupportedRegionException()
		else:
			svc = self.amazon_domain_map[domain]
			tmpl_context.region = svc.country_code
			websession['region'] = tmpl_context.region
			tmpl_context.searchresult = svc.get_product_from_url(url)
		return tmpl_context
	
	def getaltproduct(self, product, region):
		product = self.amazon_region_map[region].get_product_from_merchant_ref(product['merchant_ref'])
		return product
	
	def set_product_from_amazon(self, pool, product_merchant_ref, request):
		tmpl_context = self.setup_region(request)
		product = self.amazon_region_map[tmpl_context.region].get_product_from_merchant_ref(product_merchant_ref)
		if not product:
			return self.ajax_messages(_("POOL_CREATE_Product not Found"))
		pool.set_product(product)
		return pool
	
	def set_product_from_guid(self, pool, product_guid, product_list):
		for p in product_list:
			if p.guid == product_guid:
				pool.set_product(p)
				return pool
	
	
	def get_products_from_open_graph(self, params, referer):
		transl = {  "og:description":(["description"], lambda x:x, False),
					"og:name":(["name"], lambda x:x, False),
					"og:price":(["price"], lambda x:int(x), False),
					"og:tracking_link":(["tracking_link"], lambda x:x, True),
					"og:shipping_handling":(["shipping_cost"], lambda x:int(x), False),
					"og:image":(["picture"], lambda x:x, False),
					"og:currency":(["currency"], lambda x:x, False)}
		if params.get("og:type") != 'product':
			log.error("Markup not OKAY")
			abort(404)
		### Create and fill out Product List Objects for later reference
		products = {}
		for k in params:
			parts = k.rsplit('-',1)
			if parts[0] in transl:
				if len(parts) == 1:
					no = u'0'
				else:
					no = unicode(parts[1])
				if no not in products:
					products[no] = DisplayProduct(merchant_ref=referer, tracking_link = referer, guid=str(uuid.uuid4()))
				attr_names, transf, override = transl.get(parts[0])
				for attr in attr_names:
					if override or not getattr(products[no], attr, None):
						setattr(products[no], attr, transf(params.get(k)))
		### Persist product list for later reference
		product_list = [products[k] for k in sorted(products)]
		return product_list
	
	def set_product_from_open_web(self, query):
		try:
			socket.setdefaulttimeout(60)
			scheme, domain, path, query_str, fragment = urlparse.urlsplit(query)
			if not scheme:query='http://%s'%query
			req = urllib2.Request(query, headers={'User-Agent' : "FriendFundIt Browser"})
			product_page = urllib2.urlopen( req )
		except Exception, e:
			raise QueryMalformedException("Query could not be opened or is not wellformed: %s (%s)" % (query, e))
		else:
			name, descr, imgs = url_parser.get_title_descr_imgs(query, product_page)
			product_image = imgs and imgs[0] or None
			product = Product(name=name,
								description=descr,
								tracking_link = query.strip(), 
								picture = product_image
							)
			return query, product, imgs
