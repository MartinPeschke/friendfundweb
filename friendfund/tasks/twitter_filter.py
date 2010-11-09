import subprocess, simplejson, pprint, sys, getopt, urllib, urllib2
from collections import deque
from celery.task.sets import TaskSet


from friendfund.model.mapper import DBMapper
from friendfund.model.pool import PoolUser, AddInviteesProc
from friendfund.lib import tw_helper
from friendfund.tasks.photo_renderer import remote_profile_picture_render
from friendfund.tasks import get_dbm, get_config

UNAME="MartinPeschke"
UPWD="thebard43"
SEARCH_TERMS = ['bieber']
ADMIN_ID=23624
POOL_URL="UC0xMjQ0OA~~"
POOL_ID=12448

import logging
import logging.config
logging.config.fileConfig("notifier_logging.conf")
logging.basicConfig()
log = logging.getLogger(__name__)
CONNECTION_NAME = 'pool'


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
	for line in res:
		print line
		status =  simplejson.loads(line)
		if len(status['entities']['hashtags']) < 2 and status['user']['followers_count'] > 25 and status['user']['lang'] in ['de','en']:
			users[status['user']['id']] = PoolUser(
					name=status['user']['name'],
					network='twitter',
					network_id=status['user']['id'],
					screen_name=status['user']['screen_name'],
					profile_picture_url=tw_helper.get_profile_picture_url(status['user']['profile_image_url'])
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