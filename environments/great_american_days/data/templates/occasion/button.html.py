# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1291205609.06391
_template_filename=u'/home/www-data/ff_dev/friendfund/partners/jochen_schweizer/templates/occasion/button.html'
_template_uri=u'/occasion/button.html'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='utf-8'
from webhelpers.html import escape
from xml.sax.saxutils import quoteattr
_exports = []


def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        getattr = context.get('getattr', UNDEFINED)
        c = context.get('c', UNDEFINED)
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1

        occasion = getattr(getattr(c, 'pool', None), 'occasion', None)
        
        
        __M_locals_builtin_stored = __M_locals_builtin()
        __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['occasion'] if __M_key in __M_locals_builtin_stored]))
        # SOURCE LINE 3
        __M_writer(u'\n<div id="button_occasion" class="hpbutton occasion">\n')
        # SOURCE LINE 5
        if occasion:
            # SOURCE LINE 6
            __M_writer(u'\t\t<div class="button_content">\n\t\t\t<a class="content withbg"><img class="button_content" src="')
            # SOURCE LINE 7
            __M_writer(escape(getattr(occasion, 'picture_url')))
            __M_writer(u'"/></a>\n\t\t\t<div class="label">')
            # SOURCE LINE 8
            __M_writer(escape(getattr(occasion, 'display_label')))
            __M_writer(u'</div>\n\t\t</div>\n')
            # SOURCE LINE 10
        else:
            # SOURCE LINE 11
            __M_writer(u'\t\t<div class="button_content">\n\t\t\t<a class="content nobg"></a>\n\t\t\t<div class="label">')
            # SOURCE LINE 13
            __M_writer(escape(_("JOCHEN_SCHWEIZER_PAGE_INDEX_BUTTON_Select an Event")))
            __M_writer(u'\n\t\t\t\t<div class="sub_label ">')
            # SOURCE LINE 14
            __M_writer(escape(_("JOCHEN_SCHWEIZER_PAGE_INDEX_BUTTON_Select the special occasion for which your gift pool is being created.")))
            __M_writer(u'</div>\n\t\t\t</div>\n\t\t</div>\n')
            pass
        # SOURCE LINE 18
        __M_writer(u'\t<input type="hidden" name="occasion.key" id="occasion_key" value="')
        __M_writer(escape(getattr(occasion, 'key', '')))
        __M_writer(u'"/>\n\t<input type="hidden" name="occasion.name" id="occasion_name" value="')
        # SOURCE LINE 19
        __M_writer(escape(getattr(occasion, 'name', '')))
        __M_writer(u'"/>\n\t<input type="hidden" name="occasion.date" id="occasion_date" value="')
        # SOURCE LINE 20
        __M_writer(escape(getattr(occasion, 'internal_date_format', '')))
        __M_writer(u'"/>\n</div>\n<div class="extender">&nbsp;</div>')
        return ''
    finally:
        context.caller_stack._pop_frame()


