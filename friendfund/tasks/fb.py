import urllib, urllib2, simplejson, datetime, os
from celery.decorators import task
from celery.log import setup_logger
from collections import deque
from poster.streaminghttp import register_openers
from poster.encode import multipart_encode

from friendfund.lib import fb_helper
from friendfund.model import db_access
from friendfund.model.async.user_data import UserData, UserBirthday, UserBirthdayList
from friendfund.model.async.fb_user_permissions import FBUserPermissions
from friendfund.tasks import get_dbm, get_cm
from friendfund.tasks.photo_renderer import remote_profile_picture_render

log = setup_logger(loglevel=0)
CONNECTION_NAME = 'async'


@task
def upload_picture_to_event(event_id, access_token, picture_url, trial_count = 0):
	if trial_count>2:
		log.error("TOO_MANY_ERRORS_FOR_EVENTS_MODIFY: gave up after %s", trial_count)
		return '[ack]'
	register_openers()
	try:
		fname, headers = urllib.urlretrieve(picture_url)
	except Exception, e:
		log.error(e)
		upload_picture_to_event(event_id, access_token, picture_url, trial_count = trial_count + 1)
	try:
		datagen, headers = multipart_encode({"eid":event_id, "access_token":access_token, "event_info":"{}", "[no name]":open(fname, "rb"), "format":"json"})
		req = urllib2.Request('https://api.facebook.com/method/events.edit', datagen, headers)
		try: 
			log.info("FACEBOOK_EVENT_PICTURE_UPLOAD_RETURNED %s", urllib2.urlopen(req).read())
		except Exception, e:
			log.error(e.fp.read())
			upload_picture_to_event(event_id, access_token, picture_url, trial_count = trial_count + 1)
	finally:
		if fname: os.unlink(fname)




@task
def remote_persist_user(user_data):
	dbm = get_dbm(CONNECTION_NAME)
	user = UserData(**user_data)
	try:
		dbm.set(user)
	except db_access.SProcException, e:
		log.error(str(e))
	remote_profile_picture_render.delay(
				[(user_data['network'], 
				user_data['network_id'], 
				user_data['profile_picture_url'])])
	
	friends = fb_helper.get_friends_from_cache(log, 
				get_cm(CONNECTION_NAME), 
				user_data['network_id'], 
				user_data['access_token']
				)
	
	user_list = (UserBirthday(**data) for uid,data in friends.iteritems())
	users = UserBirthdayList(users = user_list, u_id = user_data['u_id'])
	try:
		dbm.set(users)
	except db_access.SProcException, e:
		log.error(str(e))
	return 'ack'

def get_email_from_permissions(fb_data):
	query = urllib.urlencode({'access_token':fb_data['access_token']})
	resp = urllib2.urlopen('https://graph.facebook.com/me?%s' % query)
	user_data = simplejson.loads(resp.read())
	return user_data['email']



