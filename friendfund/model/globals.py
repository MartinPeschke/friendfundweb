import logging, formencode
from pylons.i18n import _

from friendfund.lib.tools import AutoVivification
from friendfund.model.mapper import DBMappedObject, GenericAttrib, DBMapper, DBMapping
from friendfund.model.product import DisplayProduct

log = logging.getLogger(__name__)

class DBCountry(DBMappedObject):
	_cachable = False
	_get_root = 'COUNTRY'
	_unique_keys = ['iso2', 'name']
	_keys = [	 GenericAttrib(str ,'iso2'   ,'c_two_letter_name')
				,GenericAttrib(str ,'name','c_name')
			]
class GetCountryProc(DBMappedObject):
	_cachable = False
	_no_params = True
	_get_root = None
	_get_proc = _set_proc = 'app.get_country'
	_keys = [
				DBMapper(DBCountry ,'list', 'COUNTRY', is_list = True)
			]
	def fromDB(self, xml):
		self.list = [c.name for c in self.list]

class CountryRegion(DBMappedObject):
	_cachable = False
	_get_root = 'COUNTRY'
	_unique_keys = ['code', 'name', 'region']
	_keys = [	 GenericAttrib(str ,'code'   ,'code')
				,GenericAttrib(str ,'name','name')
				,GenericAttrib(str ,'region','region')
				,GenericAttrib(str ,'currency','currency')
				,GenericAttrib(bool ,'is_default','is_default')  # should be aptly named is_default
			]
	def fromDB(self, xml):
		self.code = self.code.lower()
		self.region = self.region.lower()
	
class GetCountryRegionProc(DBMappedObject):
	_cachable = False
	_no_params = True
	_get_root = None
	_get_proc = _set_proc = 'app.get_country_region'
	_keys = [	 DBMapper(CountryRegion ,'countries', 'COUNTRY', is_list = True) ]
	
	def get_region_name(self, key):
		return _(self.map.get(key, self.fallback).name)
	
	def fromDB(self, xml):
		setattr(self, 'map', {})
		setattr(self, 'r2c_map', {})
		setattr(self, 'currencies', set())
		for country in self.countries:
			self.r2c_map[country.region] = self.r2c_map.get(country.region, []) + [country.code]
			self.map[country.code] = country
			self.currencies.add(country.currency)
		try:
			setattr(self, 'fallback', filter(lambda x: x.is_default, self.countries)[0])
		except IndexError, e:
			raise Exception("GetCountryRegionProc: No Fallback Country provided, %s", e)

class FormField(object):
	def __init__(self, name, type):
		self.name = name
		if type == "email":
			self.validator = formencode.validators.Email(not_empty=True, min=5, max = 255, resolve_domain=True)
			self.persistence_attribute = "paypal_email"
		else:
			self.validator = formencode.validators.String(max=140, not_empty=True)
			self.persistence_attribute = None

class PaymentMethod(DBMappedObject):
	"""
		<PAYMENT_METHOD name="PAYPAL" absolute_fee="35" relative_fee="35"/>
		<PAYMENT_METHOD name="VISA" absolute_fee="10" relative_fee="10"/>
		<PAYMENT_METHOD name="MASTER_CARD" absolute_fee="10" relative_fee="10"/>
		<PAYMENT_METHOD name="AMEX" absolute_fee="10" relative_fee="10"/>
	"""
	_get_root = _set_root = 'PAYMENT_METHOD'
	_cachable = False
	_unique_keys = ['name', 'absolute_fee', 'relative_fee']
	_keys = [	 GenericAttrib(str,'name','name')
				,GenericAttrib(int,'absolute_fee','absolute_fee')
				,GenericAttrib(float,'relative_fee','relative_fee')
			]
	def fromDB(self, xml):
		self.name = self.name.lower()

class MerchantSettlement(DBMappedObject):
	_get_root = _set_root = 'SETTLEMENT'
	_cachable = False
	_unique_keys = ['name', 'fee']
	_keys = [	 GenericAttrib(unicode,'name','name')
				,GenericAttrib(float,'fee','fee')
				,DBMapper(None, "required_fields", None, is_list = True, persistable = None)
			]
	def is_valid(self, fields):
		for k in self.required_fields:
			if not k.validate(fields.get(k.name)): return False
		return True
	def fromDB(self, xml):
		if self.name=="PAYPAL_TRANSFER":
			self.required_fields.append(FormField("email", "email"))

class MerchantLink(DBMappedObject):
	_get_root = _set_root = 'MERCHANT'
	_cachable = False
	_unique_keys = ['name', 'domain']
	_keys = [	 GenericAttrib(unicode,'name','name')
				,GenericAttrib(str,'domain','merchant_domain')
				,GenericAttrib(str,'pool_type','pool_type', enumeration=set(['FREE_FORM', 'GROUP_GIFT']))
				,GenericAttrib(str,'entry_point','entry_point', enumeration=set(['LANDING_PAGE', 'IFRAME']))
				,GenericAttrib(bool,'is_default','is_default')
				,GenericAttrib(str,'logo_url','logo_url')
				,GenericAttrib(str,'home_page','home_page')
				,DBMapper(MerchantSettlement,'settlement_options','SETTLEMENT', is_list = True)
			]
	def get_logo_url(self, secured = False):
		host = self.domain
		if secured:
			protocol = "https://"
		else:
			protocol = "http://"
		return "%(protocol)s%(host)s/custom/imgs/logo.png" % locals()
		
		
	def fromDB(self, xml):
		setattr(self, 'type_is_free_form', self.pool_type=="FREE_FORM")
		setattr(self, 'type_is_group_gift', self.pool_type=="GROUP_GIFT")
		setattr(self, 'entry_is_landing_page', self.entry_point=="LANDING_PAGE")
		setattr(self, 'entry_is_iframe', self.entry_point=="IFRAME")
		setattr(self, "map", dict([(so.name,so) for so in self.settlement_options]))


class FeaturedPoolURL(DBMappedObject):
	_cachable = False
	_no_params = True
	_keys = [GenericAttrib(unicode,'p_url','p_url')]

class GetMerchantConfigProc(DBMappedObject):
	"""app.[get_merchant]"""
	_cachable = False
	_no_params = True
	_set_root = _get_root = None
	_unique_keys = []
	_get_proc = 'app.get_config'
	_keys = [
			DBMapper(PaymentMethod,'payment_methods','PAYMENT_METHOD', is_list = True),
			DBMapper(MerchantLink,'merchants_map','MERCHANT', is_dict = True, dict_key = lambda x:x.domain.lower()),
			DBMapper(FeaturedPoolURL,'featured_pools','FEATURED_POOL', is_list = True),
		]
	
	def fromDB(self, xml):
		setattr(self, 'domain_map', dict([(m.domain.lower(), m) for m in self.merchants_map.itervalues()]))
		try:
			setattr(self, 'default', filter(lambda m: m.is_default, self.merchants_map.itervalues())[0])
			setattr(self, 'default_domain', filter(lambda m: m.is_default, self.merchants_map.itervalues())[0].domain)
		except IndexError, e:
			raise Exception("GetMerchantLinksProc:No Default Merchant set, %s" % e)

class TopSellersRegion(DBMappedObject):
	_cachable = False
	_set_root = _get_root = None
	_unique_keys = ['name']
	_keys = [GenericAttrib(unicode,'name','name'),DBMapper(DisplayProduct,'list','PRODUCT', is_list = True)]

class GetTopSellersProc(DBMappedObject):
	_cachable = False
	_no_params = True
	_set_root = _get_root = None
	_unique_keys = []
	_get_proc = 'app.get_top_seller'
	_keys = [DBMapper(TopSellersRegion,'list','REGION', is_list = True)]
	def fromDB(self, xml):
		setattr(self, 'map', {})
		for region in self.list:
			self.map[region.name.lower()] = region.list
