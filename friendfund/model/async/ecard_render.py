from friendfund.model.mapper import DBMappedObject, GenericAttrib, DBMapper, DBMapping


class ECardUser(DBMappedObject):
	"""
			<USER u_id ="4437"/> 
	"""
	_cacheable = False
	_get_root = _set_root = 'USER'
	_get_proc = _set_proc = None
	_unique_keys = ['u_id']
	_keys = [GenericAttrib(int,'u_id','u_id'),
			GenericAttrib(unicode,'u_name','u_name'),
			GenericAttrib(unicode,'message','message'),
			GenericAttrib(unicode,'profile_picture_url','profile_picture_url')]

class ECard(DBMappedObject):
	"""
		<ECARD p_url ="UC0xMTE2OA~~" url ="gggg"> 
		<USER u_id ="4437"/> 
		<USER u_id ="4276"/> 
		<USER u_id ="4275"/> 
		</ECARD> 
	"""
	_cacheable = False
	_get_root = _set_root = 'ECARD'
	_get_proc = _set_proc = None
	_unique_keys = ['url', 'invitor_id']
	_keys = [GenericAttrib(str,'url','url'), GenericAttrib(int,'invitor_id','invitor_id'), DBMapper(ECardUser, 'users', 'USER', is_list = True)]

class GetPoolECardsProc(DBMappedObject):
	"""
		QUERY: exec async.get_ecards_for_rendering ?; with (u'<POOL p_url="UC0xMTM0OA~~" />',)
		RESULT <RESULT status="0" proc_name="get_ecards_for_rendering">
		<ECARD invitor="Katrin Hagen">
		<USER u_name="Aaron King-Cole" profile_picture_url="ab/2e/ab2e9c603e826b8dd92afa50a1736d87"/>
		<USER u_name="Aaron Lal" profile_picture_url="87/68/8768320b0ae1a673fad0624b96b1b475"/>
		<USER u_name="Adrian Sauberlich" profile_picture_url="9b/69/9b6937d50a4333c3b937bf45b73bfa64"/>
	"""
	_cacheable = False
	_get_root = None
	_set_root = 'POOL'
	_get_proc = _set_proc = 'async.get_ecards_for_rendering'
	_no_params = False
	_keys = [GenericAttrib(str,'p_url','p_url'), DBMapper(ECard, 'ecards', 'ECARD', is_list = True)]

class SetPoolECardsProc(DBMappedObject):
	"""
		<ECARD p_url ="UC0xMTEzMQ~~" url ="someimage"> 
		<USER u_id ="4275"/> 
		<USER u_id ="4276"/> 
		<USER u_id ="4278"/> 
	"""
	_cacheable = False
	_get_root = _set_root = 'POOL'
	_get_proc = _set_proc = 'async.add_rendered_ecard_url'
	_keys = [GenericAttrib(str,'p_url','p_url'), DBMapper(ECard, 'ecards', 'ECARD')]