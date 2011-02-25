from __future__ import with_statement
import logging, formencode, datetime
from pylons import request, response, session as websession, tmpl_context as c, url, app_globals as g, cache
from pylons.controllers.util import abort, redirect
from pylons.decorators import jsonify

from friendfund.lib import fb_helper, tw_helper, helpers as h
from friendfund.lib.auth.decorators import logged_in, post_only, checkadd_block
from friendfund.lib.base import BaseController, render, ExtBaseController
from friendfund.lib.i18n import FriendFundFormEncodeState
from friendfund.model import db_access
from friendfund.model.forms.common import to_displaymap, DecimalValidator
from friendfund.model.forms.user import ShippingAddressForm, BillingAddressForm
from friendfund.model.pool import Pool, PoolUser, PoolChat, PoolComment, PoolDescription, PoolThankYouMessage, Occasion
from friendfund.model.poolsettings import PoolSettings, ShippingAddress, ClosePoolProc, ExtendActionPoolProc, POOLACTIONS
from friendfund.tasks.photo_renderer import remote_profile_picture_render, remote_product_picture_render, remote_pool_picture_render

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

class PoolController(ExtBaseController):
	navposition=g.globalnav[1][2]
	chat_page_size = 10
	def index(self, pool_url = None):
		if pool_url is None:
			return abort(404)
		if c.pool is None:
			c.messages.append(_("POOL_PAGE_ERROR_POOL_DOES_NOT_EXIST"))
			return redirect(url('home'))
		if c.pool.is_closed():
			return redirect(url('pool_action', pool_url=pool_url, action='complete'))
		if c.pool.can_i_view(c.user):
			return self.render('/pool/pool.html')
		else:
			return self.render('/pool/pool_secret.html')
		
	def complete(self, pool_url):
		if c.pool is None:
			c.messages.append(_("POOL_PAGE_ERROR_POOL_DOES_NOT_EXIST"))
		if not c.pool.is_closed():
			 redirect(url('get_pool', pool_url=pool_url))
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
	
	###TODO: these UID Links could be shared and disclose unwanted information
	def details(self):
		c.pd = request.params.get("pd")
		try:
			c.pd = str(c.pd).strip()
		except:
			c.pd = h.get_unique_token()
			if request.method != "POST":
				return redirect(url(controller='pool', action='details', pd=c.pd))
		
		with g.cache_pool.reserve() as mc:
			wizard = h.get_wizard(mc, c.pd)
			c.pool = wizard.get("pool", Pool())
			amount = request.params.get("pool.amount")
			if amount:
				try:
					amount = moneyval.to_python(amount)
				except formencode.validators.Invalid, error:
					log.error(error)
					amount = None
				c.pool.set_amount_float(amount)
			c.pool.title = request.params.get("pool.title",c.pool.title)
			c.pool.currency = c.pool.currency or h.default_currency()
			if not c.pool.occasion:
				c.pool.occasion = Occasion(key = "EVENT_OTHER", date=datetime.datetime.today() + datetime.timedelta(14))
			if c.pool.title and c.pool.title.strip() in getattr(c.pool.product, "tracking_link", ""):
				c.pool.title = None
			if c.pool.product and "product.picture" in request.params:
				c.pool.product.picture = request.params.get("product.picture",c.pool.product.picture)
			c.images = wizard.get('product_picture_list', [])
			wizard['pool'] = c.pool
			h.set_wizard(mc, c.pd, wizard)
			return self.render('/pool/pool_details.html')

	
	@logged_in()
	def create(self):
		if request.merchant.type_is_free_form:
			return self._create_freeform()
		else:
			return self._create_groupgift()
	
	def _create_freeform(self):
		c.pd = request.params.get("pd")
		try:
			c.pd = str(c.pd).strip()
		except:
			pass
		if c.pd:
			with g.cache_pool.reserve() as mc:
				wizard = h.get_wizard(mc, c.pd)
		else:
			wizard = {}
		c.pool = wizard.get("pool", Pool())
		c.pool.merchant_domain = request.merchant.domain
		pool_map = formencode.variabledecode.variable_decode(request.params)
		c.pool.fromMap(pool_map, override = True)
		admin = PoolUser(**c.user.get_map())
		admin.is_admin = True
		receiver = PoolUser(**c.user.get_map())
		receiver.is_receiver = True
		c.pool.participants.append(admin)
		c.pool.participants.append(receiver)
		
		g.dbm.set(c.pool, merge = True, cache=False)
		if c.pool.product:
			remote_product_picture_render.delay(c.pool.p_url, c.pool.product.picture)
		remote_pool_picture_render.apply_async(args=[c.pool.p_url])
		
		if not c.pool:
			return redirect(request.referer)
		self._clean_session()
			
	def _create_groupgift(self):
		c.pool = websession.get('pool')
		if c.pool is None:
			c.messages.append(_("POOL_PAGE_ERROR_POOL_DOES_NOT_EXIST"))
			return redirect(url('home'))
		elif c.pool.product is None:
			c.messages.append(_("POOL_CREATE_Product was unknown, what can I do?"))
			return redirect(url('home'))
		elif c.pool.occasion is None:
			c.messages.append(_("POOL_CREATE_Occasion was unknown, what can I do?"))
			return redirect(url('home'))
		elif c.pool.receiver is None:
			c.messages.append(_("POOL_CREATE_Receiver was unknown, what can I do?"))
			return redirect(url('home'))
		
		admin = PoolUser(**c.user.get_map())
		if h.users_equal(c.pool.receiver, admin):
			admin.profile_picture_url = c.pool.receiver.profile_picture_url
		admin.is_admin = True
		
		#### Setting up the Pool for initial Persisting
		c.pool.participants.append(admin)
		locals = {"admin_name":admin.name, "receiver_name" : c.pool.receiver.name, "occasion_name":c.pool.occasion.get_display_name()}
		c.pool.description = (_("INVITE_PAGE_DEFAULT_MSG_%(admin_name)s has created a Friend Fund for %(receiver_name)s's %(occasion_name)s. Come and chip in!")%locals)
		remote_profile_picture_render.delay([(pu.network, pu.network_id, pu.large_profile_picture_url or pu.profile_picture_url) for pu in c.pool.participants])
		
		c.pool.merchant_domain = request.merchant.domain
		g.dbm.set(c.pool, merge = True, cache=False)
		remote_product_picture_render.delay(c.pool.p_url, c.pool.product.picture)
		remote_pool_picture_render.apply_async(args=[c.pool.p_url])
		
		if not c.pool:
			return redirect(request.referer)
		self._clean_session()
		return redirect(url('invite_index',  pool_url = c.pool.p_url))
	
	@jsonify
	def chat(self, pool_url):
		if request.method == 'POST':
			if('comment' in request.params):
				comment = request.params['comment']
				if comment:
					c.comment = PoolComment(u_id = c.user.u_id, p_url = pool_url, comment = comment)
					g.dbm.set(c.comment)
					c.comment.name = c.user.name
					c.comment.profile_picture_url = c.user.profile_picture_url
					c.comment.created = datetime.datetime.now()
					return {'data':{'html':self.render("/pool/comment.html").strip()}}
				else:
					return {'data':{'html':''}}
		else:
			c.pool_url = pool_url
			c.chat = g.dbm.get(PoolChat, p_url = pool_url)
			if len(c.chat.comments) > self.chat_page_size:
				c.chat.comments = c.chat.comments[:self.chat_page_size]
				c.offset = self.chat_page_size
			else:
				c.offset = 0
			return {'html':render("/pool/chat.html").strip()}

	@jsonify
	def chatmore(self, pool_url):
		c.pool_url = pool_url
		offset = int(request.params.get('offset', 0))
		c.chat = g.dbm.get(PoolChat, p_url = pool_url).comments or []
		if isinstance(c.chat, PoolComment): c.chat = [c.chat]
		
		if len(c.chat)-offset > self.chat_page_size:
			c.offset = offset+self.chat_page_size
		else:
			c.offset = 0
		c.chat = c.chat[offset:offset+self.chat_page_size]
		return {'data':{'offset':c.offset, 'has_more':bool(c.offset), 'html':render("/pool/chat_content.html").strip()}}
	
	@logged_in(ajax=False)
	def addresses(self, pool_url):
		c.pool_url = pool_url
		c.psettings = g.dbm.get(PoolSettings, p_url = pool_url, u_id = c.user.u_id)
		if not c.psettings.is_admin or c.psettings.is_closed():
			return redirect(url('get_pool', pool_url=pool_url))
		c.user.set_am_i_admin(pool_url, c.psettings.is_admin)
		c.shipping_values = to_displaymap(c.psettings.addresses.get("shipping"))
		c.shipping_errors = {}
		c.billing_values = to_displaymap(c.psettings.addresses.get("billing"))
		c.billing_errors = {}
		return self.render('/pool/settings_address_admin.html')
	
	@logged_in(ajax=False)
	def settings(self, pool_url):
		c.pool_url = pool_url
		c.psettings = g.dbm.get(PoolSettings, p_url = pool_url, u_id = c.user.u_id)
		if not c.psettings:
			c.messages.append("POOL_SETTINGS_Pool not found")
			return redirect(url('home'))
		c.user.set_am_i_admin(pool_url, c.psettings.is_admin)
		c.shipping_values = to_displaymap(c.psettings.addresses.get("shipping"))
		c.shipping_errors = {}

		if c.psettings.is_admin and not c.psettings.is_closed():
			c.billing_values = to_displaymap(c.psettings.addresses.get("billing"))
			c.billing_errors = {}
			return self.render('/pool/settings_admin.html')
		else:
			return redirect(url('get_pool', pool_url=pool_url))
	
	@jsonify
	@logged_in(ajax=True)
	@post_only(ajax=True)
	def edit_thankyou(self, pool_url):
		if c.pool is None:
			return self.ajax_messages(_("POOL_PAGE_ERROR_POOL_DOES_NOT_EXIST"))
		if not c.pool.am_i_receiver(c.user):
			return self.ajax_messages(_(NOT_AUTHORIZED_MESSAGE))
		c.pool_url = pool_url
		c.edit = True
		return {'html':render('/pool/parts/receiver_thank_you.html').strip()}
	
	@jsonify
	@logged_in(ajax=True)
	@post_only(ajax=True)
	def set_thankyou(self, pool_url):
		if c.pool is None:
			c.messages.append(_("POOL_PAGE_ERROR_POOL_DOES_NOT_EXIST"))
			return {"redirect" : request.referer}
		if not c.pool.am_i_receiver(c.user):
			return self.ajax_messages(_(NOT_AUTHORIZED_MESSAGE))
		c.pool_url = pool_url
		c.edit = False
		thankyou = request.params.get('thankyou', None)
		if thankyou:
			g.dbm.set(PoolThankYouMessage(p_url = pool_url, message = thankyou))
			c.pool.thank_you_message = thankyou
			g.dbm.push_to_cache(c.pool)
		return {'data':{'success':True, 'html':render('/pool/parts/receiver_thank_you.html').strip()}}
		
	@jsonify
	@logged_in(ajax=True)
	@post_only(ajax=True)
	def edit_description(self, pool_url):
		if c.pool is None:
			return self.ajax_messages(_("POOL_PAGE_ERROR_POOL_DOES_NOT_EXIST"))
		if not c.pool.am_i_admin(c.user):
			return self.ajax_messages(_(NOT_AUTHORIZED_MESSAGE))
		c.pool_url = pool_url
		c.edit = True
		return {'html':render('/pool/parts/description.html').strip()}
	
	@jsonify
	@logged_in(ajax=True)
	@post_only(ajax=True)
	def set_description(self, pool_url):
		if c.pool is None:
			c.messages.append(_("POOL_PAGE_ERROR_POOL_DOES_NOT_EXIST"))
			return {"redirect" : request.referer}
		if not c.pool.am_i_admin(c.user):
			return self.ajax_messages(_(NOT_AUTHORIZED_MESSAGE))
		c.pool_url = pool_url
		c.edit = False
		
		description = request.params.get('description', None)
		if description:
			g.dbm.set(PoolDescription(p_url = pool_url, description = description))
			c.pool.description = description
			g.dbm.push_to_cache(c.pool)
		return {'data':{'success':True, 'html':render('/pool/parts/description.html').strip()}}
	
	@jsonify
	@logged_in(ajax=True)
	@post_only(ajax=True)
	def edit_address(self, pool_url):
		c.pool_url = pool_url
		c.countries = g.countries.list
		c.psettings = g.dbm.get(PoolSettings, p_url = pool_url, u_id = c.user.u_id)
		if not c.user.am_i_admin(pool_url):
			return self.ajax_messages(_(NOT_AUTHORIZED_MESSAGE))
		type = str(request.params.get('type'))
		if not type in ['billing', 'shipping']:
			return self.ajax_messages(_(NOT_AUTHORIZED_MESSAGE))
		setattr(c, '%s_values' % type, to_displaymap(c.psettings.addresses.get(type)))
		setattr(c, '%s_errors' % type, {})
		return {"html":render('/pool/actions/%s_form.html' % type).strip()}
	@jsonify
	@logged_in(ajax=True)
	@post_only(ajax=True)
	def unedit_address(self, pool_url):
		c.pool_url = pool_url
		c.psettings = g.dbm.get(PoolSettings, p_url = pool_url, u_id = c.user.u_id)
		type = str(request.params.get('type'))
		if not type in ['billing', 'shipping']:
			return self.ajax_messages(_(NOT_AUTHORIZED_MESSAGE))
		setattr(c, '%s_values' % type, to_displaymap(c.psettings.addresses.get(type)))
		setattr(c, '%s_errors' % type, {})
		return {"html":render('/pool/actions/%s_display.html' % type).strip()}

		
	@jsonify
	@logged_in()
	@post_only()
	def set_address(self, pool_url):
		c.pool_url = pool_url
		c.countries = g.countries.list
		if not c.user.am_i_admin(pool_url):
			return self.ajax_messages(_(NOT_AUTHORIZED_MESSAGE))
		form = formencode.variabledecode.variable_decode(request.params).get('shipping', None)
		if not form:
			form = formencode.variabledecode.variable_decode(request.params).get('billing', None)
			type = 'billing'
			schema = BillingAddressForm()
		else:
			type='shipping'
			schema = ShippingAddressForm()
		try:
			form_result = schema.to_python(form, state = FriendFundFormEncodeState)
		except formencode.validators.Invalid, error:
			c.psettings = g.dbm.get(PoolSettings, p_url = pool_url, u_id = c.user.u_id)
			setattr(c, '%s_values' % type, error.value)
			setattr(c, '%s_errors' % type, error.error_dict or {})
			return {"html":render('/pool/actions/%s_form.html' % type).strip()}
		else:
			c.psettings = PoolSettings(p_url = pool_url, u_id = c.user.u_id)
			c.psettings.addresses[type] = ShippingAddress(**form_result)
			c.psettings.addresses[type].type = type
			g.dbm.set(c.psettings)
			c.psettings = g.dbm.get(PoolSettings, p_url = pool_url, u_id = c.user.u_id)
			setattr(c, '%s_values' % type, to_displaymap(c.psettings.addresses.get(type)))
			setattr(c, '%s_errors' % type, {})
		return {"html":render('/pool/actions/%s_display.html' % type).strip()}
	
	@logged_in(ajax=False)
	def close(self, pool_url):
		c.pool_url = pool_url
		c.psettings = g.dbm.get(PoolSettings, p_url = pool_url, u_id = c.user.u_id)
		if not (c.psettings.is_admin and c.psettings.is_funded()):
			c.messages.append(_(NOT_CORRECT_STATE))
			return redirect(url(controller='pool', action='settings', pool_url=pool_url))
		elif c.psettings.information_complete(c.pool):
			try:
				g.dbm.set(ClosePoolProc(p_url = pool_url))
				g.dbm.expire(Pool(p_url = pool_url))
			except db_access.SProcException,e:
				c.messages.append(e)
				return redirect(url('ctrlpoolindex', controller='pool', pool_url=pool_url))
			except db_access.SProcWarningMessage,e:
				c.messages.append(e)
			return redirect(url('get_pool', pool_url=pool_url))
		else:
			c.messages.append(_(SAVE_ADDRESS_FIRST))
			return redirect(url(controller='pool', action='addresses', pool_url=pool_url))
	
	@logged_in(ajax=False)
	def action(self, pool_url):
		action = str(request.params['action'])
		if not c.user.am_i_admin(pool_url) or action not in POOLACTIONS:
			c.messages.append(_(NOT_AUTHORIZED_MESSAGE))
			return redirect(url(controller='pool', action='settings', pool_url=pool_url))
		g.dbm.set(ExtendActionPoolProc(p_url = pool_url
										, name=action
										, expiry_date=request.params.get('expiry_date', None)
										, message=request.params['message']))
		if action=="ADMIN_ACTION_INVITE":
			return redirect(url('invite_index',  pool_url = pool_url))
		return redirect(url(controller='pool', action='settings', pool_url=pool_url))
	
	@jsonify
	def widget(self, pool_url):
		if not c.pool.am_i_member(c.user):
			return self.ajax_messages(_(NOT_AUTHORIZED_MESSAGE))
		else:
			return {"popup":render("/pool/parts/widget.html").strip()}
		