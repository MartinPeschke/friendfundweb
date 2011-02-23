import os
from gettext import NullTranslations, translation
import pylons

from pylons.i18n import LanguageError

def _get_formencode_translator(lang, **kwargs):
    """Utility method to get a valid translator object from a language
    name"""
    conf = pylons.config.current_conf()
    localedir = os.path.join(conf['pylons.paths']['root'], 'i18n')
    if not isinstance(lang, list):
        lang = [lang]
    translator = translation("FormEncode", localedir, languages=lang,fallback=True, **kwargs)
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