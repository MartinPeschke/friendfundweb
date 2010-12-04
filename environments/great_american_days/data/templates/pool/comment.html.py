# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1291292197.8020561
_template_filename=u'/home/www-data/ff_dev/friendfund/templates/pool/comment.html'
_template_uri=u'/pool/comment.html'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='utf-8'
from webhelpers.html import escape
from xml.sax.saxutils import quoteattr
_exports = ['render']


def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        self = context.get('self', UNDEFINED)
        c = context.get('c', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'\n')
        # SOURCE LINE 2
        __M_writer(escape(self.render(c.comment)))
        __M_writer(u'\n\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_render(context,comment):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        # SOURCE LINE 4
        __M_writer(u'\n\t<div class="comment">\n\t\t<img class="commentAuthor" src="')
        # SOURCE LINE 6
        __M_writer(escape(comment.profile_s_pic))
        __M_writer(u'"/>\n\t\t<div class="commentText">\n\t\t\t<span class="triangle bluetriangle"></span>\n\t\t\t<div class="commentContent">\n\t\t\t<div class="commentAuthorName">')
        # SOURCE LINE 10
        __M_writer(escape(comment.name))
        __M_writer(u':</div>\n\t\t\t\t')
        # SOURCE LINE 11
        __M_writer(escape(comment.comment))
        __M_writer(u'\n\t\t\t</div>\n\t\t</div>\n\t</div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


