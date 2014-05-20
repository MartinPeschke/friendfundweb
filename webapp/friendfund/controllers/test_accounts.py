import logging
import urllib2
import pprint

import simplejson
from pylons import url, app_globals, config
from friendfund.lib.routes_middleware import abort, redirect

from friendfund.lib.base import BaseController

log = logging.getLogger(__name__)

def make_query(query):
    try:
        result = simplejson.load(urllib2.urlopen(query))
        return result
    except urllib2.HTTPError, e:
        print e.fp.read()


def wrap_response(resp):
    return "<html><title>list test users</title><body>%s</body></html>" % resp


class TestAccountsController(BaseController):

    def __before__(self, action, environ):
        if not app_globals.debug:
            abort(404)
        else:
            super(self.__class__, self).__before__(action, environ)

    def _get_access_token(self):
        app_id = config['fbappid']
        appsecret = config['fbapisecret']
        query = "https://graph.facebook.com/oauth/access_token?client_id=%s&client_secret=%s&grant_type=client_credentials" % (app_id, appsecret)
        a = urllib2.urlopen(query)
        token = a.read().split('=')[1]
        return app_id, token

    def list(self):
        app_id, token = self._get_access_token()
        userlist = make_query("https://graph.facebook.com/%s/accounts/test-users?access_token=%s"%(app_id, token))['data']
        pprint.pprint(userlist)
        html = []
        for user in userlist:
            html.append("<tr><td>%s</td><td><a href=\"%s\">login</a></td><td>%s</td></tr>" % (user['id'], user.get('login_url'), user.get('access_token')))
        return wrap_response("<table>%s</table>" % "".join(html))

    def create(self):
        app_id, token = self._get_access_token()
        response = make_query("https://graph.facebook.com/%s/accounts/test-users?installed=false&permissions=email&method=post&access_token=%s"%(app_id, token))
        return redirect(url(controller = "test_accounts", action="list"))