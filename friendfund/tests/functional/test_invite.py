import logging, BeautifulSoup, uuid, urllib, simplejson
from StringIO import StringIO
from lxml import etree
from friendfund.tests import *
log = logging.getLogger(__name__)


class TestInviteController(TestController):
    ALL_PREVIEWS = set(['twitter', 'email', 'facebook', 'stream_publish'])
    def test_email_preview(self):
        headers = self._get_default_params()
        user = self._create_email_user()
        pool = self._create_ff_pool()
        
        for method in self.ALL_PREVIEWS:
            remainings = self.ALL_PREVIEWS.difference([method])
            params = {"is_secret":"","message":"qwfr","method":method, "subject":"TESTSUBJECT","v":"2"}
            response = self.app.post(url(controller="invite", pool_url = pool.p_url, action="preview"), headers=headers, params = params)
            result = simplejson.loads(response.body) 
            assert "popup" in result
            resp = BeautifulSoup.BeautifulSoup(result['popup'])
            networkslinks = [str(c['_method']) for c in resp.findAll("span", attrs={"class":"link message_preview"})]
            assert method not in networkslinks
            assert remainings.difference(networkslinks) == set()