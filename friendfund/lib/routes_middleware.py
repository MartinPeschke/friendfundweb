import re
import logging
import urllib
from webob import Request
from routes.base import request_config
from routes.middleware import is_form_post
from routes.util import _screenargs, _subdomain_check, cache_hostinfo
from routes.mapper import Mapper

log = logging.getLogger('friendfund.lib.routes_middleware')

class VersionedMapper(Mapper):
	def generate(self, *args, **kargs):
		prefix = kargs.get('_environ', self.environ).get('HTTP_X_VERSION')
		path = super(VersionedMapper, self).generate(*args, **kargs)
		if prefix: path = '/%s%s' % (prefix, path)
		return path