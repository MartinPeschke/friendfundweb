# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1291221742.553087
_template_filename='/home/www-data/ff_dev/friendfund/templates/receiver/fb_login.html'
_template_uri='/receiver/fb_login.html'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='utf-8'
from webhelpers.html import escape
from xml.sax.saxutils import quoteattr
_exports = []


def _mako_get_namespace(context, name):
    try:
        return context.namespaces[(__name__, name)]
    except KeyError:
        _mako_generate_namespaces(context)
        return context.namespaces[(__name__, name)]
def _mako_generate_namespaces(context):
    # SOURCE LINE 1
    ns = runtime.Namespace(u'html', context._clean_inheritance_tokens(), templateuri=u'../widgets/html_elems.html', callables=None, calling_uri=_template_uri, module=None)
    context.namespaces[(__name__, u'html')] = ns

def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        html = _mako_get_namespace(context, 'html')
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        __M_writer(u'\n<div id="inviteheader">\n\t<div class="perm_dialog">\n\t\t<a onclick="fbLogin()" class="facebookBtn" title="')
        # SOURCE LINE 4
        __M_writer(escape(_("Connect with Facebook")))
        __M_writer(u'">\n\t\t\t<span>')
        # SOURCE LINE 5
        __M_writer(escape(_("Connect with Facebook")))
        __M_writer(u'</span>\n\t\t</a>\n\t\t<br/>')
        # SOURCE LINE 7
        __M_writer(escape(_("RECEIVER_PANEL_FBLOGIN_To invite your Facebook Friends, You should Connect with Facebook!")))
        __M_writer(u'\n\t</div>\n\t')
        # SOURCE LINE 9
        __M_writer(escape(html.clearline()))
        __M_writer(u'\n</div>')
        return ''
    finally:
        context.caller_stack._pop_frame()


