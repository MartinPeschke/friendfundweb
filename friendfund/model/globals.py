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
			
		fallbacks = filter(lambda x: x.is_default, self.countries)
		if len(fallbacks) > 0:
			setattr(self, 'fallback', fallbacks[0])
		else:
			raise Exception("GetCountryRegionProc: No Fallback Country provided")

class MerchantSettings(DBMappedObject):
	_get_root = _set_root = 'SETTINGS'
	_cachable = False
	_unique_keys = ['key', 'value']
	_keys = [GenericAttrib(unicode,'key','key'),GenericAttrib(unicode,'value','value')]


class MerchantLink(DBMappedObject):
	_get_root = _set_root = 'MERCHANT'
	_cachable = False
	_unique_keys = ['name', 'domain']
	_keys = [GenericAttrib(unicode,'name','name'),GenericAttrib(str,'domain','merchant_domain'),GenericAttrib(bool,'is_default','is_default')
				, DBMapper(MerchantSettings,'settings','SETTINGS', is_dict = True, dict_key = lambda x:x.key.lower())]
	
	def get_setting(self, key):
		return getattr(self.settings.get(key), 'value', False)

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
			log.error("No Default Merchant set, %s", e)
			raise Exception("No Default Merchant set, %s" % e)