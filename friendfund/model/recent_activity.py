import uuid, random
from pylons.i18n import ugettext as _


from friendfund.lib import helpers as h
from friendfund.model.mapper import DBMappedObject, GenericAttrib, DBMapper, DBMapping
from friendfund.model.badge import ALLBADGES_DICT, Badge
from datetime import datetime, timedelta




class RecentActivityEntry(DBMappedObject):
	_get_root = _set_root = 'POOL'
	_unique_keys = ['p_url']
	_keys = [GenericAttrib(str,'p_url','p_url')
			, GenericAttrib(unicode,'receiver','receiver')
			, GenericAttrib(unicode,'product_name','product_name')
			, GenericAttrib(unicode,'product_picture_url','product_picture_url')
			, GenericAttrib(unicode,'profile_picture_url','profile_picture_url')
			, GenericAttrib(unicode,'pool_picture_url','pool_picture_url')
			, GenericAttrib(unicode,'receiver_name','receiver')
			, GenericAttrib(int,'total_contribution','total_contribution')
			, GenericAttrib(int,'no_invitees','no_invitees')
			, GenericAttrib(int,'no_contributors','no_contributors')
			, GenericAttrib(datetime,'expiry_date','expiry_date')
			, GenericAttrib(int,'amount','amount')
			, GenericAttrib(str,'currency','currency')
			, GenericAttrib(bool,'is_contributor','is_contributor')
			, GenericAttrib(bool,'is_admin','is_admin')
			, GenericAttrib(str,'status','status')
			, GenericAttrib(int, "friend_id", "friend_id")
			, GenericAttrib(unicode, "friend_name", "friend_name")
			, GenericAttrib(unicode, "friend_profile_picture", "friend_profile_picture")
			, GenericAttrib(bool, "is_secret", "is_secret")
			]
	def is_closed(self):
		return self.status in ["CLOSED", "COMPLETE"]
	def get_pool_picture(self, type = "RA"):
		return h.get_pool_picture(self.pool_picture_url, type)
	
	def get_profile_pic(self, type="RA"):
		return h.get_user_picture(self.profile_picture_url, type)	
	def get_friend_profile_pic(self, type="RA"):
		return h.get_user_picture(self.friend_profile_picture, type)
	
	def get_product_pic(self, type="RA"):
		return h.get_product_picture(self.product_picture_url, type)
	
	def get_amount_float(self):
		return float(self.amount)/100
	def get_total_contribution_float(self):
		return float(self.total_contribution)/100
	def get_amount_left_float(self):
		return self.get_amount_float() - self.get_total_contribution_float()
	
	def get_remaining_days_tuple(self):
		if self.is_closed():
			return (0, 0)
		else:
			diff = ((self.expiry_date + timedelta(1)) - datetime.today())
			if diff < timedelta(0):
				diff = timedelta(0)
			return (diff.days, diff.seconds/3600)

class RecentActivityStream(DBMappedObject):
	_expiretime = 60
	_cacheable = False
	_get_root = None
	_get_proc = _set_proc = 'app.get_current_pool'
	_no_params = True
	_keys = [DBMapper(RecentActivityEntry,'pools','POOL', is_list = True), DBMapper(Badge,'badges','BADGE', is_list = True)]
	def get_some_badges(self, count):
		if len(self.badges) > count:
			return random.sample(self.badges, count)
		else:
			return self.badges