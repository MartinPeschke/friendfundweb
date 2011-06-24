import logging
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
            log.info("TESTED %s => %s (expected: %s)", l, lang, expected)
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
        resp_tree = etree.fromstring(response)
        assert len(resp_tree.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url")) > 10