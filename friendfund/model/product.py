from babel.numbers import format_currency
from friendfund.lib import helpers as h
from friendfund.model.mapper import DBMappedObject, GenericAttrib, DBMapper, GenericElement, DBMapping

from pylons import session as websession, app_globals
from pylons.i18n import ugettext as _


class Product(DBMappedObject):
	_get_root = _set_root = 'PRODUCT'
	_unique_keys = ['aff_net','name','aff_program_id']
	_keys = [	 GenericAttrib(str     ,'guid'                     , 'guid'                     )
				,GenericAttrib(unicode ,'merchant'                 , 'merchant'                 )
				,GenericAttrib(str     ,'aff_net'                  , 'aff_net'                  )
				,GenericAttrib(str     ,'aff_id'                   , 'aff_id'                   )
				,GenericAttrib(str     ,'aff_program_id'           , 'aff_program_id'           )
				,GenericAttrib(unicode ,'aff_program_name'         , 'aff_program_name'         )
				,GenericAttrib(int     ,'amount'                    , 'amount'                   )
				,GenericAttrib(int     ,'shipping_cost'            , 'shipping_cost'            )
				,GenericAttrib(str     ,'currency'                 , 'currency'                 )
				,GenericAttrib(int     ,'category'                 , 'category'                 )
				,GenericElement(unicode,'name'                     , 'NAME'                     )
				,GenericElement(unicode,'description'              , 'DESCRIPTION'              )
				,GenericElement(unicode,'description_long'         , 'DESCRIPTION_LONG'         )
				,GenericElement(unicode,'manufacturer'             , 'MANUFACTURER'             )
				,GenericAttrib(str     ,'delivery_time'            , 'delivery_time'            )
				,GenericAttrib(str     ,'ean'                      , 'ean'                      )
				,GenericAttrib(bool    ,'is_virtual'               , 'is_virtual'               )
				,GenericAttrib(bool    ,'is_curated'               , 'is_curated'               )
				,GenericAttrib(bool    ,'is_amazon'                , None                       , persistable = False)
				,GenericAttrib(bool    ,'is_pending'               , None                       , persistable = False)
				,GenericAttrib(str     ,'aff_program_logo_url'     , 'aff_program_logo_url'     )
				,GenericAttrib(str     ,'aff_program_delivery_time', 'aff_program_delivery_time')
				,GenericAttrib(unicode ,'picture_small'            , 'picture_small'            )
				,GenericAttrib(unicode ,'picture_large'            , 'picture_large'            )
				,GenericAttrib(unicode ,'product_picture_url'      , 'product_picture_url'      )
				,GenericAttrib(unicode ,'tracking_link'            , 'tracking_link'            )
				,GenericAttrib(str     ,'_deliveryTime'            , None                       , persistable = False)
				,GenericAttrib(str     ,'_deliveryTimeWarnOffset'  , None                       , persistable = False)
				]
	
	def to_map(self):
		return dict([(k.pykey,getattr(self, k.pykey)) for k in self._keys])
	
	def get_price_float(self, include_shipping = True):
		return float(self.amount + (include_shipping and self.shipping_cost or 0))/100
	def get_display_price(self, extended = True, include_shipping = True):
		return h.format_currency(self.get_price_float(include_shipping), self.currency, extended)
	
	display_price = property(get_display_price)
	def get_shipping_cost_float(self):
		return float(self.shipping_cost)/100
	def get_shipping_price(self):
		if self.shipping_cost:
			return '(PP: %s)' %h.format_currency(self.get_shipping_cost_float(), self.currency)
		else:
			return ''
	display_shipping = property(get_shipping_price)
	
	def get_product_pic(self, type="POOL"):
		return h.get_product_picture(self.product_picture_url, type)
	
	def get_display_name(self):
		if self.is_pending:
			return _("PENDING_PRODUCT_NAME")
		else:
			return h.word_truncate_plain(self.name.title(), 2)
	
	def get_display_label(self, extended = True, words = 5, seperator = ' '):
		if self.is_pending:
			return _("PENDING_PRODUCT_NAME")
		else:
			return '%s%s%s' % (h.word_truncate_plain(self.name, words), seperator, self.get_display_price(extended))
	display_label = property(get_display_label)
	
	def fromDB(self, xml):
		self.is_virtual = self.is_virtual or False
		self.is_pending = self.name.startswith( "PENDING_PRODUCT" )
		self.is_pending_ask_friend = self.name ==  "PENDING_PRODUCT_NOMINATE"
		self.is_pending_receiver = self.name ==  "PENDING_PRODUCT_ASK_RECEIVER"

class PendingProduct(Product):
	def set_picture_urls(self, base_url):
		self.picture_small = "%s%s"%(base_url, self.picture_small)
		self.picture_large = "%s%s"%(base_url, self.picture_large)
	def get_price_float(self, include_shipping = True):
		return 0
	def get_shipping_cost_float(self):
		return 0
	def get_display_price(self, extended = True, include_shipping = True):
		return ''
	def get_display_label(self, extended = True):
		return _("PENDING_PRODUCT_NAME")
		
class ProductRetrieval(DBMappedObject):
	"""
		exec imp.get_product_with_guid '<SEARCH  guid="0071831d-a57e-454f-9476-9317f45daf1f" region="DE"/>'
	"""
	_cacheable = False
	_get_root = None
	_set_root = 'SEARCH'
	_get_proc = _set_proc = 'imp.get_product_with_guid'
	_unique_keys = ['guid']
	_keys = [	 GenericAttrib(str,'guid'      ,'guid')
				,GenericAttrib(str,'region'      ,'region')
				,GenericAttrib(bool,'is_curated'      ,'is_curated')
				,DBMapper(Product, 'product', 'PRODUCT')
			]

class ProductSuggestion(DBMappedObject):
	_expiretime = 10
	_get_root = _set_root = 'PRODUCT_SUGGESTION'
	_unique_keys = ['name', 'search', 'aff_net_ref']
	_keys = [	 GenericAttrib(str,'name'           ,'name')
				,GenericAttrib(str,'search'         ,'search')
				,GenericAttrib(str,'aff_net'        ,'aff_net')
				,GenericAttrib(str,'aff_net_ref'    ,'aff_net_ref')
				,GenericAttrib(bool,'is_virtual'    ,'is_virtual')
				,GenericAttrib(str,'sort'    ,'sort')
				,GenericAttrib(str,'help_link_title'    ,'help_link_title')
				,GenericAttrib(str,'help_link_href'    ,'help_link_href')
				,GenericAttrib(str,'picture_url'    ,'product_picture_url')
			]


class ProductSuggestionSearch(DBMappedObject):
	""" 
		exec imp.get_product_suggestion_group 
		'<PRODUCT_SUGGESTION country = "DE" occasion = "BIRTHDAY" receiver_sex = "m"/>';
	"""
	_expiretime = 10
	_get_root = None
	_set_root = 'PRODUCT_SUGGESTION'
	_get_proc   = 'imp.get_product_suggestion_group'
	_keys = [	 GenericAttrib(str,'country'         ,'country')
				,GenericAttrib(str,'occasion'        ,'occasion')
				,GenericAttrib(str,'receiver_sex'    ,'receiver_sex')
				,DBMapper(ProductSuggestion, 'suggestions','PRODUCT_SUGGESTION', is_list = True)
			]

class SetAltProductProc(DBMappedObject):
	""" 
		[app].[add_alternative_product]
	"""
	_cachable = False
	_get_root = _set_root = 'POOL'
	_get_proc = _set_proc = 'app.add_alternative_product'
	_keys = [	 GenericAttrib(str,'p_url'         ,'p_url')
				,DBMapper(Product, 'product', 'PRODUCT')
			]
			
class SwitchProductVouchersProc(DBMappedObject):
	""" 
		exec app.switch_product_vouchers'<POOL p_url ="UC0xMTE0OA~~"/>'
	"""
	_cachable = False
	_get_root = _set_root = 'POOL'
	_get_proc = _set_proc = 'app.switch_product_vouchers'
	_keys = [GenericAttrib(str,'p_url'         ,'p_url')]


class SetPendingProductProc(DBMappedObject):
	""" 
		app.add_pending_product
	"""
	_cachable = False
	_get_root = _set_root = 'POOL'
	_get_proc = _set_proc = 'app.add_pending_product'
	_keys = [	 GenericAttrib(str,'p_url'         ,'p_url')
				,DBMapper(Product, 'product', 'PRODUCT')
			]