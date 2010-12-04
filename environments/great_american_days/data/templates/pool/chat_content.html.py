# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1291292197.7954819
_template_filename=u'/home/www-data/ff_dev/friendfund/templates/pool/chat_content.html'
_template_uri=u'/pool/chat_content.html'
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
    ns = runtime.Namespace(u'cmt', context._clean_inheritance_tokens(), templateuri=u'comment.html', callables=None, calling_uri=_template_uri, module=None)
    context.namespaces[(__name__, u'cmt')] = ns

def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        c = context.get('c', UNDEFINED)
        cmt = _mako_get_namespace(context, 'cmt')
        __M_writer = context.writer()
        __M_writer(u'\n\n')
        # SOURCE LINE 3
        for comment in c.chat.comments:
            # SOURCE LINE 4
            __M_writer(u'\t')
            __M_writer(escape(cmt.render(comment)))
            __M_writer(u'\n')
            pass
        return ''
    finally:
        context.caller_stack._pop_frame()


