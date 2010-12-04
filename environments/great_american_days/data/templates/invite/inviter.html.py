# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1291205917.2129159
_template_filename=u'/home/www-data/ff_dev/friendfund/templates/invite/inviter.html'
_template_uri=u'/receiver/../invite/inviter.html'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='utf-8'
from webhelpers.html import escape
from xml.sax.saxutils import quoteattr
_exports = ['mailinviter', 'networkinviter', 'render_email_friends', 'render_network_friends']


# SOURCE LINE 1

import md5


def _mako_get_namespace(context, name):
    try:
        return context.namespaces[(__name__, name)]
    except KeyError:
        _mako_generate_namespaces(context)
        return context.namespaces[(__name__, name)]
def _mako_generate_namespaces(context):
    # SOURCE LINE 5
    ns = runtime.Namespace(u'forms', context._clean_inheritance_tokens(), templateuri=u'../widgets/forms.html', callables=None, calling_uri=_template_uri, module=None)
    context.namespaces[(__name__, u'forms')] = ns

    # SOURCE LINE 4
    ns = runtime.Namespace(u'html', context._clean_inheritance_tokens(), templateuri=u'../widgets/html_elems.html', callables=None, calling_uri=_template_uri, module=None)
    context.namespaces[(__name__, u'html')] = ns

def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        c = context.get('c', UNDEFINED)
        def networkinviter(network_name,friends,mutuals,with_pending=False):
            return render_networkinviter(context.locals_(__M_locals),network_name,friends,mutuals,with_pending)
        def mailinviter(with_pending=False):
            return render_mailinviter(context.locals_(__M_locals),with_pending)
        __M_writer = context.writer()
        # SOURCE LINE 3
        __M_writer(u'\n')
        # SOURCE LINE 4
        __M_writer(u'\n')
        # SOURCE LINE 5
        __M_writer(u'\n\n\n')
        # SOURCE LINE 8
        if c.method == 'facebook':
            # SOURCE LINE 9
            __M_writer(u'\t')
            __M_writer(escape(networkinviter("facebook", c.friends, True, with_pending = c.pool.require_pselector)))
            __M_writer(u'\n')
            # SOURCE LINE 10
        elif c.method == 'twitter':
            # SOURCE LINE 11
            __M_writer(u'\t')
            __M_writer(escape(networkinviter("twitter", c.friends, False, with_pending = c.pool.require_pselector)))
            __M_writer(u'\n')
            # SOURCE LINE 12
        elif c.method == 'email':
            # SOURCE LINE 13
            __M_writer(u'\t')
            __M_writer(escape(mailinviter(with_pending = c.pool.require_pselector)))
            __M_writer(u'\n')
            pass
        # SOURCE LINE 15
        __M_writer(u'\n')
        # SOURCE LINE 36
        __M_writer(u'\n\n')
        # SOURCE LINE 73
        __M_writer(u'\n\n\n\n\n\n')
        # SOURCE LINE 117
        __M_writer(u'\n\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_mailinviter(context,with_pending=False):
    context.caller_stack._push_frame()
    try:
        html = _mako_get_namespace(context, 'html')
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 79
        __M_writer(u'\n\t<div id="inviteheader">\n\t\t')
        # SOURCE LINE 81
        __M_writer(escape(html.clearline()))
        __M_writer(u'\n\t\t<div class="headline">\n\t\t\tSelect Friend from:\n\t\t\t<img src="/static/imgs/button_mail_gmail.png" class="networkicon" alt="GMail" />\n\t\t\t<img src="/static/imgs/button_mail_yahoo.png" class="networkicon" alt="Yahho Mail" />\n\t\t</div>\n\t\t')
        # SOURCE LINE 87
        __M_writer(escape(html.clearline()))
        __M_writer(u'\n\t\t<form action="" method="POST" id="emailinviter">\n\t\t\t<div id="inviter_name" class="input_field">\n\t\t\t<div class="label">\n\t\t\t\t<label for "email_networkname">')
        # SOURCE LINE 91
        __M_writer(escape(_("INVITE_PAGE_LABEL_Name of your friend:")))
        __M_writer(u'</label>\n\t\t\t</div>\n\t\t\t<input type="text" id="email_networkname" name="invitee.name" value=""/>\n\t\t\t</div>\n\t\t\t\n\t\t\t<div id="inviter_email" class="input_field">\n\t\t\t<div class="label">\n\t\t\t<label for "email_email">')
        # SOURCE LINE 98
        __M_writer(escape(_("INVITE_PAGE_LABEL_Email address of your friend:")))
        __M_writer(u'</label>\n\t\t\t</div>\n\t\t\t<input type="text" id="email_email" name="invitee.network_id" value=""/>\n\t\t\t\t<span id="email_inviter_error"></span>\n\t\t\t</div>\n\t\t\t<br/>\n\t\t\t<input type="hidden" name="invitee.network" value="email"/>\n\t\t\t<input type="hidden" name="invitee.with_pending" value="')
        # SOURCE LINE 105
        __M_writer(escape(with_pending and "1" or ""))
        __M_writer(u'"/>\n\t\t\t<input type="hidden" name="invitee.notification_method" value="email"/>\n\t\t\t\n\t\t\t<div style="float: right; margin:0px 50px 0px;position: relative;">\n\t\t\t\t<a class="submitSmall selector" id="emailsubmitter" _imgurl="/static/imgs/default_m.png"><span>')
        # SOURCE LINE 109
        __M_writer(escape(_("INVITE_PAGE_LABEL_Submit")))
        __M_writer(u'</span></a>\n\t\t\t</div>\n\t\t</form>\n\t')
        # SOURCE LINE 112
        __M_writer(escape(html.clearline(20)))
        __M_writer(u'\n\t</div>\n\t<div id="friend_list" class="emailpopup">\n\t\t\n\t</div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_networkinviter(context,network_name,friends,mutuals,with_pending=False):
    context.caller_stack._push_frame()
    try:
        forms = _mako_get_namespace(context, 'forms')
        c = context.get('c', UNDEFINED)
        _ = context.get('_', UNDEFINED)
        def render_network_friends(friends,active=True,mutuals=False,show_birthdays=False,with_pending=False,add_label=None,rem_label=None):
            return render_render_network_friends(context,friends,active,mutuals,show_birthdays,with_pending,add_label,rem_label)
        __M_writer = context.writer()
        # SOURCE LINE 16
        __M_writer(u'\n\t<div id="networkinviter_')
        # SOURCE LINE 17
        __M_writer(escape(network_name))
        __M_writer(u'">\n\t<div id="inviteheader" class="inviteelist ')
        # SOURCE LINE 18
        __M_writer(escape(network_name))
        __M_writer(u'">\n')
        # SOURCE LINE 19
        if mutuals:
            # SOURCE LINE 20
            __M_writer(u'\t\t\t<div class="mutual_toggle_container">\n\t\t\t\t<input type="checkbox" id="toggle_mutuals" checked="checked"/>\n\t\t\t\t<label for="toggle_mutuals">')
            # SOURCE LINE 22
            __M_writer(escape(_("INVITE_PAGE_Only Mutual Friends")))
            __M_writer(u'</label>\n\t\t\t</div>\n')
            pass
        # SOURCE LINE 25
        __M_writer(u'\t\t<div style="float: left;">\n\t\t')
        # SOURCE LINE 26
        __M_writer(escape(forms.black_input_text("fb_filter", "fb_filter", label="", default=_("INVITE_PAGE_LABEL_Search friends ..."), width=175)))
        __M_writer(u'\n\t\t</div>\n\t\t<a class="submitMini" id="inviteall">')
        # SOURCE LINE 28
        __M_writer(escape(_("INVITE_PAGE_LABEL_Invite All")))
        __M_writer(u'<span></span></a>\n\t</div>\n\n\t<div id="friend_list" class="inviteelist ')
        # SOURCE LINE 31
        __M_writer(escape(network_name))
        __M_writer(u'">\n\t\t')
        # SOURCE LINE 32
        __M_writer(render_network_friends(friends, mutuals = mutuals, with_pending=with_pending))
        __M_writer(u'\n\t\t')
        # SOURCE LINE 33
        __M_writer(render_network_friends(c.already_invited, active=False, mutuals = mutuals, with_pending=with_pending))
        __M_writer(u'\n\t</div>\n\t</div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_render_email_friends(context,friends,active=True,class_='selectable',with_pending=False,add_label=None,rem_label=None):
    context.caller_stack._push_frame()
    try:
        h = context.get('h', UNDEFINED)
        _ = context.get('_', UNDEFINED)
        enumerate = context.get('enumerate', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 119
        __M_writer(u'\n')
        # SOURCE LINE 120
        for i,(id, user_data) in enumerate(friends.items()):
            # SOURCE LINE 121
            __M_writer(u'\t<div class="invitee_row ')
            __M_writer(escape(class_))
            __M_writer(u'" id="email_')
            __M_writer(escape( md5.new(id).hexdigest() ))
            __M_writer(u'"\n')
            # SOURCE LINE 122
            if active:
                # SOURCE LINE 123
                __M_writer(u'\t\t\t\tpos="i" ')
                __M_writer(h.attrib_keys(user_data))
                __M_writer(u'\n')
                pass
            # SOURCE LINE 125
            __M_writer(u'\t\t>\n')
            # SOURCE LINE 126
            if active:
                # SOURCE LINE 127
                __M_writer(u'\t\t\t<a class="selector invite" title="')
                __M_writer(escape(user_data['name']))
                __M_writer(u'">')
                __M_writer(add_label or _("INVITE_LABEL_Invite"))
                __M_writer(u'<span class="selector invite"></span></a>\n\t\t\t<a class="selector remove" title="')
                # SOURCE LINE 128
                __M_writer(escape(user_data['name']))
                __M_writer(u'">')
                __M_writer(rem_label or _("INVITE_LABEL_Remove"))
                __M_writer(u'<span class="selector remove"></span></a>\n')
                # SOURCE LINE 129
                if user_data['with_pending'] or with_pending:
                    # SOURCE LINE 130
                    __M_writer(u'\t\t\t\t<a class="pending" title="')
                    __M_writer(escape(_("PENDINGPRODUCT_SELECTOR")))
                    __M_writer(u'">&nbsp;</a>\n')
                    pass
                pass
            # SOURCE LINE 133
            __M_writer(u'\t\t<img src="')
            __M_writer(escape(user_data['profile_picture_url']))
            __M_writer(u'" class="fbprofilepic">\n\t\t<span class="label">')
            # SOURCE LINE 134
            __M_writer(escape(user_data['name']))
            __M_writer(u'<br/>')
            __M_writer(escape(id))
            __M_writer(u'</span>\n\t</div>\n')
            pass
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_render_network_friends(context,friends,active=True,mutuals=False,show_birthdays=False,with_pending=False,add_label=None,rem_label=None):
    context.caller_stack._push_frame()
    try:
        h = context.get('h', UNDEFINED)
        _ = context.get('_', UNDEFINED)
        enumerate = context.get('enumerate', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 38
        __M_writer(u'\n')
        # SOURCE LINE 39
        for i,(id, user_data) in enumerate(friends.iteritems()):
            # SOURCE LINE 40
            __M_writer(u'\t')

            if "mutual_with" in user_data:
                    mutual_class = "mutual"
            elif mutuals:
                    mutual_class = "nonmutual hidden"
            else:
                    mutual_class = "nonmutual"
                    
            
            # SOURCE LINE 47
            __M_writer(u'\n\t<div class="invitee_row ')
            # SOURCE LINE 48
            __M_writer(escape(active and 'selectable' or 'selected'))
            __M_writer(u' ')
            __M_writer(escape(mutual_class))
            __M_writer(u'" id="')
            __M_writer(escape(user_data['network']))
            __M_writer(u'_')
            __M_writer(escape(id))
            __M_writer(u'"\n')
            # SOURCE LINE 49
            if active:
                # SOURCE LINE 50
                __M_writer(u'\t\t\t\tpos="')
                __M_writer(escape(i))
                __M_writer(u'" ')
                __M_writer(h.attrib_keys(user_data))
                __M_writer(u'\n')
                pass
            # SOURCE LINE 52
            __M_writer(u'\t\t>\n\t\t<img src="')
            # SOURCE LINE 53
            __M_writer(escape(user_data['profile_picture_url']))
            __M_writer(u'" class="fbprofilepic" alt="')
            __M_writer(escape(user_data['name']))
            __M_writer(u'"/>\n\t\t<span class="label"><b>')
            # SOURCE LINE 54
            __M_writer(escape(user_data['name']))
            __M_writer(u'</b>\n')
            # SOURCE LINE 55
            if show_birthdays and 'dob' in user_data:
                # SOURCE LINE 56
                __M_writer(u'\t\t\t')
                user_data["dob_fmt"] = h.format_short_date(user_data["dob"]) 
                
                __M_writer(u'\n\t\t\t<div class="birthdaylabel">')
                # SOURCE LINE 57
                __M_writer((_("RECEIVER_BIRTHDAY_LABEL_Birthday: %(dob_fmt)s")%user_data))
                __M_writer(u'\n')
                # SOURCE LINE 58
                if user_data['dob_difference'] < 60:
                    # SOURCE LINE 59
                    __M_writer(u'\t\t\t\t<div>')
                    __M_writer((_("RECEIVER_BIRTHDAY_LABEL_%(dob_difference)s days to go")%user_data))
                    __M_writer(u'</div>\n')
                    pass
                # SOURCE LINE 61
                __M_writer(u'\t\t\t</div>\n')
                pass
            # SOURCE LINE 63
            __M_writer(u'\t\t</span>\n')
            # SOURCE LINE 64
            if active:
                # SOURCE LINE 65
                __M_writer(u'\t\t\t<a class="selector invite" title="')
                __M_writer(escape(user_data['name']))
                __M_writer(u'">')
                __M_writer(add_label or _("INVITE_LABEL_Invite"))
                __M_writer(u'<span class="selector invite"></span></a>\n\t\t\t<a class="selector remove" title="')
                # SOURCE LINE 66
                __M_writer(escape(user_data['name']))
                __M_writer(u'">')
                __M_writer(rem_label or _("INVITE_LABEL_Remove"))
                __M_writer(u'<span class="selector remove"></span></a>\n')
                # SOURCE LINE 67
                if with_pending:
                    # SOURCE LINE 68
                    __M_writer(u'\t\t\t\t<a class="pending" title="')
                    __M_writer(escape(_("PENDINGPRODUCT_SELECTOR")))
                    __M_writer(u'">&nbsp;</a>\n')
                    pass
                pass
            # SOURCE LINE 71
            __M_writer(u'\t</div>\n')
            pass
        return ''
    finally:
        context.caller_stack._pop_frame()


