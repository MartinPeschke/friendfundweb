from friendfund.tests import *

class TestMyfriendsController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='myfriends', action='index'))
        # Test response...
