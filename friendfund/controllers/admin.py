import logging

from pylons import request, response, session, tmpl_context as c, url, config, app_globals as g
from pylons.controllers.util import abort, redirect


from friendfund.lib.base import BaseController, render
from friendfund.model.db_access import SProcException, SProcWarningMessage
from friendfund.model.admin.pool_queue import GetClosedPoolProc, SetPoolCompleteProc
from friendfund.tasks.ecard_renderer import remote_ecard_render

log = logging.getLogger(__name__)

class AdminController(BaseController):

	def __before__(self, action, environ):
		super(AdminController, self).__before__(action, environ)
		if config['app_conf']['serve_admin'] != 'true':
			return abort(401, "Action Not Allowed")

	def index(self):
		c.pools = g.dbadmin.get(GetClosedPoolProc).pools
		return self.render("/admin/index.html")

	def complete(self, pool_url):
		try:
			#c.pools = g.dbadmin.set(SetPoolCompleteProc(p_url = pool_url))
			pass
		except SProcException, e:
			c.messages.append("ERROR Occured with %s (%s)" % (pool_url, str(e)))
		else:
			c.messages.append("Pool Completed: %s" % pool_url)
			remote_ecard_render.delay(pool_url)
		return redirect('/admin')
