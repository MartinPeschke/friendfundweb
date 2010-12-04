# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1291204359.064075
_template_filename=u'/home/www-data/ff_dev/friendfund/templates/links.html'
_template_uri=u'/links.html'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='utf-8'
from webhelpers.html import escape
from xml.sax.saxutils import quoteattr
_exports = ['js_bak', 'css', 'js']


def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'\n\n')
        # SOURCE LINE 3
        __M_writer(u'\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_js_bak(context,file,path='/static/js/'):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_css(context,file,media='',path='/static/css/'):
    context.caller_stack._push_frame()
    try:
        app_globals = context.get('app_globals', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'<link rel="stylesheet" type="text/css" href="')
        __M_writer(filters.html_escape(escape(path)))
        __M_writer(filters.html_escape(escape(file)))
        __M_writer(u'?')
        __M_writer(escape(app_globals.revision_identifier()))
        __M_writer(u'" media="')
        __M_writer(escape(media))
        __M_writer(u'"/>')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_js(context,file,path='/static/js/'):
    context.caller_stack._push_frame()
    try:
        app_globals = context.get('app_globals', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 4
        __M_writer(u'\n\t<script type="text/javascript" src="')
        # SOURCE LINE 5
        __M_writer(filters.html_escape(escape(path)))
        __M_writer(filters.html_escape(escape(file)))
        __M_writer(u'?')
        __M_writer(escape(app_globals.revision_identifier()))
        __M_writer(u'"></script>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


