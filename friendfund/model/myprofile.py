from datetime import datetime, timedelta
from friendfund.lib import helpers as h
from friendfund.model.mapper import DBMappedObject, GenericAttrib, DBMapper, DBMapping
from pylons.i18n import ugettext as _

class Profile(DBMappedObject):
	_cachable = False
	_get_root = _set_root = "PROFILE"
	_unique_keys = ['network', 'name', 'email']
	_keys = [GenericAttrib(str, 'network', 'network')
			,GenericAttrib(unicode, 'name', 'un_name')
			,GenericAttrib(unicode, 'profile_picture_url', 'profile_picture_url')
			,GenericAttrib(unicode, 'email', 'email')
			,GenericAttrib(bool, 'is_default', 'is_default')
			]
	def get_profile_pic(self, type="RA"):
		return h.get_user_picture(self.profile_picture_url, type)

class GetMyProfileProc(DBMappedObject):
	"""
		[app].[get_my_profile] '<USER u_id="3540"/>'
		<RESULT status="0" proc_name="get_my_profile">
		  <PROFILE network="FACEBOOK" un_name="Harry McCarney" profile_picture_url="ff/ec/ffec818cd181715164d6dc0aceb27fdb" />
		  <PROFILE network="TWITTER" un_name="Harry McCarney" profile_picture_url="1e/3a/1e3af6b9510f5e8711098e6e045a0921" />
		</RESULT>
	"""
	_cachable = False
	_set_root = "USER"
	_get_root = None
	_get_proc = _set_proc = "app.get_my_profile"
	_unique_keys = ['u_id']
	_keys = [GenericAttrib(int, 'u_id', 'u_id')
			,DBMapper(Profile, 'profiles', 'PROFILE', is_dict = True, dict_key = lambda x: x.network.lower())
			]

class SetDefaultProfileProc(DBMappedObject):
	"""
		[app].[set_default_network] '<USER u_id="1" network ='EMAIL'/> 
	"""
	_cachable = False
	_get_root = _set_root = "USER"
	_get_proc = _set_proc = "app.set_default_network"
	_unique_keys = ['u_id']
	_keys = [GenericAttrib(int, 'u_id', 'u_id')
			,GenericAttrib(str, 'network', 'network')
			]