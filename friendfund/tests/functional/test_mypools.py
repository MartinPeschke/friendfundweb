from friendfund.tests import *

class TestMypoolsController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='mypools', action='index'))
        # Test response...
