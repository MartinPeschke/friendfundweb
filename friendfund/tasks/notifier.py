"""
FriendFund Notification Service, the only commandline argument should be the paster config file.
i.e. invoke as: python friendfund/tasks/notifier.py -f development.ini
"""
import logging, time, sys, getopt, os
from lxml import etree
from xml.sax.saxutils import quoteattr
from friendfund.tasks import get_db_pool, get_config, Usage
from friendfund.tasks.notifiers import email, facebook, twitter
from friendfund.tasks.notifiers.common import InvalidAccessTokenException

import logging
logging.config.fileConfig("notifier_logging.conf")
logging.basicConfig()
log = logging.getLogger(__name__)

import gettext

transl = gettext.translation('friendfund', os.path.normpath(os.path.join(__file__, '..','..', 'i18n')), ['en', 'de'])
_ = transl.ugettext
L10N_KEYS = ['occasion']


CONNECTION_NAME = 'job'

def empty_sender(name = None):
	def es(file_no, sndr_data, rcpt_data, template_data, config, rcpts_data = None):
		log.warning( "%s_MESSAGING_IS_OFF", name )
		return "1"
	return es
def error_sender(name = None):
	def es(file_no, sndr_data, rcpt_data, template_data, config, rcpts_data = None):
		raise Exception( "NOT_IMPLEMENTED_ERROR(%s)" % name)
	return es

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
	ROOT_URL = config['site_root_url']
	
	debug = config['debug'].lower() == 'true'
	
	facebook_on = config['notification_fb'].lower() == 'on'
	twitter_on = config['notification_tw'].lower() == 'on'
	email_on = config['notification_email'].lower() == 'on'
	
	messengers = {}
	if facebook_on:
		messengers['create_event'] = facebook.create_event_invite
		messengers['stream_publish'] = facebook.send_stream_publish
	else:
		messengers['create_event'] = empty_sender("create_event")
		messengers['stream_publish'] = empty_sender('stream_publish')
	if twitter_on:
		messengers['tweet'] = twitter.send_tweet
		messengers['tweet_dm'] = empty_sender('tweet_dm')
	else:
		messengers['tweet'] = empty_sender('tweet')
		messengers['tweet_dm'] = empty_sender('tweet_dm')
	if email_on:
		messengers['email'] = email.send
	else:
		messengers['email'] = empty_sender('email')
	
	log.info( 'DEBUG: %s for %s (fb:%s,tw:%s,email:%s)', debug, CONNECTION_NAME,  facebook_on, twitter_on, email_on )
	
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
				template_data["DEFAULT_BASE_URL"] = ROOT_URL
				rcpts_data = [msg.attrib for msg in msg_data.find("TEMPLATE").findall("RECIPIENT")]
				for k in L10N_KEYS:
					if k in template_data and template_data[k]:
						template_data[k] = _(template_data[k])
				
				log.info ( 'meta_data, %s', meta_data)
				log.info ( 'SENDER, %s', sndr_data)
				log.info ( 'RECIPIENT, %s', rcpt_data)
				log.info ( 'extraRECIPIENTs, %s', rcpts_data)
				log.info ( 'TEMPLATE, %s', template_data)
				
				try:
					notification_method = meta_data.get('notification_method').lower()
					sender = messengers.get(notification_method, error_sender(notification_method))
					msg_id = sender(meta_data['file_no'], sndr_data, rcpt_data, template_data, config, rcpts_data)
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
		time.sleep(10)

if __name__ == "__main__":
    sys.exit(main())