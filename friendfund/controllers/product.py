from __future__ import with_statement
import logging, simplejson, formencode, urlparse, urllib2, socket
from datetime import date, timedelta, datetime
from xml.sax.saxutils import quoteattr

from pylons import request, response, session as websession, tmpl_context as c, url, app_globals as g
from pylons.decorators import jsonify
from pylons.controllers.util import abort, redirect
from friendfund.lib import helpers as h
from friendfund.lib.auth.decorators import logged_in, post_only
from friendfund.lib.base import BaseController, render, _, render_def
from friendfund.lib.tools import dict_contains, remove_chars
from friendfund.model.db_access import SProcException, SProcWarningMessage
from friendfund.model.pool import Pool, UpdatePoolProc
from friendfund.model.product import Product, ProductSearch
from friendfund.tasks.photo_renderer import UnsupportedFileFormat
from friendfund.services.amazon_service import URLUnacceptableError, AttributeMissingInProductException, WrongRegionAmazonError, NoOffersError, TooManyOffersError, AmazonErrorsOccured
from friendfund.services.product_service import AmazonWrongRegionException, AmazonUnsupportedRegionException, QueryMalformedException
log = logging.getLogger(__name__)

class ProductController(BaseController):
	
	@jsonify
	def open_bounce(self):
		c.upload = bool(request.params.get("upload", False))
		try:
			query, product, img_list = g.product_service.set_product_from_open_web(request.params.get('query'))
		except QueryMalformedException, e:
			log.warning(e)
			return {'success':False}
		except socket.timeout, e:
			return {'success':False}
		else:
			if img_list is None:
				return {'success':False}
			c.parser_values = {'url':query,
						'display_url':h.word_truncate_by_letters(query, 40),
						'name':product.name,
						'display_name':h.word_truncate_by_letters(product.name, 40), 
						'description':product.description, 
						'display_description': h.word_truncate_by_letters(product.description, 180), 
						'img_list':img_list}
			html = render_def("/product/urlparser.html", "renderParser", values = c.parser_values, with_closer = True).strip()
		return {'success':True, 'html':html}
		
	def bounce(self):
		websession['pool'], c.product_list = g.product_service.set_product_from_open_graph(websession.get('pool') or Pool(), request)
		if len(c.product_list)>1:
			websession['product_list'] = c.product_list
		else:c.product_list = []
		c.pool = websession['pool']
		return self.render('/index.html')
	
	
	def picturepopup(self, pool_url):
		c.pool = g.dbm.get(Pool, p_url = pool_url)
		if not c.pool:
			return abort(404)
		elif not c.pool.am_i_admin(c.user):
			response.headers['Content-Type'] = 'application/json'
			return simplejson.dumps({'message':'Not authorized!'})
		
		pool_picture = request.params.get('pool_picture')
		if pool_picture is None:
			response.headers['Content-Type'] = 'application/json'
			return simplejson.dumps({'popup':render('/product/picturepopup.html').strip()})
		
		picture_url = g.pool_service.save_pool_picture(pool_picture)
		updater = UpdatePoolProc(p_url = c.pool.p_url)
		updater.product = c.pool.product or Product()
		updater.product.picture = picture_url
		g.dbm.set(updater)
		g.dbm.expire(Pool(p_url = c.pool.p_url))
		c.pool = updater
		return '<html><body><textarea>{"reload":true}</textarea></body></html>'
	
	def ulpicture(self):
		pool_picture = request.params.get('pool_picture')
		if pool_picture is None:
			response.headers['Content-Type'] = 'application/json'
			return simplejson.dumps({'popup':render('/product/ulpicture_popup.html').strip()})
		try:
			picture_url = g.pool_service.save_pool_picture_sync(pool_picture, type="TMP")
		except UnsupportedFileFormat, e:
			result = {"data":{"success":False}}
		else:
			result = {"data":{"success":True, "rendered_picture_url":h.get_product_picture(picture_url, type="TMP", site_root = request.qualified_host)}}
		result = '<html><body><textarea>%s</textarea></body></html>'%simplejson.dumps(result)
		return result
	
	
	
	
	
	
	
	
	
	
	
	
	
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
		params = formencode.variabledecode.variable_decode(request.params)
		product = params.get('product', None)
		if not product or 'merchant_ref' not in product:
			return self.ajax_messages(_("INDEX_PAGE_No Product"))
		websession['pool'] = g.product_service.set_product_from_amazon(websession.get('pool') or Pool(), product['merchant_ref'], request)
		c.pool = websession['pool']
		return {'clearmessage':True, 'html':render('/product/button.html').strip()}
	
	@jsonify
	def set_minified(self):
		product_guid = request.params.get('product_guid')
		c.product_list = websession.get('product_list')
		if not product_guid or not c.product_list:
			return {'clearmessage':True, 'html':render('/product/button.html').strip()} 
		websession['pool'] = g.product_service.set_product_from_guid(websession.get('pool') or Pool(), product_guid, c.product_list)
		c.pool = websession['pool']
		return {'clearmessage':True, 'html':render('/product/button.html').strip()}
