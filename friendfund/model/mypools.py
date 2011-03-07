from friendfund.model.mapper import DBMappedObject, GenericAttrib, DBMapper
from friendfund.model.recent_activity import RecentActivityEntry

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
			,DBMapper(RecentActivityEntry, 'pools', 'POOL', is_list = True)
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
				,DBMapper(RecentActivityEntry, 'pools', 'POOL', is_list = True)
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

