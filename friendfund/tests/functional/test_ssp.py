from friendfund.tests import *

class TestSspController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='ssp', action='index'))
        # Test response...
