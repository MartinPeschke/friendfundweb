from babel.numbers import format_currency
from friendfund.lib import helpers as h
from friendfund.model.mapper import DBMappedObject, GenericAttrib, DBMapper, GenericElement, DBMapping

from pylons import session as websession, app_globals
from pylons.i18n import ugettext as _

class Product(DBMappedObject):
	_get_root = _set_root = 'PRODUCT'
	_unique_keys = ['merchant_ref','name']
	_keys = [	GenericAttrib(int     ,'shipping_cost', 'shipping_cost'    )
				,GenericElement(unicode,'name'         , 'NAME'             )
				,GenericElement(unicode,'description'  , 'DESCRIPTION'      )
				,GenericAttrib(unicode ,'ean'          , 'ean'              )
				,GenericAttrib(unicode ,'picture'      , 'picture'          )
				,GenericAttrib(unicode ,'tracking_link', 'tracking_link'    )
				]
	def get_product_pic(self, type="POOL"):
		return h.get_product_picture(self.picture, type)
	def get_display_name(self):
		return h.word_truncate_plain(self.name.title(), 2)

class DisplayProduct(Product):
	_keys = [	GenericAttrib(unicode  ,'guid'         , 'guid'             , persistable=False)
				,GenericAttrib(unicode ,'merchant_ref' , 'merchant_ref'     )
				,GenericAttrib(int     ,'price'        , 'price'            , persistable=False)
				,GenericAttrib(int     ,'shipping_cost', 'shipping_cost'    )
				,GenericAttrib(str     ,'currency'     , 'currency'         , persistable=False)
				,GenericElement(unicode,'name'         , 'NAME'             )
				,GenericElement(unicode,'description'  , 'DESCRIPTION'      )
				,GenericAttrib(unicode ,'ean'          , 'ean'              )
				,GenericAttrib(unicode ,'picture'      , 'picture'          )
				,GenericAttrib(unicode ,'tracking_link', 'tracking_link'    )
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