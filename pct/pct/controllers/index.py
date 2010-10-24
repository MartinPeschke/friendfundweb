import logging
from lxml import etree
from pylons import request, response, tmpl_context as c, url, app_globals as g
from pylons.decorators import jsonify
from pylons.controllers.util import abort, redirect

from pct.lib.base import BaseController, render
from pct.model.curation import GetCurationQueue, SetCurationResultProc, CurationProduct, CurationCategory, CurationCategoryWrapper

log = logging.getLogger(__name__)

class IndexController(BaseController):
	navposition=g.globalnav[0][2]
	def index(self, region):
		c.curation_queue = g.dbm.get( GetCurationQueue, region = region, type="UPDATE")
		return render("/index.html")
	def update(self, region):
		c.curation_queue = g.dbm.get( GetCurationQueue, region = region, type="UPDATE")
		return render("/index.html")
	def insert(self, region):
		c.curation_queue = g.dbm.get( GetCurationQueue, region = region, type="INSERT")
		return render("/index.html")
	
	@jsonify
	def curate(self):
		scrp = SetCurationResultProc(region=request.params.get('region'))
		cp = CurationProduct.from_xml(etree.fromstring(request.params.get('curation_xml')))
		cp.outcome = str(request.params.get('outcome'))
		
		cats = dict([(name, CurationCategory(name=name)) for name in request.params.getall('category')])
		if cp.outcome == 'ACCEPT'  and len(cats) < 1: return {'data':{'success':False, 'error_data':'You Must add at least one category'}}
		cp.versions['NEW'].categories = CurationCategoryWrapper(map = cats)
		scrp.cp.append(cp)
		try:
			c.curation_queue = g.dbm.set( scrp )
		except Exception, e:
			return {'data':{'success':False, 'error_data':'SOME ERROR!!!! %s' % e}}
		return {'data':{'success':True}}