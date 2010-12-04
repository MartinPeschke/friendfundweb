# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1291204359.0553081
_template_filename=u'/home/www-data/ff_dev/friendfund/templates/widgets/html_elems.html'
_template_uri=u'/widgets/html_elems.html'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='utf-8'
from webhelpers.html import escape
from xml.sax.saxutils import quoteattr
_exports = ['ajax_loading_animation_src', 'ajax_loading_animation', 'button', 'counter', 'loading_animation', 'clearline']


def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'\n\n\n')
        # SOURCE LINE 5
        __M_writer(u'\n\n\n')
        # SOURCE LINE 8
        __M_writer(u'\n\n')
        # SOURCE LINE 10
        __M_writer(u'\n')
        # SOURCE LINE 11
        __M_writer(u'\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_ajax_loading_animation_src(context):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        # SOURCE LINE 11
        __M_writer(u'/static/imgs/ajax-loader.gif')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_ajax_loading_animation(context):
    context.caller_stack._push_frame()
    try:
        def ajax_loading_animation_src():
            return render_ajax_loading_animation_src(context)
        __M_writer = context.writer()
        # SOURCE LINE 12
        __M_writer(u"<div class='loading_animation'><img src='")
        __M_writer(escape(ajax_loading_animation_src()))
        __M_writer(u"'></div>")
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_button(context,href,onclick='',name='',_class='button_container'):
    context.caller_stack._push_frame()
    try:
        caller = context.get('caller', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 8
        __M_writer(u'<a href="')
        __M_writer(escape(href))
        __M_writer(u'" name="')
        __M_writer(escape(name))
        __M_writer(u'" onclick="')
        __M_writer(escape(onclick))
        __M_writer(u'" class="')
        __M_writer(escape(_class))
        __M_writer(u'"><div class="button_left">&nbsp;</div><div class="button_right">&nbsp;</div><span class="button_label">')
        __M_writer(escape(caller.body()))
        __M_writer(u'</span></a>')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_counter(context,number,subscript):
    context.caller_stack._push_frame()
    try:
        unicode = context.get('unicode', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 4
        __M_writer(u'<div class="counter_container"><div class="counter"><div class="counter_left">&nbsp;</div><div class="counter_right">&nbsp;</div><span class="counter_number">')
        __M_writer(unicode(number))
        __M_writer(u'</span><hr/></div><div class="subscript">')
        __M_writer(escape(subscript))
        __M_writer(u'</div></div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_loading_animation(context):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        # SOURCE LINE 10
        __M_writer(u'<div class="loading_animation"><img src="/static/imgs/ajax-loader.gif"></div>')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_clearline(context,height=0):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'<div style="clear: both; line-height: ')
        __M_writer(escape(height))
        __M_writer(u'px; height: ')
        __M_writer(escape(height))
        __M_writer(u'px;">&nbsp;</div>')
        return ''
    finally:
        context.caller_stack._pop_frame()


