from friendfund.tests import *

class TestContentController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='content', action='index'))
        # Test response...
