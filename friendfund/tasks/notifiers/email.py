# -*- coding: utf-8 -*-
from string import Template as Template
import urllib2, os, logging, mako, markdown
from mako.lookup import TemplateLookup
from lxml import etree
from docutils.core import publish_parts
from datetime import datetime, date
from decimal import Decimal

from poster.encode import multipart_encode
from poster.streaminghttp import register_openers

from friendfund.lib import helpers as h
from friendfund.tasks import data_root
from friendfund.tasks.notifiers.common import MissingTemplateException
from friendfund.lib.helpers import format_int_amount

from babel.numbers import format_currency as fc, format_decimal as fdec, get_currency_symbol, get_decimal_symbol, get_group_symbol, parse_number as pn
from babel.dates import format_date as fdate, format_datetime as fdatetime

register_openers()

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tmpl_lookup = TemplateLookup(directories=[os.path.join(root, '..', 'templates_free_form','messaging')]
		, module_directory=os.path.join(data_root, 'templates_free_form','messaging')
		, output_encoding='utf-8'
		)
ums_url = "http://sysmail.fagms.net/c/sm"
ums_standard_params = {'AID':"27220", "ACTION":"SYSTEM"}

log = logging.getLogger(__name__)

class UMSEmailUploadException(Exception):pass



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
	

TRANSLATIONS = {"expiry_date": date, "target_amount":amount, "chip_in_amount":currency}

def localize(data_map):
	result = {}
	for key in data_map:
		if key in TRANSLATIONS:
			updates = TRANSLATIONS[key](key, data_map)
			result.update(updates)
		else:
			result[key] = data_map[key]
	return result


def send_email(template, sndr_data, rcpt_data, template_data):
	message_params = ums_standard_params.copy()
	message_params['email'] = rcpt_data['email']
	
	data = localize(template_data)
	
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
	
	
def send(file_no, sndr_data, rcpt_data, template_data, config):
	try:
		template = tmpl_lookup.get_template('email/msg_%s.txt' % file_no)
	except mako.exceptions.TopLevelLookupException, e:
		log.warning( "ERROR Template not Found for (%s)" , ('email/msg_%s.txt' % file_no) )
		# raise MissingTemplateException(e)
		return "0"
	else:
		return send_email(template, sndr_data, rcpt_data, template_data)