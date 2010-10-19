from __future__ import with_statement
import logging, urllib, urllib2, simplejson, os, celery
from friendfund.lib import oauth

from celery.decorators import task

from friendfund.model.async.user_data import UserData
from friendfund.lib import tw_helper
from friendfund.model import common
from friendfund.tasks import get_dbm, get_cm, config
from friendfund.tasks.photo_renderer import remote_profile_picture_render
from celery.log import setup_logger
log = setup_logger(loglevel=0)

CONNECTION_NAME = 'jobs'


@task
def remote_persist_user(user_data):
	user = UserData(**user_data)
	try:
		get_dbm(CONNECTION_NAME).set(user)
	except common.SProcException, e:
		log.error(str(e))
	remote_profile_picture_render.delay([(user_data['network'], user_data['network_id'], user_data['profile_picture_url'])])
	tw_helper.get_friends_from_cache(log, get_cm(CONNECTION_NAME), user_data['access_token'], user_data['access_token_secret'], config)
	return 'ack'

@task
def get_friends(key, consumer, access_token, access_token_secret, expiretime=3600):
	cache_pool = get_cm(CONNECTION_NAME)
	with cache_pool.reserve() as mc:
		obj = tw_helper.get_friends(log, access_token, access_token_secret, consumer)
		mc.set(key, obj, expiretime)