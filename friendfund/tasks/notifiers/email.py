# -*- coding: utf-8 -*-
from string import Template as Template
import urllib2, os, logging, mako
from mako.lookup import TemplateLookup
from lxml import etree
from docutils.core import publish_parts

from poster.encode import multipart_encode
from poster.streaminghttp import register_openers

from friendfund.lib import helpers as h
from friendfund.tasks import data_root
from friendfund.tasks.notifiers.common import MissingTemplateException

register_openers()

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tmpl_lookup = TemplateLookup(directories=[os.path.join(root, '..', 'templates','notification')]
		, module_directory=os.path.join(data_root, 'templates','notification')
		, output_encoding='utf-8'
		)
ums_url = "http://sysmail.fagms.net/c/sm"
ums_standard_params = {'AID':"27220", "ACTION":"SYSTEM"}

log = logging.getLogger(__name__)


email = {
		'INVITE': {'subject':Template("Invitation")},
		'INVITE_WITH_ACCOUNT_ACTIVATION' : {'subject':Template("Invitation")},
		'PASSWORD_RESET': {'subject':Template("Reset Password")},
		'ADMIN_EMAIL_ACCOUNT_VALIDATION': {'subject':Template("Account Validation")},
		'ADMIN_FUNDING_REMINDER': {'subject':Template("Funding Reminder")},
		'CONTRIBUTION_RECEIPT': {'subject':Template("Contribution Received")},
		
		'REMIND_INVITEES': {'subject':Template("Please help out")},
		'ASK_RECEIVER': {'subject':Template("Please help out for the awesome gift we are getting you")},
		'ASK_CONTRIBUTORS': {'subject':Template("Please help out just the little bit more")},
		'ASK_CONTRIBUTORS_TO_INVITE': {'subject':Template("Please help out and invite more friends")},
		
		'ECARD_PROMPT': {'subject':Template("Send an eCard")},
		'EMAIL_ECARD_RECEIVER': {'subject':Template("Happy %(occasion)s")},
		'PHOTO_UPLOAD_ECARD_RECEIVER': {'subject':Template("Say Thank You")},
		'POOL_FUNDED_ADMIN': {'subject':Template("${receiver}'s Gift Pool is Funded")},
		'FRIEND_SELECTOR': {'subject':Template("${admin} has nominated you to choose a gift for ${receiver}")}
	}

class UMSEmailUploadException(Exception):pass

def send_email(subject, template, sndr_data, rcpt_data, template_data):
	message_params = ums_standard_params.copy()
	message_params['email'] = rcpt_data['email']
	message_params['subject'] = subject.substitute(**dict(template_data)).encode("utf-8")
	message_params['text'] = template.render_unicode(**{'h':h, 'data': template_data}) #'h':h, when locale is available
	message_params['html'] = publish_parts(message_params['text'], writer_name="html")["html_body"]
	datagen, headers = multipart_encode(message_params)
	request = urllib2.Request(ums_url, datagen, headers)
	response = etree.parse(urllib2.urlopen(request))
	if response.find("emstatus").text=='SUCCESS':
		return response.find("emguid").text
	else:
		log.warning("UMS Sending Failed %s (%s)" , response.find("emstatus").text, response.find("emstatuscodes").text)
		raise UMSEmailUploadException("UMS Sending Failed %s (%s)" % (response.find("emstatus").text, response.find("emstatuscodes").text))
	
	
def send(sndr_data, rcpt_data, template_data):
	templ_name = template_data['t_name']
	subject = email[templ_name]['subject']
	try:
		template = tmpl_lookup.get_template('email/%s.txt' % templ_name.lower())
	except mako.exceptions.TopLevelLookupException, e:
		log.warning( "ERROR Template not Found for (%s)" , ('email/%s.txt' % templ_name.lower()) )
		raise MissingTemplateException(e)
	else:
		return send_email(subject, template, sndr_data, rcpt_data, template_data)