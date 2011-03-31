# -*- coding: utf-8 -*-
"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to templates as 'h'.
"""
import os, md5, base64, uuid
from xml.sax.saxutils import quoteattr
from friendfund.lib.i18n import *
import itertools

POOL_STATIC_ROOT = '/s/pool'
PROFILE_STATIC_ROOT = '/s/user'
PRODUCT_STATIC_ROOT = '/s/product'
ACTION_PIC_STATIC_ROOT = '/static/imgs'


from babel.core import Locale

def zigzag(map, pred, mod):
	t1,t2 = itertools.tee(map.iteritems())
	even = itertools.imap(mod, itertools.ifilter(pred, t1))
	odd = itertools.ifilterfalse(pred, t2)
	return even,odd

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


def decode_unique_token(token):
	return uuid.UUID(bytes=base64.urlsafe_b64decode(token+'=='))
def get_unique_token():
	return base64.urlsafe_b64encode(uuid.uuid4().bytes).strip('=')
def get_wizard(mc, pd):
	return mc.get("wizard_pd_%s"%pd) or {}
def set_wizard(mc, pd, wizard):
	mc.set("wizard_pd_%s"%pd, wizard, 7200)

def get_upload_pic_name(name):
	return os.path.join(name[0:2], name[2:4],name)

def get_upload_pic_name_ext(name, ext="jpg"):
	return os.extsep.join([os.path.join(name[0:2], name[2:4],name), ext])


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


################## Picture Helpers #################

def get_action_picture(action, ext='png'):
	name = action.name
	static_root = ACTION_PIC_STATIC_ROOT
	return '%(static_root)s/icon-%(name)s.%(ext)s' % locals()

def get_pool_picture(pool_pic_url, type, ext="png"):
	if pool_pic_url:
		static_root = POOL_STATIC_ROOT
		return '%(static_root)s/%(pool_pic_url)s_%(type)s.%(ext)s'%locals()
	else: 
		return ''

def url_is_local(url):
	return not url.startswith('http')

def get_default_user_picture_token():
	return "DEFAULT_USER_PICTURE"

def get_user_picture(profile_picture_url, type, ext="jpg", site_root = ''):
	static_root = PROFILE_STATIC_ROOT
	if not isinstance(profile_picture_url, basestring) or not profile_picture_url or profile_picture_url == "DEFAULT_USER_PICTURE": 
		return '%(site_root)s/static/imgs/default_user_PROFILE_M.png'%locals()
	elif isinstance(profile_picture_url, basestring):
		if profile_picture_url.startswith('/'):
			return '%(site_root)s%(profile_picture_url)s'%locals()
		elif profile_picture_url.startswith('http'):
			return profile_picture_url
		else:
			return ('%(site_root)s%(static_root)s/%(profile_picture_url)s_%(type)s.%(ext)s'%locals())
	else:
		return None


def get_default_product_picture_token():
	return "DEFAULT_PRODUCT_PICTURE"
def get_product_picture(product_picture_url, type, ext="jpg", site_root = ''):
	static_root = PRODUCT_STATIC_ROOT
	if not isinstance(product_picture_url, basestring) or not product_picture_url or product_picture_url == 'DEFAULT_PRODUCT_PICTURE':
		return '%(site_root)s/static/imgs/default_product_FF_POOL.png'%locals()
	elif product_picture_url.startswith('http'):
		return product_picture_url
	elif product_picture_url.startswith('/'):
		return '%(site_root)s%(product_picture_url)s'%locals()
	else:
		return '%(site_root)s%(static_root)s/%(product_picture_url)s_%(type)s.%(ext)s'%locals()
			

def get_merchant_logo(name):
	return '/static/imgs/merch/%s' % name
def get_merchant_logo_url(request):
	return get_merchant_logo(request.merchant.logo_url)
	
def pool_users_equal(user1, user2):
	### find at least one coresponding user network overlap
	if not (user1.networks and user2.networks):
		return False
	else:
		for network in user1.networks:
			if (user1.networks[network].network_id and user1.networks[network].network_id == user2.networks[network].network_id) \
				or (user1.networks[network].email and user1.networks[network].email == user2.networks['network'].email):
				return True
	return False
		
def users_equal(user1, user2):
	if not user1.network or not user1.network_id or not user2.network or not user2.network_id:
		return False
	return str(user1.network).lower() == str(user2.network).lower() and str(user1.network_id).lower() == str(user2.network_id).lower()


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

