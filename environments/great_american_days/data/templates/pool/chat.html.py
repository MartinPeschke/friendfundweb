# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1291292197.7897329
_template_filename='/home/www-data/ff_dev/friendfund/templates/pool/chat.html'
_template_uri='/pool/chat.html'
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
        url = context.get('url', UNDEFINED)
        c = context.get('c', UNDEFINED)
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        __M_writer(u'\n\n\n<div>\n')
        # SOURCE LINE 5
        if c.chat:
            # SOURCE LINE 6
            __M_writer(u'\t<div id="fundchatmore">\n\t\t')
            # SOURCE LINE 7
            runtime._include_file(context, u'chat_content.html', _template_uri)
            __M_writer(u'\n\t</div>\n')
            # SOURCE LINE 9
            if c.offset:
                # SOURCE LINE 10
                __M_writer(u'\t\t<a href="#commentsend" id="chat_get_more_link" _href="')
                __M_writer(escape(url(controller='pool', pool_url=c.pool_url, action='chatmore')))
                __M_writer(u'" _offset="')
                __M_writer(escape(c.offset))
                __M_writer(u'" onclick="loadnext_fundchat_batch(this)">')
                __M_writer(escape(_("POOL_CHAT_Display More")))
                __M_writer(u'</a>\n')
                pass
            # SOURCE LINE 12
        else:
            # SOURCE LINE 13
            __M_writer(u'\t<div class="placeholder">')
            __M_writer(escape(_("POOL_CHAT_No Comments!")))
            __M_writer(u'</div>\n')
            pass
        # SOURCE LINE 15
        __M_writer(u'\n</div>')
        return ''
    finally:
        context.caller_stack._pop_frame()


