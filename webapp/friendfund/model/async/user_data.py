from friendfund.model.mapper import DBMappedObject, GenericAttrib, DBMapper
from datetime import datetime

class UserData(DBMappedObject):
	"""
		<USER sex="m"
			first_name="somelastname"
			last_name="firstnamesome"
			name="somename"
			expires="1282125600"
			timezone="2"
			locale="de_DE"
			network="FACEBOOK"
			network_id="100001433388202"
			session_key="2.IVsJ9q52A2UvwyJa2W2zcQ__.3600.1282125600-100001433388202"
			sig="b059acdc87c2b486468a7b149cdbaa79"
			access_token="114609745252547|2.IVsJ9q52A2UvwyJa2W2zcQ__.3600.1282125600-100001433388202|LJnGNz6_C1FbPR4-6Q2amSr9OKU."
			secret="36IehPhAHVRV_B82FBfzyw__"
			link="http://www.facebook.com/profile.php?id=100001433388202"
		/>
	"""
	_set_root = _get_root = 'USER'
	_get_proc = _set_proc = "async.create_update_user"
	_unique_keys = ['network', 'network_id']
	_cachable = False
	_keys = [	 GenericAttrib(str,'network','network')
				,GenericAttrib(str,'network_id','id')
				,GenericAttrib(str,'email','email')
				,GenericAttrib(unicode,'name','name')
				,GenericAttrib(unicode,'first_name','first_name')
				,GenericAttrib(unicode,'last_name','last_name')
				,GenericAttrib(str,'screen_name','screen_name')
				,GenericAttrib(str,'session_key','session_key')
				,GenericAttrib(datetime,'birthday','birthday')
				,GenericAttrib(str,'sig','sig')
				,GenericAttrib(str,'access_token','access_token')
				,GenericAttrib(str,'access_token_secret','access_token_secret')
				,GenericAttrib(str,'link','link')
				,GenericAttrib(str,'birthdays','birthdays')
				,GenericAttrib(str,'locale','locale')
				,GenericAttrib(int,'timezone','timezone')
				,GenericAttrib(int,'expires','expires')
				,GenericAttrib(str,'sex','sex')
				,GenericAttrib(str,'profile_picture_url','profile_picture_url')
			]
			
class UserBirthday(DBMappedObject):
	_set_root = _get_root = 'USER'
	_unique_keys = ['network', 'network_id']
	_cachable = False
	_keys = [	 GenericAttrib(str,'network','network')
				,GenericAttrib(str,'network_id','id')
				,GenericAttrib(unicode,'name','name')
				,GenericAttrib(str,'email','email')
				,GenericAttrib(unicode,'networkname','name')
				,GenericAttrib(datetime,'dob','dob')
				,GenericAttrib(str,'gender','sex')
				,GenericAttrib(str,'pic_big','profile_picture_url')
			]

class UserBirthdayList(DBMappedObject):
	_set_root = _get_root = 'FRIEND_LIST'
	_get_proc = _set_proc = "async.add_fb_friend_list"
	_cachable = False
	_keys = [GenericAttrib(int,'u_id','u_id'), DBMapper(UserBirthday,'users','USER', is_list = True)]
