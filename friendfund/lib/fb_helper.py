from __future__ import with_statement
import cgi, hashlib, time, urllib2, re, simplejson, time, logging, hmac, urllib, base64, os
from StringIO import StringIO
from hashlib import sha256
from datetime import datetime, timedelta
from ordereddict import OrderedDict
from operator import itemgetter
from friendfund.lib import helpers as h

log = logging.getLogger(__name__)

picture_url_matcher = re.compile("https://graph.facebook.com/([0-9]+)/picture(\?type=large)?")
INPROCESS_TOKEN = 1
FRIENDS_QUERY = '?'.join([
			'https://graph.facebook.com/%s/friends',
			'fields=id,name,birthday,gender,email,locale&access_token=%s'
		])
MUTUAL_FRIENDS_QUERY = '?'.join([
			'https://api.facebook.com/method/friends.getMutualFriends',
			'target_uid=%s&format=json&access_token=%s'
		])
				
				
class FBNoCookiesFoundException(Exception):
	pass
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
	if not cookie: raise FBNoCookiesFoundException("No Facebook Cookies Found")
	args = dict((str(k), v[-1]) for k, v in cgi.parse_qs(cookie.strip('"')).items())
	payload = "".join("%s=%s"%(k, args[k]) for k in sorted(args.keys())
					  if k != "sig")
	sig = hashlib.md5(payload + app_secret).hexdigest()
	expires = int(args["expires"])
	if sig == args.get("sig") and (expires == 0 or time.time() < expires):
		args['id'] = args.get("uid", args.get("id"))
		if user is not None and not user.is_anon:
			nets = getattr(user, 'networks', {})
			if nets.get('facebook') and getattr(nets.get('facebook'), "network_id", None) != str(args['id']):
				raise FBLoggedInWithIncorrectUser("No Facebook Cookies Found")
		return args
	else:
		raise FBNotLoggedInException("No Facebook Cookies Found")

def get_user_from_request(request, app_id, app_secret, user = None, set_cookie = False, response = None):
	try:
		args = simplejson.loads(request.params.get('fbsession'))
	except:
		raise FBNotLoggedInException("No Facebook Request Params Found")
	if not args: raise FBNotLoggedInException("No Facebook Cookies Found")
	args = dict((str(k),v) for k,v in args.items())
	payload = "".join("%s=%s"%(k, args[k]) for k in sorted(args.keys())
					  if k not in ["sig"])
	sig = hashlib.md5(payload + app_secret).hexdigest()
	expires = int(args["expires"])
	if sig == args.get("sig") and (expires == 0 or time.time() < expires):
		if user is not None and not user.is_anon:
			nets = getattr(user, 'networks', {})
			if nets.get('facebook') and getattr(nets.get('facebook'), "network_id", None) != str(args['uid']):
				raise FBLoggedInWithIncorrectUser("No Facebook Cookies Found, %s" % args)
		if set_cookie and response and not request.cookies.get("fbs_" + app_id, None):
			response.set_cookie("fbs_" + app_id, urllib.urlencode(args), 1800)
		args['id'] = args.get("uid", args.get("id"))
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

def extract_user_data(request, app_globals, tmpl_context, response):
	try:
		fb_data = get_user_from_cookie(request.cookies, app_globals.FbApiKey, app_globals.FbApiSecret.__call__(), tmpl_context.user)
	except FBNoCookiesFoundException, e: 
		log.warning("COULDNT_FIND_FB_COOKIES_%s(%s)", e, request.headers.get("User-Agent"))
		fb_data = get_user_from_request(request, app_globals.FbApiKey, app_globals.FbApiSecret.__call__(), tmpl_context.user, True, response)
	user_data = dict([(k,v) for k,v in request.params.iteritems()])
	user_data.update(fb_data)
	user_data['network'] = 'facebook'
	user_data['network_id'] = user_data.pop('id')
	user_data['profile_picture_url'] = get_large_pic_url(user_data['network_id'])
	user_data['access_token_secret'] = user_data.pop('secret')
	return user_data

		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
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


def package(elem):
	repr = {### Pool User Attributes, unusable for display
				'notification_method':'CREATE_EVENT'
				,'network':'facebook'
				,'network_id':elem["id"]
				,'email':elem.get('email')
				,'profile_picture_url':get_large_pic_url(elem['id'])
				,'locale':elem.get('locale', "").lower()
		}
	
	dob = elem.get('birthday')
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
			repr['dob'] = datetime(year, 1,1) + doy
			repr['dob_difference'] = (repr['dob'] - datetime.today()).days
			if repr['dob_difference'] < 2:
				repr['dob'] = datetime(year + 1, 1,1) + doy
				repr['dob_difference'] = (repr['dob'] - datetime.today()).days
	return (elem['id'], {
				'name':elem['name']
				,'network_id':elem["id"]
				,'profile_picture_url':get_pic_url(elem['id'])
				,'minimal_repr': h.encode_minimal_repr(repr)
			})
			


def set_friend_to_cache(mc, proto_key, logger, id, access_token, expiretime, slice_size = 100):
	query = FRIENDS_QUERY % (id, access_token)
	try:
		data = simplejson.loads(urllib2.urlopen(query).read())['data']
	except urllib2.HTTPError, e:
		logger.error("Error opening URL %s (%s):" % (query, e.fp.read()))
		ud = {}
	else:
		user_data = [ package(elem) for elem in sorted(data, key=itemgetter("name")) if 'name' in elem ]
		logger.info('CACHE MISS %s, %s', query, len(user_data))
		total = len(user_data)
		pagenumber = total/slice_size + bool(total%slice_size)
		pages = [("<%s>" % (i), 
						{
							"payload":user_data[i*slice_size:(i+1)*slice_size]
							,"is_final": i+1 == pagenumber
						}) for i in range(0, pagenumber)]
		mc.set_multi(dict(pages), time = expiretime,  key_prefix = proto_key)
		return pages

def get_friends_from_cache(
				logger, 
				cache_pool, 
				id, 
				access_token, 
				expiretime=4200,
				friend_id = None,
				offset = None, 
				timeout = 30
			):
	sleeper = 0
	offset = offset or 0
	
	proto_key = '<friends_facebook>%s' % str(id)
	key = '%s<%s>' % (proto_key, offset)
	with cache_pool.reserve() as mc:
		if friend_id is None:
			value = mc.get(key)
		else:
			mutual_key = '%s//MUTUALWITH<%s>' % (proto_key, friend_id)
			values = mc.get_multi([key, mutual_key])
			value = values.get(key)
			mutual_with = values.get(mutual_key)
			
		if value is None:
			if offset>0:
				logger.error('FACEBOOK, GET_FRIENDS_FROM_CACHE, tried getting followups, None Found: %s', key)
			mc.set(key, INPROCESS_TOKEN, 30)
			values = set_friend_to_cache(mc, proto_key, logger, id, access_token, expiretime)
			if not len(values):
				logger.error('FACEBOOK, NOFRIENDSFOUND, FOR REALZ, TIMEOUT for %s with INPROCESS_TOKEN', key)
				return None, None, None
			value = values[0][1]
		while value in (None,INPROCESS_TOKEN) and sleeper < timeout:
			time.sleep(0.2)
			value = mc.get(key)
			sleeper += 0.2
		
		if not (isinstance(value, dict) and 'payload' in value and "is_final" in value): 
			logger.error('FACEBOOK, WAITEDLONGANDSTILLNOTHINGFOUND, TIMEOUT for %s, without necessary values, %s', key, value)
			return None, None, None
		
		payload = OrderedDict(value['payload'])
		
		if friend_id is not None:
			if mutual_with is None:
				mc.set(mutual_key, INPROCESS_TOKEN, 30)
				mutual_friends = get_mutual_friends(logger, friend_id, access_token)
				mc.set(mutual_key, mutual_friends, time=expiretime)
			while mutual_with in (None,INPROCESS_TOKEN) and sleeper < timeout:  ##not resetting sleep, dont wanna wait double time
				time.sleep(0.2)
				mutual_with = mc.get(key)
				sleeper += 0.2
			
			for id in mutual_with:
				if str(id) in payload:
					payload[str(id)]['mutual_with'] = str(friend_id)
	logger.info('FACEBOOK, Retrieved %s FBFriends' % len(payload))
	return payload, value['is_final'], offset+1