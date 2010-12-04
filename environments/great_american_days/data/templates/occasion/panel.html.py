# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1291293096.2337439
_template_filename='/home/www-data/ff_dev/friendfund/templates/occasion/panel.html'
_template_uri='/occasion/panel.html'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='utf-8'
from webhelpers.html import escape
from xml.sax.saxutils import quoteattr
_exports = []


# SOURCE LINE 1
 
from datetime import date, timedelta


def _mako_get_namespace(context, name):
    try:
        return context.namespaces[(__name__, name)]
    except KeyError:
        _mako_generate_namespaces(context)
        return context.namespaces[(__name__, name)]
def _mako_generate_namespaces(context):
    # SOURCE LINE 4
    ns = runtime.Namespace(u'forms', context._clean_inheritance_tokens(), templateuri=u'../widgets/forms.html', callables=None, calling_uri=_template_uri, module=None)
    context.namespaces[(__name__, u'forms')] = ns

    # SOURCE LINE 5
    ns = runtime.Namespace(u'html', context._clean_inheritance_tokens(), templateuri=u'../widgets/html_elems.html', callables=None, calling_uri=_template_uri, module=None)
    context.namespaces[(__name__, u'html')] = ns

def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        int = context.get('int', UNDEFINED)
        forms = _mako_get_namespace(context, 'forms')
        c = context.get('c', UNDEFINED)
        html = _mako_get_namespace(context, 'html')
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 3
        __M_writer(u'\n')
        # SOURCE LINE 4
        __M_writer(u'\n')
        # SOURCE LINE 5
        __M_writer(u'\n\n\n<div id="button_panel" class="occasion">\n\n\t<div class="TabsContainer"><a _type="recommended_tab" class="methodselector ajaxlink selected "><span>')
        # SOURCE LINE 10
        __M_writer(escape(_("EVENT_PANEL_Select an Event")))
        __M_writer(u'</span></a></div>\n\t<a class="button_panel_closer">&nbsp;</a>\n\t')
        # SOURCE LINE 12
        __M_writer(html.clearline())
        __M_writer(u'\n\t<div id="occasion_button_bar">\n')
        # SOURCE LINE 14
        for occ in c.olist:
            # SOURCE LINE 15
            __M_writer(u'\t\t\t<a href="#" class="occasion_panel_button">\n\t\t\t\t<div class="selector ')
            # SOURCE LINE 16
            __M_writer(escape(c.key != occ.key and ' ' or 'selected'))
            __M_writer(u'" imgurl="/static/imgs/')
            __M_writer(escape(occ.picture_url))
            __M_writer(u'" \n\t\t\t\t\tcustom="')
            # SOURCE LINE 17
            __M_writer(escape(int(occ.custom or 0)))
            __M_writer(u'" key="')
            __M_writer(escape(occ.key))
            __M_writer(u'" displayname="')
            __M_writer(escape(occ.get_display_name()))
            __M_writer(u'" date="')
            __M_writer(escape(occ.internal_date_format))
            __M_writer(u'">\n\t\t\t\t\t<img src="/static/imgs/')
            # SOURCE LINE 18
            __M_writer(escape(occ.picture_url))
            __M_writer(u'"/>\n\t\t\t\t\t<div class="label">\n')
            # SOURCE LINE 20
            if occ.custom:
                # SOURCE LINE 21
                __M_writer(u'\t\t\t\t\t\t')
                __M_writer(escape(forms.black_input_text(occ.key, "name", value=c.name, default=_("EVENT_PANEL_Just because..."), width=106)))
                __M_writer(u'\n')
                # SOURCE LINE 22
            else:
                # SOURCE LINE 23
                __M_writer(u'\t\t\t\t\t\t')
                __M_writer(escape(occ.get_display_name()))
                __M_writer(u'\n')
                pass
            # SOURCE LINE 25
            __M_writer(u'\t\t\t\t\t</div>\n\t\t\t\t</div>\n\t\t\t</a>\n')
            pass
        # SOURCE LINE 29
        __M_writer(u'\t\t<div id="occasion_date_input_bar">\n\t\t\t<div style="margin-right:50px;"> \n\t\t\t\t<a class="submitSmall occasion_submitter"><span>')
        # SOURCE LINE 31
        __M_writer(escape(_("EVENT_PANEL_Submit")))
        __M_writer(u'</span></a>\n\t\t\t</div>\n\t\t\t<div style="top: 5px; position: relative;float:right;margin-right:50px;">\n\t\t\t\t')
        # SOURCE LINE 34
        __M_writer(forms.black_input_datepicker("datestamp", "datestamp", c.date, label=_("EVENT_PANEL_And Pick a Date"), width=100, args=[("constraints", "{min:'%s'}"%c.lower_limit_date)]))
        __M_writer(u'\n\t\t\t</div>\n\t\t</div>\n\t</div>\n</div>')
        return ''
    finally:
        context.caller_stack._pop_frame()


