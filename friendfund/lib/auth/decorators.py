from decorator import decorator

from pylons import url
from pylons.i18n import ugettext as _

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





from pylons import request, session as websession, tmpl_context as c

BLOCKS = {
	'email':lambda user:user.has_email,
	'fb_streampub':lambda user: user.has_perm('facebook', 'stream_publish'),
	'create_event':lambda user: user.has_perm('facebook', 'create_event')
}


def add_block(block):
	if block not in websession.get('blocks', []):
		websession['blocks'] = websession.get('blocks', []) + [block]
def remove_block(block):
		websession['blocks'] = filter(lambda x: x!=block, websession.get('blocks', []))
def clear_blocks():
		if 'blocks' in websession:
			del websession['blocks']

def checkadd_block(block):
	if block not in BLOCKS:
		return False
	else:
		if BLOCKS[block](c.user):
			remove_block(block)
			return False
		else:
			add_block(block)
			return True

def enforce_blocks(block): 
	def validate(func, self, *args, **kwargs):
		c.enforce_blocks = True
		checkadd_block(block)
		return func(self, *args, **kwargs)
	return decorator(validate)

def no_blocks(ajax = False, furl = None):
	def validate(func, self, *args, **kwargs):
		if websession.get('blocks', None):
			if ajax:
				return {'redirect':request.referer}
			else:
				c.messages.append("Please finish the below!")
				return redirect(request.referer)
		return func(self, *args, **kwargs)
	return decorator(validate)