from friendfund.tests import *

class TestInvitesController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='invite', action='index'))
        # Test response...
