import logging
from pylons import app_globals as g, request, config
from friendfund.model.mapper import DBMappedObject, GenericAttrib, DBMapper
from friendfund.model.pool import PoolStub, Pool

from friendfund.lib import helpers as h, fb_helper, tw_helper

log = logging.getLogger(__name__)


class UserSignupException(Exception):
	pass
class UserNotLoggedInWithMethod(Exception):
	pass
class GetFriendsNotSupported(Exception):
	pass

class OtherUserData(DBMappedObject):
	_set_root = _get_root = "USER"
	_get_proc = _set_proc = "app.add_other_account"
	_unique_keys = ['network', 'network_id']
	_cachable = False
	_keys = [	 GenericAttrib(int,'u_id','u_id')
				,GenericAttrib(str,'network','network')
				,GenericAttrib(str,'network_id','id')
				,GenericAttrib(str,'email','email')
				,GenericAttrib(str,'profile_picture_url','profile_picture_url')
				,GenericAttrib(unicode,'pwd','pwd')
				,GenericAttrib(unicode,'name','name')
				,GenericAttrib(unicode,'first_name','first_name')
				,GenericAttrib(unicode,'last_name','last_name')
				,GenericAttrib(str,'screen_name','screen_name')
				,GenericAttrib(str,'session_key','session_key')
				,GenericAttrib(str,'sig','sig')
				,GenericAttrib(str,'access_token','access_token')
				,GenericAttrib(str,'access_token_secret','access_token_secret')
				,GenericAttrib(str,'link','link')
				,GenericAttrib(str,'birthdays','birthdays')
				,GenericAttrib(str,'locale','locale')
				,GenericAttrib(int,'timezone','timezone')
				,GenericAttrib(int,'expires','expires')
				,GenericAttrib(str,'sex','sex')
			]

class VerifyAdminEmailProc(DBMappedObject):
	"""[app].[validate_admin_email]  <VALIDATE token = "asdfasdfsdfasd"/>"""
	_set_root = _get_root = 'VALIDATE'
	_cachable = False
	_set_proc = 'app.validate_admin_email'
	_unique_key = []
	_keys = [GenericAttrib(str, 'token', 'token')]

class SetUserEmailProc(DBMappedObject):
	_set_root = _get_root = 'USER'
	_cachable = False
	_set_proc = 'app.add_admin_contributor_email_account'
	_unique_key = []
	_keys = [GenericAttrib(int, 'u_id', 'u_id'), GenericAttrib(str, 'email', 'email'), GenericAttrib(str, 'name', 'name')]

class UserPermissions(DBMappedObject):
	"""<PERMISSIONS network="FACEBOOK" id="100000924808399" stream_publish="0" permanent="0" birthdays="0" has_email="0"/>"""
	_set_root = _get_root = 'PERMISSIONS'
	_unique_keys = ['network', 'network_id']
	_cachable = False
	_keys = [	GenericAttrib(str,'network','network')
				,GenericAttrib(str,'network_id','id')
				,GenericAttrib(bool,'has_email','has_email')
				,GenericAttrib(str,'email','email')
				,GenericAttrib(bool,'stream_publish','stream_publish')
				,GenericAttrib(bool,'permanent','permanent')
				,GenericAttrib(bool,'birthdays','birthdays')
			]

class SocialNetworkInformation(object):
	def __init__(self, network, network_id, access_token, access_token_secret):
		self.network = network
		self.network_id = network_id
		self.access_token = access_token
		self.access_token_secret = access_token_secret

class User(DBMappedObject):
	"""
		<RESULT status="0" proc_name="web_login">
			<USER u_id="6102" name="Mapa Technorac" profile_picture_url="14/b8/14b87c7561441af56b1c9c26f7cd4aee" has_email="1">
				<POOL p_id="11375" p_url="UC0xMTM3NQ~~"/><POOL p_id="11377" p_url="UC0xMTM3Nw~~"/>
				<PERMISSIONS network="FACEBOOK" id="100000924808399" stream_publish="1" permanent="0" birthdays="0" email="martin.peschke@gmx.net"/>
			</USER>
		</RESULT>
	"""
	_cachable = False
	_unique_keys = ['u_id', 'profile_picture_url', 'network', 'network_id']
	_get_proc = "app.web_login"
	_set_proc = "app.create_email_user"
	_set_root = _get_root = "USER"
	_keys = [	 GenericAttrib(int, 'u_id', 'u_id')
				,GenericAttrib(unicode,'name','name')
				,GenericAttrib(str,'network','network')
				,GenericAttrib(str,'network_id','id')
				,GenericAttrib(str,'profile_picture_url','profile_picture_url')
				,GenericAttrib(str,'email','email')
				,GenericAttrib(str,'pwd','pwd')
				,GenericAttrib(bool,'has_email','has_email')
				,GenericAttrib(str,'sex','sex')
				,GenericAttrib(str,'token','token')
				,GenericAttrib(str,'access_token','access_token')
				,GenericAttrib(str,'access_token_secret','access_token_secret')
				,DBMapper(UserPermissions, 'permissions', 'PERMISSIONS', is_list = True)
				,DBMapper(PoolStub, 'pools', 'POOL', persistable = False, is_list = True)
				,DBMapper(PoolStub,'_current_pool',None, persistable = False)
				,DBMapper(None,'_perms',None, persistable = False)
				,GenericAttrib(dict,'networks', None, persistable = False)
			]
	def set_pool_url(self, p_url):
		if p_url not in self.pools:
			return None
		else:
			self.current_pool = self.pools[p_url]
			return self.current_pool
	def has_pool(self, p_url):
		return p_url in self.pools
	
	def set_network(self, network, **args):
		if args:
			network_info = SocialNetworkInformation(network=network, **args)
			self.networks[str(network)]=network_info
			self.__dict__['current_network'] = network
		else:
			self.networks[str(network)]=None
	
	def get_current_network(self):
		return getattr(self, 'current_network', self.network)
	
	def is_logged_in_with(self, network):
		return isinstance(self.networks.get(network, None), SocialNetworkInformation)
	
	def has_tried_logging_in_with(self, network):
		return network in self.networks
	
	def get_friends(self, network, friend_id = None, html_renderer = None):
		if not self.is_logged_in_with(network):
			raise UserNotLoggedInWithMethod("User is not signed into %s" % network)
		elif network == 'facebook':
			try:
				fb_data = fb_helper.get_user_from_cookie(
							request.cookies, 
							g.FbApiKey, 
							g.FbApiSecret.__call__()
						)
			except fb_helper.FBNotLoggedInException, e:
				raise UserNotLoggedInWithMethod("User is not signed into %s" % network)
			else:
				self.networks['facebook'].access_token = fb_data['access_token']
				self.networks['facebook'].access_token_secret = fb_data['session_key']
				friends = fb_helper.get_friends_from_cache(
								log, 
								g.cache_pool, 
								self.networks['facebook'].network_id, 
								self.networks['facebook'].access_token, 
								friend_id=friend_id,
								html_renderer = html_renderer
							)
		elif network == 'twitter':
			friends = tw_helper.get_friends_from_cache(
								log, 
								g.cache_pool, 
								self.networks['twitter'].access_token, 
								self.networks['twitter'].access_token_secret, 
								config,
								html_renderer = html_renderer
							)
		else:
			raise GetFriendsNotSupported(
					"Get Friends Method not supported for %s" % network
				)
		return friends
	
	
	def _get_current_pool(self):
		"""Returns current PoolStub, no full Pools are returned, as this would be stored inSession otherwise"""
		return self._current_pool
	def _set_current_pool(self, pool):
		"""Takes a PoolInstance and sets a PoolStub into Users Session, as not to pickle a whole Pool in Session"""
		if not pool: return None
		if not (isinstance(pool, PoolStub) or isinstance(pool, Pool)):
			raise ValueError('Parameter pool is neither Pool nor PoolStub')
		if isinstance(pool, PoolStub):
			self._current_pool = pool
		elif isinstance(pool, Pool):
			self._current_pool = PoolStub(p_url = pool.p_url, p_id = pool.p_id)
			self._current_pool.im_admin = pool.am_i_admin(self)
			self._current_pool.im_receiver = pool.am_i_receiver(self)
		self.pools[pool.p_url] = self._current_pool
	current_pool = property(_get_current_pool, _set_current_pool)
	
	def _get_is_anon(self):
		return not self.u_id
	is_anon = property(_get_is_anon)
	
	def am_i_admin(self, pool_url):
		try: 
			return self.pools[pool_url].im_admin or False
		except:
			return False
	
	def set_am_i_admin(self, pool_url, value):
		try: 
			self.pools[pool_url].im_admin = value
		except:
			pass
	
	def fromDB(self, xml):
		self.networks = self.networks or {}
		self.pools = dict([(p.p_url, p) for p in self.pools])
		self._perms = dict([(p.network.lower(), p) for p in self.permissions])
	
	def has_perm(self, network, perm):
		return getattr(self._perms.get(network.lower(), None), perm, False)
	def set_perm(self, network, perm, val):
		if not self._perms.get(network.lower(), None):
			new_perm = UserPermissions(network=network)
			self._perms[network] = new_perm
			self.permissions = (self.permissions or []) + [new_perm]
		setattr(self._perms.get(network.lower(), None), perm, val)
		return None

	def get_profile_pic(self, type="PROFILE_S"):
		return h.get_user_picture(self.profile_picture_url, type)


class WebLoginUserByTokenProc(User):
	_get_proc = "app.web_login_token"
class SetNewPasswordForUser(User):
	_set_proc = "app.set_new_pwd"
class FBWebLogin(User):
	_set_proc = "app.web_login"


class DBRequestPWProc(DBMappedObject):
	"""exec app.[set_user_forgot_password_token] '<USER u_id= "1340"/>'"""
	_set_root = 'USER'
	_set_proc = 'app.set_user_forgot_password_token'
	_unique_keys = ['email']
	_keys = [	 GenericAttrib(str,'email','email')	]

ANONUSER = User(networks={})