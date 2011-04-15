import os
from gettext import NullTranslations, translation
import pylons
from babel import negotiate_locale as nl
from babel.numbers import format_currency as fc, format_decimal as fdec, get_currency_symbol, get_decimal_symbol, get_group_symbol, parse_number as pn
from babel.dates import format_date as fdate, format_datetime as fdatetime
from decimal import Decimal

from pylons import session as websession, app_globals
from pylons.i18n import LanguageError
from pylons.i18n.translation import get_lang

def _get_formencode_translator(lang, **kwargs):
	"""Utility method to get a valid translator object from a language
	name"""
	conf = pylons.config.current_conf()
	localedir = os.path.join(conf['pylons.paths']['root'], 'i18n')
	if not isinstance(lang, list):
		lang = [lang]
	translator = translation("friendfund", localedir, languages=lang,fallback=True, **kwargs)
	translator.add_fallback(translation("FormEncode", localedir, languages=lang,fallback=True, **kwargs))
	return translator

def friendfund_formencode_gettext(value):
	trans = _get_formencode_translator(getattr(pylons.translator, 'pylons_lang', None))
	return trans.ugettext(value)
class FriendFundFormEncodeState(object):
	"""A ``state`` for FormEncode validate API that includes smart
	``_`` hook.
	"""
	_ = staticmethod(friendfund_formencode_gettext)

def _get_translator(lang, **kwargs):
	"""Utility method to get a valid translator object from a language
	name"""
	if not lang:
		return NullTranslations()
	if 'pylons_config' in kwargs:
		conf = kwargs.pop('pylons_config')
	else:
		conf = pylons.config.current_conf()
	localedir = os.path.join(conf['pylons.paths']['root'], 'i18n')
	if not isinstance(lang, list):
		lang = [lang]
	try:
		translator = translation(conf['pylons.package'], localedir,
								 languages=lang, **kwargs)
	except IOError, ioe:
		raise LanguageError('IOError: %s' % ioe)
	translator.pylons_lang = lang
	return translator


def set_lang(lang, **kwargs):
	"""Set the current language used for translations.

	``lang`` should be a string or a list of strings. If a list of
	strings, the first language is set as the main and the subsequent
	languages are added as fallbacks.
	"""
	translator = _get_translator(lang, **kwargs)
	environ = pylons.request.environ
	environ['pylons.pylons'].translator = translator
	if 'paste.registry' in environ:
		environ['paste.registry'].replace(pylons.translator, translator)
	
	
def get_language_locale():
	lang = get_lang()
	if isinstance(lang, basestring):
		return lang
	elif len(lang)>0:
		return lang[0]
	else:
		log.warning("GET_LANG_CONTAINED_CRAP:%s" % lang)
		return websession['lang']
	
		
def get_format(locale):
	locale = Locale.parse(locale)
	format = locale.currency_formats.get(None)
	return format
def normalize_locale(loc):
	return unicode(loc).replace('-', '_')
def negotiate_locale(accept_langs, available_languages):
	langs = map(normalize_locale, accept_langs)
	return nl(langs, available_languages, sep="_")


def format_int_amount(number):
	number = float(number)/100
	if round(number) == number:
		return '%d' % int(number)
	else:
		return '%.2f' % number

def default_currency():
	return app_globals.country_choices.map.get(websession.get('region'), app_globals.country_choices.fallback).currency

def get_thous_sep():
	return get_group_symbol(locale=websession['lang'])
def get_dec_sep():
	return get_decimal_symbol(locale=websession['lang'])
def display_currency(currency):
	return get_currency_symbol(currency, locale=websession['lang'])
def format_currency(number, currency):
	fnumber = Decimal('%.2f' % number)
	return fc(fnumber, currency, locale=websession['lang'])

def parse_number(strNum):
	return pn(strNum, locale=websession['lang'])
def format_number(number):
	if number is None or number=="": return ""
	fnumber = Decimal('%.2f' % number)
	return fdec(fnumber, format='#,##0.##;-#', locale=websession['lang'])

def format_date(date, with_time = False, format="medium"):
	if not date: return ""
	if with_time:
		return fdatetime(date, format=format, locale=websession['lang'])
	else:
		return fdate(date, format=format, locale=websession['lang'])

def format_date_internal(date):
	if not date: return ""
	return date.strftime('%Y-%m-%d')

def format_short_date(date, with_time = False):
	return fdate(date, "d. MMM", locale=websession['lang'])
