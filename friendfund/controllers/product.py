import logging, simplejson, formencode, urlparse, urllib2
from datetime import date, timedelta, datetime

from pylons import request, response, session as websession, tmpl_context as c, url, app_globals as g
from pylons.decorators import jsonify
from pylons.controllers.util import abort, redirect

from friendfund.lib.auth.decorators import logged_in, post_only
from friendfund.lib.base import BaseController, render, _
from friendfund.lib.tools import dict_contains, remove_chars
from friendfund.model.db_access import SProcException, SProcWarningMessage
from friendfund.model.pool import Pool
from friendfund.model.product_search import ProductSearch
from friendfund.services.amazon_service import URLUnacceptableError, AttributeMissingInProductException, WrongRegionAmazonError, NoOffersError, TooManyOffersError, AmazonErrorsOccured
from friendfund.services.product_service import AmazonWrongRegionException, AmazonUnsupportedRegionException
log = logging.getLogger(__name__)


class ProductController(BaseController):
	navposition=g.globalnav[1][2]
	def bounce(self):
		websession['pool'], product_list = g.product_service.set_product_from_open_graph(websession.get('pool') or Pool(), request)
		if len(product_list) > 1:
			c.product_list = [product_list[k] for k in sorted(product_list)]
			websession['product_list'] = c.product_list
		else:
			c.product_list = []
		c.pool = websession['pool']
		return self.render('/index.html')
	
	@jsonify
	def set_minified(self):
		product_guid = request.params.get("product_guid")
		c.product_list = websession.get('product_list')
		if not product_guid or not c.product_list:
			return {'clearmessage':True, 'html':render('/product/button.html').strip()} 
		product = None
		for p in c.product_list:
			if unicode(p.guid) == product_guid:
				product = p
				break
		if not product:
			return {'clearmessage':True, 'html':render('/product/button.html').strip()} 
		c.pool = websession['pool']
		c.pool.product = product
		websession['pool'] = c.pool
		return {'clearmessage':True, 'html':render('/product/button.html').strip()} 
	
	@jsonify
	def search_tab(self):
		c = g.product_service.search_tab(request)
		return {'clearmessage':True, 'html':remove_chars(render('/product/search_tab.html').strip(), '\n\r\t')}
	
	@jsonify
	def search_tab_search(self):
		c.product_messages = []
		try:
			g.product_service.search_tab_search(request)
		except AmazonUnsupportedRegionException, e:
			c.searchresult = ProductSearch()
			c.product_messages.append(_("AMAZON_PRODUCT_SEARCH_URL not recognized"))
		except AmazonWrongRegionException, e:
			c.searchresult = ProductSearch()
			c.product_messages.append(_("AMAZON_PRODUCT_SEARCH_URL is not from %(amazondomain)s, please use only links from %(amazondomain)s or switch your shipping region.")\
										% {"amazondomain":g.product_service.amazon_services[c.region].domain})
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
		return {'clearmessage':True, 'html':remove_chars(render('/product/search_tab_search.html').strip(), '\n\r\t')}
	
	
	@jsonify
	def search_tab_extension(self):
		c.products = []
		g.product_service.search_tab_extension(request)
		return {'clearmessage':True, 'data':{
					'page_no':c.searchresult.page_no, 
					'has_more':c.searchresult.page_no < c.searchresult.pages,
					'html':remove_chars(render('/product/search_tab_extension.html').strip(), '\n\r\t')
				}
			}
	
	@jsonify
	def remote_search(self):
		g.product_service.search_tab(request)
		g.product_service.search_tab_search(request)
		return {'clearmessage':True, 'html':remove_chars(render('/product/search_tab.html').strip(), '\n\r\t')}
	
	def set_region(self):
		region = request.params.get('region')
		if region not in g.country_choices.map:
			abort(404)
		websession['region'] = region
		return getattr(self, request.params.get('action'), self.search_tab)()
	
	@jsonify
	def unset(self):
		c.pool = websession.get('pool') or Pool()
		del pool.product
		websession['pool'] = c.pool
		return {'clearmessage':True, 'html':render('/product/button.html').strip()}
	
	@jsonify
	def set(self):
		strbool = formencode.validators.StringBoolean(if_missing=False)
		params = formencode.variabledecode.variable_decode(request.params)
		product = params.get('product', None)
		if not product or 'merchant_ref' not in product:
			return self.ajax_messages(_("INDEX_PAGE_No Product"))
		websession['pool'] = g.product_service.set_product(websession.get('pool') or Pool(), product, request)
		c.pool = websession['pool']
		return {'clearmessage':True, 'html':render('/product/button.html').strip()}