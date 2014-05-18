import logging
from friendfund.lib.base import BaseController
from pylons.templating import render_mako as render

log = logging.getLogger(__name__)

class FacebookStaticController(BaseController):
    def index(self):
        return render("/facebook_static/like_page.html")