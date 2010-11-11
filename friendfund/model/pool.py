import simplejson, logging
from datetime import datetime, timedelta, date

from friendfund.lib import helpers as h, tools
from friendfund.model.mapper import DBMappedObject, DBCDATA, GenericAttrib, DBMapper, DBMapping
from friendfund.model.product import Product
from pylons.i18n import _

from pylons import session as websession


log = logging.getLogger(__name__)

class NoPoolAdminException(AttributeError):pass
class NoPoolReceiverException(AttributeError):pass
class TooManyPoolAdminException(AttributeError):pass
class TooManyPoolReceiverException(AttributeError):pass
class InsufficientParamsException(Exception):pass

class PoolComment(DBMappedObject):
	_set_root = _get_root = 'COMMENT'
	_set_proc = _get_proc = "app.add_pool_comment"
	_unique_keys = ['p_url', 'u_id']
	_keys = [	GenericAttrib(str,'p_url','p_url')
				,GenericAttrib(int,'u_id','u_id')
				,GenericAttrib(unicode,'name','name')
				,GenericAttrib(unicode,'comment','comment')
				,GenericAttrib(unicode,'profile_picture_url','profile_picture_url')
				,GenericAttrib(datetime,'created','created')
			]
	def get_profile_pic(self, type="PROFILE_M"):
		return h.get_user_picture(self.profile_picture_url, type)
	def get_profile_s_pic(self):
		return self.get_profile_pic(type="PROFILE_S")
	profile_s_pic = property(get_profile_s_pic)
	

class PoolDescription(DBMappedObject):
	"""
		exec app.add_pool_description '<POOL url ="UC0xMDE4OQ~~" description = "balh de blah"/>'
	"""
	_set_root = _get_root = 'POOL'
	_set_proc = _get_proc = "app.add_pool_description"
	_unique_keys = ['p_url']
	_keys = [	GenericAttrib(str,'p_url','p_url')
				,GenericAttrib(unicode,'description','description')
			]


class PoolChat(DBMappedObject):
	_get_root = _set_root = "POOLCHAT"
	_get_proc = _set_proc = "app.get_pool_comment"
	_keys = [	GenericAttrib(str,'p_url','p_url')
				,GenericAttrib(bool,'is_secret','is_secret')
				,DBMapper(PoolComment,'comments','COMMENT', is_list = True)
			]


class PoolStub(DBMappedObject):
	"""<POOL p_id="10733" p_url="UC0xMDczMw~~"/>"""
	_set_root = _get_root = 'POOL'
	_unique_keys = ['p_id', 'p_url']
	_keys = [	GenericAttrib(int,'p_id','p_id')
				,GenericAttrib(str,'p_url','p_url')
				,GenericAttrib(bool,'im_admin',None)
				,GenericAttrib(bool,'im_receiver',None)
			]
	def get_pool_picture(self):
		return h.get_pool_picture(self.p_url)

class Occasion(DBMappedObject):
	_get_root = _set_root = 'OCCASION'
	_unique_keys = ['key']
	_keys = [GenericAttrib(str,'key' , 'key'  )
			,GenericAttrib(unicode,'name', 'name')
			,GenericAttrib(datetime,'date', 'date')
			,GenericAttrib(str,'picture_url', 'picture_url')
			,GenericAttrib(bool,'custom', 'custom')
			]
	def get_display_name(self):
		return self.name or (self.key and _(self.key)) or ''
	def get_display_label(self):
		return '%s - %s' % (self.get_display_name(), h.format_date(self.date))
	display_label = property(get_display_label)
	
	def get_internal_date_format(self):
		return self.date and h.format_date_internal(self.date) or ''
	internal_date_format = property(get_internal_date_format)

class OccasionSearch(DBMappedObject):
	_get_proc = "imp.get_occasion_group"
	_get_root = None
	_set_root = 'OCCASION'
	_unique_keys = ['date', 'country']
	_keys = [GenericAttrib(str,'date', 'date')
			,GenericAttrib(str,'country', 'country')
			,DBMapper(Occasion,'occasions', 'OCCASION', is_list=True)
			]


class PoolUserNetwork(DBMappedObject):
	_set_root = None
	_get_root = 'POOLUSERNETWORK'
	_unique_keys = ['network', 'network_id', 'email']
	_keys = [ GenericAttrib(str,'network', 'network')
			, GenericAttrib(str,'network_id', 'id')
			, GenericAttrib(str,'email', 'email')]

class PoolUser(DBMappedObject):
	_set_root = _get_root = 'POOLUSER'
	_unique_keys = ['u_id', 'name']
	_required_attribs = ['name', 'network', 'network_id']
	_keys = [ GenericAttrib(int,'u_id'               , 'u_id'               )
			, GenericAttrib(unicode ,'name'          , 'name'               )
			, GenericAttrib(bool,'is_admin'          , 'is_admin'           )
			, GenericAttrib(bool,'is_receiver'       , 'is_receiver'        )
			, GenericAttrib(bool,'is_suspected'       , 'is_suspected'      )
			, GenericAttrib(bool,'is_selector'       , 'is_selector'      )
			, GenericAttrib(bool,'has_email'         , 'has_email'          )
			, GenericAttrib(str,'network'            , 'network'            )
			, GenericAttrib(str,'network_id'         , 'id'                 )
			, GenericAttrib(str,'screen_name'         ,'screen_name'        )
			, GenericAttrib(str,'email'              , 'email'              )
			, GenericAttrib(str,'_sex'               , 'sex'                )
			, GenericAttrib(str,'profile_picture_url', 'profile_picture_url')
			, GenericAttrib(str,'large_profile_picture_url', None, persistable = False)
			, GenericAttrib(int,'contributed_amount' , 'contribution')
			, GenericAttrib(bool,'contribution_secret', 'secret')
			, GenericAttrib(bool,'anonymous', 'anonymous')
			, DBMapper(PoolUserNetwork,'networks', 'POOLUSERNETWORK', is_dict=True, dict_key = lambda x: x.network.lower())
			]
	def _set_sex(self, sex):
		if sex and len(sex)>1:
			self._sex 		= sex[0]
		else:
			self._sex 		= sex
	def _get_sex(self):
		return self._sex
	sex = property(_get_sex, _set_sex)
	
	def get_receiver_label(self):
		return self.name
	receiver_label = property(get_receiver_label)
	
	def _get_contributed_amount_float(self):
		return float(self.contributed_amount)/100
	contributed_amount_float = property(_get_contributed_amount_float)
	
	def get_contribution_amount_text(self, is_virtual, currency):
		if self.contributed_amount:
			if(self.contribution_secret==False):
				return '%s' % h.format_currency(self._get_contributed_amount_float(), currency)
			else:
				return _("CONTRIBPAGE_LABEL_A pot of gold")
		else:
			return h.format_currency(0, currency)
	
	def get_profile_pic(self, type="PROFILE_M"):
		img = h.get_user_picture(self.profile_picture_url, type)
		return img
	def get_profile_s_pic(self):
		return self.get_profile_pic(type="PROFILE_S")
	profile_s_pic = property(get_profile_s_pic)
	
	@classmethod
	def fromMap(cls, params):
		if not tools.dict_contains(params, cls._required_attribs):
			raise InsufficientParamsException("Missing one of %s" % cls._required_attribs)
		else:
			if params['network'] == 'email':
				params['email'] = params.pop('network_id')
			params['is_selector'] = False
			print params
			return PoolUser(**dict((str(k),v) for k,v in params.iteritems()))

class PoolInvitee(PoolUser):
	_keys = PoolUser._keys + [GenericAttrib(str,'notification_method', 'notification_method')]

class Pool(DBMappedObject):
	_set_proc   = 'app.create_pool'
	_get_proc   = 'app.get_pool'
	_get_root = _set_root = 'POOL'
	_unique_keys = ['p_url']
	_expiretime = 2
	_keys = [ GenericAttrib(str,'p_url', 'p_url'				)
			, GenericAttrib(int,'p_id', 'p_id'					)
			, DBMapper(PoolUser,'participants', 'POOLUSER', is_list = True)
			, DBMapper(Product,'product', 'PRODUCT'				)
			, DBMapper(Occasion,'occasion', 'OCCASION'			)
			, GenericAttrib(unicode,'description','description'	)
			, GenericAttrib(str,'currency', 'currency'			)
			, GenericAttrib(str,'region', 'region'				)
			, GenericAttrib(str,'status', 'status'				)
			, GenericAttrib(str,'phase', 'phase'				)
			, GenericAttrib(datetime,'expiry_date', 'expiry_date')
			, GenericAttrib(bool, 'is_secret', 'is_secret'		)

			, DBMapper(PoolUser, 'admin', None, persistable = False)
			, DBMapper(PoolUser, 'receiver', None, persistable = False)
			, DBMapper(PoolUser, 'suspect', None, persistable = False)
			, DBMapper(PoolUser, 'invitees', None, persistable = False)
			, DBMapper(PoolUser, 'participant_map', None, persistable = False)
			]
	
	def get_invitee_json(self):
		return simplejson.dumps(dict((pu.network_id, pu.network_id) for pu in self.invitees))
	def get_comma_seperated_invitees(self):
		return str(','.join([inv.network_id for inv in self.invitees if inv.network and inv.network.upper() == 'FACEBOOK']))
	def get_pool_users(self):
		return [pu.u_id for pu in self.participants]
	
	def get_invitees(self, network):
		network = network.lower()
		if network == 'email':
			return [pu.networks[network].email for pu in self.participants if network in pu.networks]
		else:
			return [pu.networks[network].network_id for pu in self.participants if network in pu.networks]
	
	def get_total_contribution(self):
		total = 0
		for invitee in self.participants:
			total += (invitee.contributed_amount or 0)
		return total
	def get_total_contrib_float(self):
		return float(self.get_total_contribution())/100
	def get_amount_left(self):
		return self.product.get_price_float() - self.get_total_contrib_float()
	def get_fixed_chipin_amount(self):
		if self.product.is_virtual:
			return 1
		else:
			return self.product.get_price_float() - self.get_total_contrib_float()
	def get_number_of_contributors(self):
		return len([pu for pu in self.participants if pu.contributed_amount > 0])
	
	def get_remaining_days_tuple(self):
		diff = ((self.expiry_date + timedelta(1)) - datetime.today())
		if diff < timedelta(0):
			diff = timedelta(0)
		return (diff.days, diff.seconds/3600)
	
	def am_i_admin(self, user):
		return self.admin.u_id == user.u_id
	def am_i_receiver(self, user):
		return self.receiver.u_id == user.u_id
	def am_i_member(self, user):
		return user.u_id in self.participant_map
	def am_i_contributor(self, user):
		pu = self.participant_map.get(user.u_id)
		if pu:
			return (pu.contributed_amount or 0) > 0
		else:
			return False
		
	def can_i_view(self, user):
		return self.am_i_member(user) or not self.is_secret
	
	def determine_roles(self):
		self.participant_map = {}
		for pu in self.participants:
			self.participant_map[pu.u_id] = pu
			if not (pu.is_admin or pu.is_receiver):
				self.invitees.append(pu)
			else:
				if pu.is_admin == True:
					self.admin = pu
				if pu.is_receiver == True:
					self.receiver = pu
			if pu.is_suspected:
				self.suspect = pu
		if not self.admin:
			raise NoPoolAdminException('Pool has no Admin: %s' % self)
		if not self.receiver:
			raise NoPoolReceiverException('Pool has no Receiver: %s' % self)
	
	def get_pool_picture(self, type = "RA"):
		return h.get_pool_picture(self.p_url, type)
	
	
	def is_closed(self):
		return self.status in ["CLOSED", "COMPLETE"]
	def is_expired(self):
		return self.phase in ["EXPIRED", "EXTENSION_EXPIRED"]
	def is_funded(self):
		return self.status == "FUNDED"
	def is_contributable(self):
		return self.status == "OPEN" and (self.phase == "INITIAL" or self.phase == "EXTENDED")
	
	
	def mergewDB(self, xml):
		super(self.__class__, self).mergewDB(xml)
		self.determine_roles()
	def fromDB(self, xml):
		self.invitees = []
		self.product.currency = self.currency
		self.determine_roles()
		self.region = self.region.lower()
		return self

class AddInviteesProc(DBMappedObject):
	_set_proc = "app.add_pool_invitees"
	_set_root = "POOL_INVITEES"
	_get_root = None
	_unique_keys = ['p_id', 'p_url']
	_keys = [GenericAttrib(int, 'p_id', 'p_id')
			,GenericAttrib(str, 'p_url', 'p_url')
			,GenericAttrib(str, 'inviter_user_id', 'u_id')
			,GenericAttrib(unicode, 'description', 'description')
			,GenericAttrib(bool, 'is_secret', 'is_secret')
			,DBMapper(PoolUser, 'users', 'USER')
			]