from __future__ import with_statement
from friendfund.model.mapper import DBMapper
from friendfund.model.db_access import execute_query, SProcException, SProcWarningMessage

import pylibmc
import logging
log = logging.getLogger(__name__)

class DBManager(object):
	_expiretime = 1
	def __init__(self, dbpool, cache_pool, logger, statics_service):
		self.dbpool = dbpool
		self.cache_pool = cache_pool
		self.logger = logger
		self.logger.info('DB Settings Connection Pool set up')
		self._statics = statics_service
	
	def _fetch_from_db(self, cls, **kwargs):
		if cls._no_params:
			result, cur = execute_query(self.dbpool, self.logger, 'exec %s;' % cls._get_proc, None)
		else:
			result, cur = execute_query(self.dbpool, self.logger, 'exec %s ?;' % 
						cls._get_proc, DBMapper._get_template(cls, **kwargs))
		if cls._get_root is None:
			p = DBMapper.fromDB(cls, result, self._statics)
		else:
			root = result.find(cls._get_root)
			p = DBMapper.fromDB(cls, root, self._statics)
		return p
	
	def get(self, cls, **kwargs):
		if cls._cachable:
			key = cls._no_params and cls.__name__.lower() or '_'.join(map(unicode, kwargs.itervalues()))
			key = '<%s>%s' % (cls.__name__.lower(), key)
			key = key.encode("latin-1", "xmlcharrefreplace")
			with self.cache_pool.reserve() as mc:
				obj = mc.get(key)
				if obj is None:
					obj = self._fetch_from_db(cls, **kwargs)
					try:
						mc.set(key, obj, cls._expiretime or self._expiretime)
					except pylibmc.Error, e:
						log.error("MEMCACHED ERROR:%s for key:%s", e, key)
						mc.delete(key)
		else:
			obj = self._fetch_from_db(cls, **kwargs)
		return obj
	
	def call(self, obj, cls, cache = False):
		result, cur = execute_query(self.dbpool, self.logger, 'exec %s ?;' % obj._set_proc, DBMapper.toDB(obj))
		
		if cls._get_root is None:
			p = DBMapper.fromDB(cls, result, self._statics)
		else:
			p = DBMapper.fromDB(cls, result.find(cls._get_root), self._statics)
		if cache and p._cachable:self.push_to_cache(p)
		return p
	
	def set(self, obj, cache = True):
		result, cur = execute_query(self.dbpool, self.logger, 'exec %s ?;' % obj._set_proc, DBMapper.toDB(obj))
		if cache and obj._cachable:self.push_to_cache(obj)
		return obj
	
	def push_to_cache(self, obj):
		with self.cache_pool.reserve() as mc:
				key = '_'.join(map(unicode, [getattr(obj, k) for k in obj._unique_keys]))
				key = '<%s>%s' % (obj.__class__.__name__.lower(), key)
				key = key.encode("latin-1", "xmlcharrefreplace")
				try:
					mc.set(key, obj, obj._expiretime or self._expiretime)
				except pylibmc.Error, e:
					log.error("MEMCACHED ERROR:%s for key:%s", e, key)
					mc.delete(key)
					
	def expire(self, obj):
		with self.cache_pool.reserve() as mc:
			key = '_'.join(map(unicode, [getattr(obj, k) for k in obj._unique_keys]))
			key = '<%s>%s' % (obj.__class__.__name__.lower(), key)
			key = key.encode("latin-1", "xmlcharrefreplace")
			mc.delete(key)