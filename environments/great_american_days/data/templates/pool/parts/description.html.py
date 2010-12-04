# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1291292196.9467039
_template_filename=u'/home/www-data/ff_dev/friendfund/templates/pool/parts/description.html'
_template_uri=u'/pool/parts/description.html'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='utf-8'
from webhelpers.html import escape
from xml.sax.saxutils import quoteattr
_exports = ['edit', 'view']


def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        def edit(pool):
            return render_edit(context.locals_(__M_locals),pool)
        c = context.get('c', UNDEFINED)
        def view(pool):
            return render_view(context.locals_(__M_locals),pool)
        __M_writer = context.writer()
        # SOURCE LINE 1
        if c.edit:
            # SOURCE LINE 2
            __M_writer(u'\t')
            __M_writer(edit(c.pool))
            __M_writer(u'\n')
            # SOURCE LINE 3
        else:
            # SOURCE LINE 4
            __M_writer(u'\t')
            __M_writer(view(c.pool))
            __M_writer(u'\n')
            pass
        # SOURCE LINE 6
        __M_writer(u'\n')
        # SOURCE LINE 17
        __M_writer(u'\n\n\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_edit(context,pool):
    context.caller_stack._push_frame()
    try:
        url = context.get('url', UNDEFINED)
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 7
        __M_writer(u'\n\t<div id="description_editor">\n\t\t<form id="description_form" method="POST">\n\t\t\t<textarea cols="68" rows="5" name="description">')
        # SOURCE LINE 10
        __M_writer(escape(pool.description))
        __M_writer(u'</textarea>\n\t\t\t<div style="position:absolute; right:30px;bottom:15px;">\n\t\t\t\t<a class="Save" onclick="loadFormElement(\'')
        # SOURCE LINE 12
        __M_writer(escape(url(controller='pool', pool_url=pool.p_url, action='set_description')))
        __M_writer(u'\', \'description_editor\', \'description_form\', place_element(\'description_editor\'));">\n\t\t\t\t\t<span>')
        # SOURCE LINE 13
        __M_writer(escape(_("POOLSETTINGS_Save Changes")))
        __M_writer(u'</span></a>\n\t\t\t</div>\n\t\t</form>\n\t</div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_view(context,pool):
    context.caller_stack._push_frame()
    try:
        url = context.get('url', UNDEFINED)
        c = context.get('c', UNDEFINED)
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 20
        __M_writer(u'\n\t<div id="description_editor">\n\t\t<span class="triangle bluetriangle"></span>\n')
        # SOURCE LINE 23
        if pool.am_i_admin(c.user):
            # SOURCE LINE 24
            __M_writer(u'\t\t<div class="raisedEditIcon" onclick="loadElement(\'')
            __M_writer(escape(url(controller='pool', pool_url=pool.p_url, action='edit_description')))
            __M_writer(u'\', \'description_editor\', {});">')
            __M_writer(escape(_("POOL_DESCRIPTION_edit")))
            __M_writer(u'</div>\n')
            pass
        # SOURCE LINE 26
        __M_writer(u'\t\t<div class="bold">')
        __M_writer(escape(pool.admin.name))
        __M_writer(u' ')
        __M_writer(_("POOL_PAGE_DESCRIPTON_(Pool Admin)"))
        __M_writer(u'</div>\n\t\t<div class="sloganText">')
        # SOURCE LINE 27
        __M_writer(pool.description or "")
        __M_writer(u'</div>\n\t</div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


