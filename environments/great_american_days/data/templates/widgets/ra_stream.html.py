# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1291204359.042974
_template_filename=u'/home/www-data/ff_dev/friendfund/templates/widgets/ra_stream.html'
_template_uri=u'/widgets/ra_stream.html'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='utf-8'
from webhelpers.html import escape
from xml.sax.saxutils import quoteattr
_exports = ['render_stream_block']


def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        def render_stream_block(recent_activity,uuid,offset=0):
            return render_render_stream_block(context.locals_(__M_locals),recent_activity,uuid,offset)
        c = context.get('c', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'\n\n')
        # SOURCE LINE 3
        __M_writer(escape(render_stream_block(c.recent_activity, c.uuid)))
        __M_writer(u'\n\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_render_stream_block(context,recent_activity,uuid,offset=0):
    context.caller_stack._push_frame()
    try:
        url = context.get('url', UNDEFINED)
        len = context.get('len', UNDEFINED)
        enumerate = context.get('enumerate', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 5
        __M_writer(u'\n\t')
        # SOURCE LINE 6

        pools = recent_activity.pools
        total = len(pools)
        offset_margin = -170*(total-offset)
                
        
        # SOURCE LINE 10
        __M_writer(u'\n\t<div id="')
        # SOURCE LINE 11
        __M_writer(escape(uuid))
        __M_writer(u'" class="ra_scroller" style="position: relative;height:')
        __M_writer(escape(170*total))
        __M_writer(u'px;margin-top:')
        __M_writer(escape(offset_margin))
        __M_writer(u'px" _top="')
        __M_writer(escape(offset_margin))
        __M_writer(u'px">\n')
        # SOURCE LINE 12
        for i, ra in enumerate(pools):
            # SOURCE LINE 13
            __M_writer(u'\t\t<a href="')
            __M_writer(escape(url(controller='pool', action='index', pool_url = ra.p_url)))
            __M_writer(u'">\n\t\t<div class="rabody" id="')
            # SOURCE LINE 14
            __M_writer(escape(uuid))
            __M_writer(u'_')
            __M_writer(escape(i))
            __M_writer(u'">\n\t\t\t<div class="rabodycol"><img class="pool" src="')
            # SOURCE LINE 15
            __M_writer(escape(ra.get_pool_picture()))
            __M_writer(u'"/></div>\n\t\t\t<div class="rabodycol">\n\t\t\t<img class="product" src="')
            # SOURCE LINE 17
            __M_writer(escape(ra.get_product_pic()))
            __M_writer(u'" alt="')
            __M_writer(escape(ra.product_name))
            __M_writer(u'"/></div>\n\t\t\t<div class="rabodycol"><img class="profile" src="')
            # SOURCE LINE 18
            __M_writer(escape(ra.get_profile_pic()))
            __M_writer(u'"/></div>\n\t\t</div>\n\t\t</a>\n')
            pass
        # SOURCE LINE 22
        __M_writer(u'\t</div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


