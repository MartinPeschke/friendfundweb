from friendfund.model.mapper import DBMappedObject, GenericAttrib

class PoolAddress(DBMappedObject):
	"""
		[app].[get_shipping_address] '<POOL_ADDRESS p_url ="P3to.Alice-Mrongovius-Mother-s-Day-Airplane-Flying-Lessons-in-LA-CA" />' 
		<RESULT status="0" proc_name="get_shipping_address"> 
		  <POOL_ADDRESS line1="harry co friendfund" line2="117 landsberger" line3="" zipcode="90210" country_name="COUNTRY_GERMANY" /> 
		</RESULT>
	"""
	_cachable = False
	_get_root = _set_root = 'POOL_ADDRESS'
	_unique_keys = ['p_url']
	_set_proc   = 'app.set_shipping_address'
	_get_proc   = 'app.get_shipping_address'
	_keys = [	 GenericAttrib(str ,'p_url'     , 'p_url' )
				,GenericAttrib(unicode,'first_name'  ,'first_name'  )
				,GenericAttrib(unicode,'last_name'  ,'last_name'  )
				,GenericAttrib(unicode,'line1'  ,'line1'  )
				,GenericAttrib(unicode,'line2'  ,'line2'  )
				,GenericAttrib(unicode,'line3'  ,'line3'  )
				,GenericAttrib(unicode,'zipcode','zipcode')
				,GenericAttrib(unicode,'country','country')
				,GenericAttrib(unicode,'phone'  ,'phone'  )
				,GenericAttrib(unicode,'shipping_note'  ,'shipping_note')
			]