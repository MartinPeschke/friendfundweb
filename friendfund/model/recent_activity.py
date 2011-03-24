import uuid, random, logging
from pylons.i18n import ugettext as _

from friendfund.lib import helpers as h
from friendfund.model.mapper import DBMappedObject, GenericAttrib, DBMapper, DBMapping

from datetime import datetime, timedelta

log = logging.getLogger(__name__)


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
			, GenericAttrib(bool,'is_admin','is_admin')
			, GenericAttrib(str,'status','status')
			, GenericAttrib(int, "friend_id", "friend_id")
			, GenericAttrib(unicode, "friend_name", "friend_name")
			, GenericAttrib(unicode, "friend_profile_picture", "friend_profile_picture")
			, GenericAttrib(str, "merchant_domain", "merchant_domain")
			
			
			, GenericAttrib(unicode, "title", "title")
			, GenericAttrib(unicode, "description", "description")
			, GenericAttrib(datetime,'expiry_date','expiry_date')
			, GenericAttrib(bool, "is_secret", "is_secret")
			, GenericAttrib(int,'total_contribution','total_contribution')
			, GenericAttrib(int,'no_invitees','no_invitees')
			, GenericAttrib(int,'no_contributors','no_contributors')
			, GenericAttrib(int,'amount','amount')
			, GenericAttrib(int,'shipping_cost','shipping_cost')
			, GenericAttrib(str,'currency','currency')
			, GenericAttrib(bool,'is_contributor','is_contributor')
			, GenericAttrib(bool,'is_commenter','is_commenter')
			]
	def is_closed(self):
		return self.status in ["CLOSED", "COMPLETE"]
	def is_expired(self):
		return self.expiry_date<datetime.today()
	def get_pool_picture(self, type = "RA"):
		return h.get_pool_picture(self.pool_picture_url, type)
	
	def get_profile_pic(self, type="RA"):
		return h.get_user_picture(self.profile_picture_url, type)
	get_receiver_profile_pic = get_profile_pic
	def get_friend_profile_pic(self, type="RA"):
		return h.get_user_picture(self.friend_profile_picture, type)
	def get_product_pic(self, type="RA"):
		return h.get_product_picture(self.product_picture_url, type)
	
	def get_amount_float(self):
		return float(self.amount + (self.shipping_cost or 0))/100
	def get_total_contribution_float(self):
		return float(self.total_contribution)/100
	def get_amount_left_float(self):
		return self.get_amount_float() - self.get_total_contribution_float()
	get_amount_left = get_amount_left_float
	def funding_progress(self):
		return self.get_total_contribution_float() / self.get_amount_float()
	
	def get_product_display_name(self):
		if self.product_name:
			return h.word_truncate_plain(self.product_name.title(), 2)
		else:
			log.error("NO PRODUCT NAME FOUND")
			return "XXX"
	def get_remaining_days(self):
		if self.is_closed():
			return 0
		else:
			diff = ((self.expiry_date + timedelta(1)) - datetime.today())
			if diff < timedelta(0):
				diff = timedelta(0)
			return diff.days
class RecentActivityStream(DBMappedObject):
	_expiretime = 60
	_cacheable = False
	_get_root = None
	_get_proc = _set_proc = 'app.get_current_pool'
	_no_params = True
	_keys = [DBMapper(RecentActivityEntry,'pools','POOL', is_list = True)]