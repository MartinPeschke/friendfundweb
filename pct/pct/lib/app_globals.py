"""The application's Globals object"""

import logging, pyodbc, md5, pylibmc
from random import random
from DBUtils.PooledDB import PooledDB

from friendfund.model import common
from pct.model.curation import GetCategoriesQueue, GetProgramsProc
log = logging.getLogger(__name__)

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
		
		self.cache = pylibmc.Client([config['app_conf']['memcached.cache.url']], binary=True)
		self.cache.behaviors = {"tcp_nodelay": True, "ketama": True}
		self.cache_pool = pylibmc.ThreadMappedPool(self.cache)
		log.info("memcached set up at %s", config['app_conf']['memcached.cache.url'])
		
		self.revision_identifier = 1
		self.globalnav = [('Home',{'args':['home'], 'kwargs':{'program' : None}}, 'home'), 
						('Update',{'args':[], 'kwargs':{'action':'update'}}, 'home'),
						('Insert',{'args':[], 'kwargs':{'action':'insert'}}, 'home'),
						('Germany',{'args':[], 'kwargs':{'region':'de','program' : None}}, 'home'),
						('UK',{'args':[], 'kwargs':{'region':'gb','program' : None}}, 'home'),
						('USA',{'args':[], 'kwargs':{'region':'us','program' : None}}, 'home')]
		dbm = PooledDB(pyodbc,2,autocommit=True
				,driver=app_conf['pool.connectstring.driver']
				,server=app_conf['pool.connectstring.server']
				,instance=app_conf['pool.connectstring.instance']
				,database=app_conf['pool.connectstring.database']
				,port=app_conf['pool.connectstring.port']
				,tds_version=app_conf['pool.connectstring.tds_version']
				,uid=app_conf['pool.connectstring.uid']
				,pwd=app_conf['pool.connectstring.pwd']
				,client_charset=app_conf['pool.connectstring.client_charset'])
		self.dbm = common.DBManager(dbm, self.cache_pool, logging.getLogger('DBM'))
		
		self.categories = self.dbm.get(GetCategoriesQueue)
		self.programs = self.dbm.get(GetProgramsProc)