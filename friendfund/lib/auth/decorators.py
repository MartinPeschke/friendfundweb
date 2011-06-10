from __future__ import with_statement
import logging, urlparse, simplejson, uuid, base64
import warnings
from decorator import decorator
from pylons import url
from pylons.i18n import ugettext as _, set_lang
from pylons.controllers.util import abort, redirect
from pylons.decorators.util import get_pylons
from friendfund.lib import helpers as h
from friendfund.lib.notifications.messages import Message, ErrorMessage, SuccessMessage
from friendfund.model.db_access import SProcException
from friendfund.model.pool import Pool

log = logging.getLogger(__name__)

class WorkFlow(dict):
	def __init__(self, key, *args, **kwargs):
		self._dirty = False
		self._key = key
		super(self.__class__, self).__init__(*args, **kwargs)
	def __setitem__(self, k, v):
		self._dirty = True
		super(self.__class__, self).__setitem__(k,v)
	def setdefault(self, k, v):
		self._dirty = True
		super(self.__class__, self).setdefault(k,v)


@decorator
def jsonify(func, *args, **kwargs):
	"""Action decorator that formats output for JSON

	Given a function that will return content, this decorator will turn
	the result into JSON, with a content-type of 'application/json' and
	output it.

	"""
	pylons = get_pylons(args)
	pylons.response.headers['Content-Type'] = 'application/json'
	data = func(*args, **kwargs)
	if isinstance(data, (list, tuple)):
		msg = "JSON responses with Array envelopes are susceptible to " \
			  "cross-site data leak attacks, see " \
			  "http://pylonshq.com/warnings/JSONArray"
		warnings.warn(msg, Warning, 2)
		log.warning(msg)
	log.debug("Returning JSON wrapped action output")
	return simplejson.dumps(data, cls=h.DateAwareJSONEncoder)


def logged_in(ajax = False, redirect_to = url('index', action='login'), furl = None, level = 3): 
	def validate(func, self, *args, **kwargs):
		pylons = get_pylons(args)
		c = pylons.tmpl_context
		if c.user.is_anon or c.user.get_clearance()<level:
			if ajax:
				return {'redirect':redirect_to}
			else:
				return redirect('%s?furl=%s' % (redirect_to, furl or pylons.request.path_info))
		return func(self, *args, **kwargs)
	return decorator(validate)


def pool_available(contributable_only = False, contributable_error = None, admin_only = False):
	def validate(func, self, *args, **kwargs):
		pylons = get_pylons(args)
		environ = pylons.request.environ
		c = pylons.tmpl_context
		dbm = pylons.app_globals.dbm
		pool_url = environ['wsgiorg.routing_args'][1].get('pool_url')
		if pool_url is not None:
			try:
				c.pool = dbm.get(Pool, p_url = pool_url)
			except SProcException, e:
				c.pool = None
		if not pool_url or not c.pool:
			c.messages.append(_("FF_SORRY_PAGE_NOT_FOUND_404_STYLE"))
			return redirect(url("home"))
		elif c.pool.merchant_key != pylons.request.merchant.key:
			domain = pylons.app_globals.merchants.key_map[c.pool.merchant_key].domain
			return redirect(url.current(host=domain))
		elif admin_only and not c.pool.am_i_admin(c.user):
			c.messages.append(ErrorMessage(_("POOL_Your not authorized for this operation.")))
			return redirect(url("get_pool", pool_url = pool_url, view="1"))
		elif contributable_only and not c.pool.is_contributable():
			c.messages.append(ErrorMessage(contributable_error or _("FF_POOL_ERROR_Sorry, this pool is no longer active")))
			return redirect(url("get_pool", pool_url = pool_url, view="1"))
		return func(self, *args, **kwargs)
	return decorator(validate)


def workflow_available(presence_required = False, expiretime = 92000):
	def validate(func, self, *args, **kwargs):
		pylons = get_pylons(args)
		environ = pylons.request.environ
		c = pylons.tmpl_context
		cm = pylons.app_globals.cache_pool
		cache_proto_key = pylons.request.params.get('ck')
		if presence_required and not cache_proto_key:
			raise Exception("NoWorkFlowFound! (%s) (%s)", pylons.request.url, pylons.request.referer)
		cache_proto_key = cache_proto_key and cache_proto_key.encode("latin-1", "xmlcharrefreplace") or base64.urlsafe_b64encode(str(uuid.uuid4()))
		with cm.reserve() as cache:
			key = "<WORKFLOW_CACHE><%s>"% cache_proto_key
			wf = cache.get(key)
			if presence_required and not wf:
				raise Exception("WorkFlowExpiredOrNotPresent! (%s) (%s)", pylons.request.url, pylons.request.referer)
			c._workflow = wf or WorkFlow(cache_proto_key)
			c._workflow._dirty = False
			result = func(self, *args, **kwargs)
			if c._workflow._dirty:
				cache.set(key, c._workflow, time=expiretime)
				del c._workflow
		return result
	return decorator(validate)




def provide_lang():
	def validate(func, self, *args, **kwargs):
		pylons = get_pylons(args)
		environ = pylons.request.environ
		routing = environ['wsgiorg.routing_args'][1]
		locales = pylons.app_globals.LANGUAGES
		lang = h.negotiate_locale([routing.get('lang'), pylons.session.get('lang') or 'en'], locales)
		if lang != routing.get('lang'):
			return redirect(url(controller=str(routing['controller']), action = str(routing['action']), lang = str(lang)))
		else:
			set_lang(lang)
		return func(self, *args, **kwargs)
	return decorator(validate)



def default_domain_only(): 
	def validate(func, self, *args, **kwargs):
		pylons = get_pylons(args)
		if not pylons.request.merchant.is_default:
			prot, host, path, params, query, fragment = urlparse.urlparse(pylons.request.url)
			return redirect(urlparse.urlunparse((prot, pylons.app_globals.default_host, path, params, query, fragment)))
		return func(self, *args, **kwargs)
	return decorator(validate)

def is_ssp_admin(ajax = False, redirect_to = url(controller='ssp', action='index'), furl = None): 
	def validate(func, self, *args, **kwargs):
		pylons = get_pylons(args)
		c = pylons.tmpl_context
		if not c.user.is_ssp_admin:
			if ajax:
				return {'redirect':redirect_to}
			else:
				return redirect('%s?furl=%s' % (redirect_to, furl or pylons.request.path_info))
		return func(self, *args, **kwargs)
	return decorator(validate)
	


def post_only(ajax = False): 
	def validate(func, self, *args, **kwargs):
		pylons = get_pylons(args)
		if pylons.request.method != 'POST':
			if ajax:
				return {"message":_("METHOD_NOT_AUTHORIZED_MESSAGE")}
			else:
				pylons.tmpl_context.messages.append(_("METHOD_NOT_AUTHORIZED_MESSAGE"))
				return redirect(pylons.request.referer or url("home"))
		else:
			return func(self, *args, **kwargs)
	return decorator(validate)
	