from friendfund.model.mapper import DBMappedObject, GenericAttrib, DBMapper, GenericElement, DBMapping
from friendfund.model.product import Product

class ProductPager(object):
	SORTERS = {
			'RANK': lambda x:x,
			'PRICE_UP':lambda x: sorted(x, key = (lambda y:y.amount) ),
			'PRICE_DOWN':lambda x: sorted(x, key = (lambda y:y.amount), reverse = True),
			'MERCHANT':lambda x:x
		}
	
	
	def __init__(self,region,page_no,page_size,sort,products):
		self.products  = self.SORTERS[sort](products)
		self.region    = region   
		self.page_no   = page_no  
		self.items     = len(products)
		self.page_size = page_size
		self.sort      = sort     
		self.pages     = (self.items / self.page_size) + (self.items % self.page_size != 0)
		
	def page_field(self):
		def lower(x):
			return x>2 and x-2 or 1
		def upper(x):
			return x+2<self.pages and x+2 or self.pages
		result = sorted(list(set([1] + range(lower(self.page_no), upper(self.page_no + 1)) + [self.pages] )))
		return result

class VirtualGiftRegion(DBMappedObject):
	_cachable = False
	_set_root = _get_root = None
	_unique_keys = []
	_keys = [GenericAttrib(unicode,'name','name'),DBMapper(Product,'list','PRODUCT', is_list = True)]

class GetVirtualGiftsProc(DBMappedObject):
	_cachable = False
	_no_params = True
	_set_root = _get_root = None
	_unique_keys = []
	_get_proc = 'imp.get_virtual_gift'
	_keys = [DBMapper(VirtualGiftRegion,'list','REGION', is_list = True)]
	def fromDB(self, xml):
		setattr(self, 'map', {})
		for region in self.list:
			self.map[region.name] = region.list