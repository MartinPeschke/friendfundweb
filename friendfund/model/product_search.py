from friendfund.lib import helpers as h
from friendfund.model.mapper import DBMappedObject, GenericAttrib, DBMapper, GenericElement, DBMapping
from friendfund.model.product import Product

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
	
	def page_field(self):
		def lower(x):
			return x>2 and x-2 or 1
		def upper(x):
			return x+2<self.pages and x+2 or self.pages
		result = sorted(list(set([1] + range(lower(self.page_no), upper(self.page_no + 1)) + [self.pages] )))
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
	_get_proc = 'imp.get_top_seller'
	_keys = [DBMapper(TopSellersRegion,'list','REGION', is_list = True)]
	def fromDB(self, xml):
		setattr(self, 'map', {})
		for region in self.list:
			self.map[region.name] = region.list