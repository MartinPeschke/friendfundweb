# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1291204359.23053
_template_filename=u'/home/www-data/ff_dev/friendfund/templates/messages/blocks.html'
_template_uri=u'/messages/blocks.html'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='utf-8'
from webhelpers.html import escape
from xml.sax.saxutils import quoteattr
_exports = []


def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        url = context.get('url', UNDEFINED)
        getattr = context.get('getattr', UNDEFINED)
        app_globals = context.get('app_globals', UNDEFINED)
        c = context.get('c', UNDEFINED)
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1

        blocks = getattr(c, 'blocks', False)
        
        if getattr(c, 'page', None) == 'contrib':
                HEADER_MSG = _("CONTRIB_CONTRIB_PERMISSIONS_POPUP_We need some additional Permissions!")
                SUBHEADER = _("CONTRIB_PERMISSIONS_POPUP_To keep your friends apprised of your funding efforts, we need some additional permissions as listed below!")
                
                EMAIL_TITLE = _("CONTRIB_PERMISSIONS_POPUP_TITLE_Your Email")
                EMAIL_INTRO = _("CONTRIB_PERMISSIONS_POPUP_To be able to give you personal notices for pool events, we require email addresses of any person that invites their friends.")
                EMAIL_LABEL = _("CONTRIB_PERMISSIONS_POPUP_Enter  Email:")
                EMAIL_FB = _("CONTRIB_PERMISSIONS_POPUP_Grant Facebook Email")
                
                STREAM_PUBLISH_TITLE = _("CONTRIB_PERMISSIONS_POPUP_TITLE_Your Facebook Stream Publish Permission")
                STREAM_PUBLISH_INTRO = _("CONTRIB_PERMISSIONS_POPUP_In you are inviting friends from facebook, we do require Stream Publish to send out your invite messages bearing your personal notice.")
                STREAM_PUBLISH = _("CONTRIB_PERMISSIONS_POPUP_Grant Stream Publish")
                
                CREATE_EVENT_TITLE = _("INVITE_PERMISSIONS_POPUP_TITLE_Your Facebook Create Event Permission")
                CREATE_EVENT_INTRO = _("INVITE_PERMISSIONS_POPUP_Because you're not yet invited, we want to invite you to this pool and the associated Facebook event. To do this we need your create event persmission. We will not create events in your name, without your approval to do so, ever!")
                CREATE_EVENT = _("INVITE_PERMISSIONS_POPUP_Grant Create Event")
                GRANT_BOTH_INTRO = _("CONTRIB_PERMISSIONS_POPUP_Or simply grant both in one go!")
                GRANT_BOTH = _("CONTRIB_PERMISSIONS_POPUP_Grant Both!")
                SKIPTHISLINK = _("CONTRIB_PERMISSIONS_POPUP_Of course you can skip granting, by not inviting any one.")
                SKIPABLE = False
        else:
                HEADER_MSG = _("INVITE_PERMISSIONS_POPUP_Almost there!")
                SUBHEADER = _("INVITE_PERMISSIONS_POPUP_To keep your friends up to date with your gift pool, we'll need:")
                EMAIL_TITLE = _("INVITE_PERMISSIONS_POPUP_TITLE_Your Email")
                EMAIL_INTRO = _("INVITE_PERMISSIONS_POPUP_To receive notifications of any updates on your pool, please enter your email address or use your facebook email.")
                EMAIL_LABEL = _("INVITE_PERMISSIONS_POPUP_Email:")
                EMAIL_FB = _("INVITE_PERMISSIONS_POPUP_Grant Facebook Email")
                
                STREAM_PUBLISH_TITLE = _("INVITE_PERMISSIONS_POPUP_TITLE_Your Facebook Stream Publish Permission")
                STREAM_PUBLISH_INTRO = _("INVITE_PERMISSIONS_POPUP_Because you're inviting friends from Facebook, we need Stream Publish permission so they can receive your personal invitation.")
                STREAM_PUBLISH = _("INVITE_PERMISSIONS_POPUP_Grant Stream Publish")
        
                CREATE_EVENT_TITLE = _("INVITE_PERMISSIONS_POPUP_TITLE_Your Facebook Create Event Permission")
                CREATE_EVENT_INTRO = _("INVITE_PERMISSIONS_POPUP_Because you're inviting friends from Facebook, we need Create Event permission so they can receive your personal invitation.")
                CREATE_EVENT = _("INVITE_PERMISSIONS_POPUP_Grant Create Event")
                GRANT_BOTH_INTRO = _("INVITE_PERMISSIONS_POPUP_...or grant both in one go!")
                GRANT_BOTH = _("INVITE_PERMISSIONS_POPUP_Grant Both!")
                SKIPTHISLINK = _("INVITE_PERMISSIONS_POPUP_Of course you can skip granting, by not inviting any one.")
                SKIPABLE = False
        
        
        __M_locals_builtin_stored = __M_locals_builtin()
        __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['SUBHEADER','EMAIL_INTRO','HEADER_MSG','blocks','CREATE_EVENT','STREAM_PUBLISH_INTRO','EMAIL_TITLE','GRANT_BOTH_INTRO','CREATE_EVENT_TITLE','STREAM_PUBLISH','STREAM_PUBLISH_TITLE','EMAIL_FB','SKIPTHISLINK','SKIPABLE','CREATE_EVENT_INTRO','EMAIL_LABEL','GRANT_BOTH'] if __M_key in __M_locals_builtin_stored]))
        # SOURCE LINE 43
        __M_writer(u'\n')
        # SOURCE LINE 44
        if blocks and getattr(c, 'enforce_blocks', False):
            # SOURCE LINE 45
            __M_writer(u'\t<div class="window_background">&nbsp;</div>\n\t<div class="window_container">\n\t\t<div class="window">\n\t\t\t<div class="header">')
            # SOURCE LINE 48
            __M_writer(HEADER_MSG)
            __M_writer(u'</div>\n\t\t\t<div class="subheader">')
            # SOURCE LINE 49
            __M_writer(SUBHEADER)
            __M_writer(u'</div>\n\t\t\t<a href="#" class="panelclosing_x">x</a>\n\t\t<div class="popupContent">\n')
            # SOURCE LINE 52
            if 'email' in blocks:
                # SOURCE LINE 53
                __M_writer(u'\t\t\t<div class="blocking" id="emailblock">\n\t\t\t\t<div class="block_header">\n\t\t\t\t\t')
                # SOURCE LINE 55
                __M_writer(EMAIL_TITLE)
                __M_writer(u'\n\t\t\t\t</div>\n\t\t\t\t<div class="block_intro">\n\t\t\t\t\t')
                # SOURCE LINE 58
                __M_writer(EMAIL_INTRO)
                __M_writer(u'\n\t\t\t\t</div>\n\t\t\t\t<form action="')
                # SOURCE LINE 60
                __M_writer(escape(url('index', action='set_email')))
                __M_writer(u'" method="POST" id="blockingemailform">\n\t\t\t\t\t<a class="facebookBtn floaterRight" onclick="getfbEmail(\'')
                # SOURCE LINE 61
                __M_writer(escape(app_globals.FbApiKey))
                __M_writer(u'\')"><span>')
                __M_writer(escape(EMAIL_FB))
                __M_writer(u'</span></a>\n\t\t\t\t\t<label for="email">')
                # SOURCE LINE 62
                __M_writer(EMAIL_LABEL)
                __M_writer(u'</label>\n\t\t\t\t\t<input type="text" value="')
                # SOURCE LINE 63
                __M_writer(escape(getattr(c, 'email', '')))
                __M_writer(u'" name="email" id="email"/>\n\t\t\t\t\t<input type="button" value="submit" onclick="loadFormElement(\'')
                # SOURCE LINE 64
                __M_writer(escape(url('index', action='set_email')))
                __M_writer(u'\', \'blocking_email_error\', \'blockingemailform\', page_reloader);"/>\n\t\t\t\t\t<div id="blocking_email_error"></div>\n\t\t\t\t</form>\n\t\t\t\t<div class="clear"></div>\n\t\t\t</div>\n')
                pass
            # SOURCE LINE 70
            if 'fb_streampub' in blocks:
                # SOURCE LINE 71
                __M_writer(u'\t\t\t<div class="blocking" id="fb_streampubblock">\n\t\t\t\t<div class="block_header">\n\t\t\t\t\t')
                # SOURCE LINE 73
                __M_writer(STREAM_PUBLISH_TITLE)
                __M_writer(u'\n\t\t\t\t</div>\n\t\t\t\t<div class="block_intro">\n\t\t\t\t\t')
                # SOURCE LINE 76
                __M_writer(STREAM_PUBLISH_INTRO)
                __M_writer(u'\n\t\t\t\t</div>\n\t\t\t\t<a class="facebookBtn floaterRight" onclick="getfbStreamPublish(\'')
                # SOURCE LINE 78
                __M_writer(escape(app_globals.FbApiKey))
                __M_writer(u'\')"><span>')
                __M_writer(escape(STREAM_PUBLISH))
                __M_writer(u'</span></a>\n\t\t\t\t<div class="clear"></div>\n\t\t\t</div>\n')
                pass
            # SOURCE LINE 82
            if 'create_event' in blocks:
                # SOURCE LINE 83
                __M_writer(u'\t\t\t<div class="blocking" id="fb_create_eventblock">\n\t\t\t\t<div class="block_header">\n\t\t\t\t\t')
                # SOURCE LINE 85
                __M_writer(CREATE_EVENT_TITLE)
                __M_writer(u'\n\t\t\t\t</div>\n\t\t\t\t<div class="block_intro">\n\t\t\t\t\t')
                # SOURCE LINE 88
                __M_writer(CREATE_EVENT_INTRO)
                __M_writer(u'\n\t\t\t\t</div>\n\t\t\t\t<a class="facebookBtn floaterRight" onclick="getfbCreateEvent(\'')
                # SOURCE LINE 90
                __M_writer(escape(app_globals.FbApiKey))
                __M_writer(u'\')"><span>')
                __M_writer(escape(CREATE_EVENT))
                __M_writer(u'</span></a>\n\t\t\t\t<div class="clear"></div>\n\t\t\t</div>\n')
                pass
            # SOURCE LINE 94
            if 'email' in blocks and 'fb_streampub' in blocks:
                # SOURCE LINE 95
                __M_writer(u'\t\t\t<div class="blocking block_grantboth">\n\t\t\t\t<div class="block_header">\n\t\t\t\t<a class="facebookBtn floaterRight" onclick="getfbStreamPublishnEmail(\'')
                # SOURCE LINE 97
                __M_writer(escape(app_globals.FbApiKey))
                __M_writer(u'\')"><span>')
                __M_writer(escape(GRANT_BOTH))
                __M_writer(u'</span></a>\n\t\t\t\t<div class="floaterRight grantboth">\n\t\t\t\t\t')
                # SOURCE LINE 99
                __M_writer(GRANT_BOTH_INTRO)
                __M_writer(u'\n\t\t\t\t</div>\n\t\t\t\t</div>\n\t\t\t\t<div class="clear"></div>\n\t\t\t</div>\n')
                pass
            # SOURCE LINE 105
            if SKIPABLE:
                # SOURCE LINE 106
                __M_writer(u'\t\t\t<div class="blocking">\n\t\t\t\t\t<div class="block_intro floaterRight">\n\t\t\t\t\t\t')
                # SOURCE LINE 108
                __M_writer(SKIPTHISLINK)
                __M_writer(u'<a href="#" onclick="checkForward()"> ')
                __M_writer(escape(_("Skip")))
                __M_writer(u'</a>\n\t\t\t\t\t</div>\n\t\t\t\t\t<div class="clear"></div>\n\t\t\t\t</div>\n\t\t\t</div>\n')
                pass
            # SOURCE LINE 114
            __M_writer(u'\t</div>\n\t</div>\n\t<script type="text/javascript">\n\t\tdojo.addOnLoad( function() {\n\t\t\tdojo.query(".panelclosing_x", "blocking_msgs").connect("onclick", closeBlocks);\n\t\t});\n\t</script>\n')
            pass
        # SOURCE LINE 122
        __M_writer(u'\n\n\n\n\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


