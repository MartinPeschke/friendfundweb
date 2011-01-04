from friendfund.tests import *

class TestCustomizerController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='customizer', action='index'))
        # Test response...
