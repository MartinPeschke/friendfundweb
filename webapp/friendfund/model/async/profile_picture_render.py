from friendfund.model.mapper import DBMappedObject, GenericAttrib, DBMapper

class AddRenderedProfilePictureProc(DBMappedObject):
	"""
		exec [async].[add_rendered_profile_picture]
			<PROFILE_PICTURE network ="FACEBOOK" id="1234123" email"" profile_picture_url ="asdfasdfawds.png"/>
	"""
	_set_root = _get_root = "PROFILE_PICTURE"
	_get_proc = _set_proc = "async.add_rendered_profile_picture"
	_unique_keys = ['network', 'network_id', 'email']
	_cachable = False
	_keys = [GenericAttrib(str,'network','network')
			,GenericAttrib(str,'network_id','id')
			,GenericAttrib(str,'email','email')
			,GenericAttrib(str,'profile_picture_url','profile_picture_url')
			]