from friendfund.tests import *

class TestInvitesController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='invites', action='index'))
        # Test response...
