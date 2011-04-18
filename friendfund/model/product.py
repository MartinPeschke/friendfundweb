import simplejson
from babel.numbers import format_currency
from friendfund.lib import helpers as h
from friendfund.model.mapper import DBMappedObject, GenericAttrib, DBMapper, GenericElement, DBMapping
from friendfund.services import static_service as statics
from pylons import session as websession, app_globals
from pylons.i18n import ugettext as _

class Product(DBMappedObject):
	_get_root = _set_root = 'PRODUCT'
	_unique_keys = ['merchant_ref','name']
	_keys = [	GenericAttrib(int      ,'shipping_cost', 'shipping_cost'    )
				,GenericAttrib(unicode ,'merchant_ref' , 'merchant_ref'     )
				,GenericElement(unicode,'name'         , 'NAME'             , default="")
				,GenericElement(unicode,'description'  , 'DESCRIPTION'      , default="")
				,GenericAttrib(unicode ,'ean'          , 'ean'              )
				,GenericAttrib(unicode ,'picture'      , 'picture'          )
				,GenericAttrib(unicode ,'tracking_link', 'tracking_link'    )
				,GenericAttrib(unicode ,'guid'         , 'guid'             , persistable=False)
				]
	def get_product_pic(self, type="POOL"):
		return self._statics.get_product_picture(self.picture, type)
	def get_display_link(self):
		return h.word_truncate_by_letters(self.tracking_link, 40)
	def get_display_name(self):
		return h.word_truncate_plain(self.name.title(), 2)
	def get_display_description(self):
		return h.word_truncate_by_letters(self.description, 180)
	def has_picture(self):
		return self.picture and self.picture!= statics.DEFAULT_PRODUCT_PICTURE_TOKEN
	def toJsonMap(self):
		return simplejson.dumps(self.get_map())
	

class DisplayProduct(Product):
	_get_root = _set_root = None
	_get_proc = _set_proc = None
	_keys = [	GenericAttrib(unicode  ,'guid'         , 'guid'             , persistable=False)
				,GenericAttrib(unicode ,'merchant_ref' , 'merchant_ref'     , persistable=False)
				,GenericAttrib(int     ,'price'        , 'price'            , persistable=False)
				,GenericAttrib(int     ,'shipping_cost', 'shipping_cost'    , persistable=False)
				,GenericAttrib(str     ,'currency'     , 'currency'         , persistable=False)
				,GenericElement(unicode,'name'         , 'NAME'             , default="", persistable=False)
				,GenericElement(unicode,'description'  , 'DESCRIPTION'      , default="", persistable=False)
				,GenericAttrib(unicode ,'ean'          , 'ean'              , persistable=False)
				,GenericAttrib(unicode ,'picture'      , 'picture'          , persistable=False)
				,GenericAttrib(unicode ,'tracking_link', 'tracking_link'    , persistable=False)
			]
	
	def get_price_float(self, include_shipping = True):
		return float(self.price + (include_shipping and self.shipping_cost or 0))/100
	def get_display_price(self, include_shipping = True):
		return h.format_currency(self.get_price_float(include_shipping), self.currency)
	def get_shipping_cost_float(self):
		return float(self.shipping_cost)/100
	def get_shipping_price(self):
		if self.shipping_cost:
			return '(PP: %s)' %h.format_currency(self.get_shipping_cost_float(), self.currency)
		else:
			return ''
	def get_total_price_units(self):
		return self.price + (self.shipping_cost or 0)
	display_price = property(get_display_price)
	display_shipping = property(get_shipping_price)
	
	def get_display_label(self, words = 5, seperator = ' '):
		return '%s%s%s' % (h.word_truncate_plain(self.name, words), seperator, self.display_price)
	display_label = property(get_display_label)
	def get_product_pic(self, type="POOL"):
		return self.picture
	get_picture = get_product_pic

class ProductSearch(DBMappedObject):
	def __init__(self, page_no, pages, page_size, items, products):
		self.page_no = page_no
		self.pages = pages
		self.page_size = page_size
		self.items = items
		self.products = products
	def page_field(self):
		def lower(x):
			return x>2 and x-2 or 1
		def upper(x):
			return x+2<self.pages and x+2 or self.pages
		return sorted(list(set([1] + range(lower(self.page_no), upper(self.page_no + 1)) + [self.pages] )))