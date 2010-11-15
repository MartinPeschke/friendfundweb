from friendfund.tests import *

class TestFbController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='fb', action='index'))
        # Test response...
