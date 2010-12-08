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

class ProductSearchByCategory(DBMappedObject):
	"""
		QUERY: exec imp.search_curated_product ?; with (u'<SEARCH region="de" page_no="1" page_size="5" category="ADVENTURER" sort="RANK" />',)
		RESULT <RESULT status="0" proc_name="search_curated_product"><SEARCH items="132" page_size="5" page_no="1" pages="26"><PRODUCT 
	"""
	_get_root = _set_root = 'SEARCH'
	_get_proc = _set_proc = 'imp.search_curated_product'
	_unique_keys = ['region', 'category']
	_cacheable = False
	_keys = [	 GenericAttrib(str,'region'      ,'region')
				,GenericAttrib(int,'page_no'     ,'page_no')
				,GenericAttrib(int,'pages'     ,'pages')
				,GenericAttrib(int,'items'     ,'items')
				,GenericAttrib(int,'page_size' ,'page_size')
				,GenericAttrib(unicode,'category'    ,'category')
				,GenericAttrib(str,'sort' ,'sort')
				,DBMapper(Product, 'products', 'PRODUCT', is_list = True)
			]
	def fromDB(self, xml):
		for product in self.products:
			product.is_curated = True
	page_field = page_field



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
	_get_proc = 'imp.get_top_seller'
	_keys = [DBMapper(TopSellersRegion,'list','REGION', is_list = True)]
	def fromDB(self, xml):
		setattr(self, 'map', {})
		for region in self.list:
			self.map[region.name] = region.list




class ProductSearch(DBMappedObject):
	"""
		exec app.search_product'<SEARCH category ="garden" program_id ="123" search="schloss" page_no="1" region="de"/>'
	"""
	_get_root = _set_root = 'SEARCH'
	_get_proc = _set_proc = 'imp.search_product'
	_unique_keys = ['region', 'program_id', 'search', 'category', 'page_no']
	_cacheable = False
	_keys = [	 GenericAttrib(str ,'region'     ,'region')
				,GenericAttrib(str ,'search'     ,'search')
				,GenericAttrib(int ,'max_price'  ,'max_price')
				,GenericAttrib(str ,'program_id' ,'program_id')
				,GenericAttrib(int ,'category'   ,'category')
				,GenericAttrib(int ,'page_no'    ,'page_no')
				,GenericAttrib(int ,'pages'      ,'pages')
				,GenericAttrib(int ,'page_size'  ,'page_size')
				,GenericAttrib(int ,'items'      ,'items')
				,GenericAttrib(str ,'sort'       ,'sort')
				,DBMapper(Product  ,'products'   ,'PRODUCT', is_list = True)
			]
	page_field = page_field


class CombinedSearchResult(object):
	def __init__(self, s1, s2, page_no):
		self.region = s1.region
		self.page_size = s1.page_size
		self.category = s1.category
		self.sort = s1.sort
		
		self.page_no = page_no
		if self.page_no>1:
			self.products = s2.products[:self.page_size]
		else:
			self.products = (s1.products + s2.products)[:self.page_size]
		self.items = s1.items + s2.items
		
		self.pages = self.items/self.page_size + (self.items%self.page_size>0)
	
	page_field = page_field