"""The base Controller API

Provides the BaseController class for subclassing.
"""
import logging, base64
from pylons.controllers import WSGIController
from pylons.templating import render_mako as render
from pylons import app_globals as g, tmpl_context as c, request, url


log = logging.getLogger(__name__)

class BaseController(WSGIController):
	navposition=g.globalnav[0][2]
	def __call__(self, environ, start_response):
		"""Invoke the Controller"""
		# WSGIController.__call__ dispatches to the Controller method
		# the request is routed to. This routing information is
		# available in environ['pylons.routes_dict']
		c.region = environ['pylons.routes_dict'].get('region', 'de')
		c.program = environ['pylons.routes_dict'].get('program', None)
		if c.program: c.program = unicode(c.program)
		return WSGIController.__call__(self, environ, start_response)
	def __before__(self, action, environ):
		"""Provides HTTP Request Logging before any error should occur"""
		c.navposition = self.navposition
		c.furl = request.path_info
		c.username = base64.urlsafe_b64decode(request.headers.get('Authorization').split()[1]).split(':')[0]
		log.info('[%s] Incoming Request at %s', c.username, url.current())