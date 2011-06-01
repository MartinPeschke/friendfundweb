from __future__ import with_statement
import logging, formencode, uuid, md5, os
from cgi import FieldStorage

from pylons import request, response, session as websession, tmpl_context as c, config, app_globals, url
from pylons.controllers.util import abort, redirect
from pylons.decorators import jsonify

from friendfund.lib.i18n import FriendFundFormEncodeState
from friendfund.lib.auth.decorators import logged_in
from friendfund.lib.base import BaseController, render, _
from friendfund.lib import fb_helper, helpers as h

from friendfund.model.forms.user import LoginForm
from friendfund.model.pool import FeaturedPool
from friendfund.model.common import SProcWarningMessage
from friendfund.model.authuser import User, SetUserEmailProc, ANONUSER
from friendfund.model.product import Product
from friendfund.model.sitemap import SiteMap
from friendfund.tasks.cache_refresher import FEATURED_POOLS_CACHEKEY, HOMEPAGE_STATS_CACHEKEY

log = logging.getLogger(__name__)
ulpath = config['pylons.paths']['uploads']

class IndexController(BaseController):
	ra_total_page_size = 50
	ra_page_size = 5
	
	def _get_featured_pools(self):
		with app_globals.cache_pool.reserve() as mc:
			featured_pools = mc.get(FEATURED_POOLS_CACHEKEY)
		if featured_pools is None:
			log.warning("NO_FEATURED_POOLS_FOUND_IN_CACHE_REVERTING_TO_LOCAL_GET")
			featured_pools = []
			for p in app_globals.featured_pools:
				 featured_pools.append(app_globals.dbm.get(FeaturedPool, p_url = p.p_url))
		return featured_pools
	
	def index(self):
		if request.merchant.home_page:
			return redirect(request.merchant.home_page, code=301)
		if 'pool' in websession:
			c.pool = websession['pool']
		c.get_featured_pools = self._get_featured_pools
		
		with app_globals.cache_pool.reserve() as mc:
			c.homepage_stats = mc.get(HOMEPAGE_STATS_CACHEKEY)
		if not c.homepage_stats:
			log.error("NO_HOMEPAGE_STATS_FOUND_IN_CACHE_REVERTING_TO_LOCAL_GET")
			c.homepage_stats = app_globals.homepage_stats
		return self.render('/index.html')
	
	def sitemap(self):
		c.pool_urls = app_globals.dbm.get(SiteMap).entries
		return render('/sitemap.xml')
	
	def close(self):
		c.reload = False
		return render('/closepopup.html')
	
	@jsonify
	def jsonlo(self):
		c.user = ANONUSER
		c.settings = {}
		c.messages = []
		if 'invitees' in websession:
			del websession['invitees']
		if 'pool' in websession:
			del websession['pool']
		return {"success":True}
	
	def logout(self):
		if not request.referer or request.referer == c.furl:
			c.furl = "/"
		c.user = ANONUSER
		c.settings = {}
		c.messages = []
		if 'invitees' in websession:
			del websession['invitees']
		if 'pool' in websession:
			del websession['pool']
		return redirect(c.furl)
	
	def signup(self):
		if not c.furl or request.referer == c.furl:
			c.furl = "/"
		c.signup_values = {}
		c.signup_errors = {}
		if not c.user.is_anon:
			return redirect(c.furl)
		if request.method != 'POST':
			return self.render('/myprofile/login_screen.html')
		signup = formencode.variabledecode.variable_decode(request.params).get('signup', None)
		try:
			c.user = app_globals.user_service.signup_email_user(signup)
			return redirect(url('home'))
		except formencode.validators.Invalid, error:
			c.signup_values = error.value
			c.signup_errors = error.error_dict or {}
			return self.render('/myprofile/login_screen.html')
		except SProcWarningMessage, e:
			c.signup_values = signup
			c.signup_errors = {'email':_("USER_SIGNUP_EMAIL_ALREADY_EXISTS")}
			c.messages.append(_(u"USER_SIGNUP_If this is you, please try logging in with your email address and password or %(link_open)srequest a password change!%(link_close)s") \
							% {'link_open':"<a onclick=\"window.__auth__.forgotPassword('%s')\">" %url(controller='myprofile', action='rppopup'), 'link_close':'</a>'})
			return self.render('/myprofile/login_screen.html')