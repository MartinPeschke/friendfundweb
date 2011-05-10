from __future__ import with_statement
import urlparse
from decorator import decorator
from pylons import url
from pylons.i18n import ugettext as _, set_lang
from pylons.controllers.util import abort, redirect
from pylons.decorators.util import get_pylons
from friendfund.lib import helpers as h
from friendfund.lib.notifications.messages import Message, ErrorMessage, SuccessMessage
from friendfund.model.db_access import SProcException
from friendfund.model.pool import Pool

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
				return redirect(pylons.request.referer)
		else:
			return func(self, *args, **kwargs)
	return decorator(validate)