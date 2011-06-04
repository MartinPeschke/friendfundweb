import logging, md5
from pylons import app_globals, request, config
from friendfund.model.mapper import DBMappedObject, GenericAttrib, DBMapper

from friendfund.services import static_service as statics
from friendfund.lib import helpers as h, fb_helper, tw_helper

log = logging.getLogger(__name__)
class UserSignupException(Exception):
	pass
class UserNotLoggedInWithMethod(Exception):
	pass
class GetFriendsNotSupported(Exception):
	pass

CLEARANCES = {"ANON":0, "BASE" : 1, "CONTRIBUTE":3, "INVITE":6, "FULL":9}



class OtherUserData(DBMappedObject):
	_set_root = _get_root = "USER"
	_get_proc = _set_proc = "app.add_other_account"
	_unique_keys = ['network', 'network_id']
	_cachable = False
	_keys = [	 GenericAttrib(int,'u_id','u_id')
				,GenericAttrib(str,'network','network')
				,GenericAttrib(str,'network_id','id')
				,GenericAttrib(str,'email','email')
				,GenericAttrib(str,'profile_picture_url','profile_picture_url', default = statics.DEFAULT_USER_PICTURE_TOKEN)
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
	_set_proc = 'app.add_twitter_email_account'
	_unique_key = []
	_keys = [GenericAttrib(int, 'u_id', 'u_id'), GenericAttrib(str, 'email', 'email')]

class SetNewPasswordForUser(DBMappedObject):
	_set_root = _get_root = "USER"
	_set_proc = "app.set_new_pwd"
	_cachable = False
	_unique_key = []
	_keys = [	 GenericAttrib(int, 'u_id', 'u_id'),GenericAttrib(str,'pwd','pwd')]


class NetworkUserPermissions(DBMappedObject):
	_set_root = _get_root = 'PERMISSIONS'
	_get_proc = _set_proc = "app.set_permissions"
	_unique_keys = ['network', 'network_id']
	_cachable = False
	_keys = [	GenericAttrib(str,'network','network')
				,GenericAttrib(str,'network_id','id')
				,GenericAttrib(bool,'has_email','has_email')
				,GenericAttrib(str,'email','email')
				,GenericAttrib(bool,'stream_publish','stream_publish')
				,GenericAttrib(bool,'create_event','create_event')
				,GenericAttrib(bool,'permanent','permanent')
				,GenericAttrib(bool,'birthdays','birthdays')
			]
	def has_some_changes(self):
		return bool(len(filter(lambda x:x is not None, [self.has_email, self.email, self.stream_publish, self.create_event, self.permanent, self.birthdays])))
	def add_perms_from_scope(self, scope, email):
		if not isinstance(scope, basestring):
			raise Exception("set_perms_from_scope scope is not string, it is %s", type(scope))
		had_changes = False
		if not self.stream_publish:
			self.stream_publish = "publish_stream" in scope
			had_changes = True
		if not self.create_event:
			self.create_event = "create_event" in scope
			had_changes = True
		if not self.email:
			self.email = email
			self.has_email = True
			had_changes = True
		if not self.birthdays:
			self.birthdays = ("user_birthday" in scope) and ("friends_birthday" in scope)
			had_changes = True
		return had_changes
		
		
class SocialNetworkInformation(object):
	def __init__(self, network, network_id, access_token, access_token_secret):
		self.network = network
		self.network_id = network_id
		self.access_token = access_token
		self.access_token_secret = access_token_secret

class ProtoUser(DBMappedObject):
	is_ssp_admin = False



class User(ProtoUser):
	_cachable = False
	_unique_keys = ['u_id', 'default_email', 'network', 'network_id']
	_set_proc = _get_proc = "app.web_login"
	_set_root = _get_root = "USER"
	_keys = [	 GenericAttrib(int, 'u_id', 'u_id', required = True)
				,GenericAttrib(unicode,'name','name')
				,GenericAttrib(str,'network','network')
				,GenericAttrib(str,'network_id','id')
				,GenericAttrib(str,'profile_picture_url','profile_picture_url')
				,GenericAttrib(str,'email','email')
				,GenericAttrib(str,'default_email','default_email', required = True)
				,GenericAttrib(bool,'has_activity','has_activity', default = False)
				,GenericAttrib(str,'pwd','pwd')
				,GenericAttrib(str,'sex','sex')
				,GenericAttrib(str,'locale','locale')
				,DBMapper(NetworkUserPermissions, 'permissions', 'PERMISSIONS', is_dict = True, dict_key = lambda x:x.network.lower() )
				,DBMapper(dict,'networks', None, persistable = False, is_dict = True, dict_key = lambda x:x)
				,GenericAttrib(dict,'user_data_temp', None, persistable = False)
				,GenericAttrib(str,"failover_pic", None, persistable = False)
			]
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
		return bool(isinstance(self.networks.get(network, None), SocialNetworkInformation) and self.networks.get(network).network_id)
	def has_tried_logging_in_with(self, network):
		return network in self.networks
	
	def get_clearance(self):
		if self.is_anon:
			return CLEARANCES['ANON']
		if "facebook" in self.permissions and self.get_perm_network_id("facebook"):
			perm = self.permissions['facebook']
			if perm.stream_publish and perm.create_event:
				return CLEARANCES['FULL']
			elif perm.stream_publish:
				return CLEARANCES['INVITE']
			elif perm.email:
				return CLEARANCES['CONTRIBUTE']
			else:
				log.error("USER_WITH_NOFACEBOOK_PERMISSIONS_LOGGED_IN %s", self.u_id)
				return CLEARANCES['ANON']
		else:
			return CLEARANCES['FULL'] 
	def _get_is_anon(self):
		return not (self.default_email and self.u_id)
	is_anon = property(_get_is_anon)
	
	
	def rem_perm_network(self, network):
		network = network.lower()
		if network in self.permissions:
			del self.permissions[network]
		return None
	def get_perm_network(self, network, network_id):
		network = network.lower()
		perms = self.permissions.setdefault(network, NetworkUserPermissions(network=network, network_id = network_id))
		if perms.network_id is not None and perms.network_id != network_id:
			log.error("FOUND_MISTAKEN_NETWORK_ID:expected (%s) found (%s)", perms.network_id, network_id)
		return perms
	def get_perm_network_id(self, network):
		network = network.lower()
		perms_id = getattr(self.permissions.get(network), "network_id", None)
		return perms_id
	
	def has_perm(self, network, perm):
		network = network.lower()
		return getattr(self.permissions.get(network), perm, False)
	def set_perm(self, network, perm, val):
		network = network.lower()
		perm_obj = self.permissions.setdefault(network, NetworkUserPermissions(network=network))
		setattr(perm_obj, perm, val)
		return None
	
	def get_has_email(self):
		return bool(self.default_email)
	has_email = property(get_has_email)
	
	def get_friends(self, network, friend_id = None, offset = None, level = CLEARANCES['CONTRIBUTE']):
		if not self.is_logged_in_with(network) or self.get_clearance() < level:
			raise UserNotLoggedInWithMethod("User is not signed into %s" % network)
		elif network == 'facebook':
			try:
				fb_data = fb_helper.get_user_from_cookie(
							request.cookies, 
							app_globals.FbApiKey, 
							app_globals.FbApiSecret.__call__()
						)
			except (fb_helper.FBNoCookiesFoundException, fb_helper.FBNotLoggedInException), e:
				raise UserNotLoggedInWithMethod("User is not signed into %s" % network)
			else:
				self.networks['facebook'].access_token = fb_data['access_token']
				self.networks['facebook'].access_token_secret = fb_data['session_key']
				friends, is_complete, offset  = fb_helper.get_friends_from_cache(
								log, 
								app_globals.cache_pool, 
								self.networks['facebook'].network_id, 
								self.networks['facebook'].access_token, 
								friend_id=friend_id,
								offset = offset
							)
		elif network == 'twitter':
			friends, is_complete, offset = tw_helper.get_friends_from_cache(
								log, 
								app_globals.cache_pool, 
								self.networks['twitter'].access_token, 
								self.networks['twitter'].access_token_secret, 
								config,
								offset = offset
							)
			if friends is None:
				raise Exception('NoFriendsFoundSomeErrorOccured')
		else:
			raise GetFriendsNotSupported(
					"Get Friends Method not supported for %s" % network
				)
		return friends, is_complete, offset
	
	def set_profile_picture_url(self, value):
		if not self.profile_picture_url:
			self.profile_picture_url = value
		if isinstance(self.profile_picture_url, basestring) and self.profile_picture_url.startswith("http"):
			log.warning("EXTERNAL_USER_PICTURE <%s>", self.profile_picture_url)
			self.failover_pic = self.profile_picture_url
			self.profile_picture_url = statics.tokenize_url(self.profile_picture_url)
	
	def get_profile_pic(self, type="PROFILE_S", secured = False):
		return self._statics.get_user_picture(self.profile_picture_url, type, secured = secured)
	def get_failover(self, type="PROFILE_S", secured = False):
		if getattr(self, "failover_pic", False):
			return 'onerror="this.src=\'%s\';"' % self._statics.get_user_picture(self.failover_pic, type, secured = secured)
		else: return ''

class CreateEmailUserProc(DBMappedObject):
	_set_root = _get_root = 'USER'
	_get_proc = _set_proc = "app.create_email_user"
	_unique_keys = ['name', 'default_email']
	_keys = [	 GenericAttrib(str,'network','network')
				,GenericAttrib(unicode,'name','name')
				,GenericAttrib(str,'email','email')
				,GenericAttrib(str,'locale','locale')
				,GenericAttrib(unicode,'pwd','pwd')
				,GenericAttrib(str,'profile_picture_url','profile_picture_url', default = statics.DEFAULT_USER_PICTURE_TOKEN)]
	
class WebLoginUserByTokenProc(User):
	_get_proc = "app.web_login_token"
class WebLoginUserByEmail(DBMappedObject):
	_get_proc = _set_proc = "app.web_login"
	_set_root = _get_root = 'USER'
	_unique_keys = ['email']
	_keys = [	 GenericAttrib(str,'network','network')
				,GenericAttrib(str,'email','email')
				,GenericAttrib(str,'locale','locale')
				,GenericAttrib(str,'pwd','pwd')]
	
class FBWebLogin(User):
	_set_proc = "app.web_login"


class DBRequestPWProc(DBMappedObject):
	"""exec app.[set_user_forgot_password_token] '<USER email= "some@mauil.com"/>'"""
	_set_root = 'USER'
	_set_proc = 'app.set_user_forgot_password_token'
	_unique_keys = ['email']
	_keys = [	 GenericAttrib(str,'email','email')	]

ANONUSER = User(networks={})

class TwitterUserHasEmailProc(DBMappedObject):
	"""app.has_twitter_default_email"""
	_set_root = _get_root = 'USER'
	_get_proc = _set_proc = "app.has_twitter_default_email"
	_unique_keys = ['email', 'id']
	_cachable = False
	_keys = [	GenericAttrib(str,'network_id','id'),GenericAttrib(unicode,'default_email','default_email')]

class SetUserLocaleProc(DBMappedObject):
	"""app_set_user_locale '<USER u_id ="26990" locale= "en-gb"/>'"""
	_set_root = _get_root = 'USER'
	_get_proc = _set_proc = "app.set_user_locale"
	_unique_keys = ['u_id', 'locale']
	_cachable = False
	_keys = [	GenericAttrib(int,'u_id','u_id'),GenericAttrib(unicode,'locale','locale')]
	
class DisconnectAccountProc(DBMappedObject):
	"""exec app.disconnect_account '<USER u_id ="124944" network ="email" id ="1707117978" email = "asdf@gmial.com" />'"""
	_set_root = _get_root = 'USER'
	_get_proc = _set_proc = "app.disconnect_account"
	_unique_keys = ['u_id', 'network', 'network_id']
	_cachable = False
	_keys = [GenericAttrib(int,'u_id','u_id')
			, GenericAttrib(unicode,'network','network')
			, GenericAttrib(unicode,'network_id','id')
			, GenericAttrib(unicode,'email','email')
			, GenericAttrib(unicode,'default_email','email')]
	def fromDB(self, xml):
		if self.network:
			self.network = self.network.lower()