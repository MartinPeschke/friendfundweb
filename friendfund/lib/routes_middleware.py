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
		environ = kargs.get('_environ', self.environ)
		# prefix = environ.get('HTTP_X_VERSION')
		# if prefix: path = '/%s%s' % (prefix, path)
		path = super(VersionedMapper, self).generate(*args, **kargs)
		if kargs.get("controller") == "content":
			lang = environ.get("beaker.session", {}).get("lang")
			if lang: path = str('/%s%s' % (lang, path))
		return path