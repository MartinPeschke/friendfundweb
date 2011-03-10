from datetime import datetime, timedelta
from friendfund.lib import helpers as h
from friendfund.model.mapper import DBMappedObject, GenericAttrib, DBMapper

class PoolEventUser(DBMappedObject):
	_cachable = False
	_unique_keys = ['network', 'network_id']
	_set_proc = _get_proc = None
	_set_root = _get_root = "INVITEE"
	_keys = [	 GenericAttrib(int, 'u_id', 'u_id'), GenericAttrib(unicode, 'name', 'name'), GenericAttrib(unicode, 'profile_picture_url', 'profile_picture_url') ]
	def get_profile_pic(self, type="PROFILE_M"):
		return h.get_user_picture(self.profile_picture_url, type)

class EventType(DBMappedObject):
	def get_actor_profile_pic(self, type="PROFILE_M"):
		return h.get_user_picture(self.picture, type)

class CreateGroupGiftEvent(EventType):
	_set_proc = _get_proc = _set_root = None
	_get_root = "CREATE_GROUP_GIFT_POOL"
	_cachable = False
	_unique_keys = ['title']
	_keys = [GenericAttrib(unicode, 'title', 'title')
			,GenericAttrib(unicode, 'name', 'name')
			,GenericAttrib(unicode, 'picture', 'picture')
			,GenericAttrib(unicode, 'description', 'description')
			,GenericAttrib(unicode, 'receiver', 'receiver')
			,GenericAttrib(int, 'no_invitees', 'no_invitees')
			,DBMapper(PoolEventUser, 'invitees', 'INVITEE', is_list = True)
			]
class CreateFreeFormEvent(EventType):
	_set_proc = _get_proc = _set_root = None
	_get_root = "CREATE_FREE_FORM_POOL"
	_cachable = False
	_unique_keys = ['title']
	_keys = [GenericAttrib(unicode, 'title', 'title')
			,GenericAttrib(unicode, 'name', 'name')
			,GenericAttrib(unicode, 'picture', 'picture')
			,GenericAttrib(unicode, 'description', 'description')
			,GenericAttrib(int, 'no_invitees', 'no_invitees')
			,DBMapper(PoolEventUser, 'invitees', 'INVITEE', is_list = True)
			]
class InviteEvent(EventType):
	_set_proc = _get_proc = _set_root = None
	_get_root = "INVITE"
	_cachable = False
	_unique_keys = ['title']
	_keys = [GenericAttrib(unicode, 'title', 'title')
			,GenericAttrib(unicode, 'name', 'name')
			,GenericAttrib(unicode, 'picture', 'picture')
			,GenericAttrib(unicode, 'description', 'description')
			,GenericAttrib(int, 'no_invitees', 'no_invitees')
			,DBMapper(PoolEventUser, 'invitees', 'INVITEE', is_list = True)
			]
	def get_first_invitee_profile_pic(self, type):
		pass

class ContributionEvent(EventType):
	_set_proc = _get_proc = _set_root = None
	_get_root = "CONTRIBUTION"
	_cachable = False
	_unique_keys = ['title']
	_keys = [GenericAttrib(unicode, 'title', 'title')
			,GenericAttrib(unicode, 'name', 'name')
			,GenericAttrib(unicode, 'picture', 'picture')
			,GenericAttrib(int, 'no_contributors', 'no_contributors')
			,DBMapper(PoolEventUser, 'invitees', 'INVITEE', is_list = True)
			]

class PoolSuccessEvent(EventType):
	_set_proc = _get_proc = _set_root = None
	_get_root = "SUCCESS"
	_cachable = False
	_unique_keys = ['title']
	_keys = [GenericAttrib(str, 'picture', 'picture')
			,GenericAttrib(int, 'no_contributors', 'no_contributors')
			,GenericAttrib(str, 'admin_picture', 'admin_picture')
			,GenericAttrib(unicode, 'title', 'title')
			,DBMapper(PoolEventUser, 'invitees', 'INVITEE', is_list = True)
			]
	

class ActivityStreamEvent(DBMappedObject):
	"""
		  <EVENT p_id="13630" u_id="47754"> 
			<CREATE_GROUP_GIFT_POOL name="Harry McCarney" receiver="Cora Church" title="CHIC 4 BABY 100 33 239.98" picture="39/ce/39ce628b5b169d233bac03ae4576dded" description="Harry McCarney has created a Friend Fund for Cora Churchs New Home. Come and chip in!" no_invitees="4"> 
			  <INVITEE name="Abigail Ottolangui" profile_picture_url="0f/db/0fdbdf945fcad7e9b359c3fb558a7d90" /> 
			</CREATE_GROUP_GIFT_POOL> 
		  </EVENT> 
	"""
	_set_proc = _get_proc = _set_root = None
	_get_root = "EVENT"
	_cachable = False
	_unique_keys = ['p_url']
	_keys = [GenericAttrib(int, 'p_id', 'p_id')
			,GenericAttrib(int, 'u_id', 'u_id')
			,GenericAttrib(str, 'p_url', 'p_url')
			,DBMapper(CreateGroupGiftEvent, '_cggp', 'CREATE_GROUP_GIFT_POOL')
			,DBMapper(CreateFreeFormEvent, '_cffp', 'CREATE_FREE_FORM_POOL')
			,DBMapper(InviteEvent, '_ivt', 'INVITE')
			,DBMapper(ContributionEvent, '_ctb', 'CONTRIBUTION')
			,DBMapper(PoolSuccessEvent, '_suc', 'SUCCESS')
			]
	def fromDB(self, xml):
		try:
			setattr(self, 'obj', filter(None, [self._cggp, self._cffp, self._ivt, self._ctb, self._suc])[0])
		except IndexError,e:
			raise Exception("Didnt Find any Event Details")
			

class ActivityStream(DBMappedObject):
	"""
		<STREAM type="MY">...</STREAM>
	"""
	_set_proc = _get_proc = _set_root = None
	_get_root = "STREAM"
	_cachable = False
	_unique_keys = ['type']
	_keys = [GenericAttrib(str, 'type', 'type')
			,DBMapper(ActivityStreamEvent, '_event', 'EVENT')
			]
	def fromDB(self, xml):
		setattr(self, "is_my_event", self.type=="MY")
		setattr(self, "p_url", self._event.p_url)
		setattr(self, "event", self._event.obj)
		setattr(self, "invitees", self._event.obj.invitees)

class GetActivityStreamProc(DBMappedObject):
	"""
		exec [app].[get_activity_stream] '<USER u_id ="47754"/>' 
	"""
	_set_proc = _get_proc = "app.get_activity_stream"
	_set_root = "USER"
	_get_root = None
	_cachable = True
	_expiretime = 5
	_unique_keys = ['u_id']
	_keys = [GenericAttrib(int, 'u_id', 'u_id')
			,DBMapper(ActivityStream, 'stream', 'STREAM', is_list = True)
			]