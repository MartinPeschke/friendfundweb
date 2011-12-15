"""The application's Globals object"""

import logging, pyodbc, md5, pylibmc, urlparse
from random import random
from DBUtils.PooledDB import PooledDB
from pylons import url
from datetime import datetime
from friendfund.lib import minifb, helpers as h
from friendfund.model import common
from friendfund.model.globals import GetCountryRegionProc, GetMerchantConfigProc, GetTopSellersProc

from friendfund.services.amazon_service import AmazonService
from friendfund.services.product_service import ProductService
from friendfund.services.user_service import UserService
from friendfund.services.pool_service import PoolService
from friendfund.services.static_service import StaticService

from friendfund.lib.payment import PaymentFactory

log = logging.getLogger(__name__)
_ = lambda x:x

pyodbc.pooling = False
SVNREVISION="FF_2.3.1_rc6_trial fixing of facebook login"
REVISION_ENDING = md5.md5(SVNREVISION).hexdigest()




class Globals(object):
	"""Globals acts as a container for objects available throughout the
	life of the application
	"""
	def set_merchant_config(self, merchants):
		self.merchants = merchants
		self.default_host = merchants.default_domain
	
	def __init__(self, config):
		"""One instance of Globals is created during application
		initialization and is available during requests via the
		'app_globals' variable
		"""
		
		app_conf = config['app_conf']
		self.cache = pylibmc.Client(app_conf['memcached.cache.url'].split(';'), binary=True)
		self.cache.behaviors = {"tcp_nodelay": True, "ketama": True}
		self.cache_pool = pylibmc.ThreadMappedPool(self.cache)
		log.info("memcached set up at %s", app_conf['memcached.cache.url'])
		
		self.FbAppID =  app_conf['fbappid']
		self.FbApiKey =  app_conf['fbapikey']
		self.FbApiSecret =  minifb.FacebookSecret(app_conf['fbapisecret'])
		self.TwitterApiKey = app_conf['twitterapikey']
		self.TwitterApiSecret = app_conf['twitterapisecret']
		
		self.LANGUAGES = app_conf['available_locales'].split(",")
		
		self.debug = config['debug']
		self.test = config['test'] == 'true'
		if self.debug:
			self.rv = random()
			self.revision_identifier = lambda: self.rv
			self.revision_identifier = lambda: REVISION_ENDING
		else:
			self.revision_identifier = lambda: REVISION_ENDING
		
		
		self.BASE_DOMAIN = app_conf['BASE_DOMAIN']
		# self.STATIC_HOST = app_conf['STATIC_HOST']
		self.BASE_DOMAIN_LOOKUP = '.%s'%app_conf['BASE_DOMAIN']
		self.SSL_PROTOCOL = app_conf['SSL_PROTOCOL']
		self.SUPPORT_EMAIL = app_conf['support_email']
		self.SALES_EMAIL = app_conf['sales_email']
		
		self.UPLOAD_FOLDER = app_conf['cache_dir']
		dbpool = PooledDB(pyodbc,mincached=4,maxcached=10,failures = (pyodbc.OperationalError, pyodbc.InternalError, pyodbc.Error), autocommit=True
			,driver=app_conf['pool.connectstring.driver']
			,server=app_conf['pool.connectstring.server']
			,instance=app_conf['pool.connectstring.instance']
			,database=app_conf['pool.connectstring.database']
			,port=app_conf['pool.connectstring.port']
			,tds_version=app_conf['pool.connectstring.tds_version']
			,uid=app_conf['pool.connectstring.uid']
			,pwd=app_conf['pool.connectstring.pwd']
			,client_charset=app_conf['pool.connectstring.client_charset'])
		self.statics_service = StaticService(app_conf['static.servers'],app_conf['static.ssl.servers'])
		self.dbm = common.DBManager(dbpool, self.cache_pool, logging.getLogger('DBM'), self.statics_service)
		
		##################################### DB GLOBALS SETUP #####################################
		
		self._db_globals={}
		self.country_choices = self._db_globals.setdefault('country_choices', self.dbm.get(GetCountryRegionProc))
		top_sellers = self.dbm.get(GetTopSellersProc)
		
		merchant_config = self.dbm.get(GetMerchantConfigProc)
		self.set_merchant_config(merchant_config.merchants)
		self.featured_pools = merchant_config.featured_pools   #setting up a fallback if memcached doesnt hold proper pools
		self.homepage_stats = merchant_config.stats
		log.info("STARTING UP WITH following subdomains: %s", list(merchant_config.merchants.domain_map.iterkeys()))
		
		##################################### SERVICES SETUP #####################################
		
		pfactory = PaymentFactory(
				 gtw_location = app_conf['adyen.location']
				,gtw_username = app_conf['adyen.user']
				,gtw_password = app_conf['adyen.password']
				,gtw_account = app_conf['adyen.merchantAccount']
				,hosted_base_url = app_conf['adyen.hostedlocation']
				,hosted_skincode = app_conf['adyen.skincode']
				,merchantaccount = app_conf['adyen.merchantAccount']
				,hosted_sign_secret = app_conf['adyen.hosted_secret'])
		self.payment_methods = [pfactory.get(pm) for pm in merchant_config.payment_methods]
		self.payment_methods_map = dict((pm.code, pm) for pm in self.payment_methods)
		log.info("PaymentMethods set up: %s", self.payment_methods)
		
		
		amazon_services = {}
		for country_code in self.country_choices.map.keys():
			if app_conf.get('amazon.%s.domain' % country_code):
				amazon_service = \
						AmazonService(
										country_code,
										app_conf['amazon.%s.apiurl' % country_code], 
										app_conf['amazon.%s.associateid' % country_code], 
										app_conf['amazon.%s.apikey' % country_code], 
										app_conf['amazon.%s.apisecret' % country_code],
										app_conf['amazon.%s.domain' % country_code],
										)
				amazon_services[country_code] = amazon_service
				log.info("AmazonService setup for %s", country_code)
			else:
				log.warning("AmazonService NOT AVAILABLE for %s", country_code)
		
		self.product_service = ProductService(amazon_services, top_sellers, self.country_choices, self.dbm, self.statics_service)
		log.info("ProductService set up")
		self.user_service = UserService(config, self.dbm, self.statics_service)
		self.pool_service = PoolService(config, self.dbm, self.statics_service)
		log.info("UserService set up")
