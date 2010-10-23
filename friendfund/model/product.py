from babel.numbers import format_currency
from friendfund.lib import helpers as h
from friendfund.model.mapper import DBMappedObject, GenericAttrib, DBMapper, GenericElement, DBMapping

from pylons import session as websession


class Product(DBMappedObject):
	_get_root = _set_root = 'PRODUCT'
	_unique_keys = ['aff_net','name','aff_program_id']
	_keys = [	 GenericAttrib(str,'guid'                   , 'guid'             )
				,GenericAttrib(unicode,'merchant'           , 'merchant'         )
				,GenericAttrib(str,'aff_net'                , 'aff_net'          )
				,GenericAttrib(str,'aff_id'                 , 'aff_id'           )
				,GenericAttrib(str,'aff_program_id'         , 'aff_program_id'   )
				,GenericAttrib(unicode,'aff_program_name'   , 'aff_program_name' )
				,GenericAttrib(int,'price'                  , 'amount'           )
				,GenericAttrib(int,'shipping_cost'          , 'shipping_cost'    )
				,GenericAttrib(str,'currency'               , 'currency'         )
				,GenericAttrib(int,'category'               , 'category'         )
				,GenericElement(unicode,'name'              , 'NAME'             )
				,GenericElement(unicode,'description'       , 'DESCRIPTION'      )
				,GenericElement(unicode,'description_long'  , 'DESCRIPTION_LONG' )
				,GenericElement(unicode,'manufacturer'      , 'MANUFACTURER'     )
				,GenericAttrib(str,'delivery_time'          , 'delivery_time'    )
				,GenericAttrib(str,'ean'                    , 'ean'              )
				,GenericAttrib(str,'aff_program_logo_url'   , 'aff_program_logo_url')
				,GenericAttrib(str,'aff_program_delivery_time'  , 'aff_program_delivery_time')
				,GenericAttrib(unicode,'picture_small'      , 'picture_small'    )
				,GenericAttrib(unicode,'picture_large'      , 'picture_large'    )
				,GenericAttrib(unicode,'product_picture_url', 'product_picture_url'    )
				,GenericAttrib(unicode,'tracking_link'      , 'tracking_link'    )
				,GenericAttrib(str,'_deliveryTime'          , None)
				,GenericAttrib(str,'_deliveryTimeWarnOffset', None)
				]
	
	def to_map(self):
		return dict([(k.pykey,getattr(self, k.pykey)) for k in self._keys])
	
	def get_price_float(self):
		return float(self.price)/100
	def get_display_price(self):
		return h.format_currency(self.get_price_float(), self.currency)
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
	
	def get_display_label(self):
		return '%s %s' % (h.word_truncate_plain(self.name, 5), self.display_price)
	display_label = property(get_display_label)
	
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
				,DBMapper(Product, 'product', 'PRODUCT')
			]
class ProductSearch(DBMappedObject):
	"""
		exec app.search_product'<SEARCH category ="garden" program_id ="123" search="schloss" page_no="1" region="de"/>'
	"""
	_get_root = _set_root = 'SEARCH'
	_get_proc = _set_proc = 'imp.search_product'
	_unique_keys = ['region', 'program_id', 'search', 'category', 'page_no']
	_cacheable = False
	_keys = [	 GenericAttrib(str,'region'      ,'region')
				,GenericAttrib(str,'search'      ,'search')
				,GenericAttrib(int,'max_price'      ,'max_price')
				,GenericAttrib(str,'program_id'  ,'program_id')
				,GenericAttrib(int,'category'    ,'category')
				,GenericAttrib(int,'page_no'     ,'page_no')
				,GenericAttrib(int,'pages'     ,'pages')
				,GenericAttrib(int,'page_size' ,'page_size')
				,GenericAttrib(int,'items' ,'items')
				,GenericAttrib(str,'sort' ,'sort')
				,GenericAttrib(bool,'is_virtual' ,'is_virtual')
				,DBMapper(Product, 'products', 'PRODUCT', is_list = True)
			]
	
	def page_field(self):
		def lower(x):
			return x>2 and x-2 or 1
		def upper(x):
			return x+2<self.pages and x+2 or self.pages
		result = sorted(list(set([1] + range(lower(self.page_no), upper(self.page_no + 1)) + [self.pages] )))
		return result

class ProductSuggestion(DBMappedObject):
	_expiretime = 10
	_get_root = _set_root = 'PRODUCT_SUGGESTION'
	_unique_keys = ['name', 'search', 'aff_net_ref']
	_keys = [	 GenericAttrib(str,'name'           ,'name')
				,GenericAttrib(str,'search'         ,'search')
				,GenericAttrib(str,'aff_net'        ,'aff_net')
				,GenericAttrib(str,'aff_net_ref'    ,'aff_net_ref')
				,GenericAttrib(bool,'is_virtual'    ,'is_virtual')
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

import math 
class ProductDisplay(object):
	def __init__(self, **kwargs):
		self.productlist = kwargs.get('productlist', [])
		self.items_current = int(kwargs.get('items_current', 0))
		self.items_total = int(kwargs.get('items_total', 0))
		self.page_current = int(kwargs.get('page_current', 0))
		self.page_total = int(kwargs.get('page_total', 0))
		self.page_size = int(kwargs.get('page_size', 20))
		self.query = kwargs.get('query', None)
		self._total_pages = None

	def get_total_pages(self):
		if not self._total_pages:
			self._total_pages = int(math.ceil(float(self.items_total) / self.page_size))
		return self._total_pages
	def max_page(self):
		return self.get_total_pages() - 1
	
	def page_field(self):
		def lower(x):
			return x>3 and x-3 or 0
		def upper(x):
			return x+3<self.max_page() and x+3 or self.max_page()
		result = sorted(list(set([0] + range(lower(self.page_current), upper(self.page_current)) + [self.max_page()] )))
		return result

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