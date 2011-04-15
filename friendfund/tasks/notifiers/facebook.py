import urllib, urllib2, simplejson, logging, StringIO, os
from datetime import datetime, date

from celery.execute import send_task
from poster.streaminghttp import register_openers
from poster.encode import multipart_encode

from friendfund.lib import helpers as h
from friendfund.model.db_access import execute_query
from friendfund.tasks import data_root, get_db_pool
log = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
log.addHandler(ch)

SET_EVENT_ID = "exec job.set_pool_event_id ?;"
SET_EVENT_ID_PARAM = '<POOL p_url="%(p_url)s" event_id="%(event_id)s"/>'

from friendfund.tasks.notifiers.common import InvalidAccessTokenException


def _create_event(access_token, query, image_url, pool_url, config):
	query['access_token'] = access_token
	query['format'] = "json"
	log.info('CREATing EVENT WITH: (%s)', query)
	register_openers()
	datagen, headers = multipart_encode(query)
	req = urllib2.Request('https://graph.facebook.com/me/events', datagen, headers)
	event_id = simplejson.load(urllib2.urlopen(req)).get('id')
	send_task('friendfund.tasks.fb.upload_picture_to_event', args = [event_id, query['access_token'], image_url])
	
	result, cur = execute_query(get_db_pool(config, "job"), log, SET_EVENT_ID, SET_EVENT_ID_PARAM % {'p_url':pool_url, 'event_id':event_id})
	return event_id


def _create_event_oldstyle(access_token, query, image_url, pool_url, config):
	params = {"event_info":simplejson.dumps(query), "access_token":access_token, "format":"json"}
	log.info('CREATING EVENT WITH: (%s)', urllib.urlencode(params))
	req = urllib2.Request('https://api.facebook.com/method/events.create', urllib.urlencode(params))
	try:
		event_id = urllib2.urlopen(req).read()
	except urllib2.HTTPError, e:
		error = e.fp.read()
		log.error( error )
		raise Exception(error)
	else:
		log.info( event_id )
	send_task('friendfund.tasks.fb.upload_picture_to_event', args = [event_id, access_token, image_url])
	
	result, cur = execute_query(get_db_pool(config, "job"), log, SET_EVENT_ID, SET_EVENT_ID_PARAM % {'p_url':pool_url, 'event_id':event_id})
	return event_id

def _create_event_invite(template, sndr_data, rcpt_data, template_data, config):
	data = template_data
	query = {}
	query['description'] = template.get_def("description").render_unicode(h = h, data = data).encode("utf-8")
	if not template_data.get('event_id'):
		query['name'] = template.get_def("name").render_unicode(h = h, data = data).encode("utf-8")
		query['privacy_type'] = "OPEN"
		query['start_time'] = datetime.today().strftime("%Y-%m-%d")
		query['end_time'] = template_data["expiry_date_object"].strftime("%Y-%m-%d")
		query['location'] = template.get_def("location").render_unicode(h = h, data = data).encode("utf-8")
		query["host"] = "me"
		image_url = h.get_product_picture(template_data.get("pool_image"), "FF_POOLS", site_root=template_data["DEFAULT_BASE_URL"])
		event_id = _create_event(sndr_data["access_token"], query, image_url, template_data['p_url'], config)
	else:
		event_id = template_data['event_id']
	msg = {"eid":str(event_id),
			"uids" : '[%s]'%','.join(rcpt['network_id'] for rcpt in template_data['recipients']),
			"personal_message":query['description'],
			"format":"json",
			"access_token":sndr_data['access_token']}
	try:
		resp = urllib2.urlopen('https://api.facebook.com/method/events.invite', urllib.urlencode(msg)).read()
	except urllib2.HTTPError, e:
		error = e.fp.read()
		log.error( error )
		raise Exception(error)
	if resp not in ['true','false']:
		raise InvalidAccessTokenException("FACEBOOK_REPLY_NOT_EXPECTED, expected (true|false) got:(%s)"%resp)
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
	
	msg['access_token'] = sndr_data['access_token']
	
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