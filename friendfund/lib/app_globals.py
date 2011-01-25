"""The application's Globals object"""

import logging, pyodbc, md5, pylibmc, urlparse
from random import random
from DBUtils.PooledDB import PooledDB
from pylons import url
from datetime import datetime
from friendfund.lib import minifb, helpers as h
from friendfund.model import common
from friendfund.model.globals import GetCountryRegionProc, GetAffiliateProgramsProc, GetPersonalityCategoryProc, GetCountryProc, GetMerchantLinksProc
from friendfund.model.virtual_product import GetVirtualGiftsProc
from friendfund.model.product_search import GetTopSellersProc

from friendfund.services.amazon_service import AmazonService
from friendfund.services.payment_service import PaymentService
from friendfund.services.product_service import ProductService
from friendfund.services.user_service import UserService
from friendfund.services.pool_service import PoolService

from friendfund.lib.payment.adyen import CreditCardPayment, RedirectPayment, VirtualPayment

log = logging.getLogger(__name__)
_ = lambda x:x

pyodbc.pooling = False
SVNREVISION = "SPRINT_2.0.1_rc1"
REVISION_ENDING = md5.md5(SVNREVISION).hexdigest()


class Globals(object):
	"""Globals acts as a container for objects available throughout the
	life of the application
	"""
	def get_merchant_domain(self, key):
		print key, '.'.join([self.merchants.get(key, self.merchant).subdomain, self.SITE_ROOTDOMAIN])
		return '.'.join([self.merchants.get(key, self.merchant).subdomain, self.SITE_ROOTDOMAIN])

	def __init__(self, config):
		"""One instance of Globals is created during application
		initialization and is available during requests via the
		'app_globals' variable
		"""
		
		app_conf = config['app_conf']
		self.cache = pylibmc.Client([app_conf['memcached.cache.url']], binary=True)
		self.cache.behaviors = {"tcp_nodelay": True, "ketama": True}
		self.cache_pool = pylibmc.ThreadMappedPool(self.cache)
		log.info("memcached set up at %s", app_conf['memcached.cache.url'])
		
		
		self.FbAppID =  app_conf['fbappid']
		self.FbApiKey =  app_conf['fbapikey']
		self.FbApiSecret =  minifb.FacebookSecret(app_conf['fbapisecret'])
		self.TwitterApiKey = app_conf['twitterapikey']
		self.TwitterApiSecret = app_conf['twitterapisecret']
		
		self.locale_codes = app_conf['available_locale_codes'].split(',')
		self.locales = app_conf['available_locales'].split(',')
		self.locale_lookup = dict(zip(self.locales, self.locale_codes))
		
		self.debug = config['debug']
		self.test = config['test'] == 'true'
		if self.debug:
			self.rv = random()
			self.revision_identifier = lambda: self.rv
			self.revision_identifier = lambda: REVISION_ENDING
		else:
			self.revision_identifier = lambda: REVISION_ENDING
		
		
		self.SITE_ROOT_URL = app_conf['SITE_ROOT_URL']
		self.SITE_SUBDOMAIN = '.'.join(urlparse.urlparse(app_conf['SITE_ROOT_URL'])[1].split('.')[:-2])
		self.SITE_ROOTDOMAIN = '.'.join(urlparse.urlparse(app_conf['SITE_ROOT_URL'])[1].split('.')[-2:])
		self.SSL_PROTOCOL = app_conf['SSL_PROTOCOL']
		self.UPLOAD_FOLDER = app_conf['cache_dir']
		dbpool = PooledDB(pyodbc,10,autocommit=True
			,driver=app_conf['pool.connectstring.driver']
			,server=app_conf['pool.connectstring.server']
			,instance=app_conf['pool.connectstring.instance']
			,database=app_conf['pool.connectstring.database']
			,port=app_conf['pool.connectstring.port']
			,tds_version=app_conf['pool.connectstring.tds_version']
			,uid=app_conf['pool.connectstring.uid']
			,pwd=app_conf['pool.connectstring.pwd']
			,client_charset=app_conf['pool.connectstring.client_charset'])
		self.dbm = common.DBManager(dbpool, self.cache_pool, logging.getLogger('DBM'))
		
		searchpool = PooledDB(pyodbc,10,autocommit=True
			,driver=app_conf['fundbsearch.connectstring.driver']
			,server=app_conf['fundbsearch.connectstring.server']
			,instance=app_conf['fundbsearch.connectstring.instance']
			,database=app_conf['fundbsearch.connectstring.database']
			,port=app_conf['fundbsearch.connectstring.port']
			,tds_version=app_conf['fundbsearch.connectstring.tds_version']
			,uid=app_conf['fundbsearch.connectstring.uid']
			,pwd=app_conf['fundbsearch.connectstring.pwd']
			,client_charset=app_conf['fundbsearch.connectstring.client_charset'])
		self.dbsearch = common.DBManager(searchpool, self.cache_pool, logging.getLogger('DBSearch'))
		
		if app_conf['serve_admin'] == 'true':
			adminpool = PooledDB(pyodbc,2,autocommit=True
				,driver=app_conf['admin.connectstring.driver']
				,server=app_conf['admin.connectstring.server']
				,instance=app_conf['admin.connectstring.instance']
				,database=app_conf['admin.connectstring.database']
				,port=app_conf['admin.connectstring.port']
				,tds_version=app_conf['admin.connectstring.tds_version']
				,uid=app_conf['admin.connectstring.uid']
				,pwd=app_conf['admin.connectstring.pwd']
				,client_charset=app_conf['admin.connectstring.client_charset'])
			self.dbadmin = common.DBManager(adminpool, self.cache_pool, logging.getLogger('DBAdmin'))
		
		##################################### DB GLOBALS SETUP #####################################
		
		self._db_globals={}
		self.countries = self._db_globals.setdefault('countries', self.dbm.get(GetCountryProc))
		self.country_choices = self._db_globals.setdefault('country_choices', self.dbsearch.get(GetCountryRegionProc))
		self.get_aff_programs = lambda region: self._db_globals.setdefault('affiliate_programs_%s' % region, self.dbsearch.get(GetAffiliateProgramsProc, country = region))
		### Product Setup requirements ###
		product_categories = self.dbsearch.get(GetPersonalityCategoryProc)
		virtual_gifts = self.dbsearch.get(GetVirtualGiftsProc)
		for region in virtual_gifts.list:
			for vg in region.list:
				vg.set_picture_urls(self.SITE_ROOT_URL)
		top_sellers = self.dbsearch.get(GetTopSellersProc)
		
		self.merchants = self.dbm.get(GetMerchantLinksProc).merchants_map
		self.merchant = self.merchants[app_conf.get('merchant_key')]
		log.info("STARTING UP with: %s", self.merchant)
		##################################### SERVICES SETUP #####################################
		self.user_service = UserService(config)
		self.pool_service = PoolService(config)
		log.info("UserService set up")
		
		payment_methods = [
				CreditCardPayment('/static/imgs/icon-visa-mastercard-amex.png', 'credit_card', _("CONTRIBUTION_PAGE_Creditcard"), ['de','gb','us','ie','ca','ch','at'], False, 10, 2, True
					,gtw_location = app_conf['adyen.location']
					,gtw_username = app_conf['adyen.user']
					,gtw_password = app_conf['adyen.password']
					,gtw_account = app_conf['adyen.merchantAccount']
				),
				RedirectPayment('/static/imgs/icon-paypal.png', 'paypal', _("CONTRIBUTION_PAGE_Paypal"), ['de','gb','us','ie','ca','ch','at'], False, 10, 2, True
					,base_url = app_conf['adyen.hostedlocation']
					,skincode = app_conf['adyen.skincode']
					,merchantaccount = app_conf['adyen.merchantAccount']
					,secret = app_conf['adyen.hosted_secret']
				),
				RedirectPayment('/static/imgs/icon_directebanking.png', 'directEbanking', _("CONTRIBUTION_PAGE_Direct eBanking"), ['de','at'], False, 10, 2, True
					,base_url = app_conf['adyen.hostedlocation']
					,skincode = app_conf['adyen.skincode']
					,merchantaccount = app_conf['adyen.merchantAccount']
					,secret = app_conf['adyen.hosted_secret']
				),
				VirtualPayment('/static/imgs/currencies/pog_large.png', 'virtual', _("CONTRIBUTION_PAGE_Virtual Pot of Gold"), ['de','gb','us','ie','ca','ch','at'], True, 0, 0, False)
			]
		self.payment_service = PaymentService(payment_methods)
		log.info("PaymentService set up with: %s", self.payment_service.payment_methods)
		
		
		amazon_services = {}
		for k in self.country_choices.r2c_map.keys():
			if app_conf.get('amazon.%s.domain' % k):
				amazon_service = \
						AmazonService(
										app_conf['amazon.%s.apiurl' % k], 
										app_conf['amazon.%s.associateid' % k], 
										app_conf['amazon.%s.apikey' % k], 
										app_conf['amazon.%s.apisecret' % k],
										app_conf['amazon.%s.domain' % k],
										)
				amazon_services[app_conf['amazon.%s.domain' % k]] = amazon_service
				for code in self.country_choices.r2c_map[k]:
					amazon_services[code] = amazon_service
				log.info("AmazonService set up for %s:%s", self.country_choices.r2c_map[k], app_conf['amazon.%s.domain' % k])
			else:
				amazon_services[k] = None
				log.warning("AmazonService NOT AVAILABLE for %s", self.country_choices.r2c_map[k])
		
		self.product_service = ProductService(amazon_services, product_categories, virtual_gifts, top_sellers, self.country_choices, self.SITE_ROOT_URL)
		log.info("ProductService set up")
		
		self.globalnav = [(_('GLOBAL_MENU_Home'),{'args':['home'], 'kwargs':{}}, 'home', True)
							,(_('GLOBAL_MENU_My_Pools'), {'args':['controller'], 'kwargs':{'controller':'mypools'}}, 'mypools', True)
							,(_('GLOBAL_MENU_My_Badges'), {'args':['controller'], 'kwargs':{'controller':'mybadges'}}, 'badges', False)
							,(_('GLOBAL_MENU_My_Profile'), {'args':['controller'], 'kwargs':{'controller':'myprofile'}}, 'myprofile', True)]