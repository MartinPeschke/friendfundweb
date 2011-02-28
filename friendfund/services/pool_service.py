from __future__ import with_statement
import md5, uuid, os, formencode, logging
log = logging.getLogger(__name__)

from pylons import app_globals, tmpl_context, request, session as websession
from pylons.i18n import _
from friendfund.lib import helpers as h
from friendfund.model.pool import Pool, AddInviteesProc, PoolInvitee, PoolUser, Occasion
from friendfund.model.product import Product
from friendfund.tasks.photo_renderer import remote_profile_picture_render

class MissingPermissionsException(Exception):pass
class MissingPoolException(Exception):pass
class MissingProductException(Exception):pass
class MissingOccasionException(Exception):pass
class MissingReceiverException(Exception):pass
class MissingAmountException(MissingProductException):pass


class PoolService(object):
	"""
		This is shared between all threads, do not stick state in here!
	"""
	def __init__(self, config):
		self.config = config
	
	def create_free_form(self):
		from friendfund.model.forms.pool import PoolCreateForm
		
		pool_map = formencode.variabledecode.variable_decode(request.params)
		pool_schema = PoolCreateForm().to_python(pool_map, state = request)
		
		pool = Pool(title = pool_schema['title'],
				description = pool_schema['description'],
				currency = pool_schema['currency']
			)
		
		pool.set_amount_float(pool_schema.pop("amount"))
		pool.occasion = Occasion(key="EVENT_OTHER", date=pool_schema['date'])
		
		if "tracking_link" in pool_schema:
			pool.product = Product(name=pool_schema.get("product_name"), 
									description= pool_schema.get("product_description"),
									tracking_link= pool_schema.get("tracking_link"),
									picture= pool_schema.get("product_picture") )
		
		
		
		admin = PoolUser(**tmpl_context.user.get_map())
		admin.is_admin = True
		pool.participants.append(admin)
		
		receiver = PoolUser(**tmpl_context.user.get_map())
		receiver.is_receiver = True
		pool.participants.append(receiver)
		return pool
	
	def create_group_gift(self):
		pool = websession.get('pool')
		if pool is None:
			raise MissingPoolException()
		elif pool.product is None:
			raise MissingProductException()
		elif pool.occasion is None:
			raise MissingOccasionException()
		elif pool.receiver is None:
			raise MissingReceiverException()
		admin = PoolUser(**tmpl_context.user.get_map())
		if h.users_equal(pool.receiver, admin):
			admin.profile_picture_url = pool.receiver.profile_picture_url
		admin.is_admin = True
		
		#### Setting up the Pool for initial Persisting
		pool.participants.append(admin)
		locals = {"admin_name":admin.name, "receiver_name" : pool.receiver.name, "occasion_name":pool.occasion.get_display_name()}
		pool.description = (_("INVITE_PAGE_DEFAULT_MSG_%(admin_name)s has created a Friend Fund for %(receiver_name)s's %(occasion_name)s. Come and chip in!")%locals)
		remote_profile_picture_render.delay([(pu.network, pu.network_id, pu.large_profile_picture_url or pu.profile_picture_url) for pu in pool.participants])
		return pool
	
	def invite_myself(self, pool, user):
		if not pool.am_i_member(user):
			pool = app_globals.dbm.set(AddInviteesProc(p_id = pool.p_id
						, p_url = pool.p_url
						, event_id = pool.event_id
						, inviter_user_id = user.u_id
						, users=[PoolInvitee.fromUser(user)]
						, description = pool.description
						, is_secret = pool.is_secret
						, opt_out = True))
			app_globals.dbm.expire(Pool(p_url = pool.p_url))