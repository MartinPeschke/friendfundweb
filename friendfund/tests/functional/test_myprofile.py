from friendfund.tests import *

class TestUserprofileController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='myprofile', action='index'))
        # Test response...
