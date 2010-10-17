import logging, simplejson, time, cgi, urllib2
from friendfund.lib import oauth

from pylons import request, response, session as websession, tmpl_context as c, url, app_globals as g
from pylons.controllers.util import abort, redirect
from pylons.decorators import jsonify

from friendfund.lib.base import BaseController, render, _
from friendfund.lib import tw_helper

from friendfund.model.authuser import User, ANONUSER, OtherUserData
from friendfund.model.recent_activity import RecentActivityStream
from friendfund.tasks.twitter import remote_persist_user
from friendfund.model.common import SProcWarningMessage
log = logging.getLogger(__name__)

consumer = oauth.Consumer(g.TwitterApiKey, g.TwitterApiSecret)
client = oauth.Client(consumer)


class TwitterController(BaseController):
	UNKNOWN_TWITTER_ERROR = _("TWITTER_An Error occured during Twitter authentication, please try again later.")
	def index(self):
		c.ra = RecentActivityStream(entries = [])
		return self.render('/index.html')
	
	def login(self):
		websession['twitter_redirect_url'] = request.params.get('furl', request.referer)
		
		# Step 1. Get a request token from Twitter.
		resp, content = client.request(tw_helper.request_token_url, "GET")
		if resp['status'] != '200':
			log.warning("Twitter replied with Status != 200: %s", content)
			raise Exception(_("TWITTER_Invalid response from Twitter."))
		
		# Step 2. Store the request token in a session for later use.
		websession['request_token'] = dict(cgi.parse_qsl(content))
		
		# Step 3. Redirect the user to the authentication URL.
		oauth_token = websession.get('request_token', {}).get('oauth_token', None)
		if not oauth_token:
			log.warning("Twitter Oauth_Token not returned by Twitter for Get_Access_token: %s", tw_helper.request_token_url)
			c.messages.append(self.UNKNOWN_TWITTER_ERROR)
			return redirect(websession.pop('twitter_redirect_url', '/'))
		url = "%s?oauth_token=%s" % (tw_helper.authenticate_url,websession['request_token']['oauth_token'])
		return redirect(url)
	
	def authorize(self):
		furl = websession.pop('twitter_redirect_url', '/')
		
		# Step 1. Use the request token in the session to build a new client.
		oauth_token = websession.get('request_token', {}).get('oauth_token', None)
		oauth_token_secret = websession.get('request_token', {}).get('oauth_token_secret', None)
		if not oauth_token:
			log.warning("No Oauth_Token found in session, why?")
			c.messages.append(self.UNKNOWN_TWITTER_ERROR)
			return redirect(furl)
		token = oauth.Token(oauth_token, oauth_token_secret)
		client = oauth.Client(consumer, token)

		# Step 2. Request the authorized access token from Twitter.
		resp, content = client.request(tw_helper.access_token_url, "GET")
		if resp['status'] != '200':
			log.warning("Twitter replied with Status != 200: %s at %s", content, tw_helper.access_token_url)
			c.messages.append(self.UNKNOWN_TWITTER_ERROR)
			return redirect(furl)
		token_data = dict(cgi.parse_qsl(content))
		
		# Step 3. User Details
		user_data = simplejson.loads(
						tw_helper.fetch_url("https://api.twitter.com/1/" + "users/show" + "/%s.json" % token_data['user_id'], 
										"GET", 
										token_data['oauth_token'],  
										token_data['oauth_token_secret'],
										consumer
									))
		user_data['network'] = 'twitter'
		user_data['network_id'] = user_data.pop('id')
		user_data['access_token'] = token_data['oauth_token']
		user_data['access_token_secret'] = token_data['oauth_token_secret']
		user_data['profile_picture_url'] = tw_helper.get_profile_picture_url(user_data.pop('profile_image_url'))
		user_data['locale'] = user_data['lang']
		user_data['link'] = user_data['url']
		#Save and Persist, render profile
		success, msg = g.user_service.login_or_consolidate(user_data, remote_persist_user)
		if not success:
			c.messages.append(msg)
		return redirect(furl)