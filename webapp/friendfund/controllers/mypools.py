import logging

from pylons import request, session as websession, tmpl_context as c, app_globals as g

from friendfund.lib.auth.decorators import logged_in
from friendfund.lib.base import BaseController
from friendfund.model.mypools import GetUserFriendPoolsProc, GetMyPoolsProc
from friendfund.model.activity import GetActivityStreamProc

log = logging.getLogger(__name__)

class MypoolsController(BaseController):

    @logged_in(ajax=False)
    def index(self):
        c.my_pools  = g.dbm.get(GetMyPoolsProc, u_id = c.user.u_id)
        return self.render('/mypools/index.html')

    @logged_in(ajax=False)
    def friends(self):
        c.my_pools = g.dbm.get(GetUserFriendPoolsProc, u_id = c.user.u_id)
        return self.render('/mypools/friends_pools.html')

    @logged_in(ajax=False)
    def stream(self):
        c.include_friend = request.params.get("all", None)
        if c.include_friend is not None:
            websession['session_vars.include_friend'] = c.include_friend = bool(c.include_friend)
        else:
            c.include_friend = websession.get('session_vars.include_friend', True)
        c.activity = g.dbm.get(GetActivityStreamProc, u_id = c.user.u_id, include_friend = c.include_friend)
        return self.render('/mypools/stream.html')
