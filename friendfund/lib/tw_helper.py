from __future__ import with_statement
import re, time, urllib2, simplejson, time, logging
from itertools import imap
from operator import itemgetter
from collections import deque
from ordereddict import OrderedDict
from friendfund.lib import oauth, helpers as h
from celery.execute import send_task

from pylons import request

log = logging.getLogger(__name__)

request_token_url = 'https://api.twitter.com/oauth/request_token'
access_token_url = 'https://api.twitter.com/oauth/access_token'
authenticate_url = 'https://api.twitter.com/oauth/authorize'

img_matcher = re.compile('^(.*)_normal\.(gif|jpg|png|jpeg)$')
default_img_matcher = re.compile("^(.*images/default_profile_[0-9]+_)normal(\.png)$")

INPROCESS_TOKEN = 1


def get_profile_picture_url(url):
	""" 
		Extract original profile picture from mini snapshop 
			* mini: 24x24, normal: 48x48, bigger:73x73 or without=original
		'profile_image_url': 'http://a2.twimg.com/profile_images/1121172250/ferrari1_normal.jpg'
	"""
	match = default_img_matcher.match(url)
	if match: return 'bigger'.join(match.groups())
	match = img_matcher.match(url) # re.I wont work for some reason it cuts off the "ht" from http://... ???
	return match and '.'.join(match.groups()) or url
	
	
def fetch_url(url,http_method, token, token_secret, consumer, params = None):
		oauth_base_params = {
			'oauth_version': "1.0"
			,'oauth_nonce': oauth.generate_nonce()
			,'oauth_timestamp': oauth.generate_timestamp()
		}
		if token is not None:
			token = oauth.Token(token, token_secret)
		if params:
			params.update(oauth_base_params)
		else:
			params = oauth_base_params
		
		request = oauth.Request(method=http_method,url=url,parameters=params)
		request.sign_request(oauth.SignatureMethod_HMAC_SHA1(), consumer, token)
		opener = urllib2.build_opener()
		if http_method == "POST":
			data = request.get_nonoauth_parameter_text()
			header = request.to_header()
			req = urllib2.Request(request.normalized_url, data, header)
			url_data = opener.open(req).read()
		else:
			header = request.to_header()
			req = urllib2.Request(request.to_url(), headers = header)
			url_data = opener.open(req).read()
		opener.close()
		return url_data




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
										,'profile_picture_url':get_profile_picture_url(elem['profile_image_url'])
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
			json_data = fetch_url("%s?cursor=%s" % (url, next_cursor_str), "GET", access_token, access_token_secret, consumer)
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
	
def get_friends_async(logger, 
			cache_pool, 
			access_token, 
			access_token_secret, 
			config, 
			expiretime=4200):
	consumer = oauth.Consumer(config['twitterapikey'], config['twitterapisecret'])
	proto_key = '<%s>%s' % ('friends_twitter', str(access_token))
	with cache_pool.reserve() as mc:
		logger.info('CACHE MISS for followers')
		enum = 0
		is_final = False
		datasets_iter = get_friend_list("TWEET", access_token, access_token_secret, consumer)
		try:
			while not is_final:
				mc.set('%s<%s>'%(proto_key, enum), INPROCESS_TOKEN, 30)
				dataset, is_final = datasets_iter.next()
				obj = { 'payload':dataset, 'is_final' : is_final }
				mc.set('%s<%s>'%(proto_key, enum), obj, expiretime)
				logger.info('TWMEMCACHED: just set key: %s', '%s, %s: %s<%s>' % (is_final, enum, proto_key, enum))
				enum += 1
		except StopIteration:
			log.error("ITERATION_TOO_FAR")
			keys = ['<%s>'%i for i in range(0, enum+1)]
			mc.delete_multi(keys, key_prefix=proto_key)
			raise
		except:
			keys = ['<%s>'%i for i in range(0, enum+1)]
			mc.delete_multi(keys, key_prefix=proto_key)
			raise

def get_friends_from_cache(
			logger, 
			cache_pool, 
			access_token, 
			access_token_secret, 
			config,
			offset = None, 
			timeout = 30):
	sleeper = 0
	offset = offset or 0
	consumer = oauth.Consumer(config['twitterapikey'], config['twitterapisecret'])
	proto_key = '<friends_twitter>%s'%str(access_token)
	key = '%s<%s>' % (proto_key, offset)
	with cache_pool.reserve() as mc:
		value = mc.get(key)
		if value is None:
			if offset>0:
				logger.error('GET_FRIENDS_FROM_CACHE, tried getting followups, None Found: %s', key)
			mc.set(key, INPROCESS_TOKEN, 30)
			send_task('friendfund.tasks.twitter.get_friends_async', args = [access_token, access_token_secret])
			#get_friends_async(log, cache_pool, access_token, access_token_secret, config)
		
		while value in (None,INPROCESS_TOKEN) and sleeper < timeout:
			time.sleep(0.2)
			value = mc.get(key)
			sleeper += 0.2
		
		if isinstance(value, dict) and 'payload' in value and "is_final" in value: 
			return OrderedDict(value['payload']), value['is_final'], offset+1
		else:
			keys = ['<%s>'%i for i in range(0, 30)]
			mc.delete_multi(keys, key_prefix=proto_key)
			logger.error('GET_FRIENDS_FROM_CACHE, TIMEOUT for %s with INPROCESS_TOKEN', key)
			return None, None, None