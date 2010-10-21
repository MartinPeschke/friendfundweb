from friendfund.model.mapper import DBMappedObject, DBCDATA, GenericAttrib, DBMapper, DBMapping
from friendfund.model.product import Product

class ProductVersion(DBMappedObject):
	_set_root = _get_root = 'PRODUCT_VERSION'
	_set_proc = _get_proc = None
	_unique_keys = ['is_new', 'pc_id']
	_cachable = False
	_keys = [	
				GenericAttrib(bool,'is_new','is_new')
				,GenericAttrib(bool,'pc_id','pc_id')
				,DBMapper(Product,'product','PRODUCT')
			]

class CurationProduct(DBMappedObject):
	_set_root = _get_root = 'CURATION_PRODUCT'
	_set_proc = _get_proc = "cur.get_curation_products"
	_unique_keys = ['region', 'type']
	_cachable = False
	_keys = [	GenericAttrib(str,'type','type')
				,DBMapper(ProductVersion,'versions','PRODUCT_VERSION', is_dict = True, dict_key = lambda x: (x.is_new and 'NEW' or 'OLD'))
			]

class GetCurationQueue(DBMappedObject):
	"""
		exec cur.get_curation_products '<PRODUCT_CURATION region="DE" type="INSERT" page_no="0"/>'
	"""
	_set_root = 'PRODUCT_CURATION'
	_get_root = 'CURATION'
	_set_proc = _get_proc = "cur.get_curation_products"
	_unique_keys = ['region', 'type']
	_cachable = False
	_keys = [	
				GenericAttrib(str,'region','region')
				,GenericAttrib(str,'type','type')
				,DBMapper(CurationProduct,'cp','CURATION_PRODUCT', is_list = True)
			]