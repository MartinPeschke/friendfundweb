from datetime import datetime, timedelta
from random import sample
from BeautifulSoup import BeautifulSoup
from pylons import app_globals
from friendfund.lib import helpers as h
from friendfund.model.mapper import DBMappedObject, GenericAttrib, DBMapper



class PoolFriend(DBMappedObject):
	_cachable = False
	_unique_keys = ['network', 'network_id']
	_set_proc = _get_proc = None
	_set_root = _get_root = "FRIEND"
	_keys = [	 GenericAttrib(int, 'u_id', 'u_id'), GenericAttrib(unicode, 'name', 'name'), GenericAttrib(unicode, 'picture', 'picture') ]
	def get_profile_pic(self, type="PROFILE_M", secured = False):
		return self._statics.get_user_picture(self.picture, type, secured = secured)


class MyPoolEntry(DBMappedObject):
	_get_root = _set_root = 'POOL'
	_unique_keys = ['p_url']
	_keys = [GenericAttrib(str,'p_url','p_url')
			, GenericAttrib(unicode, "title", "title")
			, GenericAttrib(unicode, "description", "description")
			, GenericAttrib(str,'phase','phase')
			, GenericAttrib(str,'status','status')
			, GenericAttrib(unicode,'joined_name','joined_name')
			, GenericAttrib(unicode,'joined_picture','joined_picture')
			, GenericAttrib(unicode,'invitor_name','invitor_name')
			, GenericAttrib(unicode,'invitor_picture','invitor_picture')
			, GenericAttrib(unicode,'admin_name','admin_name')
			, GenericAttrib(unicode,'pool_picture_url','pool_picture_url')
			, GenericAttrib(unicode,'product_picture_url','product_picture_url')
			, GenericAttrib(unicode,'product_name','product_name')
			, GenericAttrib(unicode,'profile_picture_url','profile_picture_url')
			, GenericAttrib(unicode,'receiver_name','receiver')
			, GenericAttrib(int,'no_invitees','no_invitees')
			, GenericAttrib(int,'no_contributors','no_contributors')
			, GenericAttrib(int,'total_contribution','total_contribution')
			, GenericAttrib(bool,'is_contributor','is_contributor')
			, GenericAttrib(bool,'is_commenter','is_commenter')
			, GenericAttrib(bool,'is_admin','is_admin')
			, GenericAttrib(datetime,'creation_date','creation_date')
			, GenericAttrib(datetime,'creation_date','creation_date')
			, GenericAttrib(datetime,'expiry_date','expiry_date')
			, GenericAttrib(int,'amount','amount')
			, GenericAttrib(int,'shipping_cost','shipping_cost')
			, GenericAttrib(str,'currency','currency')
			, GenericAttrib(str, "merchant_key", "merchant_key")
			, GenericAttrib(bool, "is_secret", "is_secret")
			, GenericAttrib(int,		'remaining_seconds','remaining_seconds')
			, DBMapper(PoolFriend, 'friends', 'FRIEND', is_list = True)
			]
	def get_remaining_time_tuple(self):
		d = self.remaining_time.days
		h = self.remaining_time.seconds / 3600
		m = (self.remaining_time.seconds % 3600)/60
		s = self.remaining_time.seconds % 60
		return d,h,m,s
	def is_closed(self):
		return self._is_closed
	def is_expired(self):
		return self.phase in ["EXPIRED", "EXTENSION_EXPIRED"]
	def get_pool_picture(self, type = "RA"):
		return h.get_pool_picture(self.pool_picture_url, type)
	
	def get_receiver_profile_pic(self, type="RA", secured = False):
		return self._statics.get_user_picture(self.profile_picture_url, type, secured = secured)
	def get_invitor_profile_pic(self, type="RA", secured = False):
		return self._statics.get_user_picture(self.invitor_picture, type, secured = secured)
	def get_product_pic(self, type="RA", secured = False):
		return self._statics.get_product_picture(self.product_picture_url, type, secured = secured)
	
	def get_amount_float(self):
		return float(self.amount + (self.shipping_cost or 0))/100
	def get_total_contribution_float(self):
		return float(self.total_contribution)/100
	def get_amount_left_float(self):
		return self.get_amount_float() - self.get_total_contribution_float()
	get_amount_left = get_amount_left_float
	def funding_progress(self):
		return self.get_total_contribution_float() / self.get_amount_float()
	
	def get_random_n_invitees(self, n):
		if len(self.friends)>n:
			return sample(self.friends, n)
		else:
			return self.friends[:n]

	def get_product_display_name(self):
		if self.product_name:
			return h.word_truncate_plain(self.product_name, 2)
		else:
			log.error("NO PRODUCT NAME FOUND")
			return "XXX"
	def get_remaining_days(self):
		if self._is_closed:
			return 0
		else:
			diff = ((self.expiry_date + timedelta(1)) - datetime.today())
			if diff < timedelta(0):
				diff = timedelta(0)
			return diff.days
	def fromDB(self, xml):
		setattr(self, "_is_closed", self.status in ["CLOSED", "COMPLETE"])
		setattr(self, "remaining_time", timedelta(0, self.remaining_seconds))
		if self.description: self.description = ''.join(BeautifulSoup(self.description).findAll(text=True))
		return self
	
	def get_merchant(self):
		if not hasattr(self, "merchant"):
			setattr(self, "merchant", app_globals.merchants.key_map[self.merchant_key])
		return self.merchant
	
class GetMyPoolsProc(DBMappedObject):
	"""
		exec [app].[get_my_pools] '<MY_POOLS u_id="3540"/>'
	"""
	_set_proc = _get_proc = "app.get_my_pools"
	_set_root = "MY_POOLS"
	_get_root = None
	_cachable = False
	_unique_keys = ['u_id']
	_keys = [GenericAttrib(int, 'u_id', 'u_id')
			,DBMapper(MyPoolEntry, 'pools', 'POOL', is_list = True)
			,GenericAttrib(bool, 'admin_pools', None)
			,GenericAttrib(bool, 'nonadmin_pools', None)
			]
	def fromDB(self, xml):
		self.admin_pools = filter(lambda x: x.is_admin, self.pools)
		self.nonadmin_pools = filter(lambda x: not x.is_admin, self.pools)

class GetUserFriendPoolsProc(DBMappedObject):
	_cachable = False
	_unique_keys = ['u_id']
	_get_proc = _set_proc = "app.get_friend_pools"
	_set_root = "USER"
	_get_root = None
	_keys = [	 GenericAttrib(int, 'u_id', 'u_id')
				,DBMapper(MyPoolEntry, 'pools', 'POOL', is_list = True)
		]