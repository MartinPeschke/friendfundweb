from friendfund.model.mapper import DBMappedObject, DBCDATA, GenericAttrib, DBMapper, DBMapping
from friendfund.model.product import Product
from lxml import etree

images = ['aff_program_logo_url', 'picture_small', 'picture_large']
key_order = ['aff_id','description', 'description_long', 'manufacturer', 'name', 'price', 'shipping_cost']


class CurationCategory(DBMappedObject):
	_set_root = _get_root = 'CATEGORY'
	_set_proc = _get_proc = None
	_unique_keys = ['name']
	_cachable = False
	_no_params = True
	_keys = [GenericAttrib(str,'name','name')]

				
class CurationCategoryWrapper(DBMappedObject):
	_set_root = _get_root = 'CATEGORIES'
	_set_proc = _get_proc = None
	_unique_keys = []
	_cachable = False
	_no_params = True
	_keys = [DBMapper(CurationCategory,'map','CATEGORY', is_dict = True, dict_key = lambda x: x.name)]
class ProductVersion(DBMappedObject):
	_set_root = _get_root = 'PRODUCT_VERSION'
	_set_proc = _get_proc = None
	_unique_keys = ['is_new', 'pc_id']
	_cachable = False
	_keys = [	
				GenericAttrib(bool,'is_new','is_new')
				,GenericAttrib(int,'pc_id','pc_id')
				,DBMapper(Product,'product','PRODUCT')
				,DBMapper(CurationCategoryWrapper,'categories','CATEGORIES')
			]

class CurationProduct(DBMappedObject):
	_set_root = _get_root = 'CURATION_PRODUCT'
	_set_proc = _get_proc = "cur.get_curation_products"
	_unique_keys = ['region', 'type']
	_cachable = False
	_keys = [	GenericAttrib(str,'type','type')
				, GenericAttrib(str,'outcome','outcome')
				, GenericAttrib(str,'prog_id','prog_id')
				, GenericAttrib(str,'aff_id','aff_id')
				,DBMapper(ProductVersion,'versions','PRODUCT_VERSION', is_dict = True, dict_key = lambda x: (x.is_new and 'NEW' or 'OLD'))
			]
	def fromDB(self, xml):
		setattr(self, 'xml', etree.tostring(xml))
		
	@classmethod
	def from_xml(cls, xml):
		return DBMapper.fromDB(cls, xml)

class GetCurationQueue(DBMappedObject):
	"""
		exec cur.get_curation_products '<PRODUCT_CURATION region="DE" type="INSERT" page_no="0"/>'
	"""
	key_order = key_order
	image_keys = images
	_set_root = 'PRODUCT_CURATION'
	_get_root = 'CURATION'
	_set_proc = _get_proc = "cur.get_curation_products"
	_unique_keys = ['region', 'type']
	_cachable = False
	_keys = [	
				GenericAttrib(str,'region','region')
				,GenericAttrib(str,'type','type')
				,GenericAttrib(unicode,'program','program')
				,DBMapper(CurationProduct,'cp','CURATION_PRODUCT', is_list = True)
			]

class GetCategoriesQueue(DBMappedObject):
	"""
		cur.get_categories
		<RESULT status="0" proc_name="get_categories"><CATEGORY CATEGORY_ID="1">DUMMY1</CATEGORY><CATEGORY CATEGORY_ID="2">DUMMY2</CATEGORY><CATEGORY CATEGORY_ID="3">DUMMY3</CATEGORY></RESULT>
	"""
	_set_root = 'CATEGORY'
	_get_root = None
	_set_proc = _get_proc = "cur.get_categories"
	_unique_keys = []
	_cachable = False
	_no_params = True
	_keys = [DBMapper(CurationCategory,'list','CATEGORY', is_list = True)]

class CurationProgram(DBMappedObject):
	_set_root = _get_root = 'PROGRAM'
	_set_proc = _get_proc = None
	_unique_keys = ['name', 'region']
	_cachable = False
	_no_params = True
	_keys = [GenericAttrib(unicode,'name','name'), GenericAttrib(str,'region','region')]
class GetProgramsProc(DBMappedObject):
	"""
		cur.get_programs  '<PROGRAMS region="DE" />' 
		<RESULT status="0" proc_name="get_programs"><PROGRAM name="Jochen Schweizer Erlebnisgeschenke" region="DE" /> 
	"""
	_set_root = 'PROGRAMS'
	_get_root = None
	_set_proc = _get_proc = "cur.get_programs"
	_unique_keys = []
	_cachable = False
	_keys = [DBMapper(CurationProgram,'list','PROGRAM', is_list = True)]
	def fromDB(self, xml):
		setattr(self, 'map', {})
		for prog in self.list:
			self.map[prog.region.lower()] = self.map.get(prog.region.lower(), []) + [prog]
	


class SetCurationResultProc(DBMappedObject):
	_set_root = _get_root = 'CURATION'
	_set_proc = _get_proc = "cur.set_curation_products"
	_unique_keys = ['region']
	_cachable = False
	_keys = [DBMapper(CurationProduct,'cp','CURATION_PRODUCT', is_list = True), GenericAttrib(str,'region','region')]

