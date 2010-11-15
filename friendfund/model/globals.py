from pylons.i18n import _

from friendfund.lib.tools import AutoVivification
from friendfund.model.mapper import DBMappedObject, GenericAttrib, DBMapper, DBMapping

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
				,GenericAttrib(bool ,'is_fall_back','is_fall_back')
			]
	def fromDB(self, xml):
		self.code = self.code.lower()
		self.region = self.region.lower()
class GetCountryRegionProc(DBMappedObject):
	_cachable = False
	_no_params = True
	_get_root = None
	_get_proc = _set_proc = 'imp.get_country_region'
	_keys = [	 DBMapper(CountryRegion ,'countries', 'COUNTRY', is_list = True) ]
	
	def get_region_name(self, key):
		return _(self.map.get(key, self.fallback).name)
	
	def fromDB(self, xml):
		setattr(self, 'map', {})
		setattr(self, 'r2c_map', {})
		for country in self.countries:
			self.r2c_map[country.region] = self.r2c_map.get(country.region, []) + [country.code]
			self.map[country.code] = country
			
		fallbacks = filter(lambda x: x.is_fall_back, self.countries)
		if len(fallbacks) > 0:
			setattr(self, 'fallback', fallbacks[0])
		else:
			raise Exception("GetCountryRegionProc: No Fallback Country provided")

class AffProgram(DBMappedObject):
	"""
		<PROGRAM name="Conrad Electronic DE" aff_net_ref="258" shipping_days="5" shipping_days_offset_warning="5"/>
	"""
	_get_root = _set_root = 'PROGRAM'
	_cachable = False
	_unique_keys = ['id']
	_keys = [GenericAttrib(str,'id','aff_program_id')
			, GenericAttrib(unicode,'name','name')
			, GenericAttrib(str,'aff_net','aff_net')
			, GenericAttrib(int,'default_shippingdays','shipping_days')
			, GenericAttrib(int,'default_shippingdays_warnlimit','shipping_days_offset_warning')]
class GetAffiliateProgramsProc(DBMappedObject):
	_cachable = False
	_set_root = 'PRODUCT_SEARCH'
	_unique_keys = ['country']
	_get_proc = 'imp.get_affiliate_program'
	_keys = [ GenericAttrib(str, 'country', 'country')
			, DBMapper(AffProgram,'programs','PROGRAM', is_list = True)
			]
	def get_program_settings(self, id):
		return dict([(p.id, p) for p in self.programs]).get(id, None)
	def __init__(self, **kwargs):
		super(self.__class__, self).__init__(**kwargs)
		self.map = AutoVivification()
	def fromDB(self, xml):
		for p in self.programs:
			self.map[p.aff_net][p.id] ={ 'shippingdays':p.default_shippingdays, 'shippingdays_warn':p.default_shippingdays_warnlimit }


class PersonalityCategory(DBMappedObject):
	_get_root = _set_root = 'CATEGORY'
	_cachable = False
	_unique_keys = ['name']
	_keys = [GenericAttrib(unicode,'name','name'),GenericAttrib(unicode,'picture_url','picture_url')]
class GetPersonalityCategoryProc(DBMappedObject):
	_cachable = False
	_no_params = True
	_set_root = _get_root = None
	_unique_keys = []
	_get_proc = 'imp.get_categories'
	_keys = [DBMapper(PersonalityCategory,'list','CATEGORY', is_list = True)]
