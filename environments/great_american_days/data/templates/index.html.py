# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1291293721.1812489
_template_filename='/home/www-data/ff_dev/friendfund/partners/jochen_schweizer/templates/index.html'
_template_uri='/index.html'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='utf-8'
from webhelpers.html import escape
from xml.sax.saxutils import quoteattr
_exports = ['user_voice', 'onloadscripts', 'bodyclass', 'title', 'render_siteinfo_copyright', 'render_account_panel', 'header', 'scripts', 'page_slogan']


def _mako_get_namespace(context, name):
    try:
        return context.namespaces[(__name__, name)]
    except KeyError:
        _mako_generate_namespaces(context)
        return context.namespaces[(__name__, name)]
def _mako_generate_namespaces(context):
    # SOURCE LINE 4
    ns = runtime.Namespace(u'forms', context._clean_inheritance_tokens(), templateuri=u'widgets/forms.html', callables=None, calling_uri=_template_uri, module=None)
    context.namespaces[(__name__, u'forms')] = ns

    # SOURCE LINE 5
    ns = runtime.Namespace(u'ra_stream', context._clean_inheritance_tokens(), templateuri=u'widgets/ra_stream.html', callables=None, calling_uri=_template_uri, module=None)
    context.namespaces[(__name__, u'ra_stream')] = ns

    # SOURCE LINE 3
    ns = runtime.Namespace(u'html', context._clean_inheritance_tokens(), templateuri=u'widgets/html_elems.html', callables=None, calling_uri=_template_uri, module=None)
    context.namespaces[(__name__, u'html')] = ns

    # SOURCE LINE 2
    ns = runtime.Namespace(u'links', context._clean_inheritance_tokens(), templateuri=u'links.html', callables=None, calling_uri=_template_uri, module=None)
    context.namespaces[(__name__, u'links')] = ns

def _mako_inherit(template, context):
    _mako_generate_namespaces(context)
    return runtime._inherit_from(context, u'layout_layer.html', _template_uri)
def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        url = context.get('url', UNDEFINED)
        html = _mako_get_namespace(context, 'html')
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'\n')
        # SOURCE LINE 2
        __M_writer(u'\n')
        # SOURCE LINE 3
        __M_writer(u'\n')
        # SOURCE LINE 4
        __M_writer(u'\n')
        # SOURCE LINE 5
        __M_writer(u'\n')
        # SOURCE LINE 6
        __M_writer(u'\n\n')
        # SOURCE LINE 20
        __M_writer(u'\n\n')
        # SOURCE LINE 22
        __M_writer(u'\n')
        # SOURCE LINE 28
        __M_writer(u'\n')
        # SOURCE LINE 29
        __M_writer(u'\n')
        # SOURCE LINE 30
        __M_writer(u'\n')
        # SOURCE LINE 31
        __M_writer(u'\n')
        # SOURCE LINE 34
        __M_writer(u'\n\n\n')
        # SOURCE LINE 53
        __M_writer(u'\n\n\n\n<form action="')
        # SOURCE LINE 57
        __M_writer(escape(url(controller='pool', action='create')))
        __M_writer(u'" method="POST" id="pool_configurator_form" onsubmit="panels.verify()">\n\t<div id="pool_configurator">\n\t\t<div id="product_panel" _type="product" class="frontpagebutton first">\n\t\t\t')
        # SOURCE LINE 60
        runtime._include_file(context, u'product/button.html', _template_uri)
        __M_writer(u'\n\t\t</div>\n\n\t\t<div id="receiver_panel" _type="receiver" class="frontpagebutton enabled">\n\t\t\t')
        # SOURCE LINE 64
        runtime._include_file(context, u'receiver/button.html', _template_uri)
        __M_writer(u'\n\t\t</div>\n\n\t\t<div id="occasion_panel" _type="occasion" class="frontpagebutton enabled">\n\t\t\t')
        # SOURCE LINE 68
        runtime._include_file(context, u'occasion/button.html', _template_uri)
        __M_writer(u'\n\t\t</div>\n\n\t\t<div id="funders_panel" class="frontpagebutton last">\n\t\t\t<div class="hpbutton funders">\n\t\t\t\t<a class="button funders">\n\t\t\t\t\t')
        # SOURCE LINE 74
        __M_writer(escape(_(u"PAGE_INDEX_HEADING_One more step...")))
        __M_writer(u'\n\t\t\t\t</a>\n\t\t\t\t<div class="button_content funders">\n\t\t\t\t\t<span id="funders_panel_tooltip" class="hidden">')
        # SOURCE LINE 77
        __M_writer(escape(_(u"PAGE_INDEX_MESSAGE_Please select Who, When and What first!")))
        __M_writer(u'</span>\n\t\t\t\t\t<a id="funders_button" class="red_labeled_container funders inactive">\n\t\t\t\t\t\t<span>')
        # SOURCE LINE 79
        __M_writer(escape(_("PAGE_INDEX_BUTTON_Invite Friends")))
        __M_writer(u'</span>\n                    </a>\n\t\t\t\t\t<div style="position: relative; top: 15px;"><div class="sub_label ">')
        # SOURCE LINE 81
        __M_writer(escape(_(u"PAGE_INDEX_FUNDERSTEXT_Once you've selected a receiver, an event and a gift, invite your friends to chip in to your gift pool.")))
        __M_writer(u'</div></div>\n\t\t\t\t</div>\n\t\t\t</div>\n\t\t</div>\n\t\t')
        # SOURCE LINE 85
        __M_writer(html.clearline())
        __M_writer(u'\n\t\t<div id="button_panel_container">&nbsp;</div>\n\t</div>\n</form>\n\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_user_voice(context):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_onloadscripts(context):
    context.caller_stack._push_frame()
    try:
        getattr = context.get('getattr', UNDEFINED)
        app_globals = context.get('app_globals', UNDEFINED)
        c = context.get('c', UNDEFINED)
        str = context.get('str', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 37
        __M_writer(u'\n\t\t')
        # SOURCE LINE 38
 
        pool = getattr(c, "pool", None) 
        receiver = str(getattr(pool, "receiver", None) is not None).lower()
        occasion = str(getattr(pool, "occasion", None) is not None).lower()
        product = str(getattr(pool, "product", None) is not None).lower()
                        
        
        # SOURCE LINE 43
        __M_writer(u'\n\t\tpanels = new friendfund.HomePagePanel({\n\t\t\t\t\t\tref_node : "button_panel_container"\n\t\t\t\t\t\t, config_node: "pool_configurator"\n\t\t\t\t\t\t, fb_api_key : "')
        # SOURCE LINE 47
        __M_writer(escape(app_globals.FbApiKey))
        __M_writer(u'"\n\t\t\t\t\t\t, window : window.parent\n\t\t\t\t\t\t, scrolling : false\n\t\t\t\t\t\t, auto_extend : "receiver"\n\t\t\t\t\t\t, auto_suggest : false\n\t\t\t\t\t\t, selected_elems : {receiver:')
        # SOURCE LINE 52
        __M_writer(escape(receiver))
        __M_writer(u', occasion:')
        __M_writer(escape(occasion))
        __M_writer(u', product:')
        __M_writer(escape(product))
        __M_writer(u'}});\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_bodyclass(context):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        # SOURCE LINE 29
        __M_writer(u'popup')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_title(context):
    context.caller_stack._push_frame()
    try:
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 6
        __M_writer(escape(_("PAGE_INDEX_TITLE_Welcome")))
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_render_siteinfo_copyright(context):
    context.caller_stack._push_frame()
    try:
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 32
        __M_writer(u'\n\t<div class="siteinfo_copyright light"><p>')
        # SOURCE LINE 33
        __M_writer(_(u"powered by <span class=\"poweredByFriendfund\"></span>"))
        __M_writer(u'</p></div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_render_account_panel(context):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_header(context):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_scripts(context):
    context.caller_stack._push_frame()
    try:
        links = _mako_get_namespace(context, 'links')
        __M_writer = context.writer()
        # SOURCE LINE 8
        __M_writer(u'\n\t<script type="text/javascript">\n\t\tpage_reloader = function(){console.log(\'reloading\')};\n\t\tdojo.query(".frontpagebutton.enabled", "pool_configurator").forEach(\n\t\t\tfunction(elem, pos, array){\n\t\t\t\tdojo.connect(elem, "onmouseenter", function(evt){dojo.addClass(this, "frontpagebuttonhover")});\n\t\t\t\tdojo.connect(elem, "onmouseleave", function(evt){dojo.removeClass(this, "frontpagebuttonhover")});\n\t\t});\n\t</script>\n\t')
        # SOURCE LINE 17
        __M_writer(escape(links.js('friendfund/HomePagePanel.js')))
        __M_writer(u'\n\t')
        # SOURCE LINE 18
        __M_writer(escape(links.js('friendfund/FriendSelector.js')))
        __M_writer(u'\n\t')
        # SOURCE LINE 19
        __M_writer(escape(links.js('friendfund/ProductSearch.js')))
        __M_writer(u'\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_page_slogan(context):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        # SOURCE LINE 23
        __M_writer(u'\n\t<h4 class="inside">\n\t\tShare the costs with your friends!\n\t</h4>\n\t<div class="insider">Share the costs with your friends by organising a group gift pool.</div>\n\t')
        return ''
    finally:
        context.caller_stack._pop_frame()


