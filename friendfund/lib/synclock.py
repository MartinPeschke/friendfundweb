from __future__ import with_statement

class TokenAlreadyExistsException(Exception):
	pass
class TokenIncorrectException(Exception):
	pass

DEFAULT_EXPIRES = 1800
def add_token(client, token, value):
	tok = 'ftoken_%s'%str(token)
	sucs = client.add(tok, value, DEFAULT_EXPIRES)
	if not sucs: raise TokenAlreadyExistsException("Token could not be added, as it already exists: %s" % token)
	else: return sucs

def rem_token(client, token):
	tok = 'ftoken_%s'%str(token)
	val = client.get(tok)
	sucs = client.delete(tok)
	if not sucs: raise TokenIncorrectException("Token could not be removed, as it does not exist: %s" % token)
	else: return val

def get_token_value(client, token):
	tok = 'ftoken_%s'%str(token)
	val = client.get(tok)
	if not val: raise TokenIncorrectException("Token could not be fetched, as it does not exist: %s" % token)
	else: return val




from pylons import app_globals
def set_contribution(ref, user, contrib_view):
	contrib_view.is_valid = True
	contrib_view.set_user(user)
	with app_globals.cache_pool.reserve() as mc:
		tok = 'ftoken_%s'%str(ref)
		sucs = mc.add(tok, contrib_view, DEFAULT_EXPIRES)
	if not sucs: raise TokenAlreadyExistsException("Token could not be added, it already exists: %s" % token)
	else: return sucs

def get_contribution(ref, user):
	with app_globals.cache_pool.reserve() as mc:
		tok = 'ftoken_%s'%str(ref)
		print ref
		contrib_view = mc.get(tok)
	if not contrib_view: raise TokenIncorrectException("Token does not exist, invalid")
	elif not contrib_view.validate_user(user): raise TokenIncorrectException("Token does not belong to User, invalid")
	else: return contrib_view

def set_contribution_invalidated(ref, contrib_view):
	with app_globals.cache_pool.reserve() as mc:
		contrib_view.is_valid = False
		tok = 'ftoken_%s'%str(ref)
		sucs = mc.set(tok, contrib_view, DEFAULT_EXPIRES)
		return sucs

def rem_contribution(ref):
	with app_globals.cache_pool.reserve() as mc:
		tok = 'ftoken_%s'%str(ref)
		sucs = mc.delete(tok)
	if not sucs: raise TokenIncorrectException("Token could not be removed, as it does not exist: %s" % token)
	else: return sucs