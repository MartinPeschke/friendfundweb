import urllib, urllib2, simplejson, logging, StringIO
from friendfund.lib.helpers import get_product_picture
from friendfund.tasks import data_root
from friendfund.tasks.notifiers.common import MissingTemplateException, InvalidAccessTokenException

from friendfund.tasks.notifiers.facebook_templates import TEMPLATES, STANDARD_PARAMS
log = logging.getLogger(__name__)

def stream_publish(template, sndr_data, rcpt_data, template_data):
	msg = STANDARD_PARAMS.copy()
	msg.update(template)
	if 'image_url' in template_data:
		template_data['image_url'] = get_product_picture(template_data['image_url'], 'POOL', site_root=template_data['ROOT_URL'])
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

def send_stream_publish(sndr_data, rcpt_data, template_data):
	msg_realm = template_data.get('is_secret') == '0' and "public" or "secret"
	templ_name = template_data['t_name']
	try:
		template = TEMPLATES[templ_name][msg_realm]
	except KeyError, e:
		log.warning( "ERROR Facebook Stream Publish Template not Found for (%s,%s)" , templ_name, msg_realm )
		raise MissingTemplateException(e)
	else:
		return stream_publish(template, sndr_data, rcpt_data, template_data)