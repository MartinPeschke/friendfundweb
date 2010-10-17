"""
<RESULT status="0" proc_name="get_unsent_messages">
	<MESSAGE message_ref="F8511FB6-DB53-43FD-864F-805EF0A47134" template="PASSWORD_RESET" notification_method="EMAIL" email="martin@per-4.com" network="EMAIL">
		<PARAMETER key="activation_token" value="b25df4ff-d447-4c61-a77a-75a141289538"/><PARAMETER key="name" value="martin@per-4.com"/>
	</MESSAGE>
</RESULT>
"""
import urllib2, os, logging, mako
from mako.template import Template
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
		'INVITE': {'subject':"Invitation"},
		'INVITE_WITH_ACCOUNT_ACTIVATION' : {'subject':"Invitation"},
		'PASSWORD_RESET': {'subject':"Reset Password"},
		'ADMIN_EMAIL_ACCOUNT_VALIDATION': {'subject':"Account Validation"},
		'ADMIN_FUNDING_REMINDER': {'subject':"Funding Reminder"},
		'CONTRIBUTION_RECEIPT': {'subject':"Contribution Received"},
		
		'REMIND_INVITEES': {'subject':"Please help out"},
		'ASK_RECEIVER': {'subject':"Please help out for the awesome gift we are getting you"},
		'ASK_CONTRIBUTORS': {'subject':"Please help out just the little bit more"},
		'ASK_CONTRIBUTORS_TO_INVITE': {'subject':"Please help out and invite more friends"},
		
		'ECARD_PROMPT': {'subject':"Send an eCard"},
		'EMAIL_ECARD_RECEIVER': {'subject':"Happy %(occasion)s"},
		'PHOTO_UPLOAD_ECARD_RECEIVER': {'subject':"Say Thank You"}
	}

class UMSEmailUploadException(Exception):pass

def send_email(subject, template, sndr_data, rcpt_data, template_data):
	message_params = ums_standard_params.copy()
	message_params['email'] = rcpt_data['email']
	message_params['subject'] = subject % template_data
	message_params['text'] = template.render_unicode(**{'h':h, 'data': template_data}) #'h':h, when locale is available
	message_params['html'] = publish_parts(message_params['text'], writer_name="html")["html_body"]
	print message_params
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