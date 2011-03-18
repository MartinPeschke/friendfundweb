"""
FriendFund Notification Service, the only commandline argument should be the paster config file.
i.e. invoke as: python friendfund/tasks/notifier.py -f development.ini
"""
import logging, time, sys, getopt, os, mako
from lxml import etree
from xml.sax.saxutils import quoteattr
from friendfund.tasks import get_db_pool, get_config, Usage
from friendfund.tasks.notifiers import email, facebook, twitter
from friendfund.tasks.notifiers.common import InvalidAccessTokenException, MissingTemplateException
from datetime import datetime, date
from decimal import Decimal
from friendfund.lib.helpers import format_int_amount

from babel.numbers import format_currency as fc, format_decimal as fdec, get_currency_symbol, get_decimal_symbol, get_group_symbol, parse_number as pn
from babel.dates import format_date as fdate, format_datetime as fdatetime
import logging
logging.config.fileConfig("notifier_logging.conf")
logging.basicConfig()
log = logging.getLogger(__name__)

from mako.lookup import TemplateLookup
from friendfund.tasks import data_root
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tmpl_lookup = TemplateLookup(directories=[os.path.join(root, 'templates_free_form','messaging', 'messages')]
		, module_directory=os.path.join(data_root, 'templates_free_form','messaging', 'messages')
		, output_encoding='utf-8'
		)

print os.path.join(root, 'templates_free_form','messaging', 'messages')



import gettext
transl = gettext.translation('friendfund', os.path.normpath(os.path.join(__file__, '..','..', 'i18n')), ['en', 'de'])
_ = transl.ugettext
L10N_KEYS = ['occasion']


CONNECTION_NAME = 'job'

def empty_sender(name = None):
	def es(template, sndr_data, rcpt_data, template_data, config):
		log.warning( "%s_MESSAGING_IS_OFF", name )
		return "1"
	return es
def error_sender(name = None):
	def es(template, sndr_data, rcpt_data, template_data, config):
		raise Exception( "NOT_IMPLEMENTED_ERROR(%s)" % name)
	return es
	
	
def save_results(dbpool, messaging_results):

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


def identity(key, data_map):
	return {key: data_map[key]}
def pool_url(key, data_map):
	return {key: "http://%s/pool/%s" % (data_map["merchant_domain"], data_map[key])}
def amount(key, data_map):
	return {key: format_int_amount(data_map[key])}
def currency(key, data_map):
	val = float(data_map[key]) / 100
	fnumber = Decimal('%.2f' % val)
	return {key: fc(fnumber, data_map['currency'], locale="en_GB")}
def firstname(key, data_map):
	return {"firstname_%s"%key:data_map[key].split()[0], key:data_map[key]}
def date(key, data_map):
	val = data_map[key]
	try:
		val =  datetime.strptime(val.rsplit('.',1)[0], '%Y-%m-%dT%H:%M:%S')
	except ValueError, e:
		val = datetime.strptime(val.split('T')[0], '%Y-%m-%d')
	if isinstance(val, datetime):
		return {key: fdate(val, format="long", locale="en_GB")}
	else:
		return {key: val}
	

TRANSLATIONS = {"expiry_date": date, "target_amount":amount, "chip_in_amount":currency, "invitee_name": firstname}

def localize(data_map):
	result = {}
	for key in data_map:
		if key in TRANSLATIONS:
			updates = TRANSLATIONS[key](key, data_map)
			result.update(updates)
		else:
			result[key] = data_map[key]
	return result

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
				template_data = dict( msg_data.find("TEMPLATE").attrib )
				template_data["DEFAULT_BASE_URL"] = ROOT_URL
				template_data["today"] =datetime.today().strftime("%d.%m.%Y")
				
				template_data = localize(template_data)
				
				
				rcpts_data = [msg.attrib for msg in msg_data.find("TEMPLATE").findall("RECIPIENT")]
				if rcpts_data:
					template_data['recipients'] = rcpts_data
				ivts_data = [msg.attrib for msg in msg_data.find("TEMPLATE").findall("INVITEE")]
				if ivts_data:
					template_data['invitee_list']=ivts_data
				print '-'*80
				log.info ( 'meta_data, %s', meta_data)
				log.info ( 'SENDER, %s', sndr_data)
				log.info ( 'RECIPIENT, %s', rcpt_data)
				log.info ( 'extraRECIPIENTs, %s', rcpts_data)
				log.info ( 'extraINVITEEs, %s', ivts_data)
				log.info ( 'TEMPLATE, %s', template_data)
				
				
				try:
					file_no = meta_data['file_no']
					try:
						template = tmpl_lookup.get_template('/msg_%s.txt' % file_no)
					except mako.exceptions.TopLevelLookupException, e:
						log.warning( "ERROR Template not Found for (%s)" , ('/msg_%s.txt' % file_no) )
						raise MissingTemplateException(e)
					else:
						notification_method = meta_data.get('notification_method').lower()
						sender = messengers.get(notification_method, error_sender(notification_method))
						msg_id = sender(template, sndr_data, rcpt_data, template_data, config)
				
				
				except InvalidAccessTokenException, e:
					log.error( 'INVALID_ACCESS_TOKEN before SENDING: %s', str(e) )
					messaging_results[meta_data.get('message_ref')] = {'status':'INVALID_ACCESS_TOKEN'}
				except Exception, e:
					log.error( 'ERROR while SENDING: %s (%s)', meta_data, str(e) )
					messaging_results[meta_data.get('message_ref')] = {'status':'FAILED'}
					if debug: 
						save_results(dbpool, messaging_results)
						messaging_results = {}
						raise
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