from friendfund.tests import *

class TestReceiverController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='receiver', action='index'))
        # Test response...
