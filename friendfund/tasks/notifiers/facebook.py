import urllib, urllib2, simplejson, logging, StringIO, os

from friendfund.lib import helpers as h
from friendfund.tasks import data_root, get_db_pool
from celery.execute import send_task
from poster.streaminghttp import register_openers
from poster.encode import multipart_encode
from friendfund.tasks.notifiers.facebook_templates import TEMPLATES, STANDARD_PARAMS
import logging.config
logging.config.fileConfig("notifier_logging.conf")
logging.basicConfig()
log = logging.getLogger(__name__)

SET_EVENT_ID = """exec job.set_pool_event_id '<POOL p_url="%(p_url)s" event_id="%(event_id)s"/>'"""

from friendfund.tasks.notifiers.common import InvalidAccessTokenException

def _create_event(query, image_url, pool_url, config):
	log.info('CREATing EVENT WITH: (%s)', query)
	register_openers()
	datagen, headers = multipart_encode(query)
	req = urllib2.Request('https://graph.facebook.com/me/events', datagen, headers)
	event_id = simplejson.load(urllib2.urlopen(req)).get('id')
	log.info('CREATED EVENT WITH: %s (%s)', event_id, query)
	send_task('friendfund.tasks.fb.upload_picture_to_event', args = [event_id, query['access_token'], image_url])
	
	log.info ( SET_EVENT_ID % {'p_url':pool_url, 'event_id':event_id} )
	dbpool = get_db_pool(config, "job")
	conn = dbpool.connection()
	cur = conn.cursor()
	res = cur.execute(SET_EVENT_ID % {'p_url':pool_url, 'event_id':event_id})
	res = res.fetchone()[0]
	cur.close()
	conn.commit()
	conn.close()
	log.info ( res )
	return event_id

def _create_event_invite(template, sndr_data, rcpt_data, template_data, config):
	data = template_data
	if not template_data.get('event_id'):
		query = {}
		query['name'] = template.get_def("name").render_unicode(h = h, data = data).encode("utf-8")
		query['description'] = template.get_def("description").render_unicode(h = h, data = data).encode("utf-8")
		query['link'] = template.get_def("link").render_unicode(h = h, data = data).encode("utf-8")
		query['privacy_type'] = template.get_def("privacy_type").render_unicode(h = h, data = data).encode("utf-8")
		query['start_time'] = template.get_def("start_time").render_unicode(h = h, data = data).encode("utf-8")
		query['end_time'] = template.get_def("end_time").render_unicode(h = h, data = data).encode("utf-8")
		query['location'] = template.get_def("location").render_unicode(h = h, data = data).encode("utf-8")
		query["access_token"] = sndr_data["access_token"].encode("utf-8")
		query["format"] = "json"
		query["host"] = "me"
		
		image_url = h.get_product_picture(template_data.get("pool_image"), "FF_POOL", site_root=template_data["DEFAULT_BASE_URL"])
		event_id = _create_event(query, image_url, template_data['p_url'], config)
	else:
		event_id = template_data['event_id']
	msg = {"eid":str(event_id),
			"uids" : '[%s]'%','.join(rcpt['network_id'] for rcpt in template_data['recipients']),
			"personal_message":query['description'].encode("utf-8"), 
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


def _stream_publish(template, sndr_data, rcpt_data, template_data):
	data = template_data
	scrap = template.get_def("picture").render_unicode(h = h, data = data)
	msg = {}
	msg['message'] = template.get_def("message").render_unicode(h = h, data = data).encode("utf-8")
	msg['link'] = template.get_def("link").render_unicode(h = h, data = data).encode("utf-8")
	msg['name'] = template.get_def("name").render_unicode(h = h, data = data).encode("utf-8")
	msg['caption'] = template.get_def("caption").render_unicode(h = h, data = data).encode("utf-8")
	msg['description'] = template.get_def("description").render_unicode(h = h, data = data).encode("utf-8")
	actions = {}
	actions['name'] = template.get_def("action_name").render_unicode(h = h, data = data)
	actions['link'] = template.get_def("action_link").render_unicode(h = h, data = data)
	msg['actions'] = simplejson.dumps(actions).encode("utf-8")
	msg['picture'] = h.get_product_picture(template_data.get("pool_image"), "FF_POOLS", site_root=template_data["DEFAULT_BASE_URL"]).encode("utf-8")
	
	msg['access_token'] = sndr_data['access_token'].encode("utf-8")
	
	query = urllib.urlencode(msg)
	try:
		resp = urllib2.urlopen('https://graph.facebook.com/%s/feed' % rcpt_data.get('network_ref'), query)
	except urllib2.HTTPError, e:
		resp = e.fp
	post = simplejson.loads(resp.read())
	
	
	# response.get("error"):
	# raise GraphAPIError(response["error"]["type"], response["error"]["message"])
	
	
	if 'error' in post and str(post['error']['type']) == 'OAuthException':
		raise InvalidAccessTokenException(simplejson.dumps(post))
	else:
		return post['id']
	
def create_event_invite(template, sndr_data, rcpt_data, template_data, config):
	return _create_event_invite(template, sndr_data, rcpt_data, template_data, config)
def send_stream_publish(template, sndr_data, rcpt_data, template_data, config):
	return _stream_publish(template, sndr_data, rcpt_data, template_data)