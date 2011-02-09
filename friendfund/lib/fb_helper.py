from __future__ import with_statement
import cgi, hashlib, time, urllib2, re, simplejson, time, logging, hmac, urllib, base64, os
from StringIO import StringIO
from hashlib import sha256
from datetime import datetime, timedelta
from ordereddict import OrderedDict
from friendfund.lib import helpers as h

log = logging.getLogger(__name__)

picture_url_matcher = re.compile("https://graph.facebook.com/([0-9]+)/picture(\?type=large)?")
INPROCESS_TOKEN = 1
FRIENDS_QUERY = '?'.join([
			'https://graph.facebook.com/%s/friends',
			'fields=id,name,birthday,gender,email&access_token=%s'
		])
MUTUAL_FRIENDS_QUERY = '?'.join([
			'https://api.facebook.com/method/friends.getMutualFriends',
			'target_uid=%s&format=json&access_token=%s'
		])
				
				
class FBNotLoggedInException(Exception):
	pass
class FBIncorrectlySignedRequest(Exception):
	pass
class FBLoggedInWithIncorrectUser(Exception):
	pass

def get_user_from_cookie(cookies, app_id, app_secret, user = None):
	"""Parses the cookie set by the official Facebook JavaScript SDK.
	cookies should be a dictionary-like object mapping cookie names to
	cookie values.
	If the user is logged in via Facebook, we return a dictionary with the
	keys "uid" and "access_token". The former is the user's Facebook ID,
	and the latter can be used to make authenticated requests to the Graph API.
	If the user is not logged in, we return None.
	Download the official Facebook JavaScript SDK at
	http://github.com/facebook/connect-js/. Read more about Facebook
	authentication at http://developers.facebook.com/docs/authentication/.
	"""
	cookie = cookies.get("fbs_" + app_id, "")
	if not cookie: raise FBNotLoggedInException("No Facebook Cookies Found")
	args = dict((str(k), v[-1]) for k, v in cgi.parse_qs(cookie.strip('"')).items())
	payload = "".join(k + "=" + args[k] for k in sorted(args.keys())
					  if k != "sig")
	sig = hashlib.md5(payload + app_secret).hexdigest()
	expires = int(args["expires"])
	if sig == args.get("sig") and (expires == 0 or time.time() < expires):
		args['id'] = args.get("uid", args.get("id"))
		if user is not None and not user.is_anon:
			nets = getattr(user, 'networks', {})
			if "facebook" in nets and getattr(nets.get('facebook'), "network_id", None) != str(args['id']):
				log.warning("FBLoggedInWithIncorrectUser, %s" % args)
				raise FBLoggedInWithIncorrectUser("No Facebook Cookies Found")
		return args
	else:
		raise FBNotLoggedInException("No Facebook Cookies Found")

def get_user_from_signed_request(params, app_secret):
	request = params.get('signed_request')
	if not request: raise FBIncorrectlySignedRequest(params)
	sig, payload = request.split('.',1)
	data = simplejson.loads(base64.urlsafe_b64decode(str(payload)+'=='))
	if (data.get('algorithm','').upper() != 'HMAC-SHA256'):
		raise FBIncorrectlySignedRequest("Unkown Hashing Algo from Facebook %s" % payload)
	hashed = hmac.new(app_secret, digestmod=sha256)
	hashed.update(payload)
	if not base64.urlsafe_b64encode(hashed.digest())[:-1] == sig:
		raise FBIncorrectlySignedRequest("Unkown Hashing Algo from Facebook %s" % payload)
	else:
		return data["user_id"]

def get_pic_url(network_id):
	return "https://graph.facebook.com/%s/picture" % network_id
def get_large_pic_url(network_id):
	return '%s?%s' % (get_pic_url(network_id), 'type=large')

def guess_large_pic_url(picture_url):
	matcher = picture_url_matcher.search(picture_url)
	if matcher and len(filter(None, matcher.groups())) == 1:
		return '%s?type=large' % picture_url
	else:
		return picture_url

def get_mutual_friends(logger, target_id, access_token):
	if target_id is None: return []
	query = MUTUAL_FRIENDS_QUERY % (target_id, access_token)
	try:
		data = simplejson.loads(urllib2.urlopen(query).read())
	except urllib2.HTTPError, e:
		logger.error("Error getting mutual friends URL %s (%s):" % (query, e.fp.read()))
		return []
	else:
		return data


def translate_friend_entry(u_id, friend_data):
	result = {
			'name':friend_data['name'], 
			'network_id':u_id,
			'large_profile_picture_url':get_large_pic_url(friend_data['id']),
			'profile_picture_url':get_pic_url(friend_data['id']),
			'notification_method':'CREATE_EVENT',
			# 'notification_method':'STREAM_PUBLISH',
			'network':'facebook',
			'email':friend_data.get('email'),
			'is_selector':False
		}
	
	dob = friend_data.get('birthday')
	if dob:
		try:
			dob = datetime.strptime(dob, "%m/%d/%Y")
		except ValueError, e:
			try:
				dob = datetime.strptime(dob, "%m/%d")
			except ValueError, e:
				log.error( 'Facebook User Birthday: %s, %s', e , dob)
				dob = None
		if dob:
			year = datetime.today().year
			doy = dob-datetime(dob.year,1,1)
			result['dob'] = datetime(year, 1,1) + doy
			result['dob_difference'] = (result['dob'] - datetime.today()).days
			if result['dob_difference'] < 2:
				result['dob'] = datetime(year + 1, 1,1) + doy
				result['dob_difference'] = (result['dob'] - datetime.today()).days
	return (u_id, result)


def get_friends(logger, id, access_token):
	query = FRIENDS_QUERY %\
			(id, access_token)
	try:
		data = simplejson.loads(urllib2.urlopen(query).read())['data']
	except urllib2.HTTPError, e:
		logger.error("Error opening URL %s (%s):" % (query, e.fp.read()))
		ud = {}
	else:
		user_data = [
					translate_friend_entry(str(elem['id']), elem)
					for elem in data if 'name' in elem
				]
		ud = OrderedDict()
		for k,user in sorted(user_data, key=lambda x: x[1].get("dob_difference", 999)):
			ud[k] = user
	logger.info('CACHE MISS %s, %s', query, len(ud))
	return ud

def get_friends_from_cache(
				logger, 
				cache_pool, 
				id, 
				access_token, 
				expiretime=4200,
				friend_id = None
			):
	key = '<%s>%s' % ('friends_facebook', str(id))
	with cache_pool.reserve() as mc:
		obj = mc.get(key)
		if obj is None:
			mc.set(key, INPROCESS_TOKEN, 30)
			try:
				obj = get_friends(logger, id, access_token)
				mc.set(key, obj, expiretime)
			except:
				mc.delete(key)
				raise
		elif obj == INPROCESS_TOKEN:
			while obj == INPROCESS_TOKEN:
				time.sleep(1)
				obj = mc.get(key)
	if obj is not None and friend_id is not None:
		mutual_friends = get_mutual_friends(logger, friend_id, access_token)
		for id in mutual_friends:
			if str(id) in obj:
				obj[str(id)]['mutual_with'] = str(friend_id)
	logger.info('Retrieved %s FBFriends' % len(obj))
	return obj