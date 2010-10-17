"""The application's Globals object"""

import logging, pyodbc, md5, pylibmc
from random import random
from DBUtils.PooledDB import PooledDB
from datetime import datetime
from friendfund.lib import minifb
from friendfund.model import common
from friendfund.services.user_service import UserService
from friendfund.services.payment_service import PaymentService
from friendfund.services.amazon_service import AmazonService

log = logging.getLogger(__name__)
_ = lambda x:x

pyodbc.pooling = False
SVNREVISION = "$Rev$"


class Globals(object):
	"""Globals acts as a container for objects available throughout the
	life of the application
	"""

	def __init__(self, config):
		"""One instance of Globals is created during application
		initialization and is available during requests via the
		'app_globals' variable
		"""
		self.cache = pylibmc.Client([config['app_conf']['memcached.cache.url']], binary=True)
		self.cache.behaviors = {"tcp_nodelay": True, "ketama": True}
		self.cache_pool = pylibmc.ThreadMappedPool(self.cache)
		log.info("memcached set up at %s", config['app_conf']['memcached.cache.url'])
		
		self.ga_include = config.get('ga_include', '')
		self.FbApiKey =  config['app_conf']['fbapikey']
		self.FbApiSecret =  minifb.FacebookSecret(config['app_conf']['fbapisecret'])
		self.TwitterApiKey = config['app_conf']['twitterapikey']
		self.TwitterApiSecret = config['app_conf']['twitterapisecret']
		
		
		self.locale = config['app_conf']['locale']
		self.locale_codes = config['app_conf']['available_locale_codes'].split(',')
		self.locales = config['app_conf']['available_locales'].split(',')
		self.locale_lookup = dict(zip(self.locales, self.locale_codes))
		
		self.debug = config['debug']
		
		if self.debug:
			self.revision_identifier = random()
		else:
			self.revision_identifier = md5.md5(SVNREVISION).hexdigest()
		app_conf = config['app_conf']

		self.SITE_ROOT_URL = app_conf['SITE_ROOT_URL']
		self.SECURE_SITE_ROOT_URL = app_conf['SECURE_SITE_ROOT_URL']
		
		self.currencies = [("EUR", "Euro"),("USD", "USD"),("GBP", "GBP")]
		
		
		self.creditcard_types = [('visa', 'Visa'), ('amex', 'American Express')]
		self.cc_validity_years = zip(range(datetime.today().year, datetime.today().year + 100), range(datetime.today().year, datetime.today().year + 100))
		self.cc_validity_months = zip(range(1,13), range(1,13))
		
		dbpool = PooledDB(
			pyodbc
			,10
			,driver=app_conf['pool.connectstring.driver']
			,server=app_conf['pool.connectstring.server']
			,instance=app_conf['pool.connectstring.instance']
			,database=app_conf['pool.connectstring.database']
			,port=app_conf['pool.connectstring.port']
			,tds_version=app_conf['pool.connectstring.tds_version']
			,uid=app_conf['pool.connectstring.uid']
			,pwd=app_conf['pool.connectstring.pwd']
			,client_charset=app_conf['pool.connectstring.client_charset']
			,autocommit=True)
		self.dbm = common.DBManager(dbpool, self.cache_pool, logging.getLogger('DBM'))
		
		searchpool = PooledDB(
			pyodbc
			,10
			,driver=app_conf['fundbsearch.connectstring.driver']
			,server=app_conf['fundbsearch.connectstring.server']
			,instance=app_conf['fundbsearch.connectstring.instance']
			,database=app_conf['fundbsearch.connectstring.database']
			,port=app_conf['fundbsearch.connectstring.port']
			,tds_version=app_conf['fundbsearch.connectstring.tds_version']
			,uid=app_conf['fundbsearch.connectstring.uid']
			,pwd=app_conf['fundbsearch.connectstring.pwd']
			,client_charset=app_conf['fundbsearch.connectstring.client_charset']
			,autocommit=True)
		self.dbsearch = common.DBManager(searchpool, self.cache_pool, logging.getLogger('DBSearch'))
		
		if app_conf['serve_admin'] == 'true':
			adminpool = PooledDB(
				pyodbc
				,2
				,driver=app_conf['admin.connectstring.driver']
				,server=app_conf['admin.connectstring.server']
				,instance=app_conf['admin.connectstring.instance']
				,database=app_conf['admin.connectstring.database']
				,port=app_conf['admin.connectstring.port']
				,tds_version=app_conf['admin.connectstring.tds_version']
				,uid=app_conf['admin.connectstring.uid']
				,pwd=app_conf['admin.connectstring.pwd']
				,client_charset=app_conf['admin.connectstring.client_charset']
				,autocommit=True)
			self.dbadmin = common.DBManager(adminpool, self.cache_pool, logging.getLogger('DBAdmin'))
		
		self.user_service = UserService(config)
		self.payment_service = PaymentService(app_conf['adyen.hostedlocation']
											, app_conf['adyen.skincode']
											, app_conf['adyen.merchantAccount']
											, app_conf['adyen.hosted_secret'])
		log.info("UserService set up")
		self.amazon_service = {}
		for k in self.locale_codes:
			self.amazon_service[k] = AmazonService(
											app_conf['amazon.%s.apiurl' % k], 
											app_conf['amazon.%s.associateid' % k], 
											app_conf['amazon.%s.apikey' % k], 
											app_conf['amazon.%s.apisecret' % k])
			log.info("AmazonService set up for %s", k)
		
		
		
		self.globalnav = [(_('GLOBAL_MENU_Home'),'/', 'home')
							,(_('GLOBAL_MENU_My_Pools'), '/mypools', 'mypools')
							,(_('GLOBAL_MENU_My_Badges'), '/mybadges', 'badges')
							,(_('GLOBAL_MENU_My_Profile'), '/myprofile', 'myprofile')]