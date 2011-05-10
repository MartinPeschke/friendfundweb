from __future__ import with_statement
import logging, formencode, datetime, itertools
from operator import attrgetter
from babel import Locale
from pylons import request, response, session as websession, tmpl_context as c, url, app_globals, cache
from pylons.controllers.util import abort, redirect
from pylons.decorators import jsonify

from friendfund.lib import fb_helper, tw_helper, helpers as h
from friendfund.lib.auth.decorators import logged_in, pool_available
from friendfund.lib.base import BaseController, render, render_def, SuccessMessage, ErrorMessage
from friendfund.lib.i18n import FriendFundFormEncodeState, friendfund_formencode_gettext
from friendfund.model import db_access
from friendfund.model.forms.common import to_displaymap, DecimalValidator
from friendfund.model.forms.pool import PoolHomePageForm, PoolAddressForm, PoolEditPageForm
from friendfund.model.pool import Pool, PoolThankYouMessage, UpdatePoolProc
from friendfund.model.product import Product
from friendfund.model.poolsettings import PoolAddress
from friendfund.services.pool_service import MissingPoolException, MissingProductException, MissingOccasionException, MissingReceiverException


from friendfund.lib.base import _
log = logging.getLogger(__name__)

class PoolEditController(BaseController):
	
	@logged_in(ajax=False)
	@pool_available(admin_only=True)
	def index(self, pool_url):
		c.values = {"title":c.pool.title, "description":c.pool.description}
		c.parser_values = app_globals.product_service.get_parser_values_from_product(c.pool.product)
		c.errors = {}
		if request.method != "POST":
			return self.render("/pool/edit.html")
		else:
			try:
				c._ = friendfund_formencode_gettext
				c.request = request
				pool_schema = PoolEditPageForm.to_python(request.params, state = c)
				updates = UpdatePoolProc(p_url = pool_url, **pool_schema)
				
				if h.contains_one_ne(pool_schema, ["product_name", "product_description", "product_picture"]):
					updates.product = Product(name = pool_schema.get("product_name")
								,description = pool_schema.get("product_description")
								,picture = pool_schema.get("product_picture"))
				app_globals.dbm.set(updates)
				app_globals.dbm.expire(Pool(p_url = c.pool.p_url))
			except formencode.validators.Invalid, error:
				c.values = error.value
				c.errors = error.error_dict or {}
				c.messages.append(ErrorMessage(_("FF_POOL_DETAILS_PAGE_ERRORBAND_Please correct the Errors below")))
				return self.render('/pool/edit.html')
			return redirect(url("get_pool", pool_url=pool_url))
	
	@logged_in(ajax=False)
	@pool_available(admin_only=True)
	def delete(self, pool_url):
		log.error("POOL_DELETE_NOT_IMPLEMENTED")
		return redirect(request.referer)
	
	@logged_in(ajax=False)
	@pool_available(contributable_only = True)
	def join(self, pool_url):
		if not c.pool.am_i_member(c.user):
			app_globals.pool_service.invite_myself(pool_url, c.user)
			c.messages.append(SuccessMessage(_("FF_POOL_PAGE_You Joined the Pool!")))
		return redirect(url("get_pool", pool_url=pool_url))

	@jsonify
	@logged_in(ajax=False)
	@pool_available(contributable_only = True)
	def leave_popup(self, pool_url):
		if c.pool.am_i_member(c.user):
			return {"popup":render("/pool/parts/leave_popup.html").strip()}
		else:
			return {"success":False}

	
	@logged_in(ajax=False)
	@pool_available(admin_only=True)
	def address(self, pool_url):
		if not request.merchant.require_address:
			log.error(NOT_AUTHORIZED_MESSAGE)
			return redirect(url("get_pool", pool_url = pool_url))
		elif c.pool.is_closed():
			return redirect(url('pool_action', pool_url=pool_url, action='complete'))
		c.values = {}
		c.errors = {}
		address = app_globals.dbm.get(PoolAddress, p_url = pool_url)
		if address:
			c.values = address.to_map()
		territories = Locale.parse(h.get_language_locale()).territories
		c.countries = []
		for country in request.merchant.shippping_countries:
			c.countries.append((country.iso2, territories.get(country.iso2, country.iso2)))
		
		if request.method == 'GET':
			return self.render("/pool/address.html")
		else:
			try:
				schema=PoolAddressForm()
				c.values = schema.to_python(request.params)
				address = app_globals.dbm.set(PoolAddress(p_url = pool_url, **c.values))
				c.messages.append(SuccessMessage(_("FF_ADDRESS_Changes saved!")))
			except formencode.validators.Invalid, error:
				c.errors = error.error_dict or {}
				c.values = error.value
				c.messages.append(ErrorMessage(_("FF_ADDRESS_Please correct the Errors below")))
				return self.render("/pool/address.html")
			else:
				return redirect(url.current())

	@jsonify
	@logged_in(ajax=True)
	@pool_available()
	def editThankYouMessage(self, pool_url):
		if request.method == "GET":
			c.message = request.params.get('value')
			return {'html':render('/widgets/thankyoumessage_editor.html').strip()}
		else:
			c.message = request.params.get('value')
			if c.message:
				app_globals.dbm.set(PoolThankYouMessage(p_url = pool_url, message=c.message))
				app_globals.dbm.expire(Pool(p_url = c.pool.p_url))
			return {'html':render('/widgets/thankyoumessage_editor.html').strip()}