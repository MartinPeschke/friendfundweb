from __future__ import with_statement
import re, time, urllib2, simplejson, time

from collections import deque
from ordereddict import OrderedDict
from friendfund.lib import oauth
from celery.execute import send_task

request_token_url = 'http://api.twitter.com/oauth/request_token'
access_token_url = 'http://api.twitter.com/oauth/access_token'
authenticate_url = 'http://api.twitter.com/oauth/authenticate'

img_matcher = re.compile('^(.*)_normal\.(gif|jpg|png|jpeg)$')
default_img_matcher = re.compile("^(.*/images/default_profile_[0-9]+_)normal(\.png)$")

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
			,'oauth_timestamp': int(time.time())
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
			url_data = opener.open(request.to_url()).read()
		opener.close()
		return url_data





def get_friend_list(url, method, access_token, access_token_secret, consumer):
	next_cursor_str = -1
	data = []
	while next_cursor_str != '0':
		json_data = fetch_url("%s?cursor=%s" % (url, next_cursor_str), "GET", access_token, access_token_secret, consumer)
		friend_data = simplejson.loads(json_data)
		data.extend(friend_data['users'])
		next_cursor_str = friend_data['next_cursor_str']
		yield 	[
					(str(elem['id']), 
						{'networkname':elem.get('name', None),
						 'network_id':str(elem['id']),
						 'screenname':elem.get('screen_name', ''), 
						 'large_profile_picture_url':get_profile_picture_url(elem['profile_image_url']),
						 'profile_picture_url':elem['profile_image_url'],
						 'notification_method':method,
						 'network':'twitter'}
					)
					for elem in data if 'screen_name' in elem
				], next_cursor_str == '0'
	
def get_friends(logger, access_token, access_token_secret, consumer):
	logger.info('CACHE MISS for followers')
	data_dict = {}
	for data_set, is_final in get_friend_list("https://api.twitter.com/1/statuses/friends.json", "TWEET", access_token, access_token_secret, consumer):
		yield data_set, is_final
	for data_set, is_final in get_friend_list("https://api.twitter.com/1/statuses/followers.json", "TWEET", access_token, access_token_secret, consumer):
		yield data_set, is_final


def get_friends_async(logger, 
			cache_pool, 
			access_token, 
			access_token_secret, 
			config, 
			expiretime=30,
			offset = 0):
	consumer = oauth.Consumer(config['twitterapikey'], config['twitterapisecret'])
	proto_key = '<%s>%s' % ('friends_twitter', str(access_token))
	with cache_pool.reserve() as mc:
		try:
			is_final = False
			enum = 0
			datasets_iter = get_friends(logger, access_token, access_token_secret, consumer)
			try:
				while not is_final:
					mc.set('%s<%s>'%(proto_key, enum), INPROCESS_TOKEN, 30)
					print 'FOUND NOTHING, FETCHING', enum, is_final
					dataset, is_final = datasets_iter.next()
					obj = { 'payload':dataset, 'is_final' : is_final }
					mc.set('%s<%s>'%(proto_key, enum), obj, expiretime)
					enum += 1 
					logger.info('MEMCACHED: just set key: %s', '%s<%s>' % (proto_key, enum))
					if is_final: break
			except StopIteration:
				logger.info('DONE FETCHING, NOTHING LEFT')
		except:
			keys = ['<%s>'%i for i in range(offset, offset + 100)]
			mc.delete_multi(keys, key_prefix=proto_key)
			raise


def get_friends_from_cache(
			logger, 
			cache_pool, 
			access_token, 
			access_token_secret, 
			config, 
			expiretime=15,
			offset = 0, 
			timeout = 15):
	sleeper = 0
	consumer = oauth.Consumer(config['twitterapikey'], config['twitterapisecret'])
	proto_key = '<%s>%s' % ('friends_twitter', str(access_token))
	keys = ['<%s>' %i for i in range(offset, offset + 100)]
	
	with cache_pool.reserve() as mc:
		values = mc.get_multi(keys, key_prefix=proto_key)
		first_val = values.get(keys[0])
		print len(values), offset
		
		if offset>0 and first_val is None:
			logger.error('GET_FRIENDS_FROM_CACHE, tried getting followups, None Found', proto_key)
			return None, None, None
		else:
			if first_val is None:
				mc.set('%s%s'%(proto_key, keys[0]), INPROCESS_TOKEN, 30)
				first_val = INPROCESS_TOKEN
				send_task('friendfund.tasks.twitter.get_friends_async', args = [access_token, access_token_secret])
			
			while first_val == INPROCESS_TOKEN and sleeper < timeout:
				time.sleep(1)
				values = mc.get_multi(keys, key_prefix=proto_key)
				first_val = values.get(keys[0])
				sleeper += 1
				logger.info('trying fetching friends, sofar got something for: %s', keys[0])
			if first_val == INPROCESS_TOKEN: 
				logger.error('GET_FRIENDS_FROM_CACHE, TIMEOUT for %s with INPROCESS_TOKEN', proto_key)
				return None, None, None
		
		result = OrderedDict()
		for i, key in enumerate(keys):
			val = values.get(key)
			if val == INPROCESS_TOKEN or val is None:
				return result, False, i
			elif val['is_final']:
				result.update(val['payload'])
				return result, True, i
			else:
				result.update(val['payload'])
			logger.info('Retrieved %s TWFriends' % len(val['payload']))
		return result, False, i