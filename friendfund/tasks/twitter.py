from __future__ import with_statement
import logging, urllib, urllib2, simplejson, os, celery
from operator import itemgetter
from itertools import imap
from celery.decorators import task

from friendfund.model.async.user_data import UserData
from friendfund.lib import oauth, tw_helper, helpers as h
from friendfund.lib.cache_helper import set_pages_to_cache
from friendfund.model import common
from friendfund.tasks import get_dbm, get_cm, config
from friendfund.tasks.photo_renderer import remote_profile_picture_render
from celery.log import setup_logger
log = setup_logger(loglevel=0)

CONNECTION_NAME = 'async'

def get_friend_list(method, access_token, access_token_secret, consumer, slice_size = 100):
	def package(elem):
		return (str(elem['id']),   							### ID keyed Map
							{
								'name':elem.get('name', None)				### basic display properties
								,'network_id':str(elem['id'])
								,'screen_name':elem.get('screen_name', '')
								,'profile_picture_url':elem['profile_image_url']
								,'minimal_repr': h.encode_minimal_repr(	### Pool User Attributes, unusable for display
									{
										'name':elem.get('name', None)
										,'network':'twitter'
										,'network_id':str(elem['id'])
										,'screen_name':elem.get('screen_name', '')
										,'profile_picture_url':tw_helper.get_profile_picture_url(elem['profile_image_url'])
										,'notification_method':method
									}
								)
							}
				)
	
	urls = ["https://api.twitter.com/1/statuses/followers.json", "https://api.twitter.com/1/statuses/friends.json"]
	next_cursor_str = -1
	output_buffer = []
	prevLoaded = set()
	
	for url in urls:
		while next_cursor_str != '0':
			json_data = tw_helper.fetch_url("%s?cursor=%s" % (url, next_cursor_str), "GET", access_token, access_token_secret, consumer)
			friend_data = simplejson.loads(json_data)
			data, next_cursor_str = friend_data['users'], friend_data['next_cursor_str']
			
			output_buffer.extend([package(entry) for entry in data if entry['id'] not in prevLoaded])
			prevLoaded = prevLoaded.union(imap(itemgetter('id'), data))
			if len(output_buffer)>=slice_size:
				result = output_buffer[:slice_size]
				output_buffer = output_buffer[slice_size:]
				yield result, next_cursor_str == '0' and len(output_buffer) == 0
		next_cursor_str = -1
	if len(output_buffer):
		yield output_buffer, True
	
@task
def set_friends_async(proto_key, access_token, access_token_secret):
	consumer = oauth.Consumer(config['twitterapikey'], config['twitterapisecret'])
	cache_pool = get_cm(CONNECTION_NAME)
	dataprovider = get_friend_list("TWEET", access_token, access_token_secret, consumer)
	set_pages_to_cache(log, cache_pool, proto_key, dataprovider)
	
	
@task
def remote_persist_user(user_data):
	user = UserData(**user_data)
	try:
		get_dbm(CONNECTION_NAME).set(user)
	except common.SProcException, e:
		log.error(str(e))
	
	remote_profile_picture_render.delay([(user_data['network'], user_data['network_id'], user_data['profile_picture_url'])])
	consumer = oauth.Consumer(config['twitterapikey'], config['twitterapisecret'])
	cache_pool = get_cm(CONNECTION_NAME)
	dataprovider = get_friend_list("TWEET", access_token, access_token_secret, consumer)
	set_pages_to_cache(log, cache_pool, proto_key, dataprovider)
	return 'ack'
	