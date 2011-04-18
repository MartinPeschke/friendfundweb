from datetime import datetime, timedelta
from pylons.i18n import ugettext as _
from friendfund.lib import helpers as h
from friendfund.model.mapper import DBMappedObject, GenericAttrib, DBMapper, DBMapping

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
	def get_profile_pic(self, type="RA", secured = False):
		return self._statics.get_user_picture(self.profile_picture_url, type, secured = secured)
	
	def fromDB(self, xml):
		self.network = self.network.lower()
	
	
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
			,DBMapper(Profile, 'profiles', 'PROFILE', is_dict = True, dict_key = lambda x: x.network)
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

class OptOutTemplateType(DBMappedObject):
	"""app.set_template_opt_out"""
	_cachable = False
	_get_root = _set_root = "TEMPLATE_TYPE"
	_get_proc = _set_proc = None
	_unique_keys = ['name', "opt_out"]
	_keys = [GenericAttrib(str, 'name', 'name', required = True)
			,GenericAttrib(bool, 'opt_out', 'opt_out', required = True)
			]

class OptOutNotificationsProc(DBMappedObject):
	"""app.set_template_opt_out"""
	_cachable = False
	_get_root = None
	_set_root = "USER"
	_get_proc = "app.get_notification_settings"
	_set_proc = "app.set_notification_settings"
	_unique_keys = ['u_id']
	_keys = [GenericAttrib(int, 'u_id', 'u_id')
			,DBMapper(OptOutTemplateType, 'types', 'TEMPLATE_TYPE', is_list = True)
			]
