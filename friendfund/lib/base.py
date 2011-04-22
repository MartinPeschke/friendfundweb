"""The base Controller API

Provides the BaseController class for subclassing.
"""
import logging, time, urlparse
from collections import deque
from pylons import request, response, session as websession, tmpl_context as c, config, app_globals as g, url
from pylons.controllers.util import abort, redirect
from pylons.controllers import WSGIController
from pylons.i18n.translation import get_lang, set_lang, _
from pylons.templating import cached_template, pylons_globals
from webhelpers.html import literal

from friendfund.model.authuser import ANONUSER
from friendfund.model.db_access import SProcException
from friendfund.model.pool import Pool

from friendfund.lib.helpers import negotiate_locale, normalize_locale
from friendfund.lib.notifications.messages import Message, ErrorMessage, SuccessMessage

log = logging.getLogger(__name__)

def render(template_name, extra_vars=None, cache_key=None, 
				cache_type=None, cache_expire=None):
	def render_template():
		globs = extra_vars or {}
		globs.update(pylons_globals())
		if request.merchant.type_is_group_gift and request.merchant.entry_is_landing_page:
			template = globs['app_globals'].mako_lookup.get_template(template_name)
		else:
			template = globs['app_globals'].freeform_mako_lookup.get_template(template_name)
			
		return literal(template.render_unicode(**globs))
	return cached_template(template_name, render_template, cache_key=cache_key,
						   cache_type=cache_type, cache_expire=cache_expire)

def render_def(template_name, def_name, cache_key=None,
					cache_type=None, cache_expire=None, **kwargs):
	def render_template():
		globs = kwargs or {}
		globs.update(pylons_globals())
		if request.merchant.type_is_group_gift and request.merchant.entry_is_landing_page:
			template = globs['app_globals'].mako_lookup.get_template(template_name)
		else:
			template = globs['app_globals'].freeform_mako_lookup.get_template(template_name)
		template = template.get_def(def_name)
		return literal(template.render_unicode(**globs))
	return cached_template(template_name, render_template, cache_key=cache_key,
						   cache_type=cache_type, cache_expire=cache_expire)




class BaseController(WSGIController):
	def index(self):
		return abort(404)
	
	def render(self, template):
		c._msgs = deque()
		c._has_errors = False
		for m in c.messages:
			if isinstance(m, basestring):
				m = ErrorMessage(m)
			if isinstance(m, Message):
				c._msgs.append(m)
			if isinstance(m, ErrorMessage):
				c._has_errors = True
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
		return WSGIController.__call__(self, environ, start_response)
	
	def __before__(self, action, environ):
		"""Provides HTTP Request Logging before any error should occur"""
		host = request.headers.get('Host')
		if not (host and host in g.merchants.domain_map):
			prot, host, path, params, query, fragment = urlparse.urlparse(request.url)
			return redirect(urlparse.urlunparse((prot, g.default_host, path, params, query, fragment)))
		else:
			protocol = request.headers.get('X-Forwarded-Proto', 'http')
			request.merchant = g.merchants.domain_map[host]
			request.qualified_host = '%s://%s'%(protocol, host)
			request.is_secured = protocol == 'https'
		if not websession.get('region'):
			region = request.headers.get("X-COUNTRY", g.country_choices.fallback.code).lower()
			region = g.country_choices.map.get(region, g.country_choices.fallback).code
			websession['region'] = region
		c.messages = websession.get('messages', [])
		c.user = websession.get('user', ANONUSER)
		c.furl = str(request.params.get("furl") or request.url)
		log.info('[%s] [%s] [%s] Incoming Request at %s', c.user.u_id, websession['region'], request.headers.get('Host'), url.current())
		
		if 'lang' not in websession or websession['lang'] not in g.LANGUAGES:
			websession['lang'] = negotiate_locale(request.accept_language.best_matches(), g.LANGUAGES)
		set_lang(websession['lang'])
	
	def __after__(self, action, environ):
		"""When everything is said and done, Save Session State"""
		response.headers["P3P"] = "CP='CURa ADMa DEVa PSAo PSDo OUR BUS UNI PUR INT DEM STA PRE COM NAV OTC NOI DSP COR'"
		websession['user'] = c.user
		websession['messages'] = c.messages
		websession.save()