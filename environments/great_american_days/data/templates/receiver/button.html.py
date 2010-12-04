# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1291205609.0566211
_template_filename=u'/home/www-data/ff_dev/friendfund/partners/jochen_schweizer/templates/receiver/button.html'
_template_uri=u'/receiver/button.html'
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

        receiver = getattr(getattr(c, 'pool', None), 'receiver', None)
        
        
        __M_locals_builtin_stored = __M_locals_builtin()
        __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['receiver'] if __M_key in __M_locals_builtin_stored]))
        # SOURCE LINE 3
        __M_writer(u'\n<div id="button_receiver" class="hpbutton receiver">\n')
        # SOURCE LINE 5
        if receiver:
            # SOURCE LINE 6
            __M_writer(u'\t\t<div class="button_content">\n\t\t\t<a class="content withbg">\n\t\t\t\t<img class="loaders_animation" src="/static/imgs/ajax-loader.gif"/>\n\t\t\t\t<img class="button_content" src="')
            # SOURCE LINE 9
            __M_writer(escape(getattr(receiver, 'profile_picture_url')))
            __M_writer(u'"/></a>\n\t\t\t<a name="button_panel_container_anchor" id="button_panel_container_anchor" style="position: absolute;top: 135px;"></a>\n\t\t\t<div class="label">')
            # SOURCE LINE 11
            __M_writer(escape(getattr(receiver, 'receiver_label')))
            __M_writer(u'</div>\n\t\t</div>\n\t\t<input type="hidden" name="receiver.network" \t\tid="receiver_network" \t\tvalue="')
            # SOURCE LINE 13
            __M_writer(escape(getattr(receiver, 'network', '')))
            __M_writer(u'"/>\n\t\t<input type="hidden" name="receiver.network_id" \tid="receiver_network_id" \tvalue="')
            # SOURCE LINE 14
            __M_writer(escape(getattr(receiver, 'network_id', '')))
            __M_writer(u'"/>\n\t\t<input type="hidden" name="receiver.name" \t\t\tid="receiver_name" \t\t\tvalue="')
            # SOURCE LINE 15
            __M_writer(escape(getattr(receiver, 'name', '')))
            __M_writer(u'"/>\n\t\t<input type="hidden" name="receiver.email" \t\t\tid="receiver_email" \t\tvalue="')
            # SOURCE LINE 16
            __M_writer(escape(getattr(receiver, 'email', '')))
            __M_writer(u'"/>\n\t\t<input type="hidden" name="receiver.dob" \t\t\tid="receiver_dob" \t\t\tvalue="')
            # SOURCE LINE 17
            __M_writer(escape(getattr(receiver, 'dob', '')))
            __M_writer(u'"/>\n')
            # SOURCE LINE 18
        else:
            # SOURCE LINE 19
            __M_writer(u'\t\t<div class="button_content">\n\t\t\t<a class="content nobg">\n\t\t\t<a name="button_panel_container_anchor" id="button_panel_container_anchor" style="position: absolute;top: 135px;"></a>\n\t\t\t<div class="label">')
            # SOURCE LINE 22
            __M_writer(escape(_("JOCHEN_SCHWEIZER_PAGE_INDEX_BUTTON_Select a Friend")))
            __M_writer(u'\n\t\t\t\t<div class="sub_label ">')
            # SOURCE LINE 23
            __M_writer(escape(_("JOCHEN_SCHWEIZER_PAGE_INDEX_BUTTON_Select your gift receiver from your Facebook, Twitter or email friends.")))
            __M_writer(u'</div>\n\t\t\t</div>\n\t\t</div>\n')
            pass
        # SOURCE LINE 27
        __M_writer(u'\t<input type="hidden" name="receiver.sex" \t\t\tid="receiver_sex" \t\t\tvalue="')
        __M_writer(escape(getattr(receiver, 'sex', '')))
        __M_writer(u'"/>\n</div>\n<div class="extender">&nbsp;</div>')
        return ''
    finally:
        context.caller_stack._pop_frame()


