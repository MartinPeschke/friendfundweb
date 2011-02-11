from friendfund.lib import helpers as h
from friendfund.model.mapper import DBMappedObject, GenericAttrib, DBMapper, GenericElement, DBMapping
from friendfund.model.product import Product

def page_field(_self):
	def lower(x):
		return x>2 and x-2 or 1
	def upper(x):
		return x+2<_self.pages and x+2 or _self.pages
	result = sorted(list(set([1] + range(lower(_self.page_no), upper(_self.page_no + 1)) + [_self.pages] )))
	return result


class TopSellersRegion(DBMappedObject):
	_cachable = False
	_set_root = _get_root = None
	_unique_keys = ['name']
	_keys = [GenericAttrib(unicode,'name','name'),DBMapper(Product,'list','PRODUCT', is_list = True)]
	def fromDB(self, xml):
		for product in self.list:
			product.is_curated = True

class GetTopSellersProc(DBMappedObject):
	_cachable = False
	_no_params = True
	_set_root = _get_root = None
	_unique_keys = []
	_get_proc = 'app.get_top_seller'
	_keys = [DBMapper(TopSellersRegion,'list','REGION', is_list = True)]
	def fromDB(self, xml):
		setattr(self, 'map', {})
		for region in self.list:
			self.map[region.name.lower()] = region.list


class ProductSearch(DBMappedObject):
	"""
		exec app.search_product'<SEARCH category ="garden" program_id ="123" search="schloss" page_no="1" region="de"/>'
	"""
	_get_root = _set_root = 'SEARCH'
	_get_proc = _set_proc = 'imp.search_product'
	_unique_keys = ['region', 'program_id', 'search', 'category', 'page_no']
	_cacheable = False
	_keys = [	GenericAttrib(str ,'search'     ,'search')
				,GenericAttrib(int ,'page_no'    ,'page_no')
				,GenericAttrib(int ,'pages'      ,'pages')
				,GenericAttrib(int ,'page_size'  ,'page_size')
				,GenericAttrib(int ,'items'      ,'items')
				,GenericAttrib(str ,'sort'       ,'sort')
				,DBMapper(Product  ,'products'   ,'PRODUCT', is_list = True)
			]
	page_field = page_field