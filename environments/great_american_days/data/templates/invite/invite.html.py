# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1291286054.916851
_template_filename='/home/www-data/ff_dev/friendfund/templates/invite/invite.html'
_template_uri='/invite/invite.html'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='utf-8'
from webhelpers.html import escape
from xml.sax.saxutils import quoteattr
_exports = ['scripts', 'onloadscripts', 'page_slogan', 'lowerbody', 'title']


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

    # SOURCE LINE 3
    ns = runtime.Namespace(u'html', context._clean_inheritance_tokens(), templateuri=u'../widgets/html_elems.html', callables=None, calling_uri=_template_uri, module=None)
    context.namespaces[(__name__, u'html')] = ns

    # SOURCE LINE 5
    ns = runtime.Namespace(u'inviter', context._clean_inheritance_tokens(), templateuri=u'inviter.html', callables=None, calling_uri=_template_uri, module=None)
    context.namespaces[(__name__, u'inviter')] = ns

    # SOURCE LINE 2
    ns = runtime.Namespace(u'links', context._clean_inheritance_tokens(), templateuri=u'../links.html', callables=None, calling_uri=_template_uri, module=None)
    context.namespaces[(__name__, u'links')] = ns

def _mako_inherit(template, context):
    _mako_generate_namespaces(context)
    return runtime._inherit_from(context, u'../layout_layer.html', _template_uri)
def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        c = context.get('c', UNDEFINED)
        html = _mako_get_namespace(context, 'html')
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
        # SOURCE LINE 11
        __M_writer(u'\n\n')
        # SOURCE LINE 23
        __M_writer(u'\n\n')
        # SOURCE LINE 28
        __M_writer(u'\n\n<div class="innerbody" id="invite_panel_header">\n\t<div class="invite_pool_panel hpbutton first">\n\t\t<div class="picture receiver"><span class="icon"></span><img src="')
        # SOURCE LINE 32
        __M_writer(escape(c.pool.receiver.get_profile_pic('RA')))
        __M_writer(u'"/>\n\t\t</div>\n\t\t<div class="label">')
        # SOURCE LINE 34
        __M_writer(escape(c.pool.receiver.get_receiver_label()))
        __M_writer(u'</div>\n\t</div>\n\t<div class="invite_pool_panel hpbutton">\n\t\t<div class="picture occasion"><span class="icon"></span><img src="/static/imgs/')
        # SOURCE LINE 37
        __M_writer(escape(c.pool.occasion.picture_url))
        __M_writer(u'"/></div>\n\t\t<div class="label">')
        # SOURCE LINE 38
        __M_writer(escape(c.pool.occasion.display_label))
        __M_writer(u'</div>\n\t</div>\n\t<div class="invite_pool_panel hpbutton">\n\t\t<div class="picture gift"><span class="icon"></span><img src="')
        # SOURCE LINE 41
        __M_writer(escape(c.pool.product.get_product_pic()))
        __M_writer(u'"/></div>\n\t\t<div class="label">')
        # SOURCE LINE 42
        __M_writer(c.pool.product.get_display_label())
        __M_writer(u'</div>\n\t</div>\n\t')
        # SOURCE LINE 44
        __M_writer(escape(html.clearline()))
        __M_writer(u'\n</div>\n\n\n\n')
        # SOURCE LINE 126
        __M_writer(u'\n\n\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_scripts(context):
    context.caller_stack._push_frame()
    try:
        links = _mako_get_namespace(context, 'links')
        __M_writer = context.writer()
        # SOURCE LINE 8
        __M_writer(u'\n\t')
        # SOURCE LINE 9
        __M_writer(escape(links.js('friendfund/FriendSelector.js')))
        __M_writer(u'\n\t')
        # SOURCE LINE 10
        __M_writer(escape(links.js('friendfund/InvitePage.js')))
        __M_writer(u'\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_onloadscripts(context):
    context.caller_stack._push_frame()
    try:
        url = context.get('url', UNDEFINED)
        c = context.get('c', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 13
        __M_writer(u'\n\tpage = new friendfund.InvitePage({\n\t\t\tcontainer : "lowerbody_container",\n\t\t\tinvited_node :"invited",\n\t\t\tmethod : "')
        # SOURCE LINE 17
        __M_writer(escape(c.method))
        __M_writer(u'",\n\t\t\tfb_api_key : "",\n\t\t\tbase_url : "')
        # SOURCE LINE 19
        __M_writer(escape(url('invite_index', controller='invite', pool_url=c.pool.p_url)))
        __M_writer(u'"\n\t\t});\n\t\n\tpage_reloader = dojo.hitch(null, page.prepareSubmit, page);\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_page_slogan(context):
    context.caller_stack._push_frame()
    try:
        c = context.get('c', UNDEFINED)
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 25
        __M_writer(u'\n\t')
        # SOURCE LINE 26
        locals = {"receiver_name" : c.pool.receiver.name } 
        
        __M_writer(u'\n\t<div id="page_slogan">')
        # SOURCE LINE 27
        __M_writer((_("INVITE_PAGE_FB_LOGIN_Invite Your friends to chip in for <span class=\"emphasis\">%(receiver_name)s's</span> gift.") % locals))
        __M_writer(u'</div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_lowerbody(context):
    context.caller_stack._push_frame()
    try:
        c = context.get('c', UNDEFINED)
        url = context.get('url', UNDEFINED)
        forms = _mako_get_namespace(context, 'forms')
        html = _mako_get_namespace(context, 'html')
        dict = context.get('dict', UNDEFINED)
        inviter = _mako_get_namespace(context, 'inviter')
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 49
        __M_writer(u'\n')
        # SOURCE LINE 50
 
        i_am_admin = c.pool.am_i_admin(c.user)
        
        
        # SOURCE LINE 52
        __M_writer(u'\n\n<div id="lowerbody_container" class="networkinviter fullbackgroundwhite marginTop">\n\t<div id="lowerbody">\n\t\t<div id="network_methodselector" class="TabsContainer"><a class="methodselector"><span>')
        # SOURCE LINE 56
        __M_writer(escape(_("INVITE_PAGE_LABEL_Select your friends from:")))
        __M_writer(u'</span></a>\n\t\t\t\t<a class="methodselector ajaxlink ')
        # SOURCE LINE 57
        __M_writer(escape(c.method == 'facebook' and 'selected' or ''))
        __M_writer(u'" _target="inviter" _type="facebook"><span><img src="/static/imgs/icon_fb_connect.png"> Facebook</span></a>\n\t\t\t\t<a class="methodselector ajaxlink ')
        # SOURCE LINE 58
        __M_writer(escape(c.method == 'twitter' and 'selected' or ''))
        __M_writer(u'" _target="inviter" _type="twitter"><span> <img src="/static/imgs/icon_tw_connect.png"> Twitter</span></a>\n\t\t\t\t<a class="methodselector ajaxlink ')
        # SOURCE LINE 59
        __M_writer(escape(c.method == 'email' and 'selected' or ''))
        __M_writer(u'" _target="inviter" _type="email"><span><img src="/static/imgs/icon_mail.png"> Email</span></a>\n\t\t</div>\n\t\t')
        # SOURCE LINE 61
        __M_writer(escape(html.clearline()))
        __M_writer(u'\n\t\t<div id="invitescontainer" class="innerbody">\n\t\t\t<form action="')
        # SOURCE LINE 63
        __M_writer(escape(url(controller='invite', pool_url=c.pool_url, action='friends')))
        __M_writer(u'" onsubmit="return prepareSubmit()" method="POST" id="invitees">\n\t\t\t<div id="invites">\n\t\t\t\t<div id="inviter"></div>\n')
        # SOURCE LINE 66
        if c.pool.require_pselector:
            # SOURCE LINE 67
            __M_writer(u'\t\t\t\t\t<div id="PendingSelectorSelector" class="placeholder">\n\t\t\t\t\t\t<span id="PendingPlaceHolder" class="gift">')
            # SOURCE LINE 68
            __M_writer(escape(_("INVITE_PAGE_Click on one of the gift icons below to nominate a friend to choose a gift for this pool.")))
            __M_writer(u'</span>\n\t\t\t\t\t\t<span id="PendingNominator" class="nominator hidden"><img/>')
            # SOURCE LINE 69
            __M_writer(_("INVITE_PAGE_<span class=\"name\">%s</span> has been nominated to choose a gift for this pool.")%"")
            __M_writer(u'</span>\n\t\t\t\t\t</div>\n')
            # SOURCE LINE 71
        elif c.pool.selector:
            # SOURCE LINE 72
            __M_writer(u'\t\t\t\t\t<div id="PendingSelectorSelector" class="placeholder" _network="')
            __M_writer(escape(c.pool.selector.network))
            __M_writer(u'" _network_id="')
            __M_writer(escape(c.pool.selector.network_id))
            __M_writer(u'">\n\t\t\t\t\t\t<span id="PendingPlaceHolder" class="gift hidden">')
            # SOURCE LINE 73
            __M_writer(escape(_("INVITE_PAGE_Click on one of the gift icons below to nominate a friend to choose a gift for this pool.")))
            __M_writer(u'</span>\n\t\t\t\t\t\t<span id="PendingNominator" class="nominator"><img src="')
            # SOURCE LINE 74
            __M_writer(escape(c.pool.selector.profile_s_pic))
            __M_writer(u'"/>')
            __M_writer(_("INVITE_PAGE_<span class=\"name\">%s</span> has been nominated to choose a gift for this pool.")%c.pool.selector.name)
            __M_writer(u'</span>\n\t\t\t\t\t</div>\n')
            # SOURCE LINE 76
        else:
            # SOURCE LINE 77
            __M_writer(u'\t\t\t\t\t<div class="placeholder">\n\t\t\t\t\t</div>\n')
            pass
        # SOURCE LINE 80
        __M_writer(u'\t\t\t\t<div id="invited">\n\t\t\t\t\t<div id="email_invitees" class="invited_list">\n\t\t\t\t\t\t<div class="seperator"><img src="/static/imgs/icon_mail.png"/></div>\n\t\t\t\t\t\t')
        # SOURCE LINE 83
        __M_writer(escape(inviter.render_email_friends(c.invitees.get("email", dict()), with_pending = c.pool.require_pselector)))
        __M_writer(u'\n\t\t\t\t\t\t<div style="clear:both;"></div>\n\t\t\t\t\t</div>\n\t\t\t\t\t<div id="twitter_invitees" class="invited_list">\n\t\t\t\t\t\t<div class="seperator"><img src="/static/imgs/icon_tw_connect.png"/></div>\n\t\t\t\t\t\t')
        # SOURCE LINE 88
        __M_writer(inviter.render_network_friends(c.invitees.get("twitter", dict()), with_pending = c.pool.require_pselector))
        __M_writer(u'\n\t\t\t\t\t\t<div style="clear:both;"></div>\n\t\t\t\t\t</div>\n\t\t\t\t\t<div id="facebook_invitees" class="invited_list">\n\t\t\t\t\t\t<div class="seperator"><img src="/static/imgs/icon_fb_connect.png"/></div>\n\t\t\t\t\t\t')
        # SOURCE LINE 93
        __M_writer(inviter.render_network_friends(c.invitees.get("facebook", dict()), with_pending = c.pool.require_pselector))
        __M_writer(u'\n\t\t\t\t\t\t<div style="clear:both;"></div>\n\t\t\t\t\t</div>\n\t\t\t\t</div>\n\t\t\t\t<div style="clear:both;"></div>\n\t\t\t</div>\n\t\t\t<div id="invite_message">\n\t\t\t\t<div class="invite_message">')
        # SOURCE LINE 100
        __M_writer(escape(_("INVITE_PAGE_LABEL_Send a personal message to all invitees:")))
        __M_writer(u'\n\t\t\t\t')
        # SOURCE LINE 101
        locals = {"admin_name":c.pool.admin.name, "receiver_name" : c.pool.receiver.name, "occasion_name": c.pool.occasion.get_display_name()} 
        
        __M_writer(u'\n\t\t\t\t<textarea name="description" id="default_slogan" cols="60" rows="5">')
        # SOURCE LINE 102
        __M_writer(c.pool.description or (_("INVITE_PAGE_DEFAULT_MSG_%(admin_name)s has created a Friend Fund for %(receiver_name)s's %(occasion_name)s. Come and chip in!")%locals))
        __M_writer(u'</textarea></div>\n')
        # SOURCE LINE 103
        if i_am_admin and not c.pool.product.is_virtual:
            # SOURCE LINE 104
            __M_writer(u'\t\t\t\t<div class="invite_secret">\n\t\t\t\t\t')
            # SOURCE LINE 105
            locals = {"receiver_name" : c.pool.receiver.get_receiver_label()} 
            
            __M_writer(u'\n\t\t\t\t\t')
            # SOURCE LINE 106
            __M_writer((_("INVITE_PAGE_LABEL_Keep pool a secret from %(receiver_name)s")%locals))
            __M_writer(u':\n\t\t\t\t\t<div class="yes">\n\t\t\t\t\t<input type="checkbox" id="check_is_secret" name="is_secret" value="true" ')
            # SOURCE LINE 108
            __M_writer(forms.expression_quote(c.pool.is_secret or False, "checked"))
            __M_writer(u'/><label for="check_is_secret">')
            __M_writer(escape(_("INVITE_PAGE_BUTTON_Yes, please.")))
            __M_writer(u'</label></div>\n\t\t\t\t</div>\n')
            pass
        # SOURCE LINE 111
        __M_writer(u'\t\t\t\t\n\t\t\t\t<div id="inviters_panel_tooltip" class="hidden">\n\t\t\t\t\t')
        # SOURCE LINE 113
        __M_writer(escape(_("INVITE_PAGE_TIP_Please invite some friends first!")))
        __M_writer(u'\n\t\t\t\t</div>\t\t\t\t\n\t\t\t\t<div id="inviters_selector_tooltip" class="hidden">\n\t\t\t\t\t<span id="PendingPlaceHolder" class="gift">')
        # SOURCE LINE 116
        __M_writer(escape(_("INVITE_PAGE_TIP_Please chose a Gift Selector First!")))
        __M_writer(u'</span>\n\t\t\t\t</div>\n\t\t\t\t\n\t\t\t\t<a class="submitSmall" id="invite_submitter"><span>')
        # SOURCE LINE 119
        __M_writer(escape(_("INVITE_PAGE_BUTTON_Send Invites")))
        __M_writer(u'</span></a>\n\t\t\t</div>\n\t\t\t</form>\n\t\t</div>\n\t</div>\n\t')
        # SOURCE LINE 124
        __M_writer(escape(html.clearline()))
        __M_writer(u'\n</div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_title(context):
    context.caller_stack._push_frame()
    try:
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 6
        __M_writer(escape(_("INVITE_PAGE_FB_LOGIN_Invite")))
        return ''
    finally:
        context.caller_stack._pop_frame()


