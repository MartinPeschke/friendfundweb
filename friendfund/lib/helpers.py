# -*- coding: utf-8 -*-
"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to templates as 'h'.
"""
import os, md5

from pylons import config
from babel import negotiate_locale
from babel.numbers import format_currency as fc, format_decimal as fdec, get_currency_symbol, get_decimal_symbol, get_group_symbol
from babel.dates import format_date as fdate, format_datetime as fdatetime
from pylons import session as websession
from decimal import Decimal
from xml.sax.saxutils import quoteattr

POOL_STATIC_ROOT = '/s/pool'
PROFILE_STATIC_ROOT = '/s/user'
PRODUCT_STATIC_ROOT = '/s/product'
ACTION_PIC_STATIC_ROOT = '/static/imgs'


from babel.core import Locale
def get_format(locale):
    locale = Locale.parse(locale)
    format = locale.currency_formats.get(None)
    return format

def negotiate_locale_from_header(accept_langs, available_languages):
	langs = map(lambda x: x.replace('-', '_'), accept_langs)
	return unicode(negotiate_locale(langs, available_languages, aliases={"gb":"en-GB"}) or available_languages[0])

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

def format_int_amount(number):
	number = float(number)/100
	if round(number) == number:
		return '%d' % int(number)
	else:
		return '%.2f' % number

def get_thous_sep():
	return get_group_symbol(locale=websession['lang'])
def get_dec_sep():
	return get_decimal_symbol(locale=websession['lang'])
def display_currency(currency):
	return get_currency_symbol(currency, locale=websession['lang'])
def format_currency(number, currency):
	fnumber = Decimal('%.2f' % number)
	return fc(fnumber, currency, locale=websession['lang'])

def format_number(number):
	fnumber = Decimal('%.2f' % number)
	return fdec(fnumber, format='#,##0.##;-#', locale=websession['lang'])

def format_date(date, with_time = False, format="medium"):
	if with_time:
		return fdatetime(date, format=format, locale=websession['lang'])
	else:
		return fdate(date, format=format, locale=websession['lang'])

def format_date_internal(date):
	return date.strftime('%Y-%m-%d')

def format_short_date(date, with_time = False):
	return fdate(date, "d. MMM", locale=websession['lang'])



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

def get_user_picture(profile_picture_url, type, ext="jpg", site_root = ''):
	static_root = PROFILE_STATIC_ROOT
	if not isinstance(profile_picture_url, basestring) or not profile_picture_url: 
		return '%(site_root)s/static/imgs/default_m_%(type)s.png'%locals()
	elif isinstance(profile_picture_url, basestring):
		if profile_picture_url.startswith('/'):
			return '%(site_root)s%(profile_picture_url)s'%locals()
		elif profile_picture_url.startswith('http'):
			return profile_picture_url
		else:
			return ('%(site_root)s%(static_root)s/%(profile_picture_url)s_%(type)s.%(ext)s'%locals())
	else:
		return None

def get_product_picture(product_picture_url, type, ext="jpg", site_root = ''):
	static_root = PRODUCT_STATIC_ROOT
	if not isinstance(product_picture_url, basestring): 
		return ''
	return (not product_picture_url.startswith('http')) \
			and ('%(site_root)s%(static_root)s/%(product_picture_url)s_%(type)s.%(ext)s'%locals())\
			or product_picture_url
			
def get_merchant_logo_url(request):
	return '/static/imgs/merch/%s' % request.merchant.logo_url
	
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

