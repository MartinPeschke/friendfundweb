import logging, simplejson, cgi, urllib2
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
# consumer = oauth.Consumer("GDdmIQH6jhtmLUypg82g", "MCD8BKwGdgPHvAuvgvz4EQpqDAtx89grbuNMRd7Eh98")

class TwitterController(BaseController):
	UNKNOWN_TWITTER_ERROR = _("TWITTER_An Error occured during Twitter authentication, please try again later.")
	TWITTER_TIMEOUT_ERROR = _("TWITTER_Twitter seems to be overloaded again, please try again at a later time.")
	ERROR = """<html><head><title>Twitter Connect Error</title></head><body style="margin:0px">
				<div style="position:absolute;top:50px;left:200px;font-size:20px;font-family:Arial,MS Trebuchet,sans-serif;">%s</div>
				<img style="margin:0px" src="/static/imgs/error_page_twitter.png"/></body></html>""" % _("Twitter may be over capacity.<br/>Please try again later.")
	def index(self):
		c.ra = RecentActivityStream(entries = [])
		return self.render('/index.html')
	
	def login(self):
		furl = request.params.get('furl')
		# Step 1. Get a request token from Twitter.
		try:
			content = tw_helper.fetch_url(tw_helper.request_token_url,"POST", None, None, consumer, 
					params = {'oauth_callback':'%s/twitter/authorize' % (request.qualified_host)})
		except (urllib2.HTTPError, urllib2.URLError), e:
			log.error("COULDNOT GET TOKEN FROM %s, %s", tw_helper.request_token_url, e)
			return self.ERROR
		else:
			log.info("RECEIVED_TWITTER_INFO %s", content)
		websession['request_token'] = dict(cgi.parse_qsl(content))
		
		# Step 3. Redirect the user to the authentication URL.
		oauth_token = websession.get('request_token', {}).get('oauth_token', None)
		if not oauth_token:
			log.warning("Twitter Oauth_Token not returned by Twitter for Get_Access_token: %s", tw_helper.request_token_url)
			c.messages.append(self.UNKNOWN_TWITTER_ERROR)
			c.reload = False
			c.refresh_login = True
			return render('/closepopup.html')
		url = "%s?oauth_token=%s" % (tw_helper.authenticate_url,websession['request_token']['oauth_token'])
		return redirect(url)
	
	def authorize(self):
		oauth_token = websession.get('request_token', {}).get('oauth_token', None)
		oauth_token_secret = websession.get('request_token', {}).get('oauth_token_secret', None)
		oauth_verifier = request.params.get('oauth_verifier', None)
		if not oauth_token:
			log.warning("No Oauth_Token found in session, why?")
			c.messages.append(self.UNKNOWN_TWITTER_ERROR)
			c.reload = True
			return render('/closepopup.html')
		try:
			content = tw_helper.fetch_url(tw_helper.access_token_url,"GET", oauth_token, oauth_token_secret, consumer, 
					params = {'oauth_verifier':oauth_verifier})
		except (urllib2.HTTPError, urllib2.URLError), e:
			log.error("COULDNOT GET TOKEN FROM %s, %s", tw_helper.access_token_url, e)
			return render('/closepopup.html')
		token_data = dict(cgi.parse_qsl(content))
		# Step 3. User Details
		try:
			user_data = simplejson.loads(
							tw_helper.fetch_url("https://api.twitter.com/1/" + "users/show" + "/%s.json" % token_data['user_id'], 
											"GET", 
											token_data['oauth_token'],  
											token_data['oauth_token_secret'],
											consumer
										))
		except (urllib2.HTTPError, urllib2.URLError), e:
			log.error(e)
			return self.ERROR
		user_data['network'] = 'twitter'
		user_data['network_id'] = user_data.pop('id')
		user_data['access_token'] = token_data['oauth_token']
		user_data['access_token_secret'] = token_data['oauth_token_secret']
		user_data['profile_picture_url'] = tw_helper.get_profile_picture_url(user_data.pop('profile_image_url'))
		user_data['locale'] = user_data['lang']
		user_data['link'] = user_data['url']
		#Save and Persist, render profile
		success, msg = g.user_service.login_or_consolidate(user_data, remote_persist_user)
		c.refresh_login = True
		return render('/closepopup.html')