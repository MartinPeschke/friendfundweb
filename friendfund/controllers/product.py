import logging, simplejson, formencode, urlparse
from datetime import date, timedelta, datetime

from pylons import request, response, session as websession, tmpl_context as c, url, app_globals as g
from pylons.decorators import jsonify
from pylons.controllers.util import abort, redirect

from friendfund.lib.base import BaseController, render, _
from friendfund.lib.tools import dict_contains, remove_chars
from friendfund.model.db_access import SProcException, SProcWarningMessage
from friendfund.model.pool import Pool
from friendfund.model.product import ProductRetrieval, ProductSuggestionSearch, ProductSearch
from friendfund.services.amazon_service import URLUnacceptableError, AttributeMissingInProductException, WrongRegionAmazonError, NoOffersError, TooManyOffersError, AmazonErrorsOccured
from friendfund.services.product_service import AmazonWrongRegionException, AmazonUnsupportedRegionException
log = logging.getLogger(__name__)


class ProductController(BaseController):
	navposition=g.globalnav[1][2]
	
	@jsonify
	def panel(self):
		c.region = request.params.get('region', websession['region'])
		return {'clearmessage':True, 'html':remove_chars(render('/product/panel.html').strip(), '\n\r\t')}
	
	@jsonify
	def recommended_tab(self):
		c = g.product_service.recommended_tab(request)
		return {'clearmessage':True, 'html':remove_chars(render('/product/recommended_tab.html').strip(), '\n\r\t')}
	@jsonify
	def recommended_tab_search(self):
		c = g.product_service.recommended_tab_search(request)
		return {'clearmessage':True, 'html':remove_chars(render('/product/recommended_tab_search.html').strip(), '\n\r\t')}
	
	@jsonify
	def virtual_tab(self):
		c = g.product_service.virtual_tab(request)
		return {'clearmessage':True, 'html':remove_chars(render('/product/virtual_tab.html').strip(), '\n\r\t')}
	@jsonify
	def virtual_tab_search(self):
		c = g.product_service.virtual_tab(request)
		return {'clearmessage':True, 'html':remove_chars(render('/product/virtual_tab_search.html').strip(), '\n\r\t')}
	
	@jsonify
	def search_tab(self):
		c = g.product_service.search_tab(request)
		return {'clearmessage':True, 'html':remove_chars(render('/product/search_tab.html').strip(), '\n\r\t')}
	@jsonify
	def search_tab_search(self):
		c.product_messages = []
		try:
			g.product_service.search_tab_search(request)
		except SProcWarningMessage, e:
			log.warning("Product Search Warning: %s" % e)
			return self.ajax_messages(_(u"PRODUCT_SEARCH_An Error Occured during search, please try again later."))
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
	def remote_search(self):
		g.product_service.search_tab(request)
		g.product_service.search_tab_search(request)
		return {'clearmessage':True, 'html':remove_chars(render('/product/search_tab.html').strip(), '\n\r\t')}
	
	
	
	
	
	def set_region(self):
		region = request.params.get('region')
		if region not in g.country_choices.map:
			abort(404)
		websession['region'] = region
		return getattr(self, request.params.get('action'), self.recommended_tab)()
	
	
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
		if not product or not dict_contains(product, ['is_amazon', 'is_virtual', 'is_curated', 'guid']):
			return self.ajax_messages(_("INDEX_PAGE_No Product"))
		product['is_amazon']  = strbool.to_python(product['is_amazon'] )
		product['is_virtual'] = strbool.to_python(product['is_virtual'])
		product['is_curated'] = strbool.to_python(product['is_curated'])
		g.product_service.set_product(product, request)
		print websession.get('pool').product
		return {'clearmessage':True, 'html':render('/product/button.html').strip()}

	
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
			return {'clearmessage':'true'}