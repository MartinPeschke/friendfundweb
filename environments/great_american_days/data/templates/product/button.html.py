# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1291205609.0248499
_template_filename=u'/home/www-data/ff_dev/friendfund/partners/jochen_schweizer/templates/product/button.html'
_template_uri=u'/product/button.html'
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

        product = getattr(getattr(c, 'pool', None), 'product', None)
        
        
        __M_locals_builtin_stored = __M_locals_builtin()
        __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['product'] if __M_key in __M_locals_builtin_stored]))
        # SOURCE LINE 3
        __M_writer(u'\n<div id="button_product" class="hpbutton gift">\n')
        # SOURCE LINE 5
        if product:
            # SOURCE LINE 6
            __M_writer(u'\t\t<div class="button_content">\n\t\t\t<a class="content withbg">\n\t\t\t\t<img class="loaders_animation" src="/static/imgs/ajax-loader.gif"/>\n\t\t\t\t<img class="button_content" src="')
            # SOURCE LINE 9
            __M_writer(escape(getattr(product, 'picture_large')))
            __M_writer(u'"/>\n\t\t\t</a>\n\t\t\t<div class="label">')
            # SOURCE LINE 11
            __M_writer(getattr(product, 'display_label'))
            __M_writer(u'</div>\n\t\t</div>\n')
            # SOURCE LINE 13
        else:
            # SOURCE LINE 14
            __M_writer(u'\t\t<div class="button_content">\n\t\t\t<a class="content nobg"></a>\n\t\t\t<div class="label">')
            # SOURCE LINE 16
            __M_writer(escape(_("JOCHEN_SCHWEIZER_PAGE_INDEX_BUTTON_Select a Gift")))
            __M_writer(u'\n\t\t\t\t<div class="sub_label ">')
            # SOURCE LINE 17
            __M_writer(escape(_("JOCHEN_SCHWEIZER_PAGE_INDEX_BUTTON_Find the perfect gift from a selection of thousands.")))
            __M_writer(u'</div>\n\t\t\t</div>\n\t\t</div>\n')
            pass
        # SOURCE LINE 21
        __M_writer(u'\t\t<input type="hidden" id="product_guid" name="product.guid" value="')
        __M_writer(escape(getattr(product, 'guid', '')))
        __M_writer(u'"/>\n\t\t<input type="hidden" id="product_net"  name="product.aff_net" value="')
        # SOURCE LINE 22
        __M_writer(escape(getattr(product, 'aff_net', '')))
        __M_writer(u'"/>\n\t\t<input type="hidden" id="product_progid" value="')
        # SOURCE LINE 23
        __M_writer(escape(getattr(product, 'aff_program_id', '')))
        __M_writer(u'"/>\n</div>\n<div class="extender">&nbsp;</div>')
        return ''
    finally:
        context.caller_stack._pop_frame()


