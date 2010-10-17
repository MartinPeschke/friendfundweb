import pylibmc
from pylons import config


client = pylibmc.Client([config['app_conf']['memcached.cache.url']], binary=True)

class TokenAlreadyExistsException(Exception):
	pass
class TokenNotExistsException(Exception):
	pass


DEFAULT_EXPIRES = 1800
def add_token(token, value=1):
	tok = 'ftoken_%s'%str(token)
	sucs = client.add(tok, value, DEFAULT_EXPIRES)
	if not sucs: raise TokenAlreadyExistsException("Token could not be added, as it already exists: %s" % token)
	else: return sucs

def rem_token(token):
	tok = 'ftoken_%s'%str(token)
	val = client.get(tok)
	sucs = client.delete(tok)
	if not sucs: raise TokenNotExistsException("Token could not be rmeoved, as it does not exist: %s" % token)
	else: return val
