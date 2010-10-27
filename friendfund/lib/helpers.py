# -*- coding: utf-8 -*-
"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to templates as 'h'.
"""
# Import helpers as desired, or define your own, ie:
#from webhelpers.html.tags import checkbox, password
import os, md5

from pylons import config
from babel import negotiate_locale
from babel.numbers import format_currency as fc, format_decimal as fdec, get_currency_symbol, get_decimal_symbol, get_group_symbol
from babel.dates import format_date as fdate, format_datetime as fdatetime
from pylons import session as websession
from decimal import Decimal

POOL_STATIC_ROOT = '/s/pool'
PROFILE_STATIC_ROOT = '/s/user'
PRODUCT_STATIC_ROOT = '/s/product'

POG = '<span class="pog_currency_symbol">G<span class="pog_currency_symbol_subtype">&#x2551;</span></span>'
EXTENDED_POG = '<span class="pog_currency_symbol"><img class="currency_symbol" src="/static/imgs/currencies/pog.png"/>&nbsp;G<span class="pog_currency_symbol_subtype">&#x2551;</span></span>'
CURRENCY_DISPLAY = {"EUR":"&euro;", "GBP":"&#163;", "USD":"&#36;", "POG":POG}




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


def word_truncate_plain(s, length, q = '', hilights = None, debug = False):
	s = s and s.split() or ['']
	out = ' '.join((len(s) <= length) and s or s[:length])
	return out

def word_truncate(s, length, q = '', hilights = None, debug = False):
	s = s and s.split() or ['']
	out = ' '.join(((len(s) <= length) and s or (s[:length] + [' ... '])))
	return out

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
def display_currency(currency, extended = False):
	if currency == 'POG':
		if extended:
			return EXTENDED_POG
		else:
			return POG
	else:
		return get_currency_symbol(currency, locale=websession['lang'])
def format_currency(number, currency, extended = False):
	fnumber = Decimal('%.2f' % number)
	if currency == 'POG':
		if number == 0:
			return fdec(fnumber, locale=websession['lang'])
		else:
			if extended:
				pog = EXTENDED_POG
			else:
				pog = POG
			result = fc(fnumber, 'EUR', locale=websession['lang'])
			format = get_format(websession['lang']).pattern
			return result.replace(u'€', pog)
	return fc(fnumber, currency, locale=websession['lang'])

def format_number(number):
	return fdec(number, locale=websession['lang'])

def format_date(date, with_time = False):
	if with_time:
		return fdatetime(date, locale=websession['lang'])
	else:
		return fdate(date, locale=websession['lang'])

def format_date_internal(date):
	return date.strftime('%Y-%m-%d')

def get_pool_picture(pool_pic_url, type, ext="png"):
	if pool_pic_url:
		static_root = POOL_STATIC_ROOT
		return '%(static_root)s/%(pool_pic_url)s_%(type)s.%(ext)s'%locals()
	else: 
		return ''

def url_is_local(url):
	return not url.startswith('http')

def get_badge_picture(name, type): #"large, small, icon, outline"
	return "/static/imgs/badges/%s_%s.png" % (name, type)
def get_badge_default_picture():
	return get_badge_picture('badge', 'outline')


def get_user_picture(profile_picture_url, type, ext="jpg", site_root = ''):
	site_root = site_root
	static_root = PROFILE_STATIC_ROOT
	if not isinstance(profile_picture_url, basestring) or not profile_picture_url: 
		return '%(site_root)s/static/imgs/default_m_%(type)s.png'%locals()
	#dont modify absolute picture urls, just return them
	return (not (profile_picture_url.startswith('http') or profile_picture_url.startswith('/'))) \
			and ('%(site_root)s%(static_root)s/%(profile_picture_url)s_%(type)s.%(ext)s'%locals())\
			or profile_picture_url

def get_raw_product_image(product, site_root):
	picture_large = product.picture_large
	if product.is_virtual:
		return '%(site_root)s%(picture_large)s'%locals()
	else:
		return picture_large
	
	
def get_product_picture(product_picture_url, type, ext="jpg"):
	static_root = PRODUCT_STATIC_ROOT
	if not isinstance(product_picture_url, basestring): 
		return '/static/imgs/default_m.png'%locals()
	return (not product_picture_url.startswith('http')) \
			and ('%(static_root)s/%(product_picture_url)s_%(type)s.%(ext)s'%locals())\
			or product_picture_url

def users_equal(user1, user2):
	if not user1.network or not user1.network_id or not user2.network or not user2.network_id:
		return False
	return str(user1.network).lower() == str(user2.network).lower() and str(user1.network_id).lower() == str(user2.network_id).lower()