import logging

import formencode
from formencode.variabledecode import variable_decode
from pylons import request, tmpl_context as c, app_globals

from friendfund.lib import helpers as h
from friendfund.lib.auth.decorators import post_only, jsonify
from friendfund.lib.i18n import FriendFundFormEncodeState
from friendfund.lib.base import BaseController, _, render_def
from friendfund.model.authuser import UserNotLoggedInWithMethod
from friendfund.model.forms.pool import PoolEmailInviteeForm


log = logging.getLogger(__name__)

class MyfriendsController(BaseController):
    @jsonify
    def method(self, method):
        c.method = str(method)
        c.mutuals = False
        c.all = False
        c.clearance_level = 3
        if method in ['facebook', 'twitter']:
            pv =  request.params.getall('pv')
            is_complete = True
            offset = 0
            try:
                friends, is_complete, offset = c.user.get_friends(c.method)
            except UserNotLoggedInWithMethod, e:
                if c.method == 'facebook':
                    return {'data':{'is_complete': True, 'success':False, 'html':render_def('/receiver/fb_login.html', 'renderLogin', label=_("FF_Choose your recipient from Facebook")).strip()}}
                else:
                    return {'data':{'is_complete': True, 'success':False, 'html':render_def('/receiver/tw_login.html', 'renderLogin', label=_("FF_Choose your recipient from Twitter")).strip()}}
            else:
                if c.method == c.user.network:
                    usermap = c.user.to_map()
                    usermap['profile_picture_url'] = c.user.get_profile_pic("PROFILE_M")
                    usermap['minimal_repr'] = h.encode_minimal_repr(usermap)
                    friendlist = [usermap]
                else:
                    friendlist = []
                friendlist.extend([friends[id] for id in sorted(friends, key=lambda x: friends[x]['name'])])
                c.friends = friendlist
                return {'data':{'is_complete':is_complete, 'success':True, 'offset':offset
                ,'html':render_def('/receiver/inviter.html', "networkinviter",network_name=c.method).strip()
                ,'friends':c.friends
                ,"template":"""<li title="${name}" class="invitee_row selectable" _network="%s" id="${dom_id}"><div class="spacer"><div class="avt"><span class="displayable close" href="#">X</span><img src="${profile_picture_url}"></div><p>${name}</p><span class="hideable">%s &raquo;</span><input type="hidden" name="invitees" value="${minimal_repr}"/><div class="clear"></div></div></li>""" % (c.method, _("GG_RECEIVER_Select"))
                }}
        else:
            c.friends = {}
            c.email_errors = {}
            c.email_values = {}
        return {'html':render_def('/receiver/inviter.html', 'mailinviter', submit_name = _("GG_INVITER_EMAIL_Select")).strip()}

    @jsonify
    def get_extension(self, method):
        if method in ['twitter', 'facebook']:
            c.method = str(method)
            pv =  request.params.getall('pv')
            offset = int(request.params['offset'])
            friends, is_complete, offset = c.user.get_friends(c.method, offset = offset)
            c.friends = [friends[id] for id in sorted(friends, key=lambda x: friends[x]['name'])]
            return {'data':{'is_complete':is_complete, 'offset':offset, 'friends':c.friends}}
        return {'success':False}




    @jsonify
    @post_only(ajax=True)
    def validate(self):
        params = variable_decode(request.params)
        invitee = params.get("invitee")
        network = invitee['network']
        if network == 'email':
            c.email_values = c.email_errors = {}
            try:
                form_result = PoolEmailInviteeForm().to_python(invitee, state=FriendFundFormEncodeState)
            except formencode.validators.Invalid, error:
                c.email_errors = error.error_dict or {}
                c.email_values = error.value
                return {"data":{'success':False, 'html':render_def('/receiver/inviter.html', 'mailinviter', submit_name = _("GG_INVITER_EMAIL_Select")).strip()}}
            else:
                c.method = 'email'
                invitee['success'] = True
                invitee['profile_picture_url'] = invitee.get('profile_picture_url', app_globals.statics_service.get_default_user_picture("PROFILE_S"))
                invitee['large_profile_picture_url'] = invitee.get('large_profile_picture_url') or app_globals.statics_service.get_default_user_picture("POOL")
                invitee['user_data'] = h.encode_minimal_repr(invitee)
                invitee['html'] = render_def('/receiver/inviter.html', 'render_email_friend', user_data = invitee).strip()
                return {'clearmessage':True, 'data':invitee}
        elif(c.user.is_anon):
            return {'data':
                        {'success':False,
                         'html':self.render('/receiver/login_required.html').strip()
                        }
            }
        else:
            return self.ajax_messages(_(u"RECEIVER_ADD_Unknown Network or Method"))
