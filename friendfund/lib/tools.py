from decorator import decorator
import simplejson, logging

log = logging.getLogger(__name__)

class AutoVivification(dict):
	"""Implementation of perl's autovivification feature."""
	def __getitem__(self, item):
		try:
			return dict.__getitem__(self, item)
		except KeyError:
			value = self[item] = type(self)()
			return value

def dict_contains(d, keys):
	return len(keys) == len(filter(lambda x: bool(x), [d.get(k, None) for k in keys]))


@decorator
def iframe_jsonify(func, *args, **kwargs):
    """Action decorator that formats output for JSON for iFrame transport
    """
    data = func(*args, **kwargs)
    return '<html><body><textarea>%s</textarea></body></html>' % simplejson.dumps(data)

def remove_chars(refstr, chars):
	return ''.join([ c for c in refstr if c not in chars])