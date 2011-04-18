from string import Template as Template
import urllib2, logging, markdown
from lxml import etree
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers

from friendfund.lib import helpers as h
log = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
log.addHandler(ch)
register_openers()

ums_url = "http://sysmail.fagms.net/cgi-bin/systemmail-utf8"
ums_standard_params = {'AID':"33715", "ACTION":"SYSTEM"}


class UMSEmailUploadException(Exception):pass

def send_email(msg):
	msg.update(ums_standard_params)
	msg['html'] = markdown.markdown(msg['text'])
	datagen, headers = multipart_encode(msg)
	request = urllib2.Request(ums_url, datagen, headers)
	try:
		response = etree.parse(urllib2.urlopen(request))
	except urllib2.HTTPError, e:
		response = etree.parse( e.fp )
	if response.find("emstatus").text=='SUCCESS':
		return response.find("emguid").text
	else:
		log.warning("UMS Sending Failed %s (%s)" , response.find("emstatus").text, response.find("emstatuscodes").text)
		raise UMSEmailUploadException("UMS Sending Failed %s (%s)" % (response.find("emstatus").text, response.find("emstatuscodes").text))
	
	
def send(template, sndr_data, rcpt_data, template_data, config):
	message_params = {}
	message_params['email'] = rcpt_data['email']
	message_params['subject'] = template.get_def("subject").render_unicode(h = h, data = template_data)
	message_params['text'] = template.render_unicode(h = h, data = template_data)
	return send_email(message_params)