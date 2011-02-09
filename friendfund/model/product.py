from babel.numbers import format_currency
from friendfund.lib import helpers as h
from friendfund.model.mapper import DBMappedObject, GenericAttrib, DBMapper, GenericElement, DBMapping

from pylons import session as websession, app_globals
from pylons.i18n import ugettext as _


class Product(DBMappedObject):
	_get_root = _set_root = 'PRODUCT'
	_unique_keys = ['merchant_ref','name']
	_keys = [	GenericAttrib(unicode  ,'guid'         , 'guid'             , persistable=False)
				,GenericAttrib(unicode ,'merchant_ref' , 'merchant_ref'     )
				,GenericAttrib(int     ,'amount'       , 'amount'           )
				,GenericAttrib(int     ,'shipping_cost', 'shipping_cost'    )
				,GenericAttrib(str     ,'currency'     , 'currency'         )
				,GenericElement(unicode,'name'         , 'NAME'             )
				,GenericElement(unicode,'description'  , 'DESCRIPTION'      )
				,GenericAttrib(unicode ,'ean'          , 'ean'              )
				,GenericAttrib(unicode ,'picture'      , 'picture'          )
				,GenericAttrib(unicode ,'tracking_link', 'tracking_link'    )
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
		return h.get_product_picture(self.picture, type)
	
	def get_display_name(self):
		return h.word_truncate_plain(self.name.title(), 2)
	
	def get_display_label(self, extended = True, words = 5, seperator = ' '):
		return '%s%s%s' % (h.word_truncate_plain(self.name, words), seperator, self.get_display_price(extended))
	display_label = property(get_display_label)