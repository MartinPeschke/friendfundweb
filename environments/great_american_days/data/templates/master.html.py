# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1291287034.2441199
_template_filename=u'/home/www-data/ff_dev/friendfund/templates/master.html'
_template_uri=u'/master.html'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='utf-8'
from webhelpers.html import escape
from xml.sax.saxutils import quoteattr
_exports = ['render_footer_links', 'onloadscripts', 'render_flag_container', 'header', 'fb_meta_tags', 'page_slogan', 'bodyclass', 'title', 'render_foot_scripts', 'scripts_styles', 'header_navigation', 'headerclass', 'user_voice', 'headscripts', 'render_head', 'render_verisign', 'render_siteinfo_copyright', 'siteinfo', 'scripts', 'render_html', 'render_account_panel', 'create_pool_button', 'google_analytics', 'messaging', 'lowerbody']


# SOURCE LINE 1

from pylons.i18n.translation import get_lang


def _mako_get_namespace(context, name):
    try:
        return context.namespaces[(__name__, name)]
    except KeyError:
        _mako_generate_namespaces(context)
        return context.namespaces[(__name__, name)]
def _mako_generate_namespaces(context):
    # SOURCE LINE 6
    ns = runtime.Namespace(u'forms', context._clean_inheritance_tokens(), templateuri=u'widgets/forms.html', callables=None, calling_uri=_template_uri, module=None)
    context.namespaces[(__name__, u'forms')] = ns

    # SOURCE LINE 5
    ns = runtime.Namespace(u'html', context._clean_inheritance_tokens(), templateuri=u'widgets/html_elems.html', callables=None, calling_uri=_template_uri, module=None)
    context.namespaces[(__name__, u'html')] = ns

    # SOURCE LINE 4
    ns = runtime.Namespace(u'links', context._clean_inheritance_tokens(), templateuri=u'links.html', callables=None, calling_uri=_template_uri, module=None)
    context.namespaces[(__name__, u'links')] = ns

def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        self = context.get('self', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 3
        __M_writer(u'\n')
        # SOURCE LINE 4
        __M_writer(u'\n')
        # SOURCE LINE 5
        __M_writer(u'\n')
        # SOURCE LINE 6
        __M_writer(u'\n')
        # SOURCE LINE 7
        __M_writer(escape(self.render_html()))
        __M_writer(u'\n\n')
        # SOURCE LINE 26
        __M_writer(u'\n\n')
        # SOURCE LINE 39
        __M_writer(u'\n\n\n')
        # SOURCE LINE 65
        __M_writer(u'\n\n')
        # SOURCE LINE 78
        __M_writer(u'\n\n')
        # SOURCE LINE 90
        __M_writer(u'\n')
        # SOURCE LINE 93
        __M_writer(u'\n')
        # SOURCE LINE 101
        __M_writer(u'\n')
        # SOURCE LINE 108
        __M_writer(u'\n\n\n\n')
        # SOURCE LINE 114
        __M_writer(u'\n')
        # SOURCE LINE 119
        __M_writer(u'\n\n\n')
        # SOURCE LINE 122
        __M_writer(u'\n')
        # SOURCE LINE 123
        __M_writer(u'\n')
        # SOURCE LINE 124
        __M_writer(u'\n')
        # SOURCE LINE 125
        __M_writer(u'\n')
        # SOURCE LINE 126
        __M_writer(u'\n')
        # SOURCE LINE 127
        __M_writer(u'\n')
        # SOURCE LINE 128
        __M_writer(u'\n\n')
        # SOURCE LINE 137
        __M_writer(u'\n')
        # SOURCE LINE 140
        __M_writer(u'\n\n')
        # SOURCE LINE 149
        __M_writer(u'\n\n\n')
        # SOURCE LINE 154
        __M_writer(u'\n')
        # SOURCE LINE 163
        __M_writer(u'\n\n')
        # SOURCE LINE 172
        __M_writer(u'\n\n')
        # SOURCE LINE 174
        __M_writer(u'\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_render_footer_links(context):
    context.caller_stack._push_frame()
    try:
        url = context.get('url', UNDEFINED)
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 94
        __M_writer(u'\n\t<a href="http://blog.friendfund.com" class="siteinfo_content">')
        # SOURCE LINE 95
        __M_writer(_(u"SITEINFO_Blog"))
        __M_writer(u'</a>\n\t<a href="http://blog.friendfund.com/?page_id=108" class="siteinfo_content">')
        # SOURCE LINE 96
        __M_writer(_(u"SITEINFO_Jobs"))
        __M_writer(u'</a>\n\t<a href="')
        # SOURCE LINE 97
        __M_writer(escape(url(controller='content', action='tos')))
        __M_writer(u'" class="siteinfo_content">')
        __M_writer(_(u"SITEINFO_Terms"))
        __M_writer(u'</a>\n\t<a href="')
        # SOURCE LINE 98
        __M_writer(escape(url(controller='content', action='privacy')))
        __M_writer(u'" class="siteinfo_content">')
        __M_writer(_(u"SITEINFO_Privacy"))
        __M_writer(u'</a>\n\t<a href="')
        # SOURCE LINE 99
        __M_writer(escape(url(controller='content', action='impressum')))
        __M_writer(u'" class="siteinfo_content">')
        __M_writer(_(u"SITEINFO_Impressum"))
        __M_writer(u'</a>\n\t<a href="')
        # SOURCE LINE 100
        __M_writer(escape(url(controller='content', action='faq')))
        __M_writer(u'" class="siteinfo_content">')
        __M_writer(_(u"SITEINFO_FAQ"))
        __M_writer(u'</a>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_onloadscripts(context):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_render_flag_container(context):
    context.caller_stack._push_frame()
    try:
        url = context.get('url', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 102
        __M_writer(u'\n\t<div class="flagContainer">\n\t\t<a href="')
        # SOURCE LINE 104
        __M_writer(escape(url(controller='myprofile', action='set_lang')))
        __M_writer(u'?lang=de_DE" class="flag_de_DE">&nbsp;</a>\n\t\t<a href="')
        # SOURCE LINE 105
        __M_writer(escape(url(controller='myprofile', action='set_lang')))
        __M_writer(u'?lang=en_GB" class="flag_en_GB">&nbsp;</a>\n\t\t<a href="')
        # SOURCE LINE 106
        __M_writer(escape(url(controller='myprofile', action='set_lang')))
        __M_writer(u'?lang=en_US" class="flag_en_US">&nbsp;</a>\n\t</div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_header(context):
    context.caller_stack._push_frame()
    try:
        url = context.get('url', UNDEFINED)
        self = context.get('self', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 142
        __M_writer(u'\n\t<div id="headercontainer">\n\t\t<a href="')
        # SOURCE LINE 144
        __M_writer(escape(url('home', protocol='http')))
        __M_writer(u'" class="logoHeader"><img src="/static/imgs/header/logo_banner.png"/></a>\n\t\t<div class="logoBanner"><img src="/static/imgs/themes/christmas/js_christmas.png"/></div>\n\t\t')
        # SOURCE LINE 146
        __M_writer(escape(self.header_navigation()))
        __M_writer(u'\n\t\t')
        # SOURCE LINE 147
        __M_writer(escape(self.create_pool_button()))
        __M_writer(u'\n\t</div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_fb_meta_tags(context):
    context.caller_stack._push_frame()
    try:
        url = context.get('url', UNDEFINED)
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 165
        __M_writer(u'\n\t\t<link rel="image_src" href="/static/imgs/fb_stream_publish_logo.png" />\n\t\t<meta name="title" content="')
        # SOURCE LINE 167
        __M_writer(_(u"FB_METATAG_TITLE_friendfund.com"))
        __M_writer(u'" />\n\t\t<meta name="description" content="')
        # SOURCE LINE 168
        __M_writer(_(u"FB_METATAG_DESCRIPTION_friendfund.com - helping you!"))
        __M_writer(u'" />\n\t\t\n\t\t<meta property="og:site_name" content="Friendfund"/>\n\t\t<meta property="og:url" content="')
        # SOURCE LINE 171
        __M_writer(escape(url.current()))
        __M_writer(u'"/>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_page_slogan(context):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_bodyclass(context):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        # SOURCE LINE 123
        __M_writer(u'base')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_title(context):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_render_foot_scripts(context):
    context.caller_stack._push_frame()
    try:
        c = context.get('c', UNDEFINED)
        links = _mako_get_namespace(context, 'links')
        self = context.get('self', UNDEFINED)
        getattr = context.get('getattr', UNDEFINED)
        html = _mako_get_namespace(context, 'html')
        str = context.get('str', UNDEFINED)
        app_globals = context.get('app_globals', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 42
        __M_writer(u'\n\t<input type="hidden" id="furl" value="')
        # SOURCE LINE 43
        __M_writer(escape(getattr(c, 'furl', '')))
        __M_writer(u'"/>\n\t<script type="text/javascript">djConfig={baseUrl: "./", modulePaths: {"friendfund": "/static/js/friendfund"},dojoBlankHtmlUrl : "/static/blank.html",xdWaitSeconds: 5};</script> \n\t<script src="https://ajax.googleapis.com/ajax/libs/dojo/1.5/dojo/dojo.xd.js" type="text/javascript"></script>\n\t')
        # SOURCE LINE 46
        __M_writer(escape(links.js('fbinit.js')))
        __M_writer(u'\n\t')
        # SOURCE LINE 47
        __M_writer(escape(links.js('loader.js')))
        __M_writer(u'\n\t')
        # SOURCE LINE 48
        __M_writer(escape(self.scripts()))
        __M_writer(u'\n\t<div id="generic_popup"></div>\n\t<div id="blocking_msgs" class="')
        # SOURCE LINE 50
        __M_writer(escape((not (getattr(c, 'blocks', False) and getattr(c, 'enforce_blocks', False))) and 'hidden' or ''))
        __M_writer(u'">\n\t\t')
        # SOURCE LINE 51
        runtime._include_file(context, u'/messages/blocks.html', _template_uri)
        __M_writer(u'\n\t</div>\n\t<div id="fb-root"></div>\n\t<script type="text/javascript">\n\t\tvar loading_animation_src = "')
        # SOURCE LINE 55
        __M_writer(html.ajax_loading_animation_src().strip())
        __M_writer(u'";\n\t\tvar loading_animation = "')
        # SOURCE LINE 56
        __M_writer(html.ajax_loading_animation().strip())
        __M_writer(u'";\n\t\t')
        # SOURCE LINE 57
        __M_writer(escape(self.headscripts()))
        __M_writer(u'\n\t\tdojo.addOnLoad( function() {\n\t\t\tfbInit("')
        # SOURCE LINE 59
        __M_writer(escape(app_globals.FbApiKey))
        __M_writer(u'", ')
        __M_writer(escape(str(c.user.has_tried_logging_in_with("facebook")).lower()))
        __M_writer(u');\n\t\t\t')
        # SOURCE LINE 60
        __M_writer(escape(self.onloadscripts()))
        __M_writer(u'\n\t\t});\n\t</script>\n\t')
        # SOURCE LINE 63
        __M_writer(self.user_voice())
        __M_writer(u'\n\t')
        # SOURCE LINE 64
        __M_writer(self.google_analytics())
        __M_writer(u'\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_scripts_styles(context):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_header_navigation(context):
    context.caller_stack._push_frame()
    try:
        url = context.get('url', UNDEFINED)
        c = context.get('c', UNDEFINED)
        app_globals = context.get('app_globals', UNDEFINED)
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 155
        __M_writer(u'\n\t<ul class="navigation">\n')
        # SOURCE LINE 157
        for title, path, token, enabled in app_globals.globalnav:
            # SOURCE LINE 158
            if enabled:
                # SOURCE LINE 159
                __M_writer(u'\t\t\t\t<li class="floaterLeft ')
                __M_writer(escape((c.navposition==token) and 'selected' or ''))
                __M_writer(u'"><a href="')
                __M_writer(escape(url(*path['args'], **path['kwargs'])))
                __M_writer(u'">')
                __M_writer(escape(_(title)))
                __M_writer(u'</a></li>\n')
                pass
            pass
        # SOURCE LINE 162
        __M_writer(u'\t</ul>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_headerclass(context):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        # SOURCE LINE 128
        __M_writer(u'normal')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_user_voice(context):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        # SOURCE LINE 130
        __M_writer(u'\n\t<script type="text/javascript">\n\t\tvar uservoiceOptions = {\n\t\t\t/* required */key: \'friendfund\',host: \'friendfund.uservoice.com\', forum: \'81919\',showTab: true,  \n\t\t\t/* optional */alignment: \'left\',background_color:\'#333\', text_color: \'white\',hover_color: \'#06C\',lang: \'en\'};\n\t\t\tfunction _loadUserVoice() {var s = document.createElement(\'script\');s.setAttribute(\'type\', \'text/javascript\');s.setAttribute(\'src\', ("https:" == document.location.protocol ? "https://" : "http://") + "cdn.uservoice.com/javascripts/widgets/tab.js");document.getElementsByTagName(\'head\')[0].appendChild(s);}_loadSuper = window.onload;window.onload = (typeof window.onload != \'function\') ? _loadUserVoice : function() { _loadSuper(); _loadUserVoice(); };\n\t</script>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_headscripts(context):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_render_head(context):
    context.caller_stack._push_frame()
    try:
        self = context.get('self', UNDEFINED)
        c = context.get('c', UNDEFINED)
        links = _mako_get_namespace(context, 'links')
        __M_writer = context.writer()
        # SOURCE LINE 28
        __M_writer(u'\n\t\t<title>friendfund.com | ')
        # SOURCE LINE 29
        __M_writer(escape(self.title()))
        __M_writer(u'</title>\n\t\t')
        # SOURCE LINE 30
        __M_writer(escape(links.css('%s.css'%c.siteversion)))
        __M_writer(u'\n\t\t')
        # SOURCE LINE 31
        __M_writer(escape(links.css('message_block.css')))
        __M_writer(u'\n\t\t<script type="text/javascript"> \n\t\t\tpage_reloader = function(){window.location.reload();};\n\t\t\tlogin_panel_refresh = function(){loadElement(\'/index/login_panel\', "accountcontainer")};\n\t\t\tlocale_picked=function(elem){document.getElementById("set_lang").submit()}\n\t\t</script>\n\t\t')
        # SOURCE LINE 37
        __M_writer(escape(self.fb_meta_tags()))
        __M_writer(u'\n\t\t')
        # SOURCE LINE 38
        __M_writer(escape(self.scripts_styles()))
        __M_writer(u'\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_render_verisign(context,id):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        # SOURCE LINE 80
        __M_writer(u'\n\t<div id="')
        # SOURCE LINE 81
        __M_writer(escape(id))
        __M_writer(u'">\n\t\t<table width="135" border="0" cellpadding="2" cellspacing="0" title="Click to Verify - This site chose VeriSign SSL for secure e-commerce and confidential communications.">\n\t\t<tr><td width="135" align="center" valign="top">\n\t\t\t<script type="text/javascript" src="https://seal.verisign.com/getseal?host_name=www.friendfund.com&amp;size=S&amp;use_flash=NO&amp;use_transparent=NO&amp;lang=en"></script><br/>\n\t\t\t<a href="http://www.verisign.com/ssl-certificate/" target="_blank"\n\t\t\tstyle="color:#000000; text-decoration:none; font:bold 7px verdana,sans-serif; letter-spacing:.5px; text-align:center; margin:0px; padding:0px;">ABOUT SSL CERTIFICATES</a>\n\t\t</td></tr>\n\t\t</table>\n\t</div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_render_siteinfo_copyright(context):
    context.caller_stack._push_frame()
    try:
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 91
        __M_writer(u'\n\t<div class="siteinfo_copyright"><p>')
        # SOURCE LINE 92
        __M_writer(_(u"SITEINFO_2010(c) friendfund"))
        __M_writer(u'</p><p>')
        __M_writer(_(u"SITEINFO_Handmade in Berlin"))
        __M_writer(u'</p></div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_siteinfo(context):
    context.caller_stack._push_frame()
    try:
        self = context.get('self', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 67
        __M_writer(u'\n\t<div id="siteinfo">\n\t\t<div class="siteinfo1">\n\t\t\t<div class="siteinfo2">\n\t\t\t\t')
        # SOURCE LINE 71
        __M_writer(escape(self.render_verisign(id="verisignseal")))
        __M_writer(u'\n\t\t\t\t')
        # SOURCE LINE 72
        __M_writer(escape(self.render_siteinfo_copyright()))
        __M_writer(u'\n\t\t\t\t')
        # SOURCE LINE 73
        __M_writer(escape(self.render_footer_links()))
        __M_writer(u'\n\t\t\t\t')
        # SOURCE LINE 74
        __M_writer(escape(self.render_flag_container()))
        __M_writer(u'\n\t\t\t</div>\n\t\t</div>\n\t</div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_scripts(context):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_render_html(context):
    context.caller_stack._push_frame()
    try:
        self = context.get('self', UNDEFINED)
        next = context.get('next', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 9
        __M_writer(u'\n\t<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n\t<html xmlns="http://www.w3.org/1999/xhtml" xmlns:fb="https://www.facebook.com/2008/fbml">\n\t<head>\n\t\t<meta content="text/html; charset=UTF-8" http-equiv="content-type"/>\n\t\t<link rel="shortcut icon" type="image/x-icon" href="/favicon.ico" />\n\t\t<link rel="stylesheet" type="text/css" href="https://ajax.googleapis.com/ajax/libs/dojo/1.5/dijit/themes/claro/claro.css"/>\n\t\t')
        # SOURCE LINE 16
        __M_writer(escape(self.render_head()))
        __M_writer(u'\n\t</head>\n\t<body class="claro ')
        # SOURCE LINE 18
        __M_writer(escape(self.bodyclass()))
        __M_writer(u'">\n\t\t<div id="outercontainer">\n\t\t\t')
        # SOURCE LINE 20
        __M_writer(escape(next.body()))
        __M_writer(u'\n\t\t</div>\n\t\t')
        # SOURCE LINE 22
        __M_writer(escape(self.siteinfo()))
        __M_writer(u'\n\t\t')
        # SOURCE LINE 23
        __M_writer(escape(self.render_foot_scripts()))
        __M_writer(u'\n\t</body>\n\t</html>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_render_account_panel(context):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        # SOURCE LINE 115
        __M_writer(u'\n\t<div id="accountcontainer">\n\t\t')
        # SOURCE LINE 117
        runtime._include_file(context, u'/myprofile/login_panel.html', _template_uri)
        __M_writer(u'\n\t</div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_create_pool_button(context):
    context.caller_stack._push_frame()
    try:
        url = context.get('url', UNDEFINED)
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 152
        __M_writer(u'\n\t<div id="home_create_pool_button"><a class="BtnRed" href="')
        # SOURCE LINE 153
        __M_writer(escape(url(controller='pool', action='start')))
        __M_writer(u'"><span>')
        __M_writer(_(u"ALLPAGE_BUTTON_Create a Pool"))
        __M_writer(u'</span></a></div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_google_analytics(context):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        # SOURCE LINE 138
        __M_writer(u'\n\t<script type="text/javascript">var _gaq = _gaq || [];_gaq.push([\'_setAccount\', \'UA-17547754-2\']);_gaq.push([\'_trackPageview\']);(function() {var ga = document.createElement(\'script\'); ga.type = \'text/javascript\'; ga.async = true;ga.src = (\'https:\' == document.location.protocol ? \'https://ssl\' : \'http://www\') + \'.google-analytics.com/ga.js\';var s = document.getElementsByTagName(\'script\')[0]; s.parentNode.insertBefore(ga, s);})();</script>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_messaging(context):
    context.caller_stack._push_frame()
    try:
        h = context.get('h', UNDEFINED)
        c = context.get('c', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 112
        __M_writer(u'\n<div id="messaging_container"><div id="message_container" class="')
        # SOURCE LINE 113
        __M_writer(escape(not h.has_ne_prop(c, '_msgs') and 'hidden' or ''))
        __M_writer(u'">')
        runtime._include_file(context, u'/messages/standard.html', _template_uri)
        __M_writer(u'</div></div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_lowerbody(context):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        return ''
    finally:
        context.caller_stack._pop_frame()


