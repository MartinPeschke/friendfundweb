import logging, simplejson, formencode, urlparse
from datetime import date, timedelta, datetime

from pylons import request, response, session as websession, tmpl_context as c, url, app_globals as g
from pylons.decorators import jsonify
from pylons.controllers.util import abort, redirect

from friendfund.lib.tools import dict_contains, remove_chars
from friendfund.model.db_access import SProcException, SProcWarningMessage
from friendfund.model.pool import Product, Pool
from friendfund.model.product import ProductRetrieval, ProductSuggestionSearch, ProductDisplay, ProductSearch
from friendfund.services.amazon_service import URLUnacceptableError, AttributeMissingInProductException, WrongRegionAmazonError, NoOffersError, TooManyOffersError, AmazonErrorsOccured
log = logging.getLogger(__name__)

_ = lambda x:x
SORTEES = [("RANK",_("PRODUCT_SORT_ORDER_Relevancy")),
			("PRICE_UP",_("PRODUCT_SORT_ORDER_Price up")),
			("PRICE_DOWN",_("PRODUCT_SORT_ORDER_Price down")),
			("MERCHANT",_("PRODUCT_SORT_ORDER_Merchant"))]
PAGESIZE = 5

from friendfund.lib.base import BaseController, render, _

class ProductController(BaseController):
	navposition=g.globalnav[1][2]
	@jsonify
	def panel(self):
		c.region = request.params.get('region', websession['region'])
		c.psuggestions = g.dbsearch.get(ProductSuggestionSearch\
									, country = c.region\
									, occasion = request.params.get('occasion_key', None)\
									, receiver_sex = request.params.get('sex', None)).suggestions
		c.page = 0
		c.sortees = SORTEES
		c.sort = SORTEES[0][0]
		c.q = None
		c.back_q = None
		c.amazon_available = bool(g.amazon_service.get(c.region))
		return {'clearmessage':True, 'html':remove_chars(render('/product/panel.html').strip(), '\n\r\t')}
	
	@jsonify
	def unset(self):
		c.pool = websession.get('pool') or Pool()
		del pool.product
		websession['pool'] = c.pool
		return {'clearmessage':True, 'html':render('/product/button.html').strip()}
	
	@jsonify
	def set(self):
		params = formencode.variabledecode.variable_decode(request.params)
		product = params.get('product', None)
		if not product or not dict_contains(product, ['aff_net', 'guid']):
			return self.ajax_messages(_("INDEX_PAGE_No Product"))
		
		c.region = request.params.get('region', websession['region'])
		c.amazon_available = bool(g.amazon_service.get(c.region))
		if product['aff_net'] == 'AMAZON':
			product = g.amazon_service[c.region].get_product_from_guid(product['guid'])
		else:
			productresult = g.dbsearch.get(ProductRetrieval, guid=product['guid'], is_virtual=product.get('is_virtual', False), region=c.region)
			if not productresult.product:
				return self.ajax_messages(_("POOL_CREATE_Product not Found"))
			product = productresult.product
		c.pool = websession.get('pool') or Pool()
		c.pool.product = product
		c.pool.region = c.region
		websession['pool'] = c.pool
		return {'clearmessage':True, 'html':render('/product/button.html').strip()}
	
	def set_region(self):
		region = request.params.get('region')
		if region not in g.country_choices.map:
			abort(404)
		websession['region'] = region
		return self.panel()
	
	@jsonify
	def search(self):
		c.region = request.params.get('region', websession['region'])
		c.amazon_available = bool(g.amazon_service.get(c.region))
		c.psuggestions = g.dbsearch.get(ProductSuggestionSearch\
									, country = c.region\
									, occasion = request.params.get('occasion_key', None)\
									, receiver_sex = request.params.get('sex', None)).suggestions
		c.q = request.params.get('q', '')
		c.back_q = request.params.get('back_q', '')
		search_term = c.back_q or c.q
		c.page = request.params.get('page', 1)
		c.sort = request.params.get('sort', SORTEES[0][0])
		c.aff_net = request.params.get('aff_net', None)
		c.aff_net_ref = request.params.get('aff_net_ref', None)
		c.sortees = SORTEES
		c.max_price = request.params.get('price', None)
		if c.max_price:
			c.max_price = int(c.max_price)
		c.currency = request.params.get('currency', None)
		if search_term:
			if search_term.startswith("http://") and c.amazon_available:
				return self._amazon_fallback(c.region, search_term)
			else:
				try:
					c.searchresult = g.dbsearch.call(ProductSearch( 
											sort = c.sort,
											page_size=PAGESIZE, 
											program_id = c.aff_net_ref, 
											search=search_term, 
											page_no=c.page, 
											region=c.region,
											max_price = c.max_price,
											is_virtual = request.params.get('is_virtual', False)), ProductSearch)
				except SProcWarningMessage, e:
					log.warning("Product Search Warning: %s" % e)
					return self.ajax_messages(_(u"PRODUCT_SEARCH_An Error Occured during search, please try again later."))
		else:
			c.searchresult = ProductSearch()
		return {'clearmessage':True, 'html':remove_chars(render('/product/panel.html').strip(), '\n\r\t')}
	
	@jsonify
	def verify_dates(self):
		c.region = request.params.get('region', websession['region'])
		try:
			c.date = datetime.strptime(request.params.get('occasion_date', None), '%Y-%m-%d').date()
			c.aff_net = request.params.get('net', None)
			c.aff_prog_id = request.params.get('progid', None)
		except:
			log.info('parse error for date and aff_net and aff_prog_id in verify_dates: %s' % request.params)
			return {'clearmessage':'true'}

		programs = g.get_aff_programs(c.region)
		props = programs.map[str(c.aff_net)][str(c.aff_prog_id)]
		if not props:
			return {'clearmessage':'true'}
		try:
			c.deliverydays = timedelta(int(props.get('shippingdays', 0)))
			c.deliverydays_warnlimit = timedelta(int(props.get('shippingdays_warn', 0)))
		except:
			log.info('parse error for deliveryDates in verify_dates: %s' % programs.map)
			return {'clearmessage':'true'}

		if date.today() + c.deliverydays + c.deliverydays_warnlimit > c.date and date.today() + c.deliverydays <= c.date:
			c.success = True
			return self.ajax_messages(_(u"PRODUCT_DELIVERY_WARNING_Your event date doesn\'t give your funders or shipping much time!"))
		elif date.today() + c.deliverydays > c.date:
			c.success = True
			return self.ajax_messages(_(u"PRODUCT_DELIVERY_WARNING_We cannot ship this to you in time, if this is a problem please pick a later date!"))
		else:
			return  {'clearmessage':'true'}
	
	def _amazon_fallback(self, region, url):
		item_id = request.params.get("item_id")
		scheme, domain, path, query, fragment = urlparse.urlsplit(url)
		c.product_messages = []
		if domain not in g.amazon_service:
			c.searchresult = ProductSearch()
			c.product_messages.append(_("AMAZON_PRODUCT_SEARCH_URL not recognized"))
		elif g.amazon_service[domain] != g.amazon_service[region]:
			c.product_messages.append(_("AMAZON_PRODUCT_SEARCH_URL is not from %(amazondomain)s, please use only links from %(amazondomain)s or switch your shipping region.") % {"amazondomain":g.amazon_service[region].domain})
			c.searchresult = ProductSearch()
		else:
			try:
				c.searchresult = g.amazon_service[domain].get_product_from_url(url)
			except AmazonErrorsOccured, e:
				log.warning(e)
				c.searchresult = ProductSearch()
				c.product_messages.append(_("AMAZON_PRODUCT_SEARCH_Some error occured at Amazons."))
			except (NoOffersError, TooManyOffersError), e:
				log.warning(e)
				c.searchresult = ProductSearch()
				c.product_messages.append(_("AMAZON_PRODUCT_SEARCH_This article seems to be an Amazon Marketplace article and is not sold by Amazon itself. Currently we do not support Amazon Marketplace articles."))
			except AttributeMissingInProductException, e:
				c.searchresult = ProductSearch()
				c.product_messages.append(_("AMAZON_PRODUCT_SEARCH_Amazon does not provide sufficient information to purchase this article."))

		result  = {'clearmessage':True}
		result['html'] = remove_chars(render('/product/panel.html').strip(), '\n\r\t')
		return result
	
	def amazon_lookup(self):
		item_id = request.params.get("item_id")
		return g.amazon_service[websession['region']].fetch_product(item_id).read()