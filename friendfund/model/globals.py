import logging, formencode
from pylons.i18n import _

from friendfund.lib.tools import AutoVivification
from friendfund.model.mapper import DBMappedObject, GenericAttrib, DBMapper, DBMapping
from friendfund.model.product import DisplayProduct

log = logging.getLogger(__name__)

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
	def has_fee(self):
		return bool(self.fee)
	def fromDB(self, xml):
		if self.name=="PAYPAL_TRANSFER":
			self.required_fields.append(FormField("email", "email"))
			
class MerchantCountry(DBMappedObject):
	_get_root = _set_root = 'SHIPPING_COUNTRY'
	_cachable = False
	_unique_keys = ['iso2']
	_keys = [GenericAttrib(unicode,'iso2','country')]
class MerchantStyle(DBMappedObject):
	_get_root = _set_root = 'CSS_STYLE'
	_cachable = False
	_unique_keys = ['property', 'value']
	_keys = [GenericAttrib(unicode,'property','property')
			, GenericAttrib(unicode,'value','value')]
	
class MerchantLink(DBMappedObject):
	_get_root = _set_root = 'MERCHANT'
	_cachable = False
	_unique_keys = ['name', 'key', 'domain']
	_keys = [	 GenericAttrib(unicode,'name','merchant_name')
				,GenericAttrib(str,'domain','merchant_domain')
				,GenericAttrib(str,'key','merchant_key')
				,GenericAttrib(str,'pool_type','pool_type', enumeration=set(['FREE_FORM', 'GROUP_GIFT']))
				,GenericAttrib(str,'entry_point','entry_point', enumeration=set(['LANDING_PAGE', 'IFRAME']))
				,GenericAttrib(bool,'require_address','require_address')
				,GenericAttrib(bool,'is_default','is_default')
				,GenericAttrib(str,'logo_url','logo_url')
				,GenericAttrib(str,'home_page','home_page')
				,GenericAttrib(str,'default_product_url','default_product_url')
				,DBMapper(MerchantSettlement,'settlement_options','SETTLEMENT', is_list = True)
				,DBMapper(MerchantCountry,'shippping_countries','SHIPPING_COUNTRY', is_list = True)
				,DBMapper(MerchantStyle,'_styles','CSS_STYLE', is_list = True)
			]
	def get_logo_url(self, type = "lrg", secured = False):
		return self._statics.get_merchant_picture(self.logo_url, type, secured)
		
	def fromDB(self, xml):
		setattr(self, 'type_is_free_form', self.pool_type=="FREE_FORM")
		setattr(self, 'type_is_group_gift', self.pool_type=="GROUP_GIFT")
		setattr(self, 'entry_is_landing_page', self.entry_point=="LANDING_PAGE")
		setattr(self, 'entry_is_iframe', self.entry_point=="IFRAME")
		setattr(self, "map", dict([(so.name,so) for so in self.settlement_options]))
		if self.require_address and len(self.shippping_countries)==0:
			raise Exception("GET_CONFIG (%s): MERCHANT.require_address==True and NO_SHIPPING_COUNTRY provided" % self.domain)
		setattr(self, "styles", dict([(x.property, x.value) for x in self._styles]))
		
		
		
class FeaturedPoolURL(DBMappedObject):
	_cachable = False
	_no_params = True
	_keys = [GenericAttrib(unicode,'p_url','p_url')]
	
	
class MerchantHolder(object):
	def __init__(self, key_map, domain_map, default, default_domain):
		self.key_map = key_map
		self.domain_map = domain_map
		self.default = default
		self.default_domain = default_domain

class HomePageStats(DBMappedObject):
	"""<STATS funded_pools="156" contributions="336"/>"""
	_cachable = False
	_no_params = True
	_keys = [GenericAttrib(int,'funded_pools','funded_pools'), GenericAttrib(int,'contributions','contributions')]

class GetMerchantConfigProc(DBMappedObject):
	"""app.[get_merchant]"""
	_cachable = False
	_no_params = True
	_set_root = _get_root = None
	_unique_keys = []
	_get_proc = 'app.get_config'
	_keys = [
			DBMapper(PaymentMethod,'payment_methods','PAYMENT_METHOD', is_list = True),
			DBMapper(MerchantLink,'key_map','MERCHANT', is_dict = True, dict_key = lambda x:x.key),
			DBMapper(FeaturedPoolURL,'featured_pools','FEATURED_POOL', is_list = True),
			DBMapper(HomePageStats,'stats','STATS')
		]
	
	def fromDB(self, xml):
		domain_map = dict([(m.domain.lower(), m) for m in self.key_map.itervalues()])
		try:
			default = filter(lambda m: m.is_default, self.key_map.itervalues())[0]
			default_domain = default.domain
		except IndexError, e:
			raise Exception("GetMerchantLinksProc:No Default Merchant set, %s" % e)
		setattr(self, "merchants", MerchantHolder(self.key_map, domain_map, default, default_domain))

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
	
	
	
	
class CreateMerchantProc(DBMappedObject):
	_get_root = _set_root = 'MERCHANT'
	_get_proc = _set_proc = 'ssp.create_merchant'
	_cachable = False
	_unique_keys = []
	_keys = [	 GenericAttrib(unicode,'name','merchant_name')
				,GenericAttrib(bool,'require_address','require_address')
				,GenericAttrib(str,'home_page','home_page')
				,DBMapper(MerchantCountry,'shippping_countries','SHIPPING_COUNTRY', is_list = True)
			]