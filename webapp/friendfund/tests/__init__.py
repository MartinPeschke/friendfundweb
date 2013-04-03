"""Pylons application test package

This package assumes the Pylons environment is already loaded, such as
when this script is imported from the `nosetests --with-pylons=test.ini`
command.

This module initializes the application via ``websetup`` (`paster
setup-app`) and provides the base testing objects.
"""
from unittest import TestCase

from paste.deploy import loadapp
from paste.script.appinstall import SetupCommand
from pylons import url
from routes.util import URLGenerator
from webtest import TestApp
import pylons.test, uuid, logging, urlparse

log = logging.getLogger(__name__)

__all__ = ['environ', 'url', 'TestController']

# Invoke websetup with the current config file
SetupCommand('setup-app').run([pylons.test.pylonsapp.config['__file__']])

environ = {}

class TestController(TestCase):
    STANDARD_HEADERS = {'Accept-Language': 'de-AT,de;q=0.9,en-US;q=0.8,en;q=0.7,de-DE;q=0.6,es-ES;q=0.5,es;q=0.5,en-gb;q=0.4,zh-TW;q=0.3,zh;q=0.2,en;q=0.1', 'X-Country': 'DE', 'Host': 'ff.friendfund.de','X-Real-Ip': '87.162.43.22'}
    
    
    def __init__(self, *args, **kwargs):
        wsgiapp = pylons.test.pylonsapp
        config = wsgiapp.config
        self.app = TestApp(wsgiapp)
        url._push_object(URLGenerator(config['routes.map'], environ))
        TestCase.__init__(self, *args, **kwargs)

        
        


    def _get_default_host(self):
        if not getattr(self, "_default_host", None):
            headers = self.STANDARD_HEADERS.copy()
            headers['Host'] = ""
            response = self.app.get(url(controller='index', action='index'), headers=headers)
            assert response.status_int == 302
            setattr(self, "_default_host", urlparse.urlparse(response.headers.get('Location'))[1])
        return self._default_host
    def _get_default_params(self):
        headers = self.STANDARD_HEADERS.copy()
        headers['Host'] = self._get_default_host()
        return headers
    def _create_email_user(self):
        USERNAME = "NOSETEST"
        headers = self._get_default_params()
        params = {"signup.email":"test_%s@friendfund.com" % str(uuid.uuid4()), "signup.name":USERNAME, "signup.pwd":"friendfund"}
        response = self.app.post(url(controller='index', action='signup'), params = params, headers=headers)
        return response.tmpl_context.user
    def _create_ff_pool(self):
        headers = self._get_default_params()
        params = {"PAYPAL_TRANSFER.email":""
                    ,"amount":"243"
                    ,"currency":"EUR"
                    ,"description":"424tfrw3ffg"
                    ,"product_picture":""
                    ,"settlementOption":"AMAZON_CERTIFICATES"
                    ,"title":"qw4etr243r23t"
                    ,"v":"2"}
        response = self.app.post(url(controller="pool", action="create"), headers = headers, params = params)
        log.info( response )
        log.info( response.tmpl_context.pool )
        return response.tmpl_context.pool