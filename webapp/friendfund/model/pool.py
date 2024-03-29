import logging
import itertools
import random
import operator
import uuid
from datetime import datetime, timedelta

import formencode
from BeautifulSoup import BeautifulSoup
from pylons.i18n import _

from friendfund.lib import helpers as h, tools
from friendfund.model.mapper import DBMappedObject, GenericAttrib, DBMapper
from friendfund.model.product import Product, DisplayProduct
from friendfund.services import static_service as statics
from friendfund.tasks.celerytasks.photo_renderer import remote_product_picture_render


strbool = formencode.validators.StringBoolean(if_missing=False, if_empty=False)

log = logging.getLogger(__name__)

class NoPoolAdminException(AttributeError):pass
class NoPoolReceiverException(AttributeError):pass
class TooManyPoolAdminException(AttributeError):pass
class TooManyPoolReceiverException(AttributeError):pass
class InsufficientParamsException(Exception):pass

class PoolComment(DBMappedObject):
    _get_root = _set_root = 'COMMENT'
    _set_proc = _get_proc = "app.add_pool_comment"
    _unique_keys = ['p_url', 'u_id']

    _keys = [	GenericAttrib(str,'p_url','p_url')
        ,GenericAttrib(int,'u_id','u_id')
        ,GenericAttrib(unicode,'name','name')
        ,GenericAttrib(unicode,'comment','comment')
        ,GenericAttrib(bool,'is_contrib_message','is_contrib_message')
        ,GenericAttrib(unicode,'profile_picture_url','profile_picture_url')
        ,GenericAttrib(int,'recency','recency')
    ]
    def get_profile_pic(self, type):
        return self._statics.get_user_picture(self.profile_picture_url, type)

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


class PoolThankYouMessage(DBMappedObject):
    """
        exec app.add_thank_you_message'<POOL p_url ="UC0xMjUyNA~~" message = "thanks so much"/>'
    """
    _get_root = _set_root = 'POOL'
    _set_proc = _get_proc = "app.add_thank_you_message"
    _unique_keys = ['p_url']
    _keys = [	GenericAttrib(str,'p_url','p_url')
        ,GenericAttrib(unicode,'message','message')
    ]



class PoolDescription(DBMappedObject):
    """
        exec app.add_pool_description '<POOL url ="UC0xMDE4OQ~~" description = "balh de blah"/>'
    """
    _get_root = _set_root = 'POOL'
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

class Occasion(DBMappedObject):
    _get_root = _set_root = 'OCCASION'
    _unique_keys = ['key']
    _keys = [GenericAttrib(str,'key' , 'key'  )
        ,GenericAttrib(unicode,'name', 'name')
        ,GenericAttrib(datetime,'date', 'date')
        ,GenericAttrib(str,'picture_url', 'picture_url', persistable = False)
        ,GenericAttrib(bool,'custom', 'custom', persistable = False)
    ]

    def get_display_date(self):
        return h.format_date(self.date)
    display_date = property(get_display_date)

    def get_display_name(self):
        return self.name or (self.key and _(self.key)) or ''
    def get_display_label(self):
        return '%s - %s' % (self.get_display_name(), h.format_date(self.date))
    display_label = property(get_display_label)

    def get_internal_date_format(self):
        return self.date and h.format_date_internal(self.date) or ''
    internal_date_format = property(get_internal_date_format)

class OccasionSearch(DBMappedObject):
    _get_proc = "app.get_occasion_group"
    _get_root = None
    _set_root = 'OCCASION'
    _unique_keys = ['date', 'country']
    _keys = [GenericAttrib(str,'date', 'date')
        ,GenericAttrib(str,'country', 'country')
        ,DBMapper(Occasion,'occasions', 'OCCASION', is_list=True)
    ]


class PoolUserNetwork(DBMappedObject):
    _set_root = _get_root = 'POOLUSERNETWORK'
    _unique_keys = ['network', 'network_id', 'email']
    _keys = [ GenericAttrib(str,'network', 'network')
        , GenericAttrib(str,'network_id', 'id')
        , GenericAttrib(str,'email', 'email')]

class PoolUser(DBMappedObject):
    _possible_sexes = ['m', 'f']
    _set_root = _get_root = 'POOLUSER'
    _unique_keys = ['network', 'name', 'network_id']
    _required_attribs = ['network', 'name', 'network_id']
    _email_required_attribs = ['network', 'name']
    _keys = [ GenericAttrib(int,		'u_id'                       , 'u_id'               , persistable = False)
        , GenericAttrib(unicode, 	'name'                       , 'name'               )
        , GenericAttrib(unicode, 	'message'                    , 'message'            )
        , GenericAttrib(bool,		'is_admin'                   , 'is_admin'           , default = False)
        , GenericAttrib(bool,		'is_receiver'                , 'is_receiver'        , default = False)
        , GenericAttrib(bool,		'is_suspected'               , 'is_suspected'       )
        , GenericAttrib(datetime,	'dob'                        , None                 , persistable = False)
        , GenericAttrib(str,		'screen_name'                ,'screen_name'         )
        , GenericAttrib(str,		'network'                    ,'network'             )
        , GenericAttrib(str,		'locale'                     ,'locale'             )
        , GenericAttrib(str,		'network_id'                 ,'id'                  )
        , GenericAttrib(str,		'email'                      , 'email'              )###TODO: VERY DIRTY!
        , GenericAttrib(str,		'_sex'                       , 'sex'                )
        , GenericAttrib(str,		'profile_picture_url'        , 'profile_picture_url')
        , GenericAttrib(str,		'large_profile_picture_url'  , None                 , persistable = False)
        , GenericAttrib(int,		'contributed_amount'         , 'contribution'       )
        , GenericAttrib(bool,		'contribution_secret'        , 'secret'             )
        , DBMapper(PoolUserNetwork,	'networks', 'POOLUSERNETWORK', is_dict=True, dict_key = lambda x: x.network.lower())
    ]
    def get_profile_pic(self, type):
        return self._statics.get_user_picture(self.profile_picture_url, type)

    def _set_sex(self, sex):
        if sex and len(sex)>1:
            self._sex 		= sex[0]
        else:
            self._sex 		= sex
    def _get_sex(self):
        return (self._sex and self._sex == 'm' or random.choice(self._possible_sexes))
    sex = property(_get_sex, _set_sex)

    def get_receiver_label(self):
        return self.name
    receiver_label = property(get_receiver_label)

    def is_contributor(self):
        return bool(self.contributed_amount)

    def _get_contributed_amount_float(self):
        return float(self.contributed_amount)/100
    contributed_amount_float = property(_get_contributed_amount_float)

    def get_invitee_label(self, currency):
        if self.contributed_amount:
            if(self.contribution_secret==False):
                return _('FF_POOLPAGE_INVITEE_LABEL_%s - Chipped in %s') % (self.name, h.format_currency(self.contributed_amount_float, currency))
            else:
                return _("FF_POOLPAGE_INVITEE_LABEL_%s - Chipped in") % self.name
        else:
            return self.name

    @classmethod
    def from_map(cls, params):
        if params['network'] == 'email':
            params['email'] = params.pop('network_id')
            if not tools.dict_contains(params, cls._email_required_attribs):
                raise InsufficientParamsException("Missing one of %s" % cls._email_required_attribs)
            else:
                params['email'] = params['email'] or "%s_NO_INPUT@friendfund.com" % uuid.uuid4()
        elif not tools.dict_contains(params, cls._required_attribs):
            raise InsufficientParamsException("Missing one of %s" % cls._required_attribs)
        return cls(**dict((str(k),v) for k,v in params.iteritems()))

class PoolInvitee(PoolUser):
    _keys = PoolUser._keys + [GenericAttrib(str,'notification_method', 'notification_method')]
    _transl = {"default_email":"email"}
    @classmethod
    def fromUser(cls, user):
        obj = cls()
        for k in user._keys:
            nkey = cls._transl.get(k.pykey, k.pykey)
            if hasattr(obj, nkey):
                setattr(obj, nkey, getattr(user, k.pykey))
        return obj



class PoolStub(DBMappedObject):
    _get_proc   = _set_proc   = None
    _get_root = _set_root = 'POOL'
    _unique_keys = ['p_url']
    _cacheable = False
    _keys = [ GenericAttrib(str,		'p_url', 			'p_url'						,required = True)
        , GenericAttrib(int,		'p_id',				'p_id'						,required = True)
    ]


class Pool(DBMappedObject):
    _set_proc   = 'app.create_pool'
    _get_proc   = 'app.get_pool'
    _get_root = _set_root = 'POOL'
    _unique_keys = ['p_url']
    _expiretime = 2
    _keys = [ GenericAttrib(str,		'p_url', 			'p_url'						,required = True)
        , GenericAttrib(int,		'p_id',				'p_id'						,required = True)
        , GenericAttrib(int,		'event_id', 		'event_id'					)
        , GenericAttrib(unicode,	'title',			'title'						)
        , GenericAttrib(unicode,	'description',		'description'				)
        , GenericAttrib(unicode,	'thank_you_message','thank_you_message'			)
        , GenericAttrib(int,		'amount',			'amount'					)
        , GenericAttrib(str,		'currency', 		'currency'					)
        , GenericAttrib(bool,		'includes_fee',		'includes_fee'				)
        , GenericAttrib(str,		'status', 			'status'					)
        , GenericAttrib(str,		'phase',  			'phase'						)
        , GenericAttrib(datetime,	'expiry_date', 		'expiry_date'				)
        , GenericAttrib(int,		'remaining_seconds','remaining_seconds'			)
        , GenericAttrib(bool, 		'is_secret', 		'is_secret'					)
        , GenericAttrib(bool, 		'has_address', 		'has_address'				)
        , GenericAttrib(str,	 	'merchant_key', 	'merchant_key'				)
        , GenericAttrib(str,	 	'settlementOption', 'settlement'				)
        , GenericAttrib(str,	 	'paypal_email', 	'paypal_email'				)
        , GenericAttrib(int,	 	'total_contribution', 'total_contribution'		)
        , GenericAttrib(int,	 	'total_contributors', 'total_contributors'		)
        , GenericAttrib(str,	 	'u_id_csv'			, 'u_id_csv'				)

        , DBMapper(Product, 		'product', 			'PRODUCT'					)
        , DBMapper(Occasion,		'occasion', 		'OCCASION'					)
        , DBMapper(PoolUser,		'participants', 	'POOLUSER', is_list = True)

        , DBMapper(PoolUser, 'admin', None, persistable = False)
        , DBMapper(PoolUser, 'receiver', None, persistable = False)
        , DBMapper(PoolUser, 'suspect', None, persistable = False)
        , DBMapper(PoolUser, 'invitees', None, persistable = False)
        , DBMapper(PoolUser, 'participant_map', None, persistable = False)
    ]

    def get_contributors(self):
        return itertools.ifilter(lambda x:x.is_contributor(),self.participants)

    def get_amount_float(self):
        try:
            return float(self.amount)/100
        except:
            return None

    def set_amount_float(self, value):
        if value is None: return
        self.amount = int(value*100)
    def get_display_amount(self):
        return h.format_currency(self.get_amount_float(), self.currency)
    def get_total_contribution(self):
        return self.total_contribution
    def get_total_contrib_float(self):
        return float(self.get_total_contribution())/100
    def get_amount_left(self):
        return float(self.amount - self.total_contribution)/100
    get_fixed_chipin_amount = get_amount_left

    def get_number_of_contributors(self):
        return self.total_contributors
    def get_suggested_amount(self):
        return (self.amount-self.get_total_contribution())/((len(self.participant_map)-self.get_number_of_contributors()) or 1)
    def get_suggested_amount_float(self):
        return self.get_amount_left()/((len(self.participant_map)-self.get_number_of_contributors()) or 1)

    def get_product_display_label(self, words = 5, seperator = ' ', include_price = True):
        if include_price:
            return '%s%s%s' % (h.word_truncate_plain(self.product.name, words), seperator, self.get_display_amount())
        else:
            return h.word_truncate_plain(self.product.name, words)
    product_display_label = property(get_product_display_label)
    def get_display_title(self, length = 100):
        return h.word_truncate_by_letters(self.title, length)
    def get_display_description(self):
        return self.description
    def get_text_description(self):
        return ''.join(BeautifulSoup(self.description).findAll(text=True))


    def get_product_display_picture(self, type="POOL", secured = False):
        if self.product:
            picture = self.product.picture
            if not statics.url_is_local(picture):
                log.warning("EXTERNAL_PRODUCT_PICTURE <%s : %s>", self.p_url, picture)
                remote_product_picture_render.delay(self.p_url, self.product.picture)
            return self._statics.get_product_picture(picture, type, secured = secured)
        else:
            return self._statics.get_product_picture(None, type, secured = secured)

    def get_remaining_days(self):
        diff = ((self.expiry_date + timedelta(1)) - datetime.today())
        if diff < timedelta(0):
            diff = timedelta(0)
        return diff.days

    def get_pool_picture(self, type = "RA"):
        return self._statics.get_pool_picture(self.p_url, type)
    def get_pool_picture_tiles(self, type = "RA"):
        pool_picture_url = statics.tokenize_url(self.p_url)
        return self._statics.get_pool_picture(pool_picture_url, type)
    def funding_progress(self):
        return float(self.get_total_contribution()) / self.amount

    def get_my_message(self, user):
        log.warning("DEPRECATED - Pool.get_my_message() -- TODO")
        return False

    def am_i_admin(self, user):
        return self.admin.u_id == user.u_id
    def am_i_receiver(self, user):
        return self.receiver.u_id == user.u_id
    def am_i_member(self, user):
        return user.u_id in self.participant_map
    def am_i_contributor(self, user):
        log.warning("DEPRECATED - Pool.am_i_contributor()")
        return False
    def am_i_possibly_contributor(self, user):
        return user.u_id in self.partial_contributor_map

    def can_i_leave(self, user):
        return self.am_i_member(user) and not user.u_id in [self.admin.u_id, self.receiver.u_id] and not self.am_i_possibly_contributor(user)

    def can_cancel_payment(self, user):
        return self.am_i_possibly_contributor(user) and self.is_contributable()

    def get_random_n_invitees(self, n):
        try:
            return random.sample(self.invitees, n)
        except ValueError, e:
            return self.invitees

    def get_require_addresses(self):
        return self.require_address
    require_addresses = property(get_require_addresses)

    def determine_roles(self):
        self.participant_map = self.u_id_csv and set(map(int, self.u_id_csv.split(","))) or set()
        self.partial_contributor_map = set()
        for pu in self.participants:
            if not (pu.is_admin or pu.is_receiver):
                self.invitees.append(pu)
            else:
                if pu.is_admin == True:
                    self.admin = pu
                if pu.is_receiver == True:
                    self.receiver = pu
            if pu.is_contributor() == True:
                self.partial_contributor_map.add(pu.u_id)
        if not self.admin:
            raise NoPoolAdminException('Pool has no Admin: %s' % self)
        if not self.receiver:
            raise NoPoolReceiverException('Pool has no Receiver: %s' % self)

        if self.participant_map:
            self.participant_map = self.participant_map.difference([self.receiver.u_id]).union([self.admin.u_id])
        if self.receiver.u_id != self.admin.u_id:
            self.participants = filter(lambda x: x.u_id!=self.receiver.u_id, self.participants)

    def is_closed(self):
        return self.status in ["CLOSED", "COMPLETE"]
    def is_closed_or_funded(self):
        return self.status in ["CLOSED", "FUNDED", "COMPLETE"]
    def is_expired(self):
        return self.phase in ["EXPIRED", "EXTENSION_EXPIRED"]
    def is_funded(self):
        return self.status == "FUNDED"
    def is_contributable(self):
        return self.status == "OPEN" and (self.phase in ["INITIAL", "EXTENDED"])

    def get_remaining_time_tuple(self):
        d = self.remaining_time.days
        h = self.remaining_time.seconds / 3600
        m = (self.remaining_time.seconds % 3600)/60
        s = self.remaining_time.seconds % 60
        return d,h,m,s

    def fromDB(self, xml):
        self.invitees = []
        self.determine_roles()
        if self.remaining_seconds<0 or self.is_closed_or_funded():
            remainder = 0
        else:
            remainder = self.remaining_seconds
        setattr(self, "remaining_time", timedelta(0, remainder))
        return self

    def set_product(self, dproduct):
        if not isinstance(dproduct, DisplayProduct):
            raise TypeError("Product not of correct type: DisplayProduct, found: %s" % type(dproduct))
        self.product = Product(**dproduct.to_map())
        self.amount = dproduct.get_total_price_units()
        self.currency = dproduct.currency
        self.title = self.description = self.get_product_display_label(words = 8, include_price = False)

    def get_product(self):
        if not self.product:
            raise AttributeError("NoProductPresent")
        else:
            dproduct = DisplayProduct(**self.product.to_map())
            dproduct.price = self.amount - dproduct.shipping_cost
            dproduct.currency = self.currency
            dproduct.currency = self.currency
            return dproduct

class AddInviteesProc(DBMappedObject):
    _set_proc = "app.add_pool_invitees"
    _set_root = "POOL_INVITEES"
    _get_root = None
    _unique_keys = ['p_id', 'p_url']
    _keys = [GenericAttrib(int, 'p_id', 'p_id')
        ,GenericAttrib(str, 'p_url', 'p_url')
        ,GenericAttrib(str, 'event_id', 'event_id')
        ,GenericAttrib(str, 'inviter_user_id', 'u_id')
        ,GenericAttrib(unicode, 'subject', 'subject')
        ,GenericAttrib(unicode, 'message', 'message')
        ,GenericAttrib(bool, 'is_secret', 'is_secret')
        ,DBMapper(PoolUser, 'users', 'USER')
    ]

class GetMoreInviteesProc(DBMappedObject):
    """exec app.get_paged_invitee '<POOL p_url = "P3iF.WWW-SPIEGEL-DE" page_no = "1"/>' """
    _set_proc = _get_proc = "app.get_paged_invitee"
    _get_root = _set_root = "POOL"
    _unique_keys = ['page_no', 'p_url']
    _keys = [GenericAttrib(int, 'page_no', 'page_no')
        ,GenericAttrib(str, 'p_url', 'p_url')
        ,DBMapper(PoolUser, 'list', 'POOLUSER', is_list = True)
    ]
    def fromDB(self, xml):
        setattr(self, "has_more", len(self.list)>=500) ####TODO: get proper boolean from database

class UpdatePoolProc(DBMappedObject):
    _get_proc = _set_proc   = 'app.update_pool'
    _get_root = _set_root = 'POOL'
    _unique_keys = ['p_url']
    _cacheable = False
    _keys = [ GenericAttrib(str,		'p_url', 			'p_url'						)
        , GenericAttrib(unicode,	'title',			'title'						)
        , GenericAttrib(unicode,	'description',		'description'				)
        , DBMapper(Product, 		'product', 			'PRODUCT'					)
    ]

class SimpleUserNetwork(DBMappedObject):
    _cacheable = False
    _get_proc = _set_proc   = None
    _get_root = _set_root = 'POOLUSER'
    _unique_keys = ['network_id']
    _keys = [GenericAttrib(str,'network_id','id'),GenericAttrib(str,'network','network'),GenericAttrib(str,'email','email'),GenericAttrib(bool,'is_receiver','is_receiver')]


class GetPoolInviteesProc(DBMappedObject):
    """	exec [app].[get_pool_invite] '<POOL p_url = "P3iF.WWW-SPIEGEL-DE"/>'"""
    _expiretime = 5
    _get_proc = _set_proc   = 'app.get_pool_invite'
    _get_root = _set_root = 'POOL'
    _unique_keys = ['p_url', 'network']
    _keys = [ GenericAttrib(str,'p_url','p_url')
        , GenericAttrib(int,'p_id','p_id')
        , GenericAttrib(str,'network','network')
        , DBMapper(SimpleUserNetwork, 'users', 'POOLUSER', is_list = True)
        , DBMapper(PoolUser, 'receiver', None, persistable = False)]

    def fromDB(self, xml):
        setattr(self, "idset", set(map(operator.attrgetter("network_id"), self.users)))
        for pu in self.users:
            if pu.is_receiver:
                self.receiver = pu
                break

class JoinPoolProc(DBMappedObject):
    """	[app].[join_pool]  '<POOL_INVITEES p_url = "123" u_id = "123"/>'"""
    _cacheable = False
    _get_proc = _set_proc   = 'app.join_pool'
    _get_root = _set_root = 'POOL_INVITEES'
    _unique_keys = ['p_url', 'u_id']
    _keys = [ GenericAttrib(str,'p_url','p_url'), GenericAttrib(int,'u_id','u_id')]
class IsContributorProc(DBMappedObject):
    """
        'EXEC app.get_is_contributor '<POOL p_url = "P3zu.2314" u_id = "142294"/>'
        <RESULT status="0" proc_name="get_is_contributor"><USER is_contributor="0" /></RESULT>
    """
    _cacheable = False
    _get_proc = _set_proc   = 'app.get_is_contributor'
    _set_root = "POOL"
    _get_root = "USER"
    _unique_keys = ['p_url', 'u_id']
    _keys = [ GenericAttrib(str,'p_url','p_url'), GenericAttrib(int,'u_id','u_id'), GenericAttrib(bool,'is_contributor','is_contributor')]
class LeavePoolProc(DBMappedObject):
    """	[app].[join_pool]  '<POOL_INVITEES p_url = "123" u_id = "123"/>'"""
    _cacheable = False
    _get_proc = _set_proc   = 'app.leave_pool'
    _get_root = _set_root = 'POOL'
    _unique_keys = ['p_url', 'u_id']
    _keys = [ GenericAttrib(str,'p_url','p_url'), GenericAttrib(int,'u_id','u_id')]

class CancelPaymentProc(DBMappedObject):
    """	[app].[cancel_contribution] '<POOL p_url="P3H4." u_id ="142400" />'"""
    _cacheable = False
    _get_proc = _set_proc   = 'app.cancel_contribution'
    _get_root = _set_root = 'POOL'
    _unique_keys = ['p_url', 'u_id']
    _keys = [ GenericAttrib(str,'p_url','p_url'), GenericAttrib(int,'u_id','u_id')]






class ECardContributors(DBMappedObject):
    """<RESULT status="0" proc_name="get_ecard"><POOLUSER name="Henrietta Regina Goldmine" picture="8c/00/8c004e53261405b228a1f0f00c642c90" amount="800" co_message="chip in please !" /></RESULT>"""
    _cacheable = False
    _get_proc = _set_proc   = None
    _get_root = _set_root = 'POOLUSER'
    _unique_keys = ['p_url', 'u_id']
    _keys = [ GenericAttrib(unicode,'name','name')
        , GenericAttrib(unicode,'picture','picture')
        , GenericAttrib(unicode,'co_message','co_message')
        , GenericAttrib(int,'amount','amount')]
    def get_profile_pic(self, type="PROFILE_M", secured = False):
        return self._statics.get_user_picture(self.picture, type, secured = secured)
    def get_amount_float(self):
        try:
            return float(self.amount)/100
        except:
            return None

class GetECardContributorsProc(DBMappedObject):
    """exec app.get_ecard '<POOL p_url = "P3oB.my-first-pool"/>'"""
    _get_proc = _set_proc = 'app.get_ecard'
    _get_root = None
    _set_root = 'POOL'
    _unique_keys = ['p_url']
    _expiretime = 30
    _keys = [ GenericAttrib(str,'p_url','p_url')
        , DBMapper(ECardContributors, 'contributors', "POOLUSER", is_list = True)
    ]






class FeaturedPool(Pool):
    _cacheable = False