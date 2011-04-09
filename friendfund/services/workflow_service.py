from __future__ import with_statement
import md5, uuid, os, formencode, logging
log = logging.getLogger(__name__)

DEFAULT_EXPIRES = 86400

class WorkflowService(object):
	def __init__(self, namespace, cache_pool):
		self.cache_pool = cache_pool
		self.ns = str(namespace)
		self._prefix = "workflow|%s"%self.ns
	def _tokenize(self, key):
		return "%s|%s"%(self._prefix, str(key))

	def add(self, key, value, expiretime = DEFAULT_EXPIRES):
		with self.cache_pool.reserve() as mc:
			tok = self._tokenize(key)
			sucs = mc.set(tok, value, expiretime)
		return sucs
	
	def get(self, key):
		with self.cache_pool.reserve() as mc:
			tok = self._tokenize(key)
			val = mc.get(tok)
		return val
	
	def rem(self, key):
		with self.cache_pool.reserve() as mc:
			tok = _tokenize(key)
			sucs = mc.delete(tok)
		return sucs