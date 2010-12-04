# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1291293662.580117
_template_filename=u'/home/www-data/ff_dev/friendfund/partners/jochen_schweizer/templates/layout_layer.html'
_template_uri=u'/invite/../layout_layer.html'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='utf-8'
from webhelpers.html import escape
from xml.sax.saxutils import quoteattr
_exports = ['header_navigation', 'render_siteinfo_copyright', 'siteinfo', 'create_pool_button', 'messaging']


def _mako_get_namespace(context, name):
    try:
        return context.namespaces[(__name__, name)]
    except KeyError:
        _mako_generate_namespaces(context)
        return context.namespaces[(__name__, name)]
def _mako_generate_namespaces(context):
    pass
def _mako_inherit(template, context):
    _mako_generate_namespaces(context)
    return runtime._inherit_from(context, u'master.html', _template_uri)
def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        self = context.get('self', UNDEFINED)
        next = context.get('next', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'\n\n<div id="outercontainer_themed">\n<div id="container" class="')
        # SOURCE LINE 4
        __M_writer(escape(self.headerclass()))
        __M_writer(u'">\n\t<div id="top"></div>\n\t')
        # SOURCE LINE 6
        __M_writer(escape(self.header()))
        __M_writer(u'\n\t<div id="body_outer_container">\n\t\t')
        # SOURCE LINE 8
        __M_writer(escape(self.page_slogan()))
        __M_writer(u'\n\t\t<div id="body_container">\n\t\t\t')
        # SOURCE LINE 10
        __M_writer(escape(next.body()))
        __M_writer(u'\n\t\t</div>\n\t\t')
        # SOURCE LINE 12
        __M_writer(escape(self.lowerbody()))
        __M_writer(u'\n\t</div>\n\t')
        # SOURCE LINE 14
        __M_writer(escape(self.render_account_panel()))
        __M_writer(u'\n\t<div class="clear"></div>\n</div>\n</div>\n\n')
        # SOURCE LINE 28
        __M_writer(u'\n\n\n')
        # SOURCE LINE 33
        __M_writer(u'\n\n')
        # SOURCE LINE 35
        __M_writer(u'\n')
        # SOURCE LINE 36
        __M_writer(u'\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_header_navigation(context):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_render_siteinfo_copyright(context):
    context.caller_stack._push_frame()
    try:
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 31
        __M_writer(u'\n\t<div class="siteinfo_copyright"><p>')
        # SOURCE LINE 32
        __M_writer(_(u"powered by <span class=\"poweredByFriendfund\"></span>"))
        __M_writer(u'</p></div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_siteinfo(context):
    context.caller_stack._push_frame()
    try:
        self = context.get('self', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 19
        __M_writer(u'\n\t<div id="siteinfo">\n\t\t<div class="siteinfo1">\n\t\t\t<div class="siteinfo2">\n\t\t\t\t')
        # SOURCE LINE 23
        __M_writer(escape(self.render_flag_container()))
        __M_writer(u'\n\t\t\t\t')
        # SOURCE LINE 24
        __M_writer(escape(self.render_siteinfo_copyright()))
        __M_writer(u'\n\t\t\t</div>\n\t\t</div>\n\t</div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_create_pool_button(context):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_messaging(context):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        return ''
    finally:
        context.caller_stack._pop_frame()


