from datetime import datetime, timedelta
from friendfund.lib import helpers as h
from friendfund.model.mapper import DBMappedObject, GenericAttrib, DBMapper, DBMapping
from pylons import app_globals as g, request
_ = lambda x: x
POOLACTIONS = {
		"ADMIN_ACTION_INVITE":{"title":_("POOLACTIONS_INVITE_TITLE_Invite more friends to help out!"),
					"subtitle":_("POOLACTIONS_INVITE_SUBTITLE_Extending the pool's runtime and inviting more friends with a fresh message might help you get this pool completed, try it now!")
				},
		"ADMIN_ACTION_REMIND_INVITEES":{"title":_("POOLACTIONS_REMIND_INVITEES_TITLE_"), 
						"subtitle":_("POOLACTIONS_REMIND_INVITEES_SUBTITLE_")},
		"ADMIN_ACTION_ASK_RECEIVER":{"title":_("POOLACTIONS_ASK_RECEIVER_TITLE_"), 
						"subtitle":_("POOLACTIONS_ASK_RECEIVER_SUBTITLE_")},
		"ADMIN_ACTION_ASK_CONTRIBUTORS":{"title":_("POOLACTIONS_ASK_CONTRIBUTORS_TITLE_"), 
						"subtitle":_("POOLACTIONS_ASK_CONTRIBUTORS_SUBTITLE_")},
		"ADMIN_ACTION_ASK_CONTRIBUTORS_TO_INVITE":{"title":_("POOLACTIONS_ASK_CONTRIBUTORS_TO_INVITE_TITLE_"), 
						"subtitle":_("POOLACTIONS_ASK_CONTRIBUTORS_TO_INVITE_SUBTITLE_")},
		"ADMIN_ACTION_CHEAPER_PRODUCT":{"title":_("POOLACTIONS_CHEAPER_PRODUCT_TITLE_"), 
						"subtitle":_("POOLACTIONS_CHEAPER_PRODUCT_SUBTITLE_")},
		"ADMIN_ACTION_CHIP_IN_REMAINDER":{"title":_("POOLACTIONS_CHIP_IN_REMAINDER_TITLE_"), 
						"subtitle":_("POOLACTIONS_CHIP_IN_REMAINDER_SUBTITLE_")},
		"ADMIN_ACTION_ISSUE_GIFT_VOUCHERS":{"title":_("POOLACTIONS_ISSUE_GIFT_VOUCHERS_TITLE_"), 
						"subtitle":_("POOLACTIONS_ISSUE_GIFT_VOUCHERS_SUBTITLE_")}
	}
	
from pylons.i18n import ugettext
class PoolAction(DBMappedObject):
	"""
		<POOL_ACTION action="ASK_CONTRIBUTORS_TO_INVITE" closing="0" remaining="1" />
	"""
	_get_root = _set_root = "POOL_ACTION"
	_unique_keys = ['name', 'is_closing', 'remaining']
	_keys = [GenericAttrib(str, 'name', 'name')
			,GenericAttrib(bool, 'is_extending', 'is_extending')
			,GenericAttrib(int, 'remaining', 'remaining')
			]
	def get_profile_pic(self, type="RA"):
		return h.get_user_picture(self.profile_picture_url, type)	
		
	def contains_message(self):
		return self.name in [ 'ADMIN_ACTION_REMIND_INVITEES'
							, 'ADMIN_ACTION_INVITE'
							, 'ADMIN_ACTION_ASK_RECEIVER'
							, 'ADMIN_ACTION_ASK_CONTRIBUTORS_TO_INVITE'
							, 'ADMIN_ACTION_ASK_CONTRIBUTORS']
	def is_extending(self):
		return self.name in [ 'ADMIN_ACTION_REMIND_INVITEES'
							, 'ADMIN_ACTION_INVITE'
							, 'ADMIN_ACTION_ASK_RECEIVER'
							, 'ADMIN_ACTION_ASK_CONTRIBUTORS_TO_INVITE'
							, 'ADMIN_ACTION_ASK_CONTRIBUTORS']
	def has_product_search(self):
		return self.name in ["ADMIN_ACTION_CHEAPER_PRODUCT"]
	def has_payment(self):
		return self.name in ["ADMIN_ACTION_CHIP_IN_REMAINDER"]
	def is_gift_vouchers(self):
		return self.name in ["ADMIN_ACTION_ISSUE_GIFT_VOUCHERS"]
	def includes_friends(self):
		return self.name in [ 'ADMIN_ACTION_REMIND_INVITEES'
							, 'ADMIN_ACTION_INVITE'
							, 'ADMIN_ACTION_ASK_RECEIVER'
							, 'ADMIN_ACTION_ASK_CONTRIBUTORS_TO_INVITE'
							, 'ADMIN_ACTION_ASK_CONTRIBUTORS']
	
	def return_related_people(self, pool):
		return []
	
	def get_display_name(self):
		return ugettext(self.name)
	def get_display_title(self):
		return ugettext(POOLACTIONS.get(self.name, {}).get("title")) or self.get_display_name()
	def get_display_subtitle(self):
		return ugettext(POOLACTIONS.get(self.name, {}).get("subtitle", ""))
	
	def fromDB(self, xml):
		if not POOLACTIONS.get(self.name):
			log.error("ValueError: ADMIN ACTION Not None", self.name)
	
	
class ShippingAddress(DBMappedObject):
	_set_root = _get_root = 'ADDRESS'
	_keys = [	 GenericAttrib(unicode,'line1'  ,'line1'  )
				,GenericAttrib(unicode,'line2'  ,'line2'  )
				,GenericAttrib(unicode,'line3'  ,'line3'  )
				,GenericAttrib(unicode,'zipcode','zipcode')
				,GenericAttrib(unicode,'country','country')
				,GenericAttrib(unicode,'phone'  ,'phone'  )
				,GenericAttrib(str,'type'  ,'type'  )
			]

class PoolSettings(DBMappedObject):
	"""
		<RESULT status="0" proc_name="get_pool_settings">
			<SETTINGS p_url="UC0xMTEzOQ~~" expiry_date="2009-12-19" is_extended="0" is_admin="1" 
					description="YYY has created a Friend Fund for XXX's 
								CHRISTMAS, come and chip in!" is_funded="0">
				<ADDRESS/>
				<POOL_ACTION name="INVITE" is_closing="0" remaining="-1"/>
			</SETTINGS>
		</RESULT>
	"""
	_cachable = False # TODO: this should be cached for a while and expired when done, dont work yet
	_get_root = _set_root = 'SETTINGS'
	_unique_keys = ['p_url']
	_set_proc   = 'app.set_pool_settings'
	_get_proc   = 'app.get_pool_settings'
	_keys = [	 GenericAttrib(str ,'p_url'       , 'p_url' )
				,GenericAttrib(int,'u_id'         , 'u_id'  )
				,GenericAttrib(datetime           , 'expiry_date','expiry_date')
				,GenericAttrib(unicode            , 'description','description')
				,GenericAttrib(str,'status'       , 'status')
				,GenericAttrib(str,'phase'        , 'phase')
				,GenericAttrib(str,'region'       , 'region')
				,GenericAttrib(str,'shipping_country', 'shipping_country')
				,GenericAttrib(bool,'is_admin'    , 'is_admin')
				,GenericAttrib(bool, 'is_virtual' , 'is_virtual')
				, GenericAttrib(unicode			  ,	'merchant_key', 	'merchant_key')
				,DBMapper(ShippingAddress         , 'addresses','ADDRESS', is_dict = True, dict_key = lambda x: (x.type or 'shipping').lower())
				,DBMapper(PoolAction, 'actions'   , 'POOL_ACTION', is_list = True)
			]
	
	def get_internal_expiry_date(self, value = 0):
		return self.expiry_date and h.format_date_internal(self.expiry_date + timedelta(value)) or ''
	def get_require_addresses(self):
		return not(self.is_virtual or not request.merchant.get_setting("require_address"))
	require_addresses = property(get_require_addresses)

	def information_complete(self):
		return not self.require_addresses or \
				(self.shipping_address.line1 and
				self.shipping_address.line2 and 
				self.shipping_address.line3 and 
				self.shipping_address.zipcode and 
				self.billing_address.line1 and
				self.billing_address.line2 and 
				self.billing_address.line3 and 
				self.billing_address.zipcode and 
				self.billing_address.country)
				
	def is_closed(self):
		return self.status in ["CLOSED", "COMPLETE"]
	def is_expired(self):
		return self.phase in ["EXPIRED"]
	def is_funded(self):
		return self.status == "FUNDED"
	def is_contributable(self):
		return self.status == "OPEN" and (self.phase == "INITIAL" or self.phase == "EXTENDED")
	
	def fromDB(self, xml):
		self.region = self.region.lower()
		self.__dict__['shipping_address'] = self.addresses.get("shipping")
		self.__dict__['billing_address'] = self.addresses.get("billing")
		if not "billing" in self.addresses and self.addresses.get("shipping"):
			self.addresses["billing"] = ShippingAddress(country = self.addresses.get("shipping").country)

class ClosePoolProc(DBMappedObject):
	"""
		exec [app].[set_pool_closed]'<POOL p_url ="UC0xMTEwNQ~~"/>'
	"""
	_get_root = _set_root = 'POOL'
	_unique_keys = ['p_url']
	_get_proc = _set_proc   = 'app.set_pool_closed'
	_keys = [GenericAttrib(str ,'p_url'       ,'p_url' )]

class ExtendActionPoolProc(DBMappedObject):
	"""
		exec app.extending_action '<ACTION p_url ="UC0xMTE0Nw~~" name ="ASK_RECEIVER" expiry_date="12-12-2010" message= "yeah yeh" />'
	"""
	_get_root = _set_root = 'ACTION'
	_unique_keys = ['p_url']
	_get_proc = _set_proc   = 'app.extending_action'
	_keys = [GenericAttrib(str      ,'p_url'      ,'p_url' )
			,GenericAttrib(str      ,'name'       ,'name' )
			,GenericAttrib(datetime ,'expiry_date','expiry_date' )
			,GenericAttrib(unicode  ,'message'    ,'message' )
	]
