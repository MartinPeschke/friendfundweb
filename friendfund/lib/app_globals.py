"""The application's Globals object"""

import logging, pyodbc, md5, pylibmc, urlparse
from random import random
from DBUtils.PooledDB import PooledDB
from pylons import url
from datetime import datetime
from friendfund.lib import minifb, helpers as h
from friendfund.model import common
from friendfund.model.globals import GetCountryRegionProc, GetCountryProc, GetMerchantLinksProc, GetTopSellersProc

from friendfund.services.amazon_service import AmazonService
from friendfund.services.payment_service import PaymentService
from friendfund.services.product_service import ProductService
from friendfund.services.user_service import UserService
from friendfund.services.pool_service import PoolService

from friendfund.lib.payment.adyen import CreditCardPayment, RedirectPayment

log = logging.getLogger(__name__)
_ = lambda x:x

pyodbc.pooling = False
SVNREVISION = "SPRINT_2.0.2_rc1"
REVISION_ENDING = md5.md5(SVNREVISION).hexdigest()


class Globals(object):
	"""Globals acts as a container for objects available throughout the
	life of the application
	"""
	
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
		
		
		self.BASE_DOMAIN = app_conf['BASE_DOMAIN']
		self.BASE_DOMAIN_LOOKUP = '.%s'%app_conf['BASE_DOMAIN']
		self.SSL_PROTOCOL = app_conf['SSL_PROTOCOL']
		
		self.UPLOAD_FOLDER = app_conf['cache_dir']
		dbpool = PooledDB(pyodbc,10,autocommit=True,timeout=1
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
		
		##################################### DB GLOBALS SETUP #####################################
		
		self._db_globals={}
		self.countries = self._db_globals.setdefault('countries', self.dbm.get(GetCountryProc))
		self.country_choices = self._db_globals.setdefault('country_choices', self.dbm.get(GetCountryRegionProc))
		top_sellers = self.dbm.get(GetTopSellersProc)
		
		self.merchants = self.dbm.get(GetMerchantLinksProc)
		self.default_host = 'http://%s'%self.merchants.default_domain
		log.info("STARTING UP WITH following subdomains: %s", list(self.merchants.domain_map.iterkeys()))
		
		##################################### SERVICES SETUP #####################################
		self.user_service = UserService(config)
		self.pool_service = PoolService(config)
		log.info("UserService set up")
		
		payment_methods = [
				CreditCardPayment('/static/imgs/icon-visa-mastercard-amex.png', 'credit_card', _("CONTRIBUTION_PAGE_Creditcard"), ['EUR','GBP','USD'], False, 10, 2, True
					,gtw_location = app_conf['adyen.location']
					,gtw_username = app_conf['adyen.user']
					,gtw_password = app_conf['adyen.password']
					,gtw_account = app_conf['adyen.merchantAccount']
				),
				RedirectPayment('/static/imgs/icon-paypal.png', 'paypal', _("CONTRIBUTION_PAGE_Paypal"), ['EUR','GBP','USD'], False, 10, 2, True
					,base_url = app_conf['adyen.hostedlocation']
					,skincode = app_conf['adyen.skincode']
					,merchantaccount = app_conf['adyen.merchantAccount']
					,secret = app_conf['adyen.hosted_secret']
				),
				RedirectPayment('/static/imgs/icon_directebanking.png', 'directEbanking', _("CONTRIBUTION_PAGE_Direct eBanking"), ['EUR'], False, 10, 2, True
					,base_url = app_conf['adyen.hostedlocation']
					,skincode = app_conf['adyen.skincode']
					,merchantaccount = app_conf['adyen.merchantAccount']
					,secret = app_conf['adyen.hosted_secret']
				)
			]
		self.payment_service = PaymentService(payment_methods)
		log.info("PaymentService set up with: %s", self.payment_service.payment_methods)
		
		
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
				log.warning("AmazonService setup for %s", country_code)
			else:
				log.warning("AmazonService NOT AVAILABLE for %s", country_code)
		
		self.product_service = ProductService(amazon_services, top_sellers, self.country_choices)
		log.info("ProductService set up")
		
		self.globalnav = [(_('GLOBAL_MENU_Home'),{'args':['home'], 'kwargs':{}}, 'home', True)
							,(_('GLOBAL_MENU_My_Pools'), {'args':['controller'], 'kwargs':{'controller':'mypools'}}, 'mypools', True)
							,(_('GLOBAL_MENU_My_Profile'), {'args':['controller'], 'kwargs':{'controller':'myprofile'}}, 'myprofile', True)]