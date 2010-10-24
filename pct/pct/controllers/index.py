import logging
from lxml import etree
from pylons import request, response, session, tmpl_context as c, url, app_globals as g
from pylons.decorators import jsonify
from pylons.controllers.util import abort, redirect

from pct.lib.base import BaseController, render
from pct.model.curation import GetCurationQueue, SetCurationResultProc, CurationProduct

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
	
	@jsonify
	def curate(self):
		scrp = SetCurationResultProc(region=request.params.get('region'))
		cp = CurationProduct.from_xml(etree.fromstring(request.params.get('curation_xml')))
		cp.outcome = request.params.get('outcome')
		scrp.cp.append(cp)
		c.curation_queue = g.dbm.set( scrp )
		return redirect(request.referer)