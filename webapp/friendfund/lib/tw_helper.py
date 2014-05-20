from __future__ import with_statement
import re
import urllib2
import time
import logging

from collections import OrderedDict
from friendfund.lib import oauth
from celery.execute import send_task


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
    else:
        header = request.to_header()
        req = urllib2.Request(request.to_url(), headers = header)
    url_data = opener.open(req).read()
    opener.close()
    return url_data


def get_friends_from_cache(
        logger,
        cache_pool,
        access_token,
        access_token_secret, user_id, screen_name,
        config,
        offset = None,
        timeout = 30):
    sleeper = 0
    offset = offset or 0
    proto_key = '<friends_twitter>%s'%str(access_token)
    key = '%s<%s>' % (proto_key, offset)
    with cache_pool.reserve() as mc:
        value = mc.get(key)
        if value is None:
            if offset>0:
                logger.error('GET_FRIENDS_FROM_CACHE, tried getting followups, None Found: %s', key)
            mc.set(key, INPROCESS_TOKEN, 30)
            send_task('friendfund.tasks.celerytasks.twitter.set_friends_async', args = [proto_key, access_token, access_token_secret, user_id, screen_name])

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