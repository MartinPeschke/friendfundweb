"""
FriendFund Product Crawler Service, the only commandline argument should be the paster config file.
i.e. invoke as: python friendfund/services/api_crawler_zanox.py -f development.ini -r de --forcedownload

-f (file): config file
-r ('uk'|'us'|'de') : one of ['uk', 'us', 'de']
-d : force download, rather than use existing files
"""
from __future__ import with_statement # for python 2.5

import sys, getopt, urllib, urllib2, os, logging, uuid, gzip, urlparse
from collections import deque
from datetime import datetime
from lxml import etree
from xml.sax.saxutils import quoteattr, escape

from friendfund.model import db_access
from friendfund.model.common import SProcException, SProcWarningMessage
from friendfund.tasks import get_db_pool, get_config, getRecDictKey, data_root, root

FORMAT = "%(asctime)-15s -8s %(message)s"
logging.basicConfig(filename=os.path.join(os.getcwd(), 'logs', 'product_import_%s.log' % datetime.today().strftime('%Y%m%d')),level=logging.INFO)

CONNECTION_NAME = 'crawler'
log = logging.getLogger('api_crawler')
DBPAGESIZE = 200000



class FilterRejectedPropertyException(Exception):
	pass
class XMLMissingPropertyException(Exception):
	pass
class MissingAffNetConfigParamException(Exception):
	pass

class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg

root_path =  os.path.join( data_root, 'product_streams')


standard_attr = lambda x: quoteattr(x)
standard_elem = lambda x: escape(x)
cat_normalizer = lambda x: quoteattr(str((int(x)/10000)*10000))
accept = lambda conf, x: True
reject = lambda x: True
lower_limit = lambda typ, limit: (lambda x: typ(x)>limit)

price_normalizer_en  = lambda x: quoteattr(str(int(float(x.replace(',',''))*100)))
price_limit_en = lower_limit(lambda x: float(x.replace(',','')), 10)

integerizer = lambda x: int(float(x.replace(',','')))*100
price_limit_dynamic = lambda conf, key, keytyp, typ, x: typ(x)>=keytyp(conf[key])

price_limit_dynamic_number = lambda conf, x: price_limit_dynamic(conf, 'price_limit', int, integerizer, x)


AFF_NET_TRANSLATOR = {'ZANOX':{
							'NAMESPACE' : 'http://zanox.com/productdata/exportservice/v1',
							'PRODUCT_TAG' : 'product',
							'pelems' : {
								 'DESCRIPTION' : ( True, ['t:description/text()', 't:longDescription/text()'], standard_elem, accept)
								,'DESCRIPTION_LONG' : ( True, ['t:longDescription/text()', 't:description/text()'], standard_elem, accept)
								,'MANUFACTURER' : ( False, ['t:manufacturer/text()'], standard_elem, accept)
								,'NAME' :( True, ['t:name/text()'], standard_elem, accept)
							},
							'pattr' : {
								 'tracking_link' :( True, ['t:deepLink/text()'], standard_attr, accept)
								,'shipping_detail' :( False, ['t:shippingHandling/text()'], standard_attr, accept)
								# ,'valid_from' :( False, ['t:validFrom/text()'], standard_attr, accept)
								# ,'valid_to' :( False, ['t:validTo/text()'], standard_attr, accept)
								,'aff_program_id' :( True, ['t:program/text()'], standard_attr, accept)
								,'aff_id' :( True, ['@zupid'], standard_attr, accept)
								,'currency' :( True, ['t:currencyCode/text()'], standard_attr, accept)
								,'picture_small' :( True, ['t:smallImage/text()', 't:mediumImage/text()', 't:largeImage/text()'], standard_attr, accept)
								,'picture_large' :( True, ['t:largeImage/text()', 't:mediumImage/text()', 't:smallImage/text()'], standard_attr, accept)
								,'category' :( True, ['t:zanoxCategoryIds/t:id/text()'], cat_normalizer, accept)
								# <zanoxCategoryIds><id>110103</id></zanoxCategoryIds>
								, 'amount' : (True, ['t:price/text()'], price_normalizer_en, price_limit_dynamic_number)
								, 'shipping_cost' : (False, ['t:shippingHandlingCost/text()'], price_normalizer_en, accept)
							}
							,'wanted_names' : [('t:program/text()', 'program'), ('t:number/text()', 'number'), ('t:name/text()', 'name')]
						},
						'AFFILIATE_WINDOW':{
							'NAMESPACE' : '',
							'PRODUCT_TAG' : 'prod',
							'pelems' : {
								 'DESCRIPTION' : ( True, ['text/desc/text()'], standard_elem, accept)
								,'DESCRIPTION_LONG' : ( True, ['text/desc/text()'], standard_elem, accept)
								,'MANUFACTURER' : ( False, ['brand/brandName/text()'], standard_elem, accept)
								,'NAME' :( True, ['text/name/text()'], standard_elem, accept)
							},
							'pattr' : {
								 'aff_id' :( True, ['@id'], standard_attr, accept)
								,'tracking_link' :( True, ['uri/awTrack/text()'], standard_attr, accept)
								#,'shipping_detail' :( False, ['shippingHandling/text()'], standard_attr, accept) # dont exist
								# ,'valid_from' :( False, ['valFrom/text()'], standard_attr, accept)
								# ,'valid_to' :( False, ['valTo/text()'], standard_attr, accept)
								,'currency' :( True, ['price/@curr'], standard_attr, accept)
								,'picture_small' :( True, ['uri/awThumb/text()', 'uri/awImage/text()'], standard_attr, accept)
								,'picture_large' :( True, ['uri/awImage/text()', 'uri/awThumb/text()'], standard_attr, accept)
								,'category' :( True, ['cat/awCatId/text()'], lambda x: quoteattr("170000"), accept)
								,'amount' : (True, ['price/buynow/text()', 'price/store/text()', 'price/rrp/text()'], price_normalizer_en, price_limit_dynamic_number)
								,'shipping_cost' : (False, ['price/delivery/text()'], price_normalizer_en, accept)
							},
							'wanted_names' : [('@id', 'affid'), ('pId/text()', 'number'), ('name/text()', 'name')]
						},
						'CJ':{
							'NAMESPACE' : '',
							'PRODUCT_TAG' : 'product',
							'pelems' : {
								 'DESCRIPTION' : ( True, ['description/text()','promotionaltext/text()'], standard_elem, accept)
								,'DESCRIPTION_LONG' : ( True, ['promotionaltext/text()','description/text()'], standard_elem, accept)
								,'MANUFACTURER' : ( False, ['manufacturer/text()'], standard_elem, accept)
								,'NAME' :( True, ['name/text()'], standard_elem, accept)
							},
							'pattr' : {
								 'aff_id' :( True, ['sku/text()'], standard_attr, accept)
								,'tracking_link' :( True, ['buyurl/text()'], standard_attr, accept)
								#,'shipping_detail' :( False, ['shippingHandling/text()'], standard_attr, accept) # dont exist
								# ,'valid_from' :( False, ['valFrom/text()'], standard_attr, accept)
								# ,'valid_to' :( False, ['valTo/text()'], standard_attr, accept)
								,'currency' :( True, ['currency/text()'], standard_attr, accept)
								,'picture_small' :( True, ['imageurl/text()'], standard_attr, accept)
								,'picture_large' :( True, ['imageurl/text()'], standard_attr, accept)
								,'category' :( True, ['advertisercategory/text()'], lambda x: quoteattr("170000"), accept)
								,'amount' : (True, ['price/text()', 'retailprice/text()', 'saleprice/text()'], price_normalizer_en, price_limit_dynamic_number)
								,'shipping_cost' : (False, ['standardshippingcost/text()'], price_normalizer_en, accept)
							},
							'wanted_names' : [('programname/text()', 'program'), ('sku/text()', 'number'), ('name/text()', 'name')]
						}
					}

additional_config_args=['aff_program_name', 'aff_program_logo_url', 'aff_program_delivery_time', 'aff_program_id']


def logentry(errors, elem, aff_net):
	wanted_names = AFF_NET_TRANSLATOR[aff_net]['wanted_names']
	wanted_elems = {}
	if AFF_NET_TRANSLATOR[aff_net]['NAMESPACE']:
		nss = {'namespaces':{'t':AFF_NET_TRANSLATOR[aff_net]['NAMESPACE']}}
	else:
		nss = {}
	
	for (xpath,name) in wanted_names:
		if nss:
			hit = elem.xpath(xpath, **nss)
		else:
			hit = elem.xpath(xpath)
		if len(hit) > 0:
			wanted_elems[name] = hit[0] or ''
		else:
			wanted_elems[name] = 'N/A'
	
	line = [aff_net] + [wanted_elems.get(name,'') for (k,name) in wanted_names]
	line.extend( [str(errors)] )
	return '%s%s' % ( ';'.join(line).encode('latin-1', 'replace'), os.linesep )

def convert_to_product_xml(product, aff_net, region, args):
	pattr = AFF_NET_TRANSLATOR[aff_net]['pattr']
	pelems = AFF_NET_TRANSLATOR[aff_net]['pelems']
	attribs = {}
	attribs['guid'] = quoteattr(str(uuid.uuid4()))
	attribs['aff_net'] = quoteattr(aff_net)
	elems = {}
	
	if AFF_NET_TRANSLATOR[aff_net]['NAMESPACE']:
		nss = {'namespaces':{'t':AFF_NET_TRANSLATOR[aff_net]['NAMESPACE']}}
	else:
		nss = {}
	errors = deque()
	for key, (required, xpath_exps, normalizer, acceptor) in pattr.iteritems():
		for xp in xpath_exps:
			if nss:
				hits = product.xpath(xp, **nss)
			else:
				hits = product.xpath(xp)
			
			if len(hits) > 0:
				if acceptor(args, hits[0]):
					attribs[key] = normalizer(hits[0])
				else:
					raise FilterRejectedPropertyException("%s Filter not met" % key)
				break
		if len(hits) == 0 and required:
			errors.append('|'.join(xpath_exps))
	
	for key, (required, xpath_exps, normalizer, acceptor) in pelems.iteritems():
		for xp in xpath_exps:
			if nss:
				hits = product.xpath(xp, **nss)
			else:
				hits = product.xpath(xp)
			if len(hits) > 0:
				if acceptor(args, hits[0]):
					elems[key] = normalizer(hits[0])
				else:
					raise FilterRejectedPropertyException("%s Filter not met" % key)
				break
		if len(hits) == 0 and required:
			errors.append('|'.join(xpath_exps))

	if errors:
		raise XMLMissingPropertyException(','.join(sorted(errors)))
	
	for k in additional_config_args:
		if k in args:
			attribs[k] = quoteattr(args[k])
		else:
			raise MissingAffNetConfigParamException(k)
	
	attribs = ' '.join(['%s=%s' % (k, attribs[k]) for k in attribs])
	elems = ''.join(['<%s>%s</%s>' % (k, elems[k], k) for k in sorted(elems)])
	root = '<PRODUCT xml:lang=%s %s>%s</PRODUCT>' % (quoteattr(region), attribs, elems)
	return root

def download_file(aff_net, aff_program_id, url, force_download, args):
	fname = '%s_%s_%s.xml.gz' % (datetime.today().strftime('%Y%m%d'), aff_net, aff_program_id)
	fname = os.path.join(root_path, fname)
	if os.path.exists(fname) and not force_download:
		return (fname, aff_net, args)
	elif os.path.exists(fname):
		os.remove(fname)
	log.info( "Retrieving: %s from %s", fname, url)
	fname, headers = urllib.urlretrieve(url, fname)
	return (fname, aff_net, args)

def get_download_files(dbpool, region, force_download):
		try:
			result, cur = db_access.execute_query(dbpool, log, 'exec imp.get_import_datafeed ?', "<IMPORT region=%s/>" % quoteattr(region))
			for row in result.iterchildren():
				if 'aff_http_user' in row.attrib and 'aff_http_pwd' in row.attrib:
					a,b,c,d,e,f = urlparse.urlparse(row.get('data_feed_url'))
					url = urlparse.urlunparse((a, "%s:%s@%s" % (row.get('aff_http_user'), row.get('aff_http_pwd'), b) , c, d, e, f))
				else:
					url = row.get('data_feed_url')
				yield download_file(row.get('aff_net'),  row.get('aff_program_id'), url, force_download, row.attrib)
		except:
			log.error('download_files failed, something didnt work out quite right')
			raise
		return



def persist(dbpool, region, product_list, fail_count):
	query = '<PRODUCTS region="%s">%s</PRODUCTS>' % (region, ''.join(product_list))
	log.info("trying to send %s products (%s bytes), %s products didnt make the cut", len(product_list), len(query), fail_count)
	db_access.execute_query(dbpool, log, 'exec imp.add_product_catalog ?', query)

def source(sources):
	for fname, aff_net, args in sources:
		log.info( 'opening xml file %s', fname )
		try:
			fin = gzip.open(fname, 'r')
			try:
				ant = AFF_NET_TRANSLATOR[aff_net]
				context = etree.iterparse(fin, tag='{%s}%s' % (ant['NAMESPACE'], ant['PRODUCT_TAG']), load_dtd=True, no_network = False)
				for i, (action, elem) in enumerate(context):
					yield aff_net, fname, action, elem, args
			finally:
				fin.close()
		except IOError, e:
			log.error('ERROR Reading gzipped Affiliate Source File: %s (%s)' % (str(e), fname))
			continue
		log.info( 'closing xml file %s', fname )
	return


def parse_n_persist(sources, region, dbpool, pagesize = DBPAGESIZE):
	product_total = 0
	product_list = deque()
	fail_count = {}
	fail_product_logging_fname = os.path.join(root_path, os.extsep.join([datetime.now().strftime('%Y-%m-%d'), 'fail', 'log']))
	log.info('fail logging to %s', fail_product_logging_fname)
	with open(fail_product_logging_fname, 'w') as logfout:
		tfname = ''
		prod_count = 0
		for aff_net, fname, action, elem, args in source(sources):
			try:
				product_list.append(convert_to_product_xml(elem, aff_net, region, args))
				product_total += 1
			except XMLMissingPropertyException, e:
				logfout.write(logentry(e, elem, aff_net))
				fail_count[str(e)] = fail_count.get(str(e), 0) + 1
			except FilterRejectedPropertyException, e:
				logfout.write(logentry(e, elem, aff_net))
				fail_count[str(e)] = fail_count.get(str(e), 0) + 1
			if (product_total > 0 and not product_total%pagesize):
				persist(dbpool, region, product_list, fail_count)
				product_list.clear()
				fail_count = {}
			if tfname != fname: 
				log.info( "Program Product Imported for %s: %s (total fails sofar: %s)", tfname, prod_count, fail_count )
				prod_count = 0
			tfname = fname
			prod_count += 1
			elem.clear()
			while elem.getprevious() is not None:
				del elem.getparent()[0]
		if product_list:
			persist( dbpool, region, product_list, fail_count)
	return product_total

def main(argv=None):
	if argv is None:
		argv = sys.argv
	try:
		opts, args = getopt.getopt(sys.argv[1:], "r:p:f:dh", ["help", "region", "file", "forcedownload", "programs"])
		opts = dict(opts)
		if '-f' not in opts:
			raise Usage("Missing Option -f")
		config = get_config(opts['-f'])
		if '-r' not in opts:
			raise Usage("Missing Option -r")
		region = opts.get('-r', None)
		if region not in config['crawler.supported_regions'].split(','):
			raise Usage("Region '%s' not Supported, supported are: %s" % (region, config['crawler.supported_regions']))
	except getopt.error, msg:
		 raise Usage(msg)
	except Usage, err:
		print >>sys.stderr, err.msg
		print >>sys.stderr, "for help use --help"
		return 2
	dbpool = get_db_pool(config, CONNECTION_NAME)
	
	if not os.path.exists(root_path):
		os.makedirs(root_path)
	dls = get_download_files(dbpool, region, ('-d' in opts or '--forcedownload' in opts))
	result, cur = db_access.execute_query(dbpool, log, 'exec imp.truncat ?', '<TRUNCAT region=%s />' % quoteattr(region))
	
	accepted_products = parse_n_persist(dls, region, dbpool)
	if accepted_products:
		result, cur = db_access.execute_query(dbpool, log, 'exec imp.switchcat ?', '<SWITCHCAT region=%s />' % quoteattr(region))

if __name__ == "__main__":
    sys.exit(main())
