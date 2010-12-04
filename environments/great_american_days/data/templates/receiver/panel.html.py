# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1291205916.5673721
_template_filename='/home/www-data/ff_dev/friendfund/templates/receiver/panel.html'
_template_uri='/receiver/panel.html'
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

    # SOURCE LINE 2
    ns = runtime.Namespace(u'form_widgets', context._clean_inheritance_tokens(), templateuri=u'../widgets/forms.html', callables=None, calling_uri=_template_uri, module=None)
    context.namespaces[(__name__, u'form_widgets')] = ns

def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        c = context.get('c', UNDEFINED)
        html = _mako_get_namespace(context, 'html')
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'\n')
        # SOURCE LINE 2
        __M_writer(u'\n\n<div id="button_panel" class="receiver">\n\t<div id="network_methodselector" class="TabsContainer">\n\t\t\t<a class="methodselector ajaxlink ')
        # SOURCE LINE 6
        __M_writer(escape(c.method == 'facebook' and 'selected' or ''))
        __M_writer(u'" _target="inviter" _type="facebook"><span><img src="/static/imgs/icon_fb_connect.png"> Facebook</span></a>\n\t\t\t<a class="methodselector ajaxlink ')
        # SOURCE LINE 7
        __M_writer(escape(c.method == 'twitter' and 'selected' or ''))
        __M_writer(u'" _target="inviter" _type="twitter"><span><img src="/static/imgs/icon_tw_connect.png">  Twitter</span></a>\n\t\t\t<a class="methodselector ajaxlink ')
        # SOURCE LINE 8
        __M_writer(escape(c.method == 'email' and 'selected' or ''))
        __M_writer(u'" _target="inviter" _type="email"><span><img src="/static/imgs/icon_mail.png"> Email</span></a>\n\t\t\t<a class="methodselector"><span>')
        # SOURCE LINE 9
        __M_writer(escape(_("RECEIVER_PANEL_HEADER_or")))
        __M_writer(u'</span></a>\n\t\t\t<a class="methodselector ajaxlink ')
        # SOURCE LINE 10
        __M_writer(escape(c.method == 'yourself' and 'selected' or ''))
        __M_writer(u'" _target="inviter" _type="yourself">\n\t\t\t\t<span><img src="/static/imgs/header/icon_recipient_small.png"> ')
        # SOURCE LINE 11
        __M_writer(escape(_("RECEIVER_PANEL_HEADER_choose yourself")))
        __M_writer(u'</span>\n\t\t\t</a>\n\t</div>\n\t<a class="button_panel_closer">&nbsp;</a>\n\t')
        # SOURCE LINE 15
        __M_writer(escape(html.clearline()))
        __M_writer(u'\n\t<div id="receiver_selector_container"></div>\n\t')
        # SOURCE LINE 17
        __M_writer(escape(html.clearline()))
        __M_writer(u'\n</div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


