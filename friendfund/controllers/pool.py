from __future__ import with_statement
import logging, formencode, datetime
from pylons import request, response, session as websession, tmpl_context as c, url, app_globals as g, cache
from pylons.controllers.util import abort, redirect
from pylons.decorators import jsonify

from friendfund.lib import fb_helper, tw_helper, helpers as h
from friendfund.lib.auth.decorators import logged_in, post_only, pool_available
from friendfund.lib.base import BaseController, render, render_def, SuccessMessage, ErrorMessage
from friendfund.lib.i18n import FriendFundFormEncodeState
from friendfund.model import db_access
from friendfund.model.forms.common import to_displaymap, DecimalValidator
from friendfund.model.forms.user import ShippingAddressForm, BillingAddressForm
from friendfund.model.forms.pool import PoolHomePageForm
from friendfund.model.pool import Pool, PoolUser, PoolChat, PoolComment, PoolDescription, PoolThankYouMessage, Occasion, GetMoreInviteesProc, GetECardContributorsProc
from friendfund.model.poolsettings import PoolSettings, ShippingAddress, ClosePoolProc, ExtendActionPoolProc, POOLACTIONS
from friendfund.services.pool_service import MissingPoolException, MissingProductException, MissingOccasionException, MissingReceiverException
from friendfund.tasks.photo_renderer import remote_product_picture_render, remote_pool_picture_render

_ = lambda x:x
NOT_AUTHORIZED_MESSAGE = _("POOL_Your not authorized for this operation.")
CLOSING_MESSAGE = _("POOL_ACTION_Pool is now Closed and the Gift has been ordered!")
EXPIRED_MESSAGE = _("POOL_ACTION_This pool has not reached it's target. Please vist the pool admin page to continue fund raising!")
UPDATED_MESSAGE = _("POOL_ACTION_Changes saved.")
NOT_CORRECT_STATE = _("POOL_ACTION_This Action is not allowed as Pool is not in correct state.")
SAVE_ADDRESS_FIRST = _("POOL_ACTION_In order to Close the pool, you need to fill out and save Shipping and Billing Address first!")
moneyval = DecimalValidator(min=0.01)

from friendfund.lib.base import _

log = logging.getLogger(__name__)

class PoolController(BaseController):
	chat_page_size = 10
	
	@pool_available()
	def index(self, pool_url = None):
		if pool_url is None:
			return abort(404)
		if c.pool is None:
			c.messages.append(ErrorMessage(_("POOL_PAGE_ERROR_POOL_DOES_NOT_EXIST")))
			return redirect(url('home'))
		if c.pool.is_closed() and not "view" in request.params:
			return redirect(url('pool_action', pool_url=pool_url, action='complete'))
		elif c.pool.is_closed():
			c.messages.append(SuccessMessage(_('FF_POOL_SUCCESS_MSG_This pool has been successfully funded <a href="%s"> View the eCard&raquo;</a>')%url(controller="pool", pool_url=c.pool.p_url, action="complete")))
		elif c.pool.is_expired():
			c.messages.append(ErrorMessage(_('FF_POOL_EXPIRED_MSG_This pool expired without reaching its funding goal in time.')))
		if c.pool.can_i_view(c.user):
			c.workflow = request.params.get("v") or None
			return self.render('/pool/pool.html')
		else:
			return self.render('/pool/pool_secret.html')
		
	@pool_available()
	def complete(self, pool_url):
		if c.pool is None:
			c.messages.append(ErrorMessage(_("POOL_PAGE_ERROR_POOL_DOES_NOT_EXIST")))
		if not c.pool.is_closed():
			 redirect(url('get_pool', pool_url=pool_url))
		
		c.contributors = g.dbm.get(GetECardContributorsProc, p_url = pool_url).contributors
		return self.render('/pool/pool_complete.html')
	
	def _clean_session(self):
		if 'pool' in websession:
			del websession['pool']
		if 'invitees' in websession:
			del websession['invitees']
		if 'product_list' in websession:
			del websession['product_list']
	
	def reset(self):
		self._clean_session()
		return redirect(url('home'))
	
	def _determine_product(self, tracking_link):
		if tracking_link:
			parser_values = {
				"url":request.params.get("tracking_link"),
				"product_picture":request.params.get("product_picture"),
				"name":request.params.get("product_name"),
				"description":request.params.get("product_description"),
				"img_list":request.params.getall("img_list") or [],
			}
			parser_values['display_url'] = parser_values['url'] and h.word_truncate_by_letters(parser_values['url'], 40) or None
			parser_values['display_name'] = parser_values['name'] and h.word_truncate_by_letters(parser_values['name'], 40) or None
			parser_values['display_description'] = parser_values['description'] and h.word_truncate_by_letters(parser_values['description'], 180) or None
		else: 
			parser_values = {}
		return parser_values
	
	def details(self):
		c.errors = {}
		c.workflow = request.params.get("v") or "1"
		c.currencies = sorted(g.country_choices.currencies)
		
		tracking_link = request.params.get("tracking_link")
		c.values = {
			"tracking_link":tracking_link,
			"amount":request.params.get("amount"),
			"currency":h.default_currency(),
			"title":request.params.get("title"),
			"description":request.params.get("description"),
			"date": (datetime.datetime.today() + datetime.timedelta(14)),
			"settlementOption": None,
			"product_picture":request.params.get("product_picture")
			}
		try:
			c.values['date'] = datetime.datetime.strptime(request.params["date"], "%Y-%m-%d")
		except:
			pass
		c.parser_values = self._determine_product(tracking_link)
		try:
			mini_pool_schema = PoolHomePageForm().to_python(request.params, FriendFundFormEncodeState)
		except formencode.validators.Invalid, error:
			c.errors = error.error_dict or {}
			c.values.update(error.value)
		else:
			c.values.update(mini_pool_schema)
		if isinstance(c.values.get('title'),basestring) and isinstance(c.values.get('tracking_link'), basestring) \
			and c.values['title'].strip() in c.values.get('tracking_link'):
			 c.values['title'] = None
		
		
		if c.errors:
			c.messages.append(ErrorMessage(_("FF_POOL_DETAILS_PAGE_ERRORBAND_Please correct the Errors below")))
		return self.render('/pool/pool_details.html')
	
	@logged_in()
	def create(self):
		c.errors = {}
		c.values = {}
		c.workflow = request.params.get("v") or "1"
		if request.merchant.type_is_group_gift:
			try:
				if request.merchant.entry_is_iframe:
					c.pool = g.pool_service.create_group_gift_from_iframe()
				else:
					c.pool = g.pool_service.create_group_gift()
			except MissingProductException, e:
				c.messages.append(ErrorMessage(_("POOL_PAGE_ERROR_POOL_DOES_NOT_EXIST")))
				return redirect(url('home'))
			except MissingOccasionException, e:
				c.messages.append(ErrorMessage(_("POOL_CREATE_Occasion was unknown, what can I do?")))
				return redirect(url('home'))
			except MissingReceiverException, e:
				c.messages.append(ErrorMessage(_("POOL_CREATE_Receiver was unknown, what can I do?")))
				return redirect(url('home'))
		else:
			try:
				c.pool = g.pool_service.create_free_form()
			except formencode.validators.Invalid, error:
				tracking_link = request.params.get("tracking_link")
				c.parser_values = self._determine_product(tracking_link)
				c.currencies = sorted(g.country_choices.currencies)
				c.errors = error.error_dict or {}
				c.values = error.value
				if not c.values:
					return redirect(url(controller="pool", action="details", v=2))
				c.values["img_list"] = c.values.get("img_list") or []
				if not isinstance(c.values["img_list"], list):
					c.values["img_list"] = [c.values["img_list"]]
				try:
					c.values['date'] = datetime.datetime.strptime(c.values['date'], "%Y-%m-%d")
				except:
					pass
				c.messages.append(ErrorMessage(_("FF_POOL_DETAILS_PAGE_ERRORBAND_Please correct the Errors below")))
				return self.render('/pool/pool_details.html')
		c.pool.merchant_domain = request.merchant.domain
		g.dbm.set(c.pool, merge = True, cache=False)
		
		if c.pool.product and c.pool.product.has_picture():
			remote_product_picture_render.apply_async(args=[c.pool.p_url, c.pool.product.picture])
		remote_pool_picture_render.apply_async(args=[c.pool.p_url])
		
		if not c.pool:
			return redirect(request.referer)
		self._clean_session()
		return redirect(url('invite_index',  pool_url = c.pool.p_url, v=c.workflow))
	
	@jsonify
	@pool_available()
	def chat(self, pool_url):
		if request.method == 'POST':
			if('comment' in request.params):
				comment = request.params['comment']
				if comment:
					pcomment = PoolComment(u_id = c.user.u_id, p_url = pool_url, comment = comment, recency = 0)
					g.dbm.set(pcomment)
					pcomment.name = c.user.name
					pcomment.profile_picture_url = c.user.profile_picture_url
					pcomment.created = datetime.datetime.now()
					return {'data':{'html':render_def("/pool/chat.html", "renderSingleComment", comment = pcomment).strip()}}
				else:
					return {'data':{'html':''}}
		else:
			c.pool_url = pool_url
			c.chat = g.dbm.get(PoolChat, p_url = pool_url)
			if len(c.chat.comments) > self.chat_page_size:
				c.chat.comments = c.chat.comments
				c.offset = self.chat_page_size
			else:
				c.offset = 0
			return {'html':render("/pool/chat.html").strip()}
	
	@jsonify
	@pool_available()
	def get_widget(self, pool_url):
		return {"popup":render("/pool/parts/widget.html").strip()}
	@pool_available()
	def widget(self, pool_url):
		try:
			c.faces = int(request.params.get("faces", 5)) or 5
		except:
			c.faces = 5
		return render("/pool/parts/widget_frame.html")
	
	@jsonify
	@pool_available()
	def invitees(self, pool_url):
		page_no = request.params.get("page")
		try:
			c.page = int(page_no)
		except:
			return {"success":False}
		c.participants = g.dbm.get(GetMoreInviteesProc,p_url=pool_url, page_no=c.page)
		return {"data":{"html":render("/pool/parts/invitees.html").strip()}}
	
	@logged_in(ajax=False)
	@pool_available()
	def delete(self, pool_url):
		if c.pool.am_i_admin(c.user):
			log.error("POOL_DELETE_NOT_IMPLEMENTED")
		return redirect(request.referer)
	
	@logged_in(ajax=False)
	@pool_available(contributable_only = True)
	def join(self, pool_url):
		if not c.pool.am_i_member(c.user):
			g.pool_service.invite_myself(pool_url, c.user)
			c.messages.append(SuccessMessage(_("FF_POOL_PAGE_You Joined the Pool!")))
		return redirect(url("get_pool", pool_url=pool_url))
