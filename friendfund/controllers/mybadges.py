import logging
from pylons import request, response, session, tmpl_context as c, url, app_globals as g
from pylons.controllers.util import abort, redirect
from pylons.decorators import jsonify

from friendfund.lib import helpers as h
from friendfund.lib.auth.decorators import logged_in
from friendfund.lib.base import BaseController, render, _
from friendfund.model.badge import GetMyBadgesProc, ALLBADGES_DICT, GetFriendsBadgesProc, UserFriend, Badge
from friendfund.model.authuser import UserNotLoggedInWithMethod, GetFriendsNotSupported

log = logging.getLogger(__name__)


class MybadgesController(BaseController):
	navposition=g.globalnav[2][2]
	@logged_in(ajax=False)
	def index(self):
		c.mybadges = g.dbm.get(GetMyBadgesProc, u_id = c.user.u_id)
		return self.render('/mybadges/index.html')
	
	@jsonify
	def panel(self, badge_name):
		c.badge = badge_name
		c.badgename = _(badge_name)
		c.badge_url = h.get_badge_picture(ALLBADGES_DICT.get(badge_name, {}).get('badge_url'), 'large')
		c.badge_description = ALLBADGES_DICT.get(badge_name, {}).get('description','Fail')
		return {"html":render("/messages/badge.html").strip()}
	
	@jsonify
	@logged_in(ajax=True)
	def friends(self):
		badgeparams = GetFriendsBadgesProc(u_id = c.user.u_id)
		badgeparams.friends = []
		for network in c.user.networks:
			friends = []
			try:
				friends = c.user.get_friends(network)
			except UserNotLoggedInWithMethod, e:
				pass
			except GetFriendsNotSupported, e:
				pass
			for friend in friends:
				badgeparams.friends.append(UserFriend(network=network, network_id=friend))
		c.friend_badges = g.dbm.call(badgeparams, GetFriendsBadgesProc)
		c.all_badges = ALLBADGES_DICT
		return {"html":self.render('/mybadges/friends_badges.html').strip()}
	
	
	
	
	############################################################################
	def test(self):
		print c.user.networks.get("twitter").network_id, request.params.get("badge_name")
		if not ('twitter' in c.user.networks and c.user.networks.get("twitter").network_id == 125415114):
			return redirect(url('home'))
		c.messages.append(Badge(name = request.params.get("badge_name")))
		return redirect(url('home'))