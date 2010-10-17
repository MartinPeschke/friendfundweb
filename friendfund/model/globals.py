from friendfund.model.mapper import DBMappedObject, GenericAttrib, DBMapper, DBMapping

class DBCountry(DBMappedObject):
	"""
	<RESULT status="0" proc_name="get_country">
		<COUNTRY c_name="AFGHANISTAN" c_two_letter_name="AF" />
		<COUNTRY c_name="ALBANIA" c_two_letter_name="AL" />
		<COUNTRY c_name="ALGERIA" c_two_letter_name="DZ" />
	""" 
	_cachable = True
	_expiretime = 86400
	_get_root = 'COUNTRY'
	_unique_keys = ['iso2', 'name']
	_keys = [	 GenericAttrib(str ,'iso2'   ,'c_two_letter_name')
				,GenericAttrib(str ,'name','c_name')
			]

class GetCountryProc(DBMappedObject):
	"""
	<RESULT status="0" proc_name="get_country">
		<COUNTRY c_name="AFGHANISTAN" c_two_letter_name="AF" />
		<COUNTRY c_name="ALBANIA" c_two_letter_name="AL" />
		<COUNTRY c_name="ALGERIA" c_two_letter_name="DZ" />
	"""
	_cachable = True
	_expiretime = 86400
	_no_params = True
	_get_root = None
	_get_proc = _set_proc = 'app.get_country'
	_keys = [	 DBMapper(DBCountry ,'countries', 'COUNTRY', is_list = True)
			]
	def fromDB(self, xml):
		self.countries = [c.name for c in self.countries]