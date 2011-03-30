import logging

from pylons import request, tmpl_context as c, session as websession, app_globals as g
from pylons.decorators import jsonify
from friendfund.lib.base import BaseController, render
from friendfund.lib.tools import remove_chars
log = logging.getLogger(__name__)

class ProductQueryController(BaseController):
	def __before__(self, action, environ):
		pass
	def __after__(self, action, environ):
		pass
	@jsonify
	def search_tab_extension(self):
		c.products = []
		g.product_service.search_tab_extension(request)
		websession._sess = None
		websession.is_new = True
		return {'clearmessage':True, 'data':{
					'page_no':c.searchresult.page_no, 
					'has_more':c.searchresult.page_no < c.searchresult.pages,
					'html':remove_chars(render('/product/search_tab_extension.html').strip(), '\n\r\t')
				}
			}
