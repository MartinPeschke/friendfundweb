from friendfund.tests import *

class TestTwitterController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='twitter', action='index'))
        # Test response...
