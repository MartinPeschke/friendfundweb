"""The application's Globals object"""

import logging, pyodbc, md5, pylibmc
from random import random
from DBUtils.PooledDB import PooledDB
from datetime import datetime
from friendfund.lib import minifb
from friendfund.model import common
from friendfund.model.globals import GetCountryRegionProc, GetAffiliateProgramsProc
from friendfund.services.user_service import UserService
from friendfund.services.payment_service import PaymentService
from friendfund.services.amazon_service import AmazonService

from friendfund.lib.payment.adyen import CreditCardPayment, RedirectPayment, VirtualPayment

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
		
		self._db_globals={}
		self.country_choices = self._db_globals.setdefault('country_choices', self.dbsearch.get(GetCountryRegionProc))
		self.get_aff_programs = lambda region: self._db_globals.setdefault('affiliate_programs_%s' % region, self.dbsearch.get(GetAffiliateProgramsProc, country = region))
		
		
		
		self.user_service = UserService(config)
		log.info("UserService set up")
		
		payment_methods = [
				CreditCardPayment('/static/imgs/icon-visa-mastercard.png', 'credit_card', "CONTRIBUTION_PAGE_Creditcard", ['de','gb','us','ie','ca','ch','at'], False, 10, 2, True
					,gtw_location = app_conf['adyen.location']
					,gtw_username = app_conf['adyen.user']
					,gtw_password = app_conf['adyen.password']
					,gtw_account = app_conf['adyen.merchantAccount']
				),
				RedirectPayment('/static/imgs/icon-paypal.png', 'paypal', "CONTRIBUTION_PAGE_Paypal", ['de','gb','us','ie','ca','ch','at'], False, 10, 2, True
					,base_url = app_conf['adyen.hostedlocation']
					,skincode = app_conf['adyen.skincode']
					,merchantaccount = app_conf['adyen.merchantAccount']
					,secret = app_conf['adyen.hosted_secret']
				),
				RedirectPayment('/static/imgs/icon_directebanking.png', 'directEbanking', "CONTRIBUTION_PAGE_Direct eBanking", ['de','at'], False, 10, 2, True
					,base_url = app_conf['adyen.hostedlocation']
					,skincode = app_conf['adyen.skincode']
					,merchantaccount = app_conf['adyen.merchantAccount']
					,secret = app_conf['adyen.hosted_secret']
				),
				VirtualPayment('/static/imgs/currencies/pog.png', 'virtual', "CONTRIBUTION_PAGE_Virtual Pot of Gold", ['de','gb','us','ie','ca','ch','at'], True, 0, 0, False)
			]
		self.payment_service = PaymentService(payment_methods)
		log.info("PaymentService set up with: %s", self.payment_service.payment_methods)
		
		
		
		
		self.amazon_service = {}
		for k in self.locale_codes:
			self.amazon_service[app_conf['amazon.%s.domain' % k]] = \
						self.amazon_service[k] = \
							AmazonService(
											app_conf['amazon.%s.apiurl' % k], 
											app_conf['amazon.%s.associateid' % k], 
											app_conf['amazon.%s.apikey' % k], 
											app_conf['amazon.%s.apisecret' % k],
											app_conf['amazon.%s.domain' % k],
											)
			
			log.info("AmazonService set up for %s:%s", k, app_conf['amazon.%s.domain' % k])
		
		
		
		self.globalnav = [(_('GLOBAL_MENU_Home'),{'args':['home'], 'kwargs':{}}, 'home')
							,(_('GLOBAL_MENU_My_Pools'), {'args':['controller'], 'kwargs':{'controller':'mypools'}}, 'mypools')
							,(_('GLOBAL_MENU_My_Badges'), {'args':['controller'], 'kwargs':{'controller':'mybadges'}}, 'badges')
							,(_('GLOBAL_MENU_My_Profile'), {'args':['controller'], 'kwargs':{'controller':'myprofile'}}, 'myprofile')]