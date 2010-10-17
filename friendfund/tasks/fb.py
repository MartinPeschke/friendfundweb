import urllib, urllib2, simplejson, datetime
from celery.decorators import task
from collections import deque

from friendfund.lib import fb_helper
from friendfund.model import db_access
from friendfund.model.async.user_data import UserData, UserBirthday, UserList
from friendfund.model.async.fb_user_permissions import FBUserPermissions
from friendfund.tasks import get_dbm, get_cm
from friendfund.tasks.photo_renderer import remote_profile_picture_render
from celery.log import setup_logger
log = setup_logger(loglevel=0)

CONNECTION_NAME = 'jobs'

@task
def remote_persist_user(user_data):
	dbm = get_dbm(CONNECTION_NAME)
	user = UserData(**user_data)
	try:
		dbm.set(user)
	except db_access.SProcException, e:
		log.error(str(e))
	remote_profile_picture_render.delay([(user_data['network'], user_data['network_id'], user_data['profile_picture_url'])])
	friends = fb_helper.get_friends_from_cache(log, get_cm(CONNECTION_NAME), user_data['network_id'], user_data['access_token'])
	
	
	query = "SELECT uid, name, pic_big, birthday_date, sex, email FROM user WHERE uid in (%s)" % ','.join(friends.keys())
	query = 'https://api.facebook.com/method/fql.query?query=%s&format=json&access_token=%s'%\
			(urllib.quote(query), user_data['access_token'])
	data = simplejson.loads(urllib2.urlopen(query).read())
	users = deque()
	for d in data:
		d['network'] = 'facebook'
		if 'birthday_date' in d and d['birthday_date'] is not None:
			try:
				d['birthday_date'] = datetime.datetime.strptime(d['birthday_date'], "%m/%d/%Y")
			except ValueError, e:
				try:
					d['birthday_date'] = datetime.datetime.strptime(d['birthday_date'], "%m/%d")
				except ValueError, e:
					log.error( 'Facebook User Birthday: %s, %s', e , d['birthday_date'])
					del d['birthday_date']
		users.append(UserBirthday(**d))
	user = UserList(users = users, u_id = user_data['u_id'])
	try:
		dbm.set(user)
	except db_access.SProcException, e:
		log.error(str(e))
	return 'ack'

@task
def remote_fb_perm(network, network_id, **args):
	dbm = get_dbm(CONNECTION_NAME)
	args['network'] = network
	args['network_id'] = network_id
	perms = FBUserPermissions(**args)
	try:
		dbm.set(perms)
	except db_access.SProcException, e:
		log.error(str(e))
	return 'ack'


def get_email_from_permissions(fb_data):
	query = urllib.urlencode({
			'access_token':fb_data['access_token']
		})
	resp = urllib2.urlopen('https://graph.facebook.com/me?%s' % query)
	user_data = simplejson.loads(resp.read())
	return user_data['email']