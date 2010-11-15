from friendfund.tests import *

class TestBadgesController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='mybadges', action='index'))
        # Test response...
