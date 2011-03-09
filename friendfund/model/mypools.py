from datetime import datetime, timedelta
from friendfund.lib import helpers as h
from friendfund.model.mapper import DBMappedObject, GenericAttrib, DBMapper

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
			, GenericAttrib(datetime,'expiry_date','expiry_date')
			, GenericAttrib(int,'amount','amount')
			, GenericAttrib(int,'shipping_cost','shipping_cost')
			, GenericAttrib(str,'currency','currency')
			, GenericAttrib(str, "merchant_domain", "merchant_domain")
			, GenericAttrib(bool, "is_secret", "is_secret")
			]

	def is_closed(self):
		return self.status in ["CLOSED", "COMPLETE"]
	def is_expired(self):
		return self.expiry_date<datetime.today()
	def get_pool_picture(self, type = "RA"):
		return h.get_pool_picture(self.pool_picture_url, type)
	
	def get_receiver_profile_pic(self, type="RA"):
		return h.get_user_picture(self.profile_picture_url, type)
	def get_friend_profile_pic(self, type="RA"):
		return h.get_user_picture(self.joined_picture, type)
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
			return h.word_truncate_plain(self.product_name, 2)
		else:
			log.error("NO PRODUCT NAME FOUND")
			return "XXX"
	def get_remaining_days_tuple(self):
		if self.is_closed():
			return (0, 0)
		else:
			diff = ((self.expiry_date + timedelta(1)) - datetime.today())
			if diff < timedelta(0):
				diff = timedelta(0)
			return (diff.days, diff.seconds/3600)


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
			,GenericAttrib(bool, 'closed_pools', None)
			]
	def fromDB(self, xml):
		self.admin_pools = filter(lambda x: x.is_admin and not x.is_closed(), self.pools)
		self.nonadmin_pools = filter(lambda x: not x.is_admin and not x.is_closed(), self.pools)
		self.closed_pools = filter(lambda x: x.is_closed(), self.pools)

		self.ff_admin_pools = filter(lambda x: x.is_admin, self.pools)
		self.ff_nonadmin_pools = filter(lambda x: not x.is_admin, self.pools)

class UserFriend(DBMappedObject):
	_cachable = False
	_unique_keys = ['network', 'network_id']
	_set_proc = _get_proc = None
	_set_root = _get_root = "USER_FRIEND"
	_keys = [	 GenericAttrib(str, 'network', 'network'), GenericAttrib(str, 'network_id', 'id') ]

class GetUserFriendPoolsProc(DBMappedObject):
	_cachable = False
	_unique_keys = ['u_id']
	_get_proc = _set_proc = "app.get_friend_pools"
	_set_root = "USER"
	_get_root = None
	_keys = [	 GenericAttrib(int, 'u_id', 'u_id')
				,DBMapper(UserFriend, 'friends', 'USER_FRIEND')
				,DBMapper(MyPoolEntry, 'pools', 'POOL', is_list = True)
				,GenericAttrib(bool, 'open_pools', None)
				,GenericAttrib(bool, 'closed_pools', None)
		]
	def fromDB(self, xml):
		self.closed_pools = []
		self.open_pools = []
		for pool in self.pools:
			if pool.is_closed():
				self.closed_pools.append(pool)
			else:
				self.open_pools.append(pool)

