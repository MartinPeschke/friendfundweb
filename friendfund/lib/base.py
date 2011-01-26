"""The base Controller API

Provides the BaseController class for subclassing.
"""
import logging
from pylons import request, session as websession, tmpl_context as c, config, app_globals as g, url
from pylons.controllers.util import abort, redirect
from pylons.controllers import WSGIController
from pylons.i18n.translation import get_lang, set_lang, _
from pylons.templating import render_mako as render


from friendfund.model.authuser import ANONUSER
from friendfund.model.pool import Pool

from friendfund.lib.helpers import negotiate_locale_from_header

log = logging.getLogger(__name__)

class BaseController(WSGIController):
	navposition=g.globalnav[0][2]
	def index(self):
		return abort(404)
	
	def render(self, template):
		c._msgs = [m for m in c.messages if isinstance(m, basestring)]
		c.messages = []
		c.blocks = websession.get('blocks', [])
		return render(template)
	
	def ajax_messages(self, msg = None):
		if msg:
			c.messages.append(unicode(msg))
		if c.messages:
			return {'clearmessage':'true', 'message':self.render('/messages/standard.html').strip()}
		else:
			return {'clearmessage':'true'}
	
	def __call__(self, environ, start_response):
		"""Invoke the Controller"""
		if 'lang' not in websession:
			websession['lang'] = negotiate_locale_from_header(request.accept_language.best_matches(), g.locales)
		set_lang(websession['lang'])
		if 'region' not in websession:
			region = request.headers.get("X-COUNTRY", g.country_choices.fallback.code).lower()
			region = g.country_choices.map.get(region, g.country_choices.fallback).code
			websession['region'] = region
		c.siteversion = request.headers.get('X-VERSION', 'site')
		if c.siteversion not in ['site', 'fbcanvas']: abort(404)
		return WSGIController.__call__(self, environ, start_response)
	
	def __before__(self, action, environ):
		"""Provides HTTP Request Logging before any error should occur"""
		c.navposition = getattr(c, 'navposition', self.navposition)
		c.messages = websession.get('messages', [])
		c.user = websession.get('user', ANONUSER)
		c.furl = request.params.get("furl") or request.path_info
		log.info('[%s] [%s] Incoming Request at %s', c.user.u_id, websession['region'], url.current())
	
	def __after__(self, action, environ):
		"""When everything is said and done, Save Session State"""
		websession['user'] = c.user
		websession['messages'] = c.messages
		websession.save()


class ExtBaseController(BaseController):
	def __before__(self, action, environ):
		super(ExtBaseController, self).__before__(action, environ)
		pool_url = environ['wsgiorg.routing_args'][1].get('pool_url')
		if pool_url:
			c.pool = g.dbm.get(Pool, p_url = pool_url)
			if not c.pool:
				return abort(404)
			elif c.pool.merchant_key != g.merchant.key:
				return redirect(url.current(host=g.get_merchant_domain(c.pool.merchant_key)))