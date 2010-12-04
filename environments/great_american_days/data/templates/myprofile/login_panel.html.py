# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1291204920.2744789
_template_filename='/home/www-data/ff_dev/friendfund/templates/myprofile/login_panel.html'
_template_uri='/myprofile/login_panel.html'
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
    # SOURCE LINE 2
    ns = runtime.Namespace(u'forms', context._clean_inheritance_tokens(), templateuri=u'../widgets/forms.html', callables=None, calling_uri=_template_uri, module=None)
    context.namespaces[(__name__, u'forms')] = ns

    # SOURCE LINE 1
    ns = runtime.Namespace(u'html', context._clean_inheritance_tokens(), templateuri=u'../widgets/html_elems.html', callables=None, calling_uri=_template_uri, module=None)
    context.namespaces[(__name__, u'html')] = ns

def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        url = context.get('url', UNDEFINED)
        c = context.get('c', UNDEFINED)
        getattr = context.get('getattr', UNDEFINED)
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        __M_writer(u'\n')
        # SOURCE LINE 2
        __M_writer(u'\n\n<div id="loginpanel">\n')
        # SOURCE LINE 5
        if c.user.is_anon:
            # SOURCE LINE 6
            __M_writer(u'\t\t<b>')
            __M_writer(escape(_(u"PANEL_LOGIN_Connect")))
            __M_writer(u'</b>\n\t\t<a onclick="fbLogin()" class="login_loginlink hover"><img src="/static/imgs/icon_fb_connect.png"/></a>\n\t\t<a onclick="twInit(\'')
            # SOURCE LINE 8
            __M_writer(escape(getattr(c, 'furl', url('home'))))
            __M_writer(u'\')" class="login_loginlink hover"><img src="/static/imgs/icon_tw_connect.png"/></a>\n\t\t<a href="')
            # SOURCE LINE 9
            __M_writer(escape(url('index', action='login')))
            __M_writer(u'?furl=')
            __M_writer(escape(getattr(c, 'furl', url('home'))))
            __M_writer(u'" class="login_loginlink hover"><img src="/static/imgs/icon_mail.png"/></a>\n')
            # SOURCE LINE 10
        else:
            # SOURCE LINE 11
            __M_writer(u'\t\t<a href="')
            __M_writer(escape(url('controller', controller='mypools')))
            __M_writer(u'">\n\t\t\t')
            # SOURCE LINE 12
            __M_writer(escape(_("PANEL_LOGIN_Welcome")))
            __M_writer(u'\n\t\t\t<img id="login_panel_profile_pic" src="')
            # SOURCE LINE 13
            __M_writer(escape(c.user.get_profile_pic()))
            __M_writer(u'"/>\n\t\t\t<span class="name">')
            # SOURCE LINE 14
            __M_writer(escape(c.user.name or c.user.email))
            __M_writer(u'</span></a>\n')
            # SOURCE LINE 15
            if 'facebook' not in c.user.networks:
                # SOURCE LINE 16
                __M_writer(u'\t\t\t<a href="#" onclick="fbLogin()" class="login_loginlink hover"><img src="/static/imgs/icon_fb_connect.png"/></a>\n')
                pass
            # SOURCE LINE 18
            __M_writer(u'\t\t<a href="#" style="margin-left:10px;" onclick="fbLogout();">')
            __M_writer(escape(_("PANEL_LOGIN_logout")))
            __M_writer(u'</a>\n')
            pass
        # SOURCE LINE 20
        __M_writer(u'</div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


