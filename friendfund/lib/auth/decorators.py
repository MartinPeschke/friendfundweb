from __future__ import with_statement
import urlparse
from decorator import decorator
from pylons import url
from pylons.i18n import ugettext as _
from friendfund.lib import helpers as h
from pylons.controllers.util import abort, redirect
from pylons.decorators.util import get_pylons

def logged_in(ajax = False, redirect_to = url('index', action='login'), furl = None): 
	def validate(func, self, *args, **kwargs):
		pylons = get_pylons(args)
		c = pylons.tmpl_context
		if c.user.is_anon:
			if ajax:
				return {'redirect':redirect_to}
			else:
				return redirect('%s?furl=%s' % (redirect_to, furl or pylons.request.path_info))
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