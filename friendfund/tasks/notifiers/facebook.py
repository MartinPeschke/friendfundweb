import urllib, urllib2, simplejson, logging, StringIO
from friendfund.lib import helpers as h
from friendfund.tasks import data_root, get_db_pool
from friendfund.tasks.notifiers.common import MissingTemplateException, InvalidAccessTokenException
from celery.execute import send_task
from poster.streaminghttp import register_openers
from poster.encode import multipart_encode
from friendfund.tasks.notifiers.facebook_templates import TEMPLATES, STANDARD_PARAMS, EVENT_TEMPLATE
import logging.config
logging.config.fileConfig("notifier_logging.conf")
logging.basicConfig()
log = logging.getLogger(__name__)

SET_EVENT_ID = """exec job.set_pool_event_id '<POOL p_url="%(p_url)s" event_id="%(event_id)s"/>'"""

def _create_event(query, image_url, template_data, config):
	log.info('CREATing EVENT WITH: (%s)', query)
	register_openers()
	datagen, headers = multipart_encode(query)
	req = urllib2.Request('https://graph.facebook.com/me/events', datagen, headers)
	event_id = simplejson.load(urllib2.urlopen(req)).get('id')
	log.info('CREATED EVENT WITH: %s (%s)', event_id, query)
	send_task('friendfund.tasks.fb.upload_picture_to_event', args = [event_id, query['access_token'], image_url])
	
	log.info ( SET_EVENT_ID % {'p_url':template_data['p_url'], 'event_id':event_id} )
	dbpool = get_db_pool(config, "messaging")
	conn = dbpool.connection()
	cur = conn.cursor()
	res = cur.execute(SET_EVENT_ID % {'p_url':template_data['p_url'], 'event_id':event_id})
	res = res.fetchone()[0]
	cur.close()
	conn.commit()
	conn.close()
	log.info ( res )
	return event_id

def create_event_invite(sndr_data, rcpt_data, template_data, config, rcpts_data):
	if not template_data.get('event_id'):
		query = {}
		query.update(EVENT_TEMPLATE)
		query = dict((k,v.substitute(**dict(template_data)).encode("utf-8")) for k,v in query.iteritems())
		query["access_token"] = sndr_data["access_token"]
		query["format"] = "json"
		query["tagline"] = "Friendfund, group gifts"
		query["host"] = "me"
		query["privacy_type"] = template_data.get('is_secret') == '1' and "SECRET" or "OPEN"
		
		image_url = h.get_user_picture(template_data["image_url"], "POOL", site_root=template_data["ROOT_URL"])
		event_id = _create_event(query, image_url, template_data, config)
	else:
		event_id = template_data['event_id']
	msg = {"eid":str(event_id),
			"uids" : '[%s]'%','.join(rcpt['network_id'] for rcpt in rcpts_data),
			"personal_message":template_data['description'], 
			"format":"json",
			"access_token":sndr_data['access_token']}
	msg = dict((k,v.encode("utf-8")) for k,v in msg.iteritems())
	try:
		resp = urllib2.urlopen('https://api.facebook.com/method/events.invite', urllib.urlencode(msg)).read()
	except urllib2.HTTPError, e:
		resp = e.fp
	if resp not in ['true','false']:
		raise InvalidAccessTokenException(resp)
	return str(event_id)





def stream_publish(template, sndr_data, rcpt_data, template_data):
	msg = STANDARD_PARAMS.copy()
	msg.update(template)
	if 'image_url' in template_data:
		template_data['image_url'] = h.get_product_picture(template_data['image_url'], 'POOL', site_root=template_data['ROOT_URL'])
	msg = dict((k,v.substitute(**dict(template_data)).encode("utf-8")) for k,v in msg.iteritems())
	msg['access_token'] = sndr_data['access_token']
	query = urllib.urlencode(msg)
	try:
		resp = urllib2.urlopen('https://graph.facebook.com/%s/feed' % rcpt_data.get('network_ref'), query)
	except urllib2.HTTPError, e:
		resp = e.fp
	post = simplejson.loads(resp.read())
	if 'error' in post and str(post['error']['type']) == 'OAuthException':
		raise InvalidAccessTokenException(simplejson.dumps(post))
	else:
		return post['id']
	
	
	
def send_stream_publish(sndr_data, rcpt_data, template_data, config, rcpts_data = None):
	msg_realm = template_data.get('is_secret') == '0' and "public" or "secret"
	templ_name = template_data['t_name']
	try:
		template = TEMPLATES[templ_name][msg_realm]
	except KeyError, e:
		log.warning( "ERROR Facebook Stream Publish Template not Found for (%s,%s)" , templ_name, msg_realm )
		raise MissingTemplateException(e)
	else:
		return stream_publish(template, sndr_data, rcpt_data, template_data)