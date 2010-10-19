from __future__ import with_statement
import re, time, urllib2, simplejson, time
from friendfund.lib import oauth
from friendfund.lib.tools import robust_cacher


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
	return 	(
				(str(elem['id']), 
					{'networkname':elem.get('name', None),
					 'screenname':elem.get('screen_name', ''), 
					 'large_profile_picture_url':get_profile_picture_url(elem['profile_image_url']),
					 'profile_picture_url':elem['profile_image_url'],
					 'notification_method':method,
					 'network':'twitter'}
				)
				for elem in data if 'screen_name' in elem
			)
	
def get_friends(logger, access_token, access_token_secret, consumer):
	logger.info('CACHE MISS for followers')
	data_dict = {}
	data_dict.update(get_friend_list("https://api.twitter.com/1/statuses/friends.json", "TWEET", access_token, access_token_secret, consumer))
	data_dict.update(get_friend_list("https://api.twitter.com/1/statuses/followers.json", "TWEET", access_token, access_token_secret, consumer))
	return data_dict

def get_friends_from_cache(logger, cache_pool, access_token, access_token_secret, config, expiretime=3600):
	consumer = oauth.Consumer(config['twitterapikey'], config['twitterapisecret'])
	key = '<%s>%s' % ('friends_facebook', str(access_token))
	return robust_cacher(logger, cache_pool, key, expiretime, 30, 'friendfund.tasks.twitter.get_friends', key, consumer, access_token, access_token_secret, expiretime)