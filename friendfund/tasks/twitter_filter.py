import subprocess, simplejson, pprint, sys, getopt, urllib, urllib2
from collections import deque
from celery.task.sets import TaskSet


from friendfund.model.mapper import DBMapper
from friendfund.model.pool import PoolUser, AddInviteesProc
from friendfund.lib import tw_helper
from friendfund.tasks.photo_renderer import remote_profile_picture_render
from friendfund.tasks import get_dbm, get_config, get_db_pool

UNAME="Friendfund_Jany"
UPWD="friendfund"
SEARCH_TERMS = ['bieber']
ADMIN_ID=25711
POOL_URL="UC0xMjQ3Nw~~"
POOL_ID=12477

import logging
import logging.config
logging.config.fileConfig("notifier_logging.conf")
logging.basicConfig()
log = logging.getLogger(__name__)
CONNECTION_NAME = 'pool'

ACCESS_TOKEN=[
			"""exec job.update_twitter_token '<USER network="twitter" id="214107422" name="Friendfund_Jany" screen_name="Friendfund_Jany" access_token="214107422-v6hVgVs9VyA7BevzqeIVgl6UXCcy3azHvxZ5Ddhs" access_token_secret="PspL4xddG601q0y2DFN5N9OxE1ABzonfJcqQn1FCQU" locale="en" profile_picture_url="http://a2.twimg.com/profile_images/1164054394/logo_twitter.jpg" />';""",
			"""exec job.update_twitter_token '<USER network="twitter" id="214078686" name="Friendfund_Sara" screen_name="Friendfund_Sara" access_token="214078686-l5xpS9YaYKIUAiBFYqa4VnMyvdzvFZ5TxXu4cYPS" access_token_secret="cmQ5pRPUf6XKa2fkxWOxjuVB6HqwP8xh1kiurKA7sh8" locale="en" profile_picture_url="http://a2.twimg.com/profile_images/1164025326/logo_twitter.jpg" />';""",
			"""exec job.update_twitter_token '<USER network="twitter" id="214080382" name="Friendfund_Jane" screen_name="Friendfund_Jane" access_token="214080382-jJ7BrQh7N0u17QZMuZhTFrOA9LEDuQfafk3u8dGn" access_token_secret="sYN4YkwfDySe0wg1Vlbl6c1QZb4R7LRXv6BtSfRbI" locale="en" profile_picture_url="http://a1.twimg.com/profile_images/1164026705/logo_twitter.jpg" />';""",
			"""exec job.update_twitter_token '<USER network="twitter" id="214081136" name="Friendfund_Luca" screen_name="Friendfund_Luca" access_token="214081136-kPswWGZsgt45TPWSyqeL9fc8IVeyaYKVV4aldZZQ" access_token_secret="fXuuQKUYwktsSsmkhMGLxwegWD28rDpjUSQw5Zn4w" locale="en" profile_picture_url="http://a0.twimg.com/profile_images/1164028276/logo_twitter.jpg" />';""",
			"""exec job.update_twitter_token '<USER network="twitter" id="214081676" name="Friendfund_Emma" screen_name="Friendfund_Emma" access_token="214081676-WfJQA1DaEhNRECBHlPJoXtw3fVYE7ng26J6IyRk7" access_token_secret="dCmYdqgljelsviKpnprtmcRElK5NWsyZCBi27bLcbc" locale="en" profile_picture_url="http://a1.twimg.com/profile_images/1164031717/logo_twitter.jpg" />';""",
			"""exec job.update_twitter_token '<USER network="twitter" id="214084033" name="Friendfund_Pete" screen_name="Friendfund_Pete" access_token="214084033-sc7fHQGkNN4iXjOUpVQHnxAmr86QBLcmECcyxvaA" access_token_secret="G2wi2tY6O2sCfa6Xa0I8BhotEsO3CWYk6iyEShxQH8" locale="en" profile_picture_url="http://a2.twimg.com/profile_images/1164035114/logo_twitter.jpg" />';""",
			"""exec job.update_twitter_token '<USER network="twitter" id="214106291" name="Friendfund_Tony" screen_name="Friendfund_Tony" access_token="214106291-IfnQhjPhQjisdBs1BtecXNut2ENZak1kibJih1mH" access_token_secret="ICNs0umAxCiKzW2WlnPGVLZhdB9R6l1gSP7eWY29yY" locale="en" profile_picture_url="http://a2.twimg.com/profile_images/1164051858/logo_twitter.jpg" />';""",
			"""exec job.update_twitter_token '<USER network="twitter" id="214086126" name="Friendfund_John" screen_name="Friendfund_John" access_token="214086126-rUB9yh2IbxqrZT5cfl4DaN42zf5ohHjhm3kTTOQQ" access_token_secret="dgnErz79ssTyAPqKR8Yu6Aa7csZ3CrNhqqpGHBxEQ6Y" locale="en" profile_picture_url="http://a2.twimg.com/profile_images/1164046142/logo_twitter.jpg" />';""",
			"""exec job.update_twitter_token '<USER network="twitter" id="214084782" name="Friendfund_Mary" screen_name="Friendfund_Mary" access_token="214084782-UnZPOcnbmBygPSxn7oeAMUYVNejekOcgKs6mNGoU" access_token_secret="tkpPA6uuC8iUIiAm5cK7JOP7Issdu0CT2jeTFQnRg58" locale="en" profile_picture_url="http://a0.twimg.com/profile_images/1164041284/logo_twitter.jpg" />';""",
			"""exec job.update_twitter_token '<USER network="twitter" id="214105390" name="Friendfund_Caro" screen_name="Friendfund_Caro" access_token="214105390-d5VPGKRcZPsONcqS2K6Ezd2sxEoevfbbIOJZHvjS" access_token_secret="SGQV07CspR3lUbeu77CoiETM03mNd3YsCtY1KHgM" locale="en" profile_picture_url="http://a3.twimg.com/profile_images/1164050059/logo_twitter.jpg" />';"""]



def main(argv=None):
	
	if argv is None:
		argv = sys.argv
	try:
		opts, args = getopt.getopt(sys.argv[1:], "f:h", ["help", "file"])
		opts = dict(opts)
		if '-f' not in opts:
			raise Usage("Missing Option -f")
	except getopt.error, msg:
		 raise Usage(msg)
	except Usage, err:
		print >>sys.stderr, err.msg
		print >>sys.stderr, "for help use --help"
		return 2
	
	configname = opts['-f']
	config = get_config(configname)
	dbpool = get_dbm(CONNECTION_NAME)
	ROOT_URL = config['short_site_root_url']
	
	debug = config['debug'].lower() == 'true'
	log.info( 'DEBUG: %s for %s', debug, CONNECTION_NAME )
	
	data = urllib.urlencode({"count":"100,000","track":"bieber"})
	password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
	password_mgr.add_password(None, "http://stream.twitter.com", UNAME, UPWD)
	handler = urllib2.HTTPBasicAuthHandler(password_mgr)
	opener = urllib2.build_opener(handler)
	urllib2.install_opener(opener)
	
	res = urllib2.urlopen("http://stream.twitter.com/1/statuses/filter.json", data)
	users = {}
	
	
	dbjobs = get_db_pool(config, "messaging")
	conn = dbjobs.connection()
	cur = conn.cursor()
	for q in ACCESS_TOKEN:
		r = cur.execute(q)
		print r.fetchone()[0]
	
	for line in res:
		status =  simplejson.loads(line)
		if len(status['entities']['hashtags']) < 2 and status['user']['followers_count'] > 25 and status['user']['lang'] in ['de','en']:
			users[status['user']['id']] = PoolUser(
					name=status['user']['name'],
					network='twitter',
					network_id=status['user']['id'],
					screen_name=status['user']['screen_name'],
					profile_picture_url=tw_helper.get_profile_picture_url(status['user']['profile_image_url']),
					is_selector = False
				)
			print len(users)
		if len(users) > 500: break
	if len(users):
		pool = dbpool.set(AddInviteesProc(p_id = POOL_ID
						, p_url = POOL_URL
						, inviter_user_id = ADMIN_ID
						, users=users.values()
						, description = "Some Description"
						, is_secret = False))
		tasks = deque()
		for i in users.itervalues():
			tasks.append(remote_profile_picture_render.subtask(args=[[(i.network, i.network_id,i.profile_picture_url)]]))
		job = TaskSet(tasks=tasks)
		job.apply_async()

if __name__ == "__main__":
    sys.exit(main())