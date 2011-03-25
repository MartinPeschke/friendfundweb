from __future__ import with_statement

class TokenAlreadyExistsException(Exception):
	pass
class TokenIncorrectException(Exception):
	pass

DEFAULT_EXPIRES = 86400
def _tokenize(token):
	return 'ftoken_%s'%str(token)

def add_token(client, token, value):
	tok = _tokenize(token)
	sucs = client.add(tok, value, DEFAULT_EXPIRES)
	if not sucs: raise TokenAlreadyExistsException("Token could not be added, as it already exists: %s" % token)
	else: return sucs

def rem_token(client, token):
	tok = _tokenize(token)
	val = client.get(tok)
	sucs = client.delete(tok)
	if not sucs: raise TokenIncorrectException("Token could not be removed, as it does not exist: %s" % token)
	else: return val

def get_token_value(client, token):
	tok = _tokenize(token)
	val = client.get(tok)
	if not val: raise TokenIncorrectException("Token could not be fetched, as it does not exist: %s" % token)
	else: return val




from pylons import app_globals
def set_contribution(ref, user, contrib_view):
	sucs = False
	contrib_view.is_valid = True
	contrib_view.set_user(user)
	with app_globals.cache_pool.reserve() as mc:
		tok = _tokenize(ref)
		sucs = mc.add(tok, contrib_view, DEFAULT_EXPIRES)
	if not sucs: raise TokenAlreadyExistsException("Token could not be added, it already exists: %s" % token)
	else: return sucs

def get_contribution(ref, user):
	contrib_view = None
	with app_globals.cache_pool.reserve() as mc:
		tok = _tokenize(ref)
		contrib_view = mc.get(tok)
	if not contrib_view: raise TokenIncorrectException("Token does not exist, invalid")
	elif not contrib_view.validate_user(user): raise TokenIncorrectException("Token does not belong to User, invalid")
	else: return contrib_view

def set_contribution_invalidated(ref, contrib_view):
	sucs = False
	with app_globals.cache_pool.reserve() as mc:
		contrib_view.is_valid = False
		tok = _tokenize(ref)
		sucs = mc.set(tok, contrib_view, DEFAULT_EXPIRES)
	return sucs

def rem_contribution(ref):
	sucs = False
	with app_globals.cache_pool.reserve() as mc:
		tok = _tokenize(ref)
		sucs = mc.delete(tok)
	if not sucs: raise TokenIncorrectException("Token could not be removed, as it does not exist: %s" % token)
	else: return sucs