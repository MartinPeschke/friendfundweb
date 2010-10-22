import logging

from pylons import request, response, session, tmpl_context as c, url, app_globals as g
from pylons.controllers.util import abort, redirect

from pct.lib.base import BaseController, render
from pct.model.curation import GetCurationQueue

log = logging.getLogger(__name__)

class IndexController(BaseController):
	navposition=g.globalnav[0][2]
	def index(self):
		c.curation_queue = g.dbm.get( GetCurationQueue, region = 'de', type="UPDATE")
		return render("/index.html")
	def update(self):
		c.curation_queue = g.dbm.get( GetCurationQueue, region = 'de', type="UPDATE")
		return render("/index.html")
	def insert(self):
		c.curation_queue = g.dbm.get( GetCurationQueue, region = 'de', type="INSERT")
		return render("/index.html")
