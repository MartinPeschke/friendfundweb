from datetime import datetime, timedelta
from operator import attrgetter
from random import sample, choice

from pylons import app_globals
from pylons.i18n import _
from friendfund.lib import helpers as h
from friendfund.model.mapper import DBMappedObject, GenericAttrib, DBMapper


ranges = [(60,'seconds'), 
		  (3600, 'minutes'), 
		  (86400, 'hours'), 
		  (604800, 'days'), 
		  (2419200, 'weeks'), 
		  (30758400, 'months')
		]

class PoolEventUser(DBMappedObject):
	_cachable = False
	_unique_keys = ['network', 'network_id']
	_set_proc = _get_proc = None
	_set_root = _get_root = "INVITEE"
	_keys = [	 GenericAttrib(int, 'u_id', 'u_id'), GenericAttrib(unicode, 'name', 'name'), GenericAttrib(unicode, 'profile_picture_url', 'profile_picture_url') ]
	def get_profile_pic(self, type="PROFILE_M", secured = False):
		return app_globals.statics.get_user_picture(self.profile_picture_url, type, secured = secured)

class EventType(DBMappedObject):
	def get_actor_profile_pic(self, type="PROFILE_M", secured = False):
		return app_globals.statics.get_user_picture(self.picture, type, secured = secured)

class EventWithInviteesType(EventType):
	def get_random_invitee_profile_pic(self, type):
		if len(self.invitees)>0:
			return choice(self.invitees).get_profile_pic(type)
		else:
			return None
	def get_random_n_invitee_profile_pic(self, n, type):
		if len(self.invitees)<n:
			n = len(self.invitees)
		return map(lambda x: x.get_profile_pic(type), sample(self.invitees, n))
	
	def get_random_n_names(self, n):
		return map(attrgetter("name"), sample(self.invitees, n))

class CreateGroupGiftEvent(EventWithInviteesType):
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
	
class CreateFreeFormEvent(EventWithInviteesType):
	_set_proc = _get_proc = _set_root = None
	_get_root = "CREATE_FREE_FORM_POOL"
	_cachable = False
	_unique_keys = ['title']
	_keys = [GenericAttrib(unicode, 'title', 'title')
			,GenericAttrib(unicode, 'name', 'name')
			,GenericAttrib(unicode, 'picture', 'picture')
			,GenericAttrib(unicode, 'description', 'description')
			,GenericAttrib(datetime, 'creation_date', 'creation_date')
			,GenericAttrib(datetime, 'expiry_date', 'expiry_date')
			,GenericAttrib(int, 'no_invitees', 'no_invitees')
			,DBMapper(PoolEventUser, 'invitees', 'INVITEE', is_list = True)
			]

class InviteEvent(EventWithInviteesType):
	_set_proc = _get_proc = _set_root = None
	_get_root = "INVITE"
	_cachable = False
	_unique_keys = ['title']
	_keys = [GenericAttrib(unicode, 'title', 'title')
			,GenericAttrib(unicode, 'name', 'name')
			,GenericAttrib(unicode, 'picture', 'picture')
			,GenericAttrib(unicode, 'description', 'description')
			,GenericAttrib(datetime, 'creation_date', 'creation_date')
			,GenericAttrib(datetime, 'expiry_date', 'expiry_date')
			,GenericAttrib(int, 'no_invitees', 'no_invitees')
			,DBMapper(PoolEventUser, 'invitees', 'INVITEE', is_list = True)
			]

class ContributionEvent(EventType):
	_set_proc = _get_proc = _set_root = None
	_get_root = "CONTRIBUTION"
	_cachable = False
	_unique_keys = ['title']
	_keys = [GenericAttrib(unicode, 'title', 'title')
			,GenericAttrib(unicode, 'name', 'name')
			,GenericAttrib(unicode, 'picture', 'picture')
			,GenericAttrib(datetime, 'creation_date', 'creation_date')
			,GenericAttrib(datetime, 'expiry_date', 'expiry_date')
			,GenericAttrib(int, 'no_contributors', 'no_contributors')
			,GenericAttrib(int, 'amount', 'amount')
			,GenericAttrib(int, 'total_contribution', 'total_contribution')
			,GenericAttrib(int, 'target', 'target')
			,GenericAttrib(str, 'currency', 'currency')
			]
	def get_remaining_days(self):
		diff = ((self.expiry_date + timedelta(1)) - datetime.today())
		if diff < timedelta(0):
			diff = timedelta(0)
		return diff.days
	def funding_progress(self):
		return int((float(self.total_contribution) / self.target)*100)

class PoolCommentEvent(EventType):
	_set_proc = _get_proc = _set_root = None
	_get_root = "COMMENT"
	_cachable = False
	_unique_keys = ['title']
	_keys = [GenericAttrib(unicode, 'name', 'name')
			,GenericAttrib(unicode, 'picture', 'picture')
			,GenericAttrib(datetime, 'creation_date', 'creation_date')
			,GenericAttrib(datetime, 'expiry_date', 'expiry_date')
			,GenericAttrib(unicode, 'title', 'title')
			,GenericAttrib(unicode, 'comment', 'comment')
			]
class PoolSuccessEvent(EventType):
	_set_proc = _get_proc = _set_root = None
	_get_root = "SUCCESS"
	_cachable = False
	_unique_keys = ['title']
	_keys = [GenericAttrib(unicode, 'title', 'title')
			,GenericAttrib(unicode, 'name', 'name')
			,GenericAttrib(unicode, 'picture', 'picture')
			,GenericAttrib(int, 'no_contributors', 'no_contributors')
			,GenericAttrib(str, 'admin_picture', 'admin_picture')
			,GenericAttrib(datetime, 'creation_date', 'creation_date')
			,GenericAttrib(datetime, 'expiry_date', 'expiry_date')
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
			,GenericAttrib(str, 'merchant_domain', 'merchant_domain')
			,DBMapper(CreateGroupGiftEvent, '_cggp', 'CREATE_GROUP_GIFT_POOL')
			,DBMapper(CreateFreeFormEvent, '_cffp', 'CREATE_FREE_FORM_POOL')
			,DBMapper(InviteEvent, '_ivt', 'INVITE')
			,DBMapper(ContributionEvent, '_ctb', 'CONTRIBUTION')
			,DBMapper(PoolSuccessEvent, '_suc', 'SUCCESS')
			,DBMapper(PoolCommentEvent, '_cmt', 'COMMENT')
			]
	def fromDB(self, xml):
		try:
			setattr(self, 'obj', filter(None, [self._cggp, self._cffp, self._ivt, self._ctb, self._suc, self._cmt])[0])
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
			,GenericAttrib(int, 'recency', 'recency')
			,DBMapper(ActivityStreamEvent, '_event', 'EVENT')
			]
	def get_recency(self):
		diff = timedelta(0, self.recency)
		second_diff = diff.seconds
		day_diff = diff.days
		if day_diff < 0:
			return ''
		if day_diff == 0:
			if second_diff < 10:
				return _("FF_RECENCY_just now")
			if second_diff < 60:
				return _("FF_RECENCY_%(seconds)d seconds ago") % {"seconds":second_diff}
			if second_diff < 120:
				return  _("FF_RECENCY_a minute ago")
			if second_diff < 3600:
				return _("FF_RECENCY_%(minutes)d minutes ago") % {"minutes":second_diff / 60}
			if second_diff < 7200:
				return _("FF_RECENCY_an hour ago")
			if second_diff < 86400:
				return _("FF_RECENCY_%(hours)d hours ago") % {"hours":second_diff / 3600}
		if day_diff == 1:
			return _("FF_RECENCY_Yesterday")
		if day_diff < 7:
			return _("FF_RECENCY_%(days)d days ago") % {"days":day_diff}
		if day_diff < 31:
			return _("FF_RECENCY_%(weeks)d weeks ago") % {"weeks":day_diff/7}
		if day_diff < 365:
			return _("FF_RECENCY_%(months)d months ago") %{"months":day_diff/30}
		return _("FF_RECENCY_%(years)d years ago")%{"years":day_diff/365}
	
	def get_merchant(self):
		if not hasattr(self, "merchant"):
			setattr(self, "merchant", app_globals.merchants.domain_map.get(self.merchant_domain))
		return self.merchant
			
			
	def fromDB(self, xml):
		setattr(self, "is_my_event", self.type=="MY")
		setattr(self, "p_url", self._event.p_url)
		setattr(self, "merchant_domain", self._event.merchant_domain)
		setattr(self, "event", self._event.obj)

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
			,GenericAttrib(bool, 'include_friend', 'include_friend')
			,DBMapper(ActivityStream, 'stream', 'STREAM', is_list = True)
			]