import os
from gettext import NullTranslations, translation
import pylons

from pylons.i18n import LanguageError

def _get_translator(lang, **kwargs):
    """Utility method to get a valid translator object from a language
    name"""
    conf = pylons.config.current_conf()
    localedir = os.path.join(conf['pylons.paths']['root'], 'i18n')
    if not isinstance(lang, list):
        lang = [lang]
    translator = translation("FormEncode", localedir, languages=lang,fallback=True, **kwargs)
    return translator

def friendfund_formencode_gettext(value):
    trans = _get_translator(getattr(pylons.translator, 'pylons_lang', None))
    return trans.ugettext(value)
class FriendFundFormEncodeState(object):
    """A ``state`` for FormEncode validate API that includes smart
    ``_`` hook.
    """
    _ = staticmethod(friendfund_formencode_gettext)
