from friendfund.tests import *

class TestOccasionController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='occasion', action='index'))
        # Test response...
