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
	contrib_view.set_user(c.user)
	with app_globals.cache_pool.reserve() as mc:
		add_token(mc, ref, contrib_view)
	if not sucs: raise TokenAlreadyExistsException("Token could not be added, as it already exists: %s" % token)
	else: return sucs

def get_contribution(ref, user):
	with app_globals.cache_pool.reserve() as mc:
		contrib_view = get_token_value(mc, ref)
	if not contrib_view.validate_user(user): raise TokenIncorrectException("Token could does not belong to User, invalid")
	else: return contrib_view

def set_contribution_invalidated(ref, contrib_view):
	with app_globals.cache_pool.reserve() as mc:
		contrib_view.is_valid = False
		sucs = client.set(ref, contrib_view, DEFAULT_EXPIRES)
		return sucs

def rem_contribution(ref):
	with app_globals.cache_pool.reserve() as mc:
		rem_token(mc, ref)