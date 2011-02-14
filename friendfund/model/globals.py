import logging
from pylons.i18n import _

from friendfund.lib.tools import AutoVivification
from friendfund.model.mapper import DBMappedObject, GenericAttrib, DBMapper, DBMapping

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
	_keys = [	 DBMapper(DBCountry ,'list', 'COUNTRY', is_list = True)
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
		for country in self.countries:
			self.r2c_map[country.region] = self.r2c_map.get(country.region, []) + [country.code]
			self.map[country.code] = country
		try:
			setattr(self, 'fallback', filter(lambda x: x.is_default, self.countries)[0])
		except IndexError, e:
			raise Exception("GetCountryRegionProc: No Fallback Country provided, %s", e)

class MerchantLink(DBMappedObject):
	_get_root = _set_root = 'MERCHANT'
	_cachable = False
	_unique_keys = ['name', 'domain']
	_keys = [	GenericAttrib(unicode,'name','name')
				,GenericAttrib(str,'domain','merchant_domain')
				,GenericAttrib(str,'pool_type','pool_type', enumeration=set(['FREE_FORM', 'GROUP_GIFT']))
				,GenericAttrib(str,'entry_point','entry_point', enumeration=set(['LANDING_PAGE', 'IFRAME']))
				,GenericAttrib(bool,'is_default','is_default')
				,GenericAttrib(str,'logo_url','logo_url')
				,GenericAttrib(str,'home_page','home_page')
			]
	def fromDB(self, xml):
		setattr(self, 'type_is_free_form', self.pool_type=="FREE_FORM")
		setattr(self, 'type_is_group_gift', self.pool_type=="GROUP_GIFT")
		setattr(self, 'entry_is_landing_page', self.entry_point=="LANDING_PAGE")
		setattr(self, 'entry_is_iframe', self.entry_point=="IFRAME")
		

class GetMerchantLinksProc(DBMappedObject):
	"""app.[get_merchant]"""
	_cachable = False
	_no_params = True
	_set_root = _get_root = None
	_unique_keys = []
	_get_proc = 'app.get_merchant'
	_keys = [DBMapper(MerchantLink,'merchants_map','MERCHANT', is_dict = True, dict_key = lambda x:x.domain.lower())]
	
	def fromDB(self, xml):
		setattr(self, 'domain_map', dict([(m.domain.lower(), m) for m in self.merchants_map.itervalues()]))
		try:
			setattr(self, 'default', filter(lambda m: m.is_default, self.merchants_map.itervalues())[0])
			setattr(self, 'default_domain', filter(lambda m: m.is_default, self.merchants_map.itervalues())[0].domain)
		except IndexError, e:
			raise Exception("GetMerchantLinksProc:No Default Merchant set, %s" % e)