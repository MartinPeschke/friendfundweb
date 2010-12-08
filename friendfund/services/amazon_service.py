import hmac, binascii, urllib, urllib2, urlparse, re, uuid, logging
from datetime import datetime
from hashlib import sha256
from lxml import etree, html

from friendfund.model.product import Product
from friendfund.model.product_search import ProductSearch

class AttributeMissingInProductException(Exception): pass
class URLUnacceptableError(Exception): pass
class TooManyOffersError(Exception): pass
class NoOffersError(Exception): pass
class MoreThanOneProductFoundError(Exception): pass
class WrongRegionAmazonError(Exception): pass
class AmazonErrorsOccured(Exception): pass

log = logging.getLogger(__name__)

class AmazonService(object):
	"""
		This is shared between all threads, do not stick state in here!
	"""
	
	def __init__(self, base_url, affiliateid, key, secret, domain):
		self.affiliateid = affiliateid
		self.key = key
		self.hmac_256 = hmac.new(secret, digestmod=sha256)
		self.base_url = base_url
		self.base_protocol = "http"
		self.query_path = "/onca/xml"
		self.http_method = "GET"
		self.query_url = "%s://%s%s" % (self.base_protocol, self.base_url, self.query_path)
		self.api_version = "2010-09-01"
		self.result_namespace = "http://webservices.amazon.com/AWSECommerceService/%s" % self.api_version
		self.page_size = 6
		
		self.domain = domain
		self.url_product_identifer_prefixes = {
				"/dp/"			: re.compile("/dp/([0-9A-Z]{10})")
				,"/gp/product/"	: re.compile("/gp/product/([0-9A-Z]{10})")
			}
		
		self.query_nss = {"namespaces":{'t':self.result_namespace}}
		self.product_mapper = {}
		self.product_mapper['aff_id'] = 			(True,  str, ["t:ASIN/text()"])
		self.product_mapper['amount'] = 				(True,  int, ["t:Offers/t:Offer/t:OfferListing/t:Price/t:Amount/text()"])
		self.product_mapper['currency'] = 			(True,  str, ["t:Offers/t:Offer/t:OfferListing/t:Price/t:CurrencyCode/text()"])
		self.product_mapper['delivery_time'] = 		(False, unicode, ["t:Offers/t:Offer/t:OfferListing/t:Availability/text()"])
		self.product_mapper['name'] = 				(True,  unicode, ["t:ItemAttributes/t:Title/text()"])
		self.product_mapper['description'] = 		(False,  unicode, ["t:EditorialReviews/t:EditorialReview/t:Content/text()"])
		self.product_mapper['description_long'] = 	(False,  unicode, ["t:EditorialReviews/t:EditorialReview/t:Content/text()"])
		self.product_mapper['manufacturer'] = 		(False, unicode, ["t:ItemAttributes/t:Manufacturer/text()"])
		self.product_mapper['ean'] = 				(False, str, ["t:ItemAttributes/t:EAN/text()"])
		self.product_mapper['picture_small'] = 		(True, unicode, ["t:SmallImage/t:URL/text()", "t:ImageSets/t:ImageSet/t:SmallImage/t:URL/text()"])
		self.product_mapper['picture_large'] = 		(True, unicode, ["t:LargeImage/t:URL/text()", "t:ImageSets/t:ImageSet/t:LargeImage/t:URL/text()"])
		self.product_mapper['tracking_link'] = 		(True,  unicode, ["t:DetailPageURL/text()"])
	
	def get_sign_base(self, params):
		sign_query = '&'.join(['%s=%s' %(k,urllib.quote(v)) for k,v in sorted(params.items())])
		sign_base = '\n'.join([self.http_method, self.base_url, self.query_path, sign_query])
		return sign_base

	def get_signature(self, params):
		raw = self.get_sign_base(params)
		hashed = self.hmac_256.copy()
		hashed.update(raw)
		return  urllib.quote(binascii.b2a_base64(hashed.digest())[:-1], '~')
	
	def fetch_product(self, lookup_operation):
		#SearchIndex=Books&Power=subject:history%20and%20(spain%20or%20mexico)%20and%20not%20military%20and%20language:spanish
		query_base_params = {
			'Service':'AWSECommerceService'
			, 'Version':self.api_version
			, 'ResponseGroup':'Large,Images,Request,ItemAttributes,EditorialReview'
			, 'MerchantId':'Amazon'
			, 'Condition':'New'
			, 'IncludeReviewsSummary':"true"
			, 'AssociateTag':self.affiliateid
			, 'Timestamp': datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")
			, 'AWSAccessKeyId':self.key
		}
		query_base_params.update(lookup_operation)
		signature = self.get_signature(query_base_params)
		query_url = "%s?%s" % (self.query_url, urllib.urlencode(query_base_params))
		query_url += '&Signature=%s' % signature
		
		try:
			return urllib2.urlopen(query_url)
		except urllib2.HTTPError, e:
			log.error(e)
			raise e
	
	def parse_surrogate_description(self, xml):
		product_group = ','.join(xml.xpath("t:ItemAttributes/t:ProductGroup/text()", **self.query_nss)).lower()
		descr = xml.xpath("t:ItemAttributes/t:Title/text()", **self.query_nss)
		if product_group == 'book':
			descr.extend(xml.xpath("t:ItemAttributes/t:Author/text()", **self.query_nss))
		elif product_group == 'dvd':
			descr.extend(xml.xpath("t:ItemAttributes/t:Actor/text()", **self.query_nss))
		elif product_group == 'music':
			descr.extend(xml.xpath("t:ItemAttributes/t:Artist/text()", **self.query_nss))
		else:
			descr.extend(xml.xpath("t:ItemAttributes/t:Feature/text()", **self.query_nss))
		descr = '<p>%s</p>' % ('</p><p>'.join(descr))
		return descr
	
	def parse_result_xml(self, xml):
		context = etree.iterparse(xml, tag='{%s}Item' % self.result_namespace)
		products = []
		for i, (action, elem) in enumerate(context):
			product = Product()
			
			errors = elem.xpath("t:Errors/t:Error/t:Code/text()", **self.query_nss)
			if len(errors) > 1:
				log.debug( AmazonErrorsOccured("XML Contained Errors %s" % errors) )
				continue
			offers = elem.xpath("t:Offers/t:Offer", **self.query_nss)
			if len(offers) > 1:
				log.debug( TooManyOffersError("Too Many Offers Found") )
				continue
			elif len(offers) == 0:
				log.debug( "No Offers Found in Product: %s" % etree.tostring(elem) )
				continue
			for key,(required, normalizer, xmlqueries) in self.product_mapper.iteritems():
				value = None
				for query in xmlqueries:
					hits = elem.xpath(query, **self.query_nss)
					if len(hits) > 0:
						value = normalizer(hits[0])
						break
				if required and value is None:
					log.debug("Amazon Link could not be imported because of: %s " % key)
					# raise AttributeMissingInProductException(key)
					continue
				elif value is None:
					setattr(product, key, None)
				else:
					setattr(product, key, value)
			#set alternate product description, as no original was found
			if not product.description or not product.description_long:
				descr = self.parse_surrogate_description(elem)
				if not descr:
					log.debug( AttributeMissingInProductException("description") )
					continue
				product.description = descr
				product.description_long = descr
			#parse out any html tags
			product.description = html.fromstring(product.description).text_content() 
			product.description_long = html.fromstring(product.description_long).text_content()
			
			product.guid = 'AMAZON|%s' % product.aff_id
			product.aff_net = 'AMAZON'
			product.aff_program_id = '1'
			product.aff_program_name = 'AMAZON'
			product.is_amazon = True
			product.is_virtual = False
			product.category = -1
			product.delivery_time = 5
			product.aff_program_logo_url = '/static/imgs/merch/amazon.png'
			product.aff_program_delivery_time = 5
			products.append(product)
		return products
	
	def return_product_object(self, item_id):
		xml = self.fetch_product({'ItemId':item_id, 'Operation':'ItemLookup'})
		amazon_products = self.parse_result_xml(xml)
		product_search = ProductSearch(page_no=1, items=len(amazon_products), pages=1, page_size=self.page_size, categories = [])
		product_search.products = amazon_products
		return product_search
	
	def get_product_from_guid(self, guid):
		results = self.return_product_object(guid.split("|")[1])
		if len(results.products) != 1:
			raise MoreThanOneProductFoundError("too many, %s" % len(results.products))
		p = results.products[0]
		p.guid = str(uuid.uuid4())
		return p
	
	def get_product_from_url(self, url):
		scheme, netloc, path, query, fragment = urlparse.urlsplit(url)
		upip = self.url_product_identifer_prefixes
		matcher = filter(bool, map(lambda x: x in path and upip[x] or False, upip))
		if not matcher:
			raise URLUnacceptableError("Path does not contain any ASIN identifier %s: %s" % (self.url_product_identifer_prefixes, path))
		else:
			asin_suspect = matcher[0].search(path)
			if not asin_suspect or len(asin_suspect.groups()) != 1:
				raise URLUnacceptableError("Path did contain (%s) ASIN identifer but the actual ASIN was not found after it: %s" % (matcher[0].pattern, path))
			return self.return_product_object(asin_suspect.group(1))
	
	def get_products_from_search(self, searchquery):
		xml = self.fetch_product({'Keywords':searchquery, 'Operation':'ItemSearch', 'SearchIndex':'All'})
		amazon_products = self.parse_result_xml(xml)
		product_search = ProductSearch(page_no=1, items=len(amazon_products[:self.page_size]), pages=1, page_size=self.page_size, categories = [])
		product_search.products = amazon_products[:self.page_size]
		return product_search