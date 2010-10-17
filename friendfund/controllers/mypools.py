import logging

from pylons import request, response, session, tmpl_context as c, url, app_globals as g
from pylons.controllers.util import abort, redirect

from friendfund.lib.auth.decorators import logged_in
from friendfund.lib.base import BaseController
from friendfund.model.authuser import UserNotLoggedInWithMethod, GetFriendsNotSupported
from friendfund.model.mypools import GetUserFriendPoolsProc, UserFriend, GetMyPoolsProc

log = logging.getLogger(__name__)

class MypoolsController(BaseController):
	navposition=g.globalnav[1][2]
	
	@logged_in(ajax=False)
	def index(self):
		c.my_pools  = g.dbm.get(GetMyPoolsProc, u_id = c.user.u_id)
		return self.render('/mypools/index.html')
	
	@logged_in(ajax=False)
	def friends(self):
		poolsparams = GetUserFriendPoolsProc(u_id = c.user.u_id)
		poolsparams.friends = []
		for network in c.user.networks:
			friends = []
			try:
				friends = c.user.get_friends(network)
			except UserNotLoggedInWithMethod, e:
				pass
			except GetFriendsNotSupported, e:
				pass
			for friend in friends:
				poolsparams.friends.append(UserFriend(network=network, network_id=friend))
		c.my_pools = g.dbm.call(poolsparams, GetUserFriendPoolsProc)
		return self.render('/mypools/friends_pools.html')