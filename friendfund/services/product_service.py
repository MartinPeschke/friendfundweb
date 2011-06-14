import logging, urlparse, uuid, urllib2, socket
from BeautifulSoup import BeautifulSoup
from ordereddict import OrderedDict

from lxml import etree
from datetime import datetime

from pylons import tmpl_context, session as websession, app_globals
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
	
	def __init__(self, amazon_services, top_sellers, country_choices, dbm, statics_service):
		if not isinstance(amazon_services, dict) or len(amazon_services) < 3:
			raise Exception("Insufficient Amazon Services")
		
		for k,v in top_sellers.map.items():
			if len(v)%self.SCROLLER_PAGE_SIZE != 0:
				top_sellers.map[k] = v + v[:self.SCROLLER_PAGE_SIZE-len(v)%self.SCROLLER_PAGE_SIZE]
		
		self.top_sellers = {}
		self.statics_service = statics_service
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
		tmpl_context.merchant_logo_url = request.merchant.get_logo_url()
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
	
	def get_products_from_url(self, query):
		def transcode(buffer):
			try:
				return buffer.encode("latin-1").decode("utf-8")
			except:
				return buffer

		if not query:
			log.error("DEFAULT PRODUCT NOT FOUND")
			abort(404)
		try:
			socket.setdefaulttimeout(60)
			scheme, domain, path, query_str, fragment = urlparse.urlsplit(query)
			product_page = urllib2.urlopen(query)
		except Exception, e:
			log.error("Query could not be opened or not is wellformed: %s (%s)", query, e)
			abort(404)
		soup = BeautifulSoup(product_page.read())
		params  = {}
		params = dict((t['name'], transcode(t['content'])) for t in soup.findAll('meta') if t.get('name') and t.get('content'))
		params.update( dict((t['property'], transcode(t['content'])) for t in soup.findAll('meta') if t.get('property') and t.get('content')) )
		return self.get_products_from_open_graph(params, query)
	
	def get_products_from_open_graph(self, params, referer):
		transl = {  "og:description":(["description"], lambda x:x, False, True),
					"og:title":(["name"], lambda x:x, False, True),
					"og:price":(["price"], lambda x:int(x), False, True),
					"og:url":(["tracking_link"], lambda x:x, True, False),
					"og:product_id":(["merchant_ref"], lambda x:x, True, False),
					"og:shipping_handling":(["shipping_cost"], lambda x:int(x), False, False),
					"og:image":(["picture"], lambda x:x, False, True),
					"og:currency":(["currency"], lambda x:x, False, True)}
		fallBacks = {"og:name":"og:title", "description":"og:description"}
		product_map = {}
		for k in params:
			key_parts = k.rsplit("-", 1)
			if len(key_parts)==2:
				elem_no = h.atoi(key_parts[1]) or 0
			else:
				elem_no = 0
			product_map[elem_no] = product_map.get(elem_no, {})
			product_map[elem_no][key_parts[0]] = params[k]
		product_map_list = [product_map[k] for k in sorted(product_map)]
		
		for p_map in product_map_list:
			for k,v in fallBacks.iteritems():
				if v not in p_map:
					if k in p_map:
						p_map[v] = p_map[k]
					elif k in product_map_list[0]:
						p_map[v] = product_map_list[0][k]
		
		product_list = []
		for p_map in product_map_list:
			product = DisplayProduct(guid=str(uuid.uuid4()))
			for ogkey in transl:
				attr_names, transf, override, required = transl[ogkey]
				if required and ogkey not in p_map:
					log.error("PartnerBounceWithInsufficientParameters, missing: %s (%s)", ogkey, p_map)
					product = None
					break
				else:
					for attr in attr_names:
						if override or getattr(product, attr, None) is None:
							setattr(product, attr, transf(p_map.get(ogkey)))
			if product and product.name:   # catching title/name schisma
				product.referer_link = referer
				product._statics = self.statics_service
				product_list.append(product)
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
	
	def get_parser_values_from_product(self, product):
		if not isinstance(product, Product) or not product.tracking_link:
			parser_values = None
		else:
			parser_values = {
				"url":product.tracking_link,
				"product_picture":None,
				"name":product.name,
				"description":product.description,
				"img_list":[product.get_product_pic("FF_POOLS")]
			}
			parser_values['display_url'] = parser_values['url'] and h.word_truncate_by_letters(parser_values['url'], 40) or None
			parser_values['display_name'] = parser_values['name'] and h.word_truncate_by_letters(parser_values['name'], 40) or None
			parser_values['display_description'] = parser_values['description'] and h.word_truncate_by_letters(parser_values['description'], 180) or None
		return parser_values