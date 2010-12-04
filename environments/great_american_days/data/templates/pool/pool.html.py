# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1291292196.918334
_template_filename='/home/www-data/ff_dev/friendfund/templates/pool/pool.html'
_template_uri='/pool/pool.html'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='utf-8'
from webhelpers.html import escape
from xml.sax.saxutils import quoteattr
_exports = ['fundchat', 'onloadscripts', 'tooltip_text', 'admin_slogan', 'title', 'render_contributor', 'render_center_buttons', 'social_tools', 'render_product', 'pool_pool_panel', 'fb_meta_tags', 'contributors', 'render_receiver_picture', 'render_contributor_secret', 'page_slogan']


def _mako_get_namespace(context, name):
    try:
        return context.namespaces[(__name__, name)]
    except KeyError:
        _mako_generate_namespaces(context)
        return context.namespaces[(__name__, name)]
def _mako_generate_namespaces(context):
    # SOURCE LINE 4
    ns = runtime.Namespace(u'html', context._clean_inheritance_tokens(), templateuri=u'../widgets/html_elems.html', callables=None, calling_uri=_template_uri, module=None)
    context.namespaces[(__name__, u'html')] = ns

    # SOURCE LINE 5
    ns = runtime.Namespace(u'description', context._clean_inheritance_tokens(), templateuri=u'parts/description.html', callables=None, calling_uri=_template_uri, module=None)
    context.namespaces[(__name__, u'description')] = ns

    # SOURCE LINE 3
    ns = runtime.Namespace(u'links', context._clean_inheritance_tokens(), templateuri=u'../links.html', callables=None, calling_uri=_template_uri, module=None)
    context.namespaces[(__name__, u'links')] = ns

def _mako_inherit(template, context):
    _mako_generate_namespaces(context)
    return runtime._inherit_from(context, u'pool_master.html', _template_uri)
def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'\n\n')
        # SOURCE LINE 3
        __M_writer(u'\n')
        # SOURCE LINE 4
        __M_writer(u'\n')
        # SOURCE LINE 5
        __M_writer(u'\n')
        # SOURCE LINE 6
        __M_writer(u'\n\n')
        # SOURCE LINE 17
        __M_writer(u'\n\n')
        # SOURCE LINE 22
        __M_writer(u'\n\n')
        # SOURCE LINE 96
        __M_writer(u'\n\n\n\n\n\n')
        # SOURCE LINE 105
        __M_writer(u'\n\n')
        # SOURCE LINE 115
        __M_writer(u'\n\n')
        # SOURCE LINE 121
        __M_writer(u'\n\n')
        # SOURCE LINE 159
        __M_writer(u'\n\n')
        # SOURCE LINE 170
        __M_writer(u'\n\n')
        # SOURCE LINE 215
        __M_writer(u'\n\n')
        # SOURCE LINE 227
        __M_writer(u'\n\n')
        # SOURCE LINE 252
        __M_writer(u'\n\n')
        # SOURCE LINE 273
        __M_writer(u'\n\n')
        # SOURCE LINE 284
        __M_writer(u'\n\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_fundchat(context,locals):
    context.caller_stack._push_frame()
    try:
        url = context.get('url', UNDEFINED)
        c = context.get('c', UNDEFINED)
        html = _mako_get_namespace(context, 'html')
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 254
        __M_writer(u'\n\t<div id="lowerbody_container" style="margin: 10px 30px 30px;width:920px;">\n\t\t<div id="lowerbody_content"><a name="comments"></a>\n\t\t\t<h4 class="inside" style="padding:0;">')
        # SOURCE LINE 257
        __M_writer(escape(_("POOL_CHAT_Fund Chat")))
        __M_writer(u'</h4>\n')
        # SOURCE LINE 258
        if c.pool.am_i_member(c.user):
            # SOURCE LINE 259
            __M_writer(u'\t\t\t\t<div>')
            __M_writer(escape(_("POOL_CHAT_Leave your Comment:")))
            __M_writer(u'</div>\n\t\t\t\t<textarea id="addcommenttext" _href="')
            # SOURCE LINE 260
            __M_writer(escape(url(controller='pool', pool_url=c.pool.p_url, action='chat')))
            __M_writer(u'" name="comment" class="comment_text_input"></textarea>\n\t\t\t\t<div class="floaterLeft"><a class="BtnRed" href="#comments" onclick="submit_fundchat(\'addcommenttext\')"><span>')
            # SOURCE LINE 261
            __M_writer(escape(_("POOL_PAGE_BUTTON_Post!")))
            __M_writer(u'</span></a></div>\n\t\t\t\t<div style="clear:both"></div>\n')
            pass
        # SOURCE LINE 264
        if c.pool.can_i_view(c.user):
            # SOURCE LINE 265
            __M_writer(u'\t\t\t\t<div id="fundchat" class="pagelet" pagelet_href="')
            __M_writer(escape(url(controller='pool', pool_url=c.pool.p_url, action='chat')))
            __M_writer(u'">\n\t\t\t\t\t')
            # SOURCE LINE 266
            __M_writer(html.loading_animation())
            __M_writer(u'\n\t\t\t\t</div>\n')
            # SOURCE LINE 268
        else:
            # SOURCE LINE 269
            __M_writer(u'\t\t\t\t')
            __M_writer(escape(_("POOL_CHAT_This is a secret pool, no chat is shown.")))
            __M_writer(u'\n')
            pass
        # SOURCE LINE 271
        __M_writer(u'\t\t</div>\n\t</div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_onloadscripts(context):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        # SOURCE LINE 19
        __M_writer(u'\n\tonLoadPagelets("lowerbody_container");\n\tdojo.query(".popuplink", "pool_pool_panel").onclick(dojo.hitch(null, loadPopup));\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_tooltip_text(context,locals):
    context.caller_stack._push_frame()
    try:
        c = context.get('c', UNDEFINED)
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 161
        __M_writer(u'\n\t<div class="tooltip')
        # SOURCE LINE 162
        __M_writer(escape((c.pool.is_pending() or c.pool.get_total_contribution()==0) and ' withMessage' or ''))
        __M_writer(u'" style="left:')
        __M_writer(escape(locals['progress']))
        __M_writer(u'px;">\n\t\t')
        # SOURCE LINE 163
        __M_writer(locals.get("amount_contributed"))
        __M_writer(u'\n')
        # SOURCE LINE 164
        if c.pool.is_pending():
            # SOURCE LINE 165
            __M_writer(u'\t\t\t')
            __M_writer(_("POOL_PAGE_TOOLTIP_- %(selector_name)s first needs to find a gift before we can start chipping in.") % locals)
            __M_writer(u'\n')
            # SOURCE LINE 166
        elif c.pool.get_total_contribution() == 0:
            # SOURCE LINE 167
            __M_writer(u'\t\t\t')
            __M_writer(_("POOL_PAGE_TOOLTIP_- Be the first among your friends to chip in!"))
            __M_writer(u'\n')
            pass
        # SOURCE LINE 169
        __M_writer(u'\t<span class="bottomYellowTriangle"></span></div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_admin_slogan(context,locals):
    context.caller_stack._push_frame()
    try:
        c = context.get('c', UNDEFINED)
        description = _mako_get_namespace(context, 'description')
        __M_writer = context.writer()
        # SOURCE LINE 102
        __M_writer(u'\n\t<div id="pool_admin_slogan"><div class="slogan">')
        # SOURCE LINE 103
        __M_writer(description.view(c.pool))
        __M_writer(u'</div></div>\n\t<div id="pool_admin_pic"><img src="')
        # SOURCE LINE 104
        __M_writer(escape(c.pool.admin.get_profile_pic()))
        __M_writer(u'"/></div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_title(context):
    context.caller_stack._push_frame()
    try:
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 6
        __M_writer(escape(_("POOL_PAGE__TITLE_Pool")))
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_render_contributor(context,position,invitee,is_admin=False):
    context.caller_stack._push_frame()
    try:
        c = context.get('c', UNDEFINED)
        dict = context.get('dict', UNDEFINED)
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 275
        __M_writer(u'\n\t<div class="contributor">\n\t\t<img src="')
        # SOURCE LINE 277
        __M_writer(escape(invitee.get_profile_pic('PROFILE_M')))
        __M_writer(u'" alt="')
        __M_writer(escape(invitee.name))
        __M_writer(u'" class="contributor"/>\n\t\t<div class="contributor_name">')
        # SOURCE LINE 278
        __M_writer(escape(invitee.name))
        __M_writer(u' ')
        __M_writer(escape(is_admin and _("POOL_PAGE_(Admin)") or ""))
        __M_writer(u'</div>\n')
        # SOURCE LINE 279
        if invitee.contributed_amount:
            # SOURCE LINE 280
            __M_writer(u'\t\t\t<div class="contributor_amount">')
            __M_writer(_("POOL_PAGE_Has chipped in %(amount)s") % dict([("amount", invitee.get_contribution_amount_text(c.pool.product.is_virtual, c.pool.currency))]))
            __M_writer(u'</div>\n\t\t\t<span class="contributor_contributed"></span>\n')
            pass
        # SOURCE LINE 283
        __M_writer(u'\t</div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_render_center_buttons(context,locals):
    context.caller_stack._push_frame()
    try:
        session = context.get('session', UNDEFINED)
        c = context.get('c', UNDEFINED)
        url = context.get('url', UNDEFINED)
        h = context.get('h', UNDEFINED)
        html = _mako_get_namespace(context, 'html')
        app_globals = context.get('app_globals', UNDEFINED)
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 123
        __M_writer(u'\n\t')
        # SOURCE LINE 124
        daysremaining, hoursremaining = c.pool.get_remaining_days_tuple() 
        
        __M_writer(u'\n\t<div id="countdown" class="floaterLeft">\n\t\t<div class="countdown_days">')
        # SOURCE LINE 126
        __M_writer(escape(html.counter(daysremaining, _("POOL_PAGE_days and"))))
        __M_writer(u'</div>\n\t\t<div class="countdown_hours">')
        # SOURCE LINE 127
        __M_writer(escape(html.counter(hoursremaining, _("POOL_PAGE_hours left"))))
        __M_writer(u'</div>\n\t</div>\n\t<div style="clear:both;padding:10px 0 14px;text-align:center">')
        # SOURCE LINE 129
        __M_writer(_("POOL_PAGE_This gift pool closes on %(end_date)s.") % locals)
        __M_writer(u'</div>\n\t\n\t\n')
        # SOURCE LINE 132
        if c.pool.is_pending() and c.pool.am_i_selector(c.user):
            # SOURCE LINE 133
            __M_writer(u'\t\t<a href="')
            __M_writer(escape(url(action="select",pool_url=c.pool.p_url, controller="product")))
            __M_writer(u'" class="buttonRed buttonChipIn extrawide"><span>')
            __M_writer(escape(_("POOL_BUTTON_Select Product now!")))
            __M_writer(u'</span></a>\n')
            # SOURCE LINE 134
        elif c.pool.is_contributable():
            # SOURCE LINE 135
            if c.pool.product.is_virtual:
                # SOURCE LINE 136
                if c.pool.am_i_contributor(c.user):
                    # SOURCE LINE 137
                    __M_writer(u'\t\t\t\t<div class="contributor_chippid_in poolpage_contributor"><div class="content">')
                    __M_writer(_("MYPOOLS_CONTENT_Chipped In"))
                    __M_writer(u'</div></div>\n')
                    # SOURCE LINE 138
                else:
                    # SOURCE LINE 139
                    __M_writer(u'\t\t\t\t<a href="')
                    __M_writer(escape(url('contribution', pool_url=c.pool.p_url, action='virtual')))
                    __M_writer(u'" class="buttonRed buttonChipIn ')
                    __M_writer(escape(session.get('lang', '').lower()))
                    __M_writer(u'"><span>')
                    __M_writer(escape(_("POOL_BUTTON_Chip in!")))
                    __M_writer(u'</span></a>\n\t\t\t\t<a _href="')
                    # SOURCE LINE 140
                    __M_writer(escape(url(controller="content", action="our_virtual_gifts_help")))
                    __M_writer(u'" class="popuplink somelink textCenter"><img src="/static/imgs/currencies/pog_large.png"/> \n\t\t\t\t\t<div style="display: inline;position: relative;top: -10px;">')
                    # SOURCE LINE 141
                    __M_writer(escape(_("CONTRIBUTION_PAGE_Virtual Pot of Gold")))
                    __M_writer(u'(')
                    __M_writer(h.display_currency('POG'))
                    __M_writer(u')</div>\n\t\t\t\t</a>\n')
                    pass
                # SOURCE LINE 144
            else:
                # SOURCE LINE 145
                __M_writer(u'\t\t\t<a href="')
                __M_writer(escape(url('chipin', pool_url=c.pool.p_url, protocol=app_globals.SSL_PROTOCOL)))
                __M_writer(u'" class="buttonRed buttonChipIn ')
                __M_writer(escape(session.get('lang', '').lower()))
                __M_writer(u'"><span>')
                __M_writer(escape(_("POOL_BUTTON_Chip in!")))
                __M_writer(u'</span></a>\n\t\t\t<img src="/static/imgs/icons_paymethod.png"/>\n')
                pass
            # SOURCE LINE 148
        elif c.pool.am_i_admin(c.user) and c.pool.is_funded():
            # SOURCE LINE 149
            __M_writer(u'\t\t<a href="')
            __M_writer(escape(url(controller='pool', pool_url=c.pool.p_url, action='settings')))
            __M_writer(u'" class="buttonRed buttonChipIn extrawide">\n\t\t\t<span>')
            # SOURCE LINE 150
            __M_writer(escape(_("POOL_BUTTON_ACTION_Order Gift")))
            __M_writer(u'</span>\n\t\t</a>\n')
            # SOURCE LINE 152
        elif c.pool.am_i_admin(c.user) and c.pool.is_expired():
            # SOURCE LINE 153
            __M_writer(u'\t\t<a href="')
            __M_writer(escape(url(controller='pool', pool_url=c.pool.p_url, action='settings')))
            __M_writer(u'" class="buttonRed buttonChipIn superextrawide">\n\t\t\t<span>')
            # SOURCE LINE 154
            __M_writer(escape(_("POOL_PAGE_Visit Pool Admin")))
            __M_writer(u'</span>\n\t\t</a>\n')
            # SOURCE LINE 156
        else:
            # SOURCE LINE 157
            __M_writer(u'\t\t<a class="buttonRed buttonChipIn inactive ')
            __M_writer(escape(session.get('lang', '').lower()))
            __M_writer(u'"><span>')
            __M_writer(escape(_("POOL_BUTTON_Chip in!")))
            __M_writer(u'</span></a>\n')
            pass
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_social_tools(context,locals):
    context.caller_stack._push_frame()
    try:
        url = context.get('url', UNDEFINED)
        c = context.get('c', UNDEFINED)
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 217
        __M_writer(u'\n\t<div class="social_tools_free underlined1">\n\t\t\t<iframe src="http://www.facebook.com/plugins/like.php?href=')
        # SOURCE LINE 219
        __M_writer(escape(url.current(protocol="http")))
        __M_writer(u'&amp;layout=standard&amp;show_faces=FALSE&amp;&amp;width=450&amp;action=like&amp;colorscheme=light&amp;height=80" scrolling="no" frameborder="0" style="border:none; overflow:hidden; width:450px; height:35px;" allowTransparency="true"></iframe>\n\t\n')
        # SOURCE LINE 221
        if c.pool.am_i_admin(c.user):
            # SOURCE LINE 222
            __M_writer(u'\t\t<a href="')
            __M_writer(escape(url(controller='pool', pool_url = c.pool.p_url, action='settings')))
            __M_writer(u'" class="submitSmall" id="visit_pool_admin" title="')
            __M_writer(escape(_("POOL_PAGE_Visit Pool Admin")))
            __M_writer(u'">\n\t\t\t<span>')
            # SOURCE LINE 223
            __M_writer(escape(_("POOL_PAGE_Visit Pool Admin")))
            __M_writer(u'</span>\n\t\t</a>\n')
            pass
        # SOURCE LINE 226
        __M_writer(u'\t</div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_render_product(context,locals):
    context.caller_stack._push_frame()
    try:
        c = context.get('c', UNDEFINED)
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 107
        __M_writer(u'\n\t<div class="picture_area product">\n\t\t<img class="contentPic" src="')
        # SOURCE LINE 109
        __M_writer(escape(c.pool.product.get_product_pic()))
        __M_writer(u'"/>\n\t\t<div class="subtext">')
        # SOURCE LINE 110
        __M_writer(c.pool.product.get_display_label(words = 2, seperator = '<br/>'))
        __M_writer(u'</div>\n')
        # SOURCE LINE 111
        if c.pool.product.tracking_link:
            # SOURCE LINE 112
            __M_writer(u'\t\t\t<a class="submitExtraMini product_more" href="')
            __M_writer(escape(c.pool.product.tracking_link))
            __M_writer(u'" target="_blank">')
            __M_writer(escape(_("POOL_PAGE_more...")))
            __M_writer(u'<span></span></a>\n')
            pass
        # SOURCE LINE 114
        __M_writer(u'\t</div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_pool_pool_panel(context,locals):
    context.caller_stack._push_frame()
    try:
        url = context.get('url', UNDEFINED)
        h = context.get('h', UNDEFINED)
        c = context.get('c', UNDEFINED)
        self = context.get('self', UNDEFINED)
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 172
        __M_writer(u'\n\t')
        # SOURCE LINE 173
 
        if c.pool.is_pending():
                progress = 0
        else:
                progress = (850 * (c.pool.get_total_contrib_float() / c.pool.product.get_price_float())) 
                
        
        # SOURCE LINE 178
        __M_writer(u'\n\n\t<div id="pool_pool_panel" class="innerbody">\n\t\t<div class="pool_content">\n\t\t\t<div class="picture_area_outer product">\n\t\t\t\t')
        # SOURCE LINE 183
        __M_writer(escape(self.render_product(locals)))
        __M_writer(u'\n\t\t\t\t<span class="icon"></span>\n\t\t\t</div>\n\t\t\t<div class="picture_area_outer receiver_picture">\n\t\t\t\t')
        # SOURCE LINE 187
        __M_writer(escape(self.render_receiver_picture(locals)))
        __M_writer(u'\n\t\t\t\t<span class="icon"></span>\n\t\t\t</div>\n\t\t\t<div class="floaterLeft" style="text-align:center;width:412px;">\n\t\t\t\t')
        # SOURCE LINE 191
        __M_writer(escape(self.render_center_buttons(locals)))
        __M_writer(u'\n\t\t\t</div>\n\t\t</div>\n\t\t<div id="timeline_bar">\n\t\t\t\t<div class="timeline">\n\t\t\t\t\t\n\t\t\t\t\t<div class="floaterRight limit">\n')
        # SOURCE LINE 198
        if not c.pool.is_pending():
            # SOURCE LINE 199
            __M_writer(u'\t\t\t\t\t\t\t')
            __M_writer(h.format_currency(c.pool.product.get_price_float(), c.pool.product.currency))
            __M_writer(u'\n')
            # SOURCE LINE 200
        else:
            # SOURCE LINE 201
            __M_writer(u'\t\t\t\t\t\t\t???\n')
            pass
        # SOURCE LINE 203
        __M_writer(u'\t\t\t\t\t</div>\n\t\t\t\t\t<div class="floaterLeft limit">')
        # SOURCE LINE 204
        __M_writer(h.format_currency(0, c.pool.currency))
        __M_writer(u'</div>\n\t\t\t\t\t\n\t\t\t\t\t<div class="timeline_progressbar_bg"><div style="width: ')
        # SOURCE LINE 206
        __M_writer(escape(locals['progress']))
        __M_writer(u'px;" class="timeline_progressbar"></div>\n\t\t\t\t\t')
        # SOURCE LINE 207
        __M_writer(self.tooltip_text(locals))
        __M_writer(u'\n\t\t\t\t\t</div>\n\t\t\t\t\t\n\t\t\t\t\t<div class="legende floaterRight"><a href="#" _href="')
        # SOURCE LINE 210
        __M_writer(escape(url(controller='content', action='pool_too_little_money')))
        __M_writer(u'" class="popuplink">')
        __M_writer(escape(_("POOL_PAGE_What happens if we raise less money?")))
        __M_writer(u'</a></div>\n\t\t\t\t\t<div class="legende floaterLeft">')
        # SOURCE LINE 211
        __M_writer((_("POOL_PAGE_<b>%(amount_contributed)s</b> has been contributed sofar. Only <b>%(amount_left)s to go</b> before %(end_date)s!") % locals))
        __M_writer(u'</div>\n\t\t\t\t</div>\n\t\t</div>\n\t</div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_fb_meta_tags(context):
    context.caller_stack._push_frame()
    try:
        url = context.get('url', UNDEFINED)
        c = context.get('c', UNDEFINED)
        app_globals = context.get('app_globals', UNDEFINED)
        dict = context.get('dict', UNDEFINED)
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 8
        __M_writer(u'\n\t<link rel="image_src" href="')
        # SOURCE LINE 9
        __M_writer(escape(app_globals.SITE_ROOT_URL))
        __M_writer(escape(c.pool.get_pool_picture_tiles("MYPOOLS")))
        __M_writer(u'" />\n\t<meta property="og:title" content="')
        # SOURCE LINE 10
        __M_writer(escape(_("POOL_PAGE_Gift Pool for %(receiver)s") % dict([("receiver",c.pool.receiver.name)])))
        __M_writer(u'" />\n\t<meta property="og:image" content="')
        # SOURCE LINE 11
        __M_writer(escape(app_globals.SITE_ROOT_URL))
        __M_writer(escape(c.pool.get_pool_picture_tiles("MYPOOLS")))
        __M_writer(u'" />\n\t<meta property="og:description" content="')
        # SOURCE LINE 12
        __M_writer(escape(c.pool.description))
        __M_writer(u'" />\n\t<meta property="og:type" content="product"/>\n\t<meta property="og:url" content="')
        # SOURCE LINE 14
        __M_writer(escape(url.current(protocol="http")))
        __M_writer(u'"/>\n\t<meta property="og:site_name" content="Friendfund"/>\n\t<meta property="fb:app_id" content="')
        # SOURCE LINE 16
        __M_writer(escape(app_globals.FbAppID))
        __M_writer(u'"/>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_contributors(context,locals):
    context.caller_stack._push_frame()
    try:
        c = context.get('c', UNDEFINED)
        url = context.get('url', UNDEFINED)
        self = context.get('self', UNDEFINED)
        enumerate = context.get('enumerate', UNDEFINED)
        ungettext = context.get('ungettext', UNDEFINED)
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 229
        __M_writer(u'\n\t')
        # SOURCE LINE 230
        contributors_text = ungettext("POOL_PAGE_%(number_contributors)d person has chipped in for %(receiver_name)s's gift.",
                                                                                "POOL_PAGE_%(number_contributors)d people have chipped in for %(receiver_name)s's gift.", locals['number_contributors']) 
        
        # SOURCE LINE 231
        __M_writer(u'\n\n\t<h4 class="inside" style="padding:0px 30px;">')
        # SOURCE LINE 233
        __M_writer(escape(_("POOL_PAGE_Contributors")))
        __M_writer(u'\n')
        # SOURCE LINE 234
        if c.pool.am_i_member(c.user):
            # SOURCE LINE 235
            __M_writer(u'\t\t<div class="floaterRight">\n\t\t\t<a class="loginlink" href="')
            # SOURCE LINE 236
            __M_writer(escape(url('invite_index', controller='invite', pool_url=c.pool.p_url)))
            __M_writer(u'">')
            __M_writer(escape(_("POOL_BUTTON_Invite more Friends to this pool")))
            __M_writer(u' <img src="/static/imgs/icon_fb_connect.png"/><img src="/static/imgs/icon_tw_connect.png"/><img src="/static/imgs/icon_mail.png"/></a>\n\t\t</div>\n')
            pass
        # SOURCE LINE 239
        __M_writer(u'\t</h4>\n\t<div class="vertNoPadding">')
        # SOURCE LINE 240
        __M_writer(escape(contributors_text % locals))
        __M_writer(u'</div>\n\n\t<div id="pool_contributors" class="pcont_body">\n\t\t')
        # SOURCE LINE 243
        invitees = [c.pool.admin] + c.pool.invitees 
        
        __M_writer(u'\n')
        # SOURCE LINE 244
        for i, invitee in enumerate(invitees):
            # SOURCE LINE 245
            if invitee.anonymous:
                # SOURCE LINE 246
                __M_writer(u'\t\t\t\t')
                __M_writer(escape(self.render_contributor_secret(i, invitee)))
                __M_writer(u'\n')
                # SOURCE LINE 247
            else:
                # SOURCE LINE 248
                __M_writer(u'\t\t\t\t')
                __M_writer(escape(self.render_contributor(i, invitee, i==0)))
                __M_writer(u'\n')
                pass
            pass
        # SOURCE LINE 251
        __M_writer(u'\t</div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_render_receiver_picture(context,locals):
    context.caller_stack._push_frame()
    try:
        c = context.get('c', UNDEFINED)
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 117
        __M_writer(u'\n\t<div class="picture_area receiver_picture">\n\t\t<img class="contentPic" src="')
        # SOURCE LINE 119
        __M_writer(escape(c.pool.receiver.get_profile_pic('POOL')))
        __M_writer(u'"/><div class="subtext">')
        __M_writer(_("POOL_PAGE_Help make %(receiver_first_name)s's day!") % locals )
        __M_writer(u'</div>\n\t</div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_render_contributor_secret(context,position,invitee,is_admin=False):
    context.caller_stack._push_frame()
    try:
        c = context.get('c', UNDEFINED)
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 286
        __M_writer(u'\n\t<div class="contributor">\n\t\t<img src="/static/imgs/defaultcontrib_')
        # SOURCE LINE 288
        __M_writer(escape(invitee.sex))
        __M_writer(u'_PROFILE_M.png" class="contributor"/>\n')
        # SOURCE LINE 289
        if c.user.is_anon:
            # SOURCE LINE 290
            __M_writer(u'\t\t\t<div class="contributor_name">')
            __M_writer(escape(_("POOL_CHAT_Someone you might know")))
            __M_writer(u'</div>\n')
            # SOURCE LINE 291
        else:
            # SOURCE LINE 292
            __M_writer(u'\t\t\t<div class="contributor_name">')
            __M_writer(escape(_("POOL_CHAT_Anonymous")))
            __M_writer(u'</div>\n')
            pass
        # SOURCE LINE 294
        __M_writer(u'\t\t<div class="contributor_amount">')
        __M_writer(invitee.get_contribution_amount_text(c.pool.product.is_virtual, c.pool.currency))
        __M_writer(u'</div>\n\t</div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_page_slogan(context):
    context.caller_stack._push_frame()
    try:
        c = context.get('c', UNDEFINED)
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 24
        __M_writer(u'\n\t')
        # SOURCE LINE 25
        
        locals = {'user_name':(c.user.name and "<span class=\"emphasis\">%s!</span>"%c.user.name) or (c.pool.suspect and "<span class=\"emphasis\">%s!</span>"%c.pool.suspect.name) or "", 
                        'receiver_name':c.pool.receiver.name, 
                        'occasion_name': c.pool.occasion.get_display_name(), 
                        'admin_name':c.pool.admin.name, 
                        'product_name':c.pool.product.get_display_name()}
        if c.pool.is_pending():
                locals['progress'] = 0
                locals["selector_name"] = c.pool.selector and c.pool.selector.name or _("POOL_PAGE_SELECTOR_Someone")
        else:
                locals['progress'] = (850 * (c.pool.get_total_contrib_float() / c.pool.product.get_price_float())) 
                
        
        # SOURCE LINE 36
        __M_writer(u'\n')
        # SOURCE LINE 37
        if c.pool.is_funded():
            # SOURCE LINE 38
            if c.pool.am_i_admin(c.user):
                # SOURCE LINE 39
                __M_writer(u'\t\t\t<div id="page_slogan" class="underlined2">\n\t\t\t\t')
                # SOURCE LINE 40
                __M_writer(_("POOL_PAGE_SLOGAN_Hi, %(user_name)s!<br/>Congratulations, this pool is now fully funded!") % locals)
                __M_writer(u'\n\t\t\t</div>\n\t\t\t<div class="vertHalfPadding">')
                # SOURCE LINE 42
                __M_writer(_("POOL_PAGE_SLOGAN_All you need to do now is visit the Pool Admin Page to order your gift.") % locals)
                __M_writer(u'</div>\n')
                # SOURCE LINE 43
            else:
                # SOURCE LINE 44
                __M_writer(u'\t\t\t<div id="page_slogan" class="underlined2">\n\t\t\t\t')
                # SOURCE LINE 45
                __M_writer(_("POOL_PAGE_SLOGAN_SO this pool is now fully funded and we are just waiting for %(admin_name)s to give us a shipping address and order the gift.") % locals)
                __M_writer(u'\n\t\t\t</div>\n\t\t\t<div class="vertHalfPadding">')
                # SOURCE LINE 47
                __M_writer(_("POOL_PAGE_SLOGAN_%(admin_name)s has been notified and should be ordering the gift soon.") % locals)
                __M_writer(u'</div>\n')
                pass
            # SOURCE LINE 49
        elif c.pool.is_expired():
            # SOURCE LINE 50
            if c.pool.am_i_admin(c.user):
                # SOURCE LINE 51
                __M_writer(u'\t\t\t<div id="page_slogan" class="underlined2">\n\t\t\t\t')
                # SOURCE LINE 52
                __M_writer(_("POOL_PAGE_SLOGAN_Hi, %(user_name)s!<br/>Oh no! This pool has expired without reaching its goal.") % locals)
                __M_writer(u'\n\t\t\t</div>\n\t\t\t<div class="vertHalfPadding">')
                # SOURCE LINE 54
                __M_writer(_("POOL_PAGE_SLOGAN_Visit the Pool Admin Page to extend the deadline or remind your friends to chip in. ") % locals)
                __M_writer(u'</div>\n')
                # SOURCE LINE 55
            else:
                # SOURCE LINE 56
                __M_writer(u'\t\t\t<div id="page_slogan" class="underlined2">\n\t\t\t\t')
                # SOURCE LINE 57
                __M_writer(_("POOL_PAGE_SLOGAN_Hi, %(user_name)s<br/>Oh no! This pool has expired without reaching its goal.") % locals)
                __M_writer(u'\n\t\t\t</div>\n\t\t\t<div class="vertHalfPadding">')
                # SOURCE LINE 59
                __M_writer(_("POOL_PAGE_SLOGAN_It's now up to %(admin_name)s to extend the deadline so %(receiver_name)s can get a %(product_name)s.") % locals)
                __M_writer(u'</div>\n')
                pass
            # SOURCE LINE 61
        elif not c.pool.is_pending():
            # SOURCE LINE 62
            if c.user.is_anon:
                # SOURCE LINE 63
                __M_writer(u'\t\t\t<div id="page_slogan" class="underlined2">\n\t\t\t\t')
                # SOURCE LINE 64
                __M_writer(_("POOL_PAGE_SLOGAN_Hi, %(user_name)s<br/>%(admin_name)s has created a gift pool for %(receiver_name)s's %(occasion_name)s gift, log in and help out!") % locals)
                __M_writer(u'\n\t\t\t</div>\n\t\t\t<div class="vertHalfPadding">')
                # SOURCE LINE 66
                __M_writer(_("POOL_PAGE_SLOGAN_Please log in to chip in for %(receiver_name)s's %(occasion_name)s gift.") % locals)
                __M_writer(u'</div>\n')
                # SOURCE LINE 67
            elif c.pool.am_i_admin(c.user):
                # SOURCE LINE 68
                __M_writer(u'\t\t\t<div id="page_slogan" class="underlined2">\n\t\t\t\t')
                # SOURCE LINE 69
                __M_writer(_("POOL_PAGE_SLOGAN_Hi, %(user_name)s<br/>You have created a pool for %(receiver_name)s's %(occasion_name)s gift.") % locals)
                __M_writer(u'\n\t\t\t</div>\n\t\t\t<div class="vertHalfPadding">')
                # SOURCE LINE 71
                __M_writer(_("POOL_PAGE_SLOGAN_Edit pool settings any time by visiting the Pool Admin page.") % locals)
                __M_writer(u'</div>\n')
                # SOURCE LINE 72
            elif c.pool.am_i_member(c.user):
                # SOURCE LINE 73
                __M_writer(u'\t\t\t<div id="page_slogan" class="underlined2">\n\t\t\t\t')
                # SOURCE LINE 74
                __M_writer(_("POOL_PAGE_SLOGAN_Hi, %(user_name)s<br/>You've been invited to chip in for %(receiver_name)s's %(occasion_name)s gift.") % locals)
                __M_writer(u'\n\t\t\t</div>\n\t\t\t<div class="vertHalfPadding">')
                # SOURCE LINE 76
                __M_writer(_("POOL_PAGE_SLOGAN_%(admin_name)s wants to get a %(product_name)s for %(receiver_name)s's %(occasion_name)s and they want you to contribute what you can.") % locals)
                __M_writer(u'</div>\n')
                # SOURCE LINE 77
            else:
                # SOURCE LINE 78
                __M_writer(u'\t\t\t<div id="page_slogan" class="underlined2">\n\t\t\t\t')
                # SOURCE LINE 79
                __M_writer(_("POOL_PAGE_SLOGAN_Hi, %(user_name)s<br/>%(admin_name)s has created a gift pool for %(receiver_name)s's %(occasion_name)s gift, chip in and join the pool.") % locals)
                __M_writer(u'\n\t\t\t</div>\n\t\t\t<div class="vertHalfPadding">')
                # SOURCE LINE 81
                __M_writer(_("POOL_PAGE_SLOGAN_Chip in and help %(receiver_name)s get a %(product_name)s for %(occasion_name)s.") % locals)
                __M_writer(u'</div>\n')
                pass
            # SOURCE LINE 83
        else:
            # SOURCE LINE 84
            if c.pool.am_i_selector(c.user):
                # SOURCE LINE 85
                __M_writer(u'\t\t\t<div id="page_slogan" class="underlined2">\n\t\t\t\t')
                # SOURCE LINE 86
                __M_writer(_("POOL_PAGE_SLOGAN_Hi, %(user_name)s<br/>%(admin_name)s has nominated <em>you</em> to choose %(receiver_name)s's gift.") % locals)
                __M_writer(u'\n\t\t\t</div>\n\t\t\t<div class="vertHalfPadding">')
                # SOURCE LINE 88
                __M_writer(_("POOL_PAGE_SLOGAN_Please click 'Choose Gift' below and find the perfect gift.") % locals)
                __M_writer(u'</div>\n')
                # SOURCE LINE 89
            else:
                # SOURCE LINE 90
                __M_writer(u'\t\t\t<div id="page_slogan" class="underlined2">\n\t\t\t\t')
                # SOURCE LINE 91
                __M_writer(_("POOL_PAGE_SLOGAN_Hi, %(user_name)s<br/>%(admin_name)s has nominated <em>%(selector_name)s</em> to choose %(receiver_name)s's gift.") % locals)
                __M_writer(u'\n\t\t\t</div>\n\t\t\t<div class="vertHalfPadding">')
                # SOURCE LINE 93
                __M_writer(_("POOL_PAGE_SLOGAN_This pool is waiting for %(selector_name)s to select a gift, chipping in will be possible after they have chosen the perfect gift!") % locals)
                __M_writer(u'</div>\n')
                pass
            pass
        return ''
    finally:
        context.caller_stack._pop_frame()


