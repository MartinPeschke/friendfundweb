import zlib, base64, simplejson, datetime, decimal, itertools
from xml.sax.saxutils import quoteattr
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
	
	
def zigzag(map, pred, mod):
	t1,t2 = itertools.tee(map.iteritems())
	even = itertools.imap(mod, itertools.ifilter(pred, t1))
	odd = itertools.ifilterfalse(pred, t2)
	return even,odd
def split_list(list, pred):
	t1,t2 = itertools.tee(list)
	return itertools.ifilter(pred, t1), itertools.ifilterfalse(pred, t2)
	

class DateAwareJSONEncoder(simplejson.JSONEncoder):
	"""
	JSONEncoder subclass that knows how to encode date/time and decimal types.
	"""
	DATE_FORMAT = "%Y-%m-%d"
	TIME_FORMAT = "%H:%M:%S"
	def default(self, o):
		if isinstance(o, datetime.datetime):
			return o.strftime("%s %s" % (self.DATE_FORMAT, self.TIME_FORMAT))
		elif isinstance(o, datetime.date):
			return o.strftime(self.DATE_FORMAT)
		elif isinstance(o, datetime.time):
			return o.strftime(self.TIME_FORMAT)
		elif isinstance(o, decimal.Decimal):
			return str(o)
		else:
			return super(DateAwareJSONEncoder, self).default(o)
	
def encode_minimal_repr(map):
	return base64.urlsafe_b64encode(zlib.compress(simplejson.dumps(map, cls=DateAwareJSONEncoder)))
def decode_minimal_repr(value):
	if not value: return None
	return simplejson.loads(zlib.decompress(base64.urlsafe_b64decode(str(value))))
	
	
def contains_one(arr, map):
	for k in arr:
		if k in map:
			return True
	return False
def contains_one_ne(map, arr):
	for k in arr:
		if map.get(k):
			return True
	return False
def contains_all_ne(map, arr):
	for k in arr:
		if not map.get(k):
			return False
	return True
def has_ne_prop(c, key):
	return bool(hasattr(c, key) and getattr(c, key))
	

################## For Product Search Templates #################
def attrib_keys(keys, updates = {}):
	if updates:
		okeys = keys.copy()
		okeys.update(updates)
	else:
		okeys = keys
	return '_search_keys="%s" %s' % (
				','.join('_%s'%k for k in okeys.keys() if okeys[k] is not None),
				' '.join(('_%s=%s' % (k,quoteattr(unicode(okeys[k])))) for k in okeys if okeys[k] is not None)
			)

def word_truncate_plain(s, length):
	s = s and s.split() or ['']
	out = ' '.join((len(s) <= length) and s or s[:length])
	return out

def word_truncate(s, length):
	s = s and s.split() or ['']
	out = ' '.join(((len(s) <= length) and s or (s[:length] + [' ... '])))
	return out


def word_truncate_by_letters(s, length):
	if not s: return ''
	if s and len(s) > length:
		s = s[:length].rsplit(None,1)[0] + '...'
	return s


def generate_random_password():
	import random, string
	myrg = random.SystemRandom
	length = 10
	alphabet = string.letters + string.digits
	pw = str().join(myrg(random).sample(alphabet,length))
	return pw

CHARSET = ('bdfghklmnprstvwz', 'aeiou') # consonants, vowels
def generate_mnemonic_password(letters=8, digits=4, uppercase=False):
	"""Generate a random mnemonic password."""
	chars = ''.join([random.choice(CHARSET[i % 2]) for i in range(letters)])
	if uppercase:
		chars = chars.upper()
	chars += ''.join([str(random.randrange(0, 9)) for i in range(digits)])
	return chars
