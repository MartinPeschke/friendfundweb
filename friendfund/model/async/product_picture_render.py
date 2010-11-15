from friendfund.model.mapper import DBMappedObject, GenericAttrib, DBMapper

class AddRenderedProductPictureProc(DBMappedObject):
	"""
		[async].[add_rendered_product_picture] '</PRODUCT_PICTURE p_url ="asdfasdfasdfasdf" product_picture_url = "asdfasdf"/>'
	"""
	_set_root = _get_root = "PRODUCT_PICTURE"
	_get_proc = _set_proc = "async.add_rendered_product_picture"
	_unique_keys = ['p_url', 'product_picture_url']
	_cachable = False
	_keys = [GenericAttrib(str,'p_url','p_url')
			,GenericAttrib(str,'product_picture_url','product_picture_url')
			]