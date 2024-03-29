import logging
from collections import deque

import formencode
from pylons import request, tmpl_context as c, url, app_globals
from formencode.variabledecode import variable_decode
import markdown
from pylons.templating import render_mako as render, render_mako_def as render_def
from pylons.i18n import ugettext as _

from friendfund.lib import helpers as h
from friendfund.lib.auth.decorators import logged_in, post_only, pool_available, jsonify
from friendfund.lib.base import BaseController
from friendfund.lib.i18n import FriendFundFormEncodeState
from friendfund.lib.notifications.messages import ErrorMessage, SuccessMessage
from friendfund.lib.routes_middleware import redirect
from friendfund.model.authuser import CLEARANCES, UserNotLoggedInWithMethod, NoFriendsFoundSomeErrorOccured
from friendfund.model.forms.pool import PoolEmailInviteeForm
from friendfund.model.pool import Pool, PoolInvitee, AddInviteesProc, GetPoolInviteesProc
from friendfund.services import static_service as statics
from friendfund.tasks.celerytasks.photo_renderer import remote_profile_picture_render, remote_pool_picture_render
from friendfund.tasks.notifiers.common import get_template


strbool = formencode.validators.StringBoolean(if_missing=False, if_empty=False)
from celery.task.sets import TaskSet
log = logging.getLogger(__name__)


class InviteController(BaseController):
    @pool_available(contributable_only = True)
    def display(self, pool_url, level = CLEARANCES["INVITE"]):
        if c.user.is_anon or not c.pool.am_i_member(c.user):
            return redirect(url('get_pool', pool_url=pool_url))
        locals = {"closing_date":h.format_date(c.pool.expiry_date, format="full"), "pool_url":url("get_pool", pool_url=pool_url, protocol="http"), "title":c.pool.title}
        c.errors = {}
        c.values = {"subject":c.pool.title, "message":c.pool.get_text_description()}
        return self._display_invites()

    def _display_invites(self, invitees = {}):
        c.workflow = request.params.get("v") or "1"
        c.method = c.user.get_current_network() or 'facebook'
        c.invitees = invitees
        return self.render('/invite/invite.html')

    @jsonify
    @logged_in(ajax=True)
    @pool_available(contributable_only = True)
    def method(self, pool_url, method):
        c.method = str(method)
        c.mutuals = request.merchant.type_is_group_gift
        c.all = True
        if method in ['facebook', 'twitter']:
            already_invited = app_globals.dbm.get(GetPoolInviteesProc, p_url = pool_url, network=c.method)

            try:
                receiver_id = already_invited.receiver.network_id
            except:
                receiver_id = None
                c.mutuals = False
            is_complete = True
            offset = 0
            c.clearance_level = c.pool.am_i_admin(c.user) and CLEARANCES["FULL"] or CLEARANCES["INVITE"]
            try:
                friends, is_complete, offset = c.user.get_friends(c.method, receiver_id)
            except UserNotLoggedInWithMethod, e:
                if c.method == 'facebook':
                    return {'data':{'is_complete': True, 'success':False, 'html':render('/invite/fb_login.html').strip()}}
                else:
                    return {'data':{'is_complete': True, 'success':False, 'html':render('/invite/tw_login.html').strip()}}
            except NoFriendsFoundSomeErrorOccured, e:
                log.error("NoFriendsFoundSomeErrorOccured:%s", e)
                c.friends = []
                return {'data':{'is_complete':True, 'success':True, 'offset':0, "html":render("/invite/inviter.html"),
                                'friends':c.friends,
                                "template":"""<li title="${name}" class="invitee_row selectable" _network="%s" id="${dom_id}"><div class="avt"><span class="displayable close" href="#">X</span><img src="${profile_picture_url}"></div><p class="hideable">${name}</p><span class="hideable">%s &raquo;</span><input type="hidden" name="invitees" value="${minimal_repr}"/></li>""" % (c.method, _("FF_INVITER_BUTTON_Invite"))
                }}
            else:
                c.friends = [friends[id] for id in sorted(friends, key=lambda x: friends[x]['name']) if id not in already_invited.idset]
                return {'data':{'is_complete':is_complete, 'success':True, 'offset':offset, "html":render("/invite/inviter.html"),
                                'friends':c.friends,
                                "template":"""<li title="${name}" class="invitee_row selectable" _network="%s" id="${dom_id}"><div class="avt"><span class="displayable close" href="#">X</span><img src="${profile_picture_url}"></div><p class="hideable">${name}</p><span class="hideable">%s &raquo;</span><input type="hidden" name="invitees" value="${minimal_repr}"/></li>""" % (c.method, _("FF_INVITER_BUTTON_Invite"))
                }}
        else:
            c.friends = {}
            c.email_errors = {}
            c.email_values = {}
        return {'html':render('/invite/inviter.html').strip()}

    @jsonify
    def get_extension(self, pool_url, method):
        if method in ['twitter', 'facebook']:
            c.method = str(method)

            already_invited = app_globals.dbm.get(GetPoolInviteesProc, p_url = pool_url, network=c.method).idset

            offset = int(request.params['offset'])
            friends, is_complete, offset = c.user.get_friends(c.method, offset = offset)
            c.friends = [friends[id] for id in sorted(friends, key=lambda x: friends[x]['name']) if id not in already_invited]
            return {'data':{'is_complete':is_complete, 'offset':offset, 'friends':c.friends}}
        return {'success':False}

    def _return_to_input(self, invitees):
        c.invitees = {}
        c.messages.append(ErrorMessage(_("FF_INVITE_PAGE_ERRORBAND_Please fill in below values correctly.")))
        for inv in invitees:
            netw = inv['network'].lower()
            invs = c.invitees.get(netw,{})
            invs[str(inv['network_id'])] = inv
            c.invitees[netw] = invs
        return self._display_invites(c.invitees)

    @logged_in(ajax=False)
    @pool_available(contributable_only = True)
    def friends(self, pool_url):
        invitees = request.params.getall('invitees')
        c.workflow = request.params.get("v") or "1"
        c.errors = {}
        c.values = {}

        c.pool.is_secret = request.params.get("is_secret", False)
        if invitees:
            if not request.params.get('message'):
                c.errors['message']=_("Please input an Invite Message")
            if not request.params.get('subject'):
                c.errors['subject']=_("Please input an Invite Subject")
            if c.errors:
                c.values['subject'] = request.params.get('subject')
                c.values['message'] = request.params.get('message')
                return self._return_to_input(invitees)

            invitees = map(h.decode_minimal_repr, invitees)
            invittes_proc_result = app_globals.dbm.set(AddInviteesProc(p_url = c.pool.p_url
                                                                       , event_id = c.pool.event_id
                                                                       , inviter_user_id = c.user.u_id
                                                                       , users=[PoolInvitee.from_map(el) for el in invitees]
                                                                       , subject = request.params.get('subject')
                                                                       , message = request.params.get('message')
                                                                       , is_secret = c.pool.is_secret))
            app_globals.dbm.expire(Pool(p_url = c.pool.p_url))
            tasks = deque()
            for i in invitees:
                if i['network'] != 'email':
                    tasks.append(remote_profile_picture_render.subtask(args=[[(i['network'], i['network_id'],i['large_profile_picture_url'])]]))
            job = TaskSet(tasks=tasks)
            job.apply_async()

            remote_pool_picture_render.apply_async(args=[c.pool.p_url])
        if c.workflow != "3":
            if request.merchant.require_address:
                msg = SuccessMessage(_("FF_POOL_PAGE_Welcome to your new Pool! Don't forget to <a href=\"%s\">add a Shipping Address</a>")%url(controller="pedit", pool_url=c.pool.p_url, action="address"))
            else:
                msg = SuccessMessage(_("FF_POOL_PAGE_Welcome to your new Pool!"))
            c.messages.append(msg)
        return redirect(url('ctrlpoolindex', controller='pool', pool_url = c.pool.p_url, v=c.workflow))


    @jsonify
    @pool_available(contributable_only = True)
    def preview(self, pool_url):
        c.method = request.params.get("method") or "facebook"
        template_data = {}
        template_data['invitee_name'] = ''
        template_data['firstname_invitee_name'] = ''
        template_data['subject'] = request.params.get("subject")
        template_data['message'] = request.params.get("message")
        template_data['pool_description'] = c.pool.description
        template_data['expiry_date'] =  h.fdate(c.pool.expiry_date, format="long", locale=h.get_language_locale())
        template_data['p_url'] = c.pool.p_url
        template_data['admin_name'] = c.user.name
        template_data['DEFAULT_BASE_URL'] = app_globals.BASE_DOMAIN
        template_data['learn_more_url'] = url(protocol="http", controller="content",action="contact")
        template_data['merchant_domain'] = request.merchant.domain
        template_data['merchant_is_default'] = request.merchant.is_default
        template_data['merchant_name'] = request.merchant.name
        template_data['merchant_logo_url'] = request.merchant.get_logo_url()

        if c.method=="email":
            template_data['recipient_name'] = c.pool.receiver.name
            template_data['occasion'] = c.pool.occasion.get_display_name()

            if request.merchant.type_is_group_gift:
                template = get_template(h.get_language_locale(), 9, log)
            else:
                template = get_template(h.get_language_locale(), 11, log)
            c.subject = template.get_def("subject").render_unicode(h = h, data = template_data)
            c.text = markdown.markdown(template.render_unicode(h = h, data = template_data))
            return  {"popup":self.render("/invite/preview/preview_email.html").strip()}

        elif c.method=="twitter":
            return  {"popup":self.render("/invite/preview/preview_twitter.html").strip()}
        elif c.method=="stream_publish":
            template = get_template(h.get_language_locale(), 73, log)

            c.message = template.get_def("message").render_unicode(h = h, data = template_data)
            c.link = template.get_def("link").render_unicode(h = h, data = template_data)
            c.name = template.get_def("name").render_unicode(h = h, data = template_data)
            c.caption = template.get_def("caption").render_unicode(h = h, data = template_data)
            c.description = template.get_def("description").render_unicode(h = h, data = template_data)
            c.picture = c.pool.get_product_display_picture("FF_POOLS")
            c.action_name = template.get_def("action_name").render_unicode(h = h, data = template_data)

            return  {"popup":self.render("/invite/preview/preview_facebook_streampublish.html").strip()}
        else:
            template = get_template(h.get_language_locale(), 10, log)
            c.name = template.get_def("name").render_unicode(h = h, data = template_data)
            c.description = markdown.markdown(template.get_def("description").render_unicode(h = h, data = template_data))
            return  {"popup":self.render("/invite/preview/preview_facebook.html").strip()}

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
                return {"data":{'success':False, 'html':render_def('/invite/inviter.html', 'mailinviter').strip()}}
            else:
                c.method = 'email'
                invitee['success'] = True
                invitee['profile_picture_url'] = invitee.get('profile_picture_url', statics.DEFAULT_USER_PICTURE_TOKEN)
                invitee['large_profile_picture_url'] = app_globals.statics_service.get_user_picture(invitee['profile_picture_url'], "PROFILE_S")
                invitee['html'] = render_def('/invite/inviter.html', 'render_email_friends', friends = {invitee['network_id']:invitee}, active = True, class_='selectable').strip()
                invitee['input_html'] = render_def('/invite/inviter.html', 'mailinviter').strip()
                return {'clearmessage':True, 'data':invitee}
        else:
            return self.ajax_messages(_(u"RECEIVER_ADD_Unknown Network or Method"))