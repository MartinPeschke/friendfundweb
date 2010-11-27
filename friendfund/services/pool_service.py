import md5, uuid, os

from pylons import app_globals, tmpl_context
from pylons.i18n import _
from friendfund.lib.helpers import get_upload_pic_name
from friendfund.model.pool import Pool, AddInviteesProc, PoolInvitee

class MissingPermissionsException(Exception):pass

class PoolService(object):
	"""
		This is shared between all threads, do not stick state in here!
	"""
	def __init__(self, config):
		self.config = config
	
	def invite_myself(self, pool, user):
		if not pool.am_i_member(user):
			pool = app_globals.dbm.set(AddInviteesProc(p_id = pool.p_id
						, p_url = pool.p_url
						, event_id = pool.event_id
						, inviter_user_id = user.u_id
						, users=[PoolInvitee.fromUser(user)]
						, description = pool.description
						, is_secret = pool.is_secret))
			app_globals.dbm.expire(Pool(p_url = pool.p_url))