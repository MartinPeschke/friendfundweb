"""
FriendFund Notification Service, the only commandline argument should be the paster config file.
i.e. invoke as: python friendfund/services/notifier.py -f development.ini
"""
import logging, time, sys, getopt, os
from lxml import etree
from xml.sax.saxutils import quoteattr
from friendfund.tasks import get_db_pool, get_config
from friendfund.tasks.notifiers import email, facebook, twitter
from friendfund.tasks.notifiers.common import InvalidAccessTokenException

import logging.config
logging.config.fileConfig("notifier_logging.conf")
logging.basicConfig()

import logging


log = logging.getLogger(__name__)

import gettext
transl = gettext.translation('friendfund', os.path.normpath(os.path.join(__file__, '..','..', 'i18n')), ['en'])
_ = transl.ugettext
L10N_KEYS = ['occasion']


CONNECTION_NAME = 'messaging'
turbomail_config = None

class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg

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
	dbpool = get_db_pool(config, CONNECTION_NAME)
	ROOT_URL = config['short_site_root_url']
	
	debug = config['debug'].lower() == 'true'
	log.info( 'DEBUG: %s for %s', debug, CONNECTION_NAME )
	
	while 1:
		conn = dbpool.connection()
		cur = conn.cursor()
		res = cur.execute('exec job.get_unsent_messages;')
		res = res.fetchone()[0]
		cur.close()
		conn.commit()
		conn.close()
		messaging_results = {}
		log.info ( res )
		messages = etree.fromstring(res)
		msg_set = messages.findall('MESSAGE')
		if msg_set:
			log.info( 'RECEIVED %s, %s', len(msg_set), 'Messages' )
			for msg_data in msg_set:
				meta_data = msg_data.attrib
				sndr_data = msg_data.find("SENDER").attrib
				rcpt_data = msg_data.find("RECIPIENT").attrib
				template_data = msg_data.find("TEMPLATE").attrib
				template_data['ROOT_URL'] = ROOT_URL
				for k in L10N_KEYS:
					if k in template_data:
						template_data[k] = _(template_data[k])
				
				log.info ( 'meta_data, %s', meta_data)
				log.info ( 'SENDER, %s', sndr_data)
				log.info ( 'RECEIPIENT, %s', rcpt_data)
				log.info ( 'TEMPLATE, %s', template_data)
				
				try:
					notification_method = meta_data.get('notification_method').lower()
					if notification_method == 'email':
						msg_id = email.send(sndr_data, rcpt_data, template_data)
					elif notification_method == 'stream_publish':
						msg_id = "1" # facebook.send_stream_publish(sndr_data, rcpt_data, template_data)
					elif notification_method in ['tweet', 'tweet_dm']:
						if sndr_data['u_id'] in ['25710','25711','25712','25713','25714','25715','25716','25717','25718','25719','25720']:
							sndr_data['twitterapikey'] = config['testtwitterapikey']
							sndr_data['twitterapisecret'] = config['testtwitterapisecret']
							print "USED TEST APP"
						else:
							sndr_data['twitterapikey'] = config['twitterapikey']
							sndr_data['twitterapisecret'] = config['twitterapisecret']
						sndr_data['bitlylogin'] = config['bitly.login']
						sndr_data['bitlyapikey'] = config['bitly.apikey']
						
						if notification_method == 'tweet':
							msg_id = twitter.send_tweet(sndr_data, rcpt_data, template_data)
						elif notification_method == 'tweet_dm':
							pass
							# msg_id = twitter.send_dm(sndr_data, rcpt_data, template_data) @ disabled
					else:
						raise Exception("Unknown Notification Method")
				except InvalidAccessTokenException, e:
					log.warning( 'INVALID_ACCESS_TOKEN before SENDING: %s', str(e) )
					messaging_results[meta_data.get('message_ref')] = {'status':'INVALID_ACCESS_TOKEN'}
				except Exception, e:
					log.error( 'ERROR while SENDING: %s (%s)', meta_data, str(e) )
					messaging_results[meta_data.get('message_ref')] = {'status':'FAILED'}
					if debug: raise
				else:
					messaging_results[meta_data.get('message_ref')] = {'status':'SENT', "msg_id":msg_id}

			conn = dbpool.connection()
			cur = conn.cursor()
			status_update =  "<MESSAGES>"
			for mref,values in messaging_results.items():
				status_update += "<MESSAGE message_ref=%s %s/>" % \
					(quoteattr(mref), ' '.join(map(lambda x: ('%s=%s' % (x[0], quoteattr(x[1]))),
									values.iteritems())))
			status_update +=  "</MESSAGES>"
			log.info( 'exec job.set_message_status %s;', status_update )
			res = cur.execute('exec job.set_message_status ?;', status_update)
			res = res.fetchone()[0]
			log.info( res )
			cur.close()
			conn.commit()
			conn.close()
		time.sleep(2)

if __name__ == "__main__":
    sys.exit(main())