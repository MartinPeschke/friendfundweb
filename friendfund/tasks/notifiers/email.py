# -*- coding: utf-8 -*-
from string import Template as Template
import urllib2, os, logging, mako, markdown
from lxml import etree
from docutils.core import publish_parts

from poster.encode import multipart_encode
from poster.streaminghttp import register_openers

from friendfund.lib import helpers as h
from friendfund.tasks import data_root

register_openers()

ums_url = "http://sysmail.fagms.net/c/sm"
ums_standard_params = {'AID':"27220", "ACTION":"SYSTEM"}

log = logging.getLogger(__name__)

class UMSEmailUploadException(Exception):pass

def _send_email(template, sndr_data, rcpt_data, template_data):
	message_params = ums_standard_params.copy()
	message_params['email'] = rcpt_data['email']
	
	data = template_data
	
	message_params['subject'] = template.get_def("subject").render_unicode(h = h, data = data)
	message_params['text'] = template.render_unicode(h = h, data = data) #'h':h, when locale is available
	message_params['html'] = markdown.markdown(message_params['text'])
	datagen, headers = multipart_encode(message_params)
	request = urllib2.Request(ums_url, datagen, headers)
	response = etree.parse(urllib2.urlopen(request))
	if response.find("emstatus").text=='SUCCESS':
		return response.find("emguid").text
	else:
		log.warning("UMS Sending Failed %s (%s)" , response.find("emstatus").text, response.find("emstatuscodes").text)
		raise UMSEmailUploadException("UMS Sending Failed %s (%s)" % (response.find("emstatus").text, response.find("emstatuscodes").text))
	
	
def send(template, sndr_data, rcpt_data, template_data, config):
	return _send_email(template, sndr_data, rcpt_data, template_data)