import logging, formencode, datetime

from pylons import request, response, session as websession, tmpl_context as c, url, config, app_globals as g, cache
from pylons.decorators import jsonify
from pylons.controllers.util import abort, redirect
from cgi import FieldStorage
from formencode.variabledecode import variable_decode

from friendfund.lib import fb_helper, tw_helper, helpers as h
from friendfund.lib.auth.decorators import post_only
from friendfund.lib.base import BaseController, render, _
from friendfund.lib.helpers import get_upload_pic_name
from friendfund.lib.i18n import FriendFundFormEncodeState
from friendfund.model.forms import user, common
from friendfund.model.pool import PoolUser, Pool, InsufficientParamsException, Occasion, OccasionSearch
from friendfund.model.authuser import UserNotLoggedInWithMethod
from friendfund.tasks import photo_renderer, fb as fbservice, twitter as twservice

log = logging.getLogger(__name__)
ulpath = config['pylons.paths']['uploads']

class ReceiverController(BaseController):
	
	@jsonify
	def panel(self):
		c.method = c.user.get_current_network() or 'facebook'
		return {'data':{'html':render('/receiver/panel.html').strip(), 'method':c.method}}
	
	@jsonify
	def unset(self):
		c.pool = websession.get('pool') or Pool()
		del pool.receiver
		websession['pool'] = c.pool
		return {'clearmessage':True, 'html':render('/receiver/button.html').strip()}
	
	
	def setbday(self):
		receiver = formencode.variabledecode.variable_decode(request.params)
		dob = receiver.get('dob', '')
		if dob:
			dv = common.DateValidator()
			try:
				dob = dv.to_python(dob.split()[0])
			except formencode.validators.Invalid, error:
				log.warning("Set Birthday failed, unrecognized format: %s", dob)
			else:
				olist = g.dbm.get(OccasionSearch, date = h.format_date_internal(datetime.date.today()), country = websession['region']).occasions
				bday = filter(lambda x:x.key == 'EVENT_BIRTHDAY', olist)
				if dob and len(bday):
					bday = bday[0]
					c.pool = websession.get('pool') or Pool()
					c.pool.occasion = Occasion(key="EVENT_BIRTHDAY", date=dob, picture_url = '/static/imgs/%s'%bday.picture_url)
					websession['pool'] = c.pool
		return self.set()
	
	@jsonify
	def set(self):
		receiver = formencode.variabledecode.variable_decode(request.params)
		try:
			receiver = PoolUser.fromMap(receiver)
		except InsufficientParamsException, e:
			log.warning(str(e))
			return self.ajax_messages(_("POOL_CREATE_No Known ReceiverFound"))
		receiver.is_receiver = True
		c.pool = websession.get('pool') or Pool()
		receiver.profile_picture_url = receiver.large_profile_picture_url
		c.pool.participants = [receiver]
		c.pool.receiver = receiver
		websession['pool'] = c.pool
		return {'clearmessage':True, 'html':render('/receiver/button.html').strip()}