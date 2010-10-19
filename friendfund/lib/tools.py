from __future__ import with_statement
from decorator import decorator
import simplejson, logging, time
INPROCESS_TOKEN = 1

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


from celery.execute import send_task
def robust_cacher(logger, cache_pool, key, expiretime, timeout, create_func, *args, **kwargs):
	expirekey = '%s<timeout>' % key
	with cache_pool.reserve() as mc:
		objs = mc.get_multi([key, expirekey])
		expire = objs.get(expirekey)
		obj = objs.get('key')
		if expire is None:
			mc.set(expirekey, INPROCESS_TOKEN, expiretime/3)
			send_task(create_func, args=args, kwargs=kwargs)
		obj, i = None, 0
		while obj is None and i < timeout:
			logger.info('waiting get updated data to become updated')
			time.sleep(1)
			obj = mc.get(key)
			i+=1
		if obj is None:
			mc.delete(expirekey)
	return obj

def robust_primer(logger, cache_pool, key, expiretime, timeout, create_func, *args, **kwargs):
	expirekey = '%s<timeout>' % key
	with cache_pool.reserve() as mc:
		objs = mc.get_multi([key, expirekey])
		expire = objs.get(expirekey)
		obj = objs.get('key')
		if expire is None:
			mc.set(expirekey, INPROCESS_TOKEN, expiretime/3)
			send_task(create_func, args=args, kwargs=kwargs)
	return None