import logging, BeautifulSoup, uuid, urllib
from StringIO import StringIO
from lxml import etree
from friendfund.tests import *
log = logging.getLogger(__name__)


class TestIndexController(TestController):
    def _test_locales(self, list, expected):
        headers = self._get_default_params()
        locales = {}
        for l in list:
            if l:
                headers['Accept-Language'] = l
            elif 'Accept-Language' in headers:
                del headers['Accept-Language']
            response = self.app.get(url(controller='index', action='index'), headers=headers)
            lang = response.session['lang']
            assert lang == expected
            #log.info("TESTED %s => %s (expected: %s)", l, lang, expected)
    def test_index_default_lang_DE(self):
        self._test_locales(['de-CH', 'de-DE', 'de_ch', 'de_AT', 'de-at', 'de'], 'de')
    def test_index_default_lang_ES(self):
        self._test_locales(['es-ES,es', 'es-ar', 'es-co', 'es-hn', 'es'], 'es')
    def test_index_default_lang_EN(self):
        self._test_locales(['en-UK,en', 'en-GB,en', 'en-US,en', 'en_US','en-US,en;q=0.9,de-DE;q=0.8,de;q=0.7,de-AT;q=0.6,es-ES;q=0.5,es;q=0.5,en-gb;q=0.4,zh-TW;q=0.3,zh;q=0.2,en;q=0.1', 'en'], 'en')
    def test_index_default_lang_DEFAULT(self):
        self._test_locales(['zh-CN,zh', 'zh','fr-FR,fr','fr','FR-CA','ro-mo'], 'en')
    def test_index_default_lang_INVALID(self):
        self._test_locales(['ghsrefgsehgkljsehgkljsehgjklghjklshgsehgklg'], 'en')
    def test_index_default_lang_MISSING(self):
        self._test_locales([''], 'en')
    
    def test_sitemap(self):
        headers = self._get_default_params()
        response = self.app.get(url(controller='index', action='sitemap'), headers=headers)
        resp_tree = etree.parse(StringIO(response.body))
        assert len(resp_tree.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url")) > 24
    
    def test_signup_get_page(self):
        headers = self._get_default_params()
        params = {}
        response = self.app.get(url(controller='index', action='signup'), params = params, headers=headers)
        assert response.status_int == 200
        b = BeautifulSoup.BeautifulSoup(response.body)
        assert b.find("a", attrs = {"class":"facebookBtn"}) is not None
        assert b.find("a", attrs = {"class":"twitterBtn"}) is not None
    
    def test_signup_post_correct_data(self):
        USERNAME = "NOSETEST"
        headers = self._get_default_params()
        params = {"signup.email":"test_%s@friendfund.com" % str(uuid.uuid4()), "signup.name":USERNAME, "signup.pwd":"friendfund"}
        response = self.app.post(url(controller='index', action='signup'), params = params, headers=headers)
        assert response.status_int == 302
        assert response.tmpl_context.user.is_anon == False
        assert response.tmpl_context.user.name == USERNAME
        response = self.app.get(response.headers.get('Location'), headers=headers)
        assert response.status_int == 200
        assert response.tmpl_context.user.is_anon == False
        assert response.tmpl_context.user.name == USERNAME
        
        
    def test_signup_post_corrupt_data(self):
        USERNAME = "NOSETEST"
        headers = self._get_default_params()
        params = {}
        response = self.app.post(url(controller='index', action='signup'), params = params, headers=headers)
        assert response.status_int == 200
        assert "name" in response.tmpl_context.signup_errors
        assert "email" in response.tmpl_context.signup_errors
        assert "pwd" in response.tmpl_context.signup_errors
    
    def test_signup_post_double_signup(self):
        USERNAME = "NOSETEST"
        headers = self._get_default_params()
        params = {"signup.email":"test_%s@friendfund.com" % str(uuid.uuid4()), "signup.name":USERNAME, "signup.pwd":"friendfund"}
        response = self.app.post(url(controller='index', action='signup'), params = params, headers=headers)
        self.app.reset()
        response = self.app.post(url(controller='index', action='signup'), params = params, headers=headers)
        assert response.status_int == 200
        assert "email" in response.tmpl_context.signup_errors