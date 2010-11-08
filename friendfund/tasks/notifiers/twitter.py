import simplejson, urllib, urllib2, loggingfrom friendfund.lib import oauthfrom friendfund.lib import tw_helperfrom friendfund.tasks.notifiers.common import MissingTemplateException, InvalidAccessTokenExceptionfrom friendfund.tasks.notifiers.twitter_templates import TEMPLATES, STANDARD_PARAMSlog = logging.getLogger(__name__)def url_shorten(login, apikey, url):	query = urllib.quote(url)	query = "https://api-ssl.bit.ly/v3/shorten?domain=j.mp&login=%(login)s&apiKey=%(apikey)s&longUrl=%(query)s"%locals()	try:		res = urllib.urlopen(query)	except urllib.HTTPError, e:		log.error(e.fp().read())		return url	else:		result = simplejson.loads(res.read())		if result['status_code'] == 200:			return result['data']['url']		else:			log.error(result)			return urldef send_tweet(sndr_data, rcpt_data, template_data):	msg_realm = template_data.get('is_secret') == '0' and "public" or "secret"	templ_name = template_data['t_name']	try:		template = TEMPLATES[templ_name][msg_realm]		url = TEMPLATES[templ_name]['url']	except KeyError, e:		log.warning( "ERROR Twitter TWEET Template not Found for (%s)" , templ_name )		raise MissingTemplateException(e)		msg_params = dict(template_data)	msg_params['screen_name'] = rcpt_data['screen_name']	msg_params['url'] = url_shorten(sndr_data['bitlylogin'], sndr_data['bitlyapikey'], url.substitute(**msg_params))	len_url = len(msg_params['url'])		msg =  template.substitute(**msg_params).encode('utf-8')	if len(msg) + len_url > 140:		msg = msg[:137-len_url] + '...'	msg = msg + msg_params['url']		consumer = oauth.Consumer(sndr_data['twitterapikey'], sndr_data['twitterapisecret'])	try:		json_data = tw_helper.fetch_url("https://api.twitter.com/1/statuses/update.json", 										"POST", 										sndr_data['access_token'], 										sndr_data['access_token_secret'], 										consumer,										params = {"status" : msg})	except urllib2.HTTPError, e:		print e.fp.read()		raise InvalidAccessTokenException(e)	else:		json_data = simplejson.loads(json_data)		return str(json_data.get("id"))