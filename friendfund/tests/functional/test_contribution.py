from friendfund.tests import *

class TestContributionController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='contribution', action='index'))
        # Test response...
