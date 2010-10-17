from friendfund.model.mapper import DBMappedObject, GenericAttrib, DBMapper, DBMapping
from friendfund.lib.tools import AutoVivification

class AffCategory(DBMappedObject):
	_expiretime = 10
	_get_root = _set_root = 'CATEGORY'
	_unique_keys = ['id', 'name']
	_keys = [GenericAttrib(int,'id','id'), GenericAttrib(unicode,'name','name')]
	
	def get_display_name(self):
		return self.name and self.name.replace('_', ' ').title() or ''
	

class AffProgram(DBMappedObject):
	"""
		<PROGRAM name="Conrad Electronic DE" aff_net_ref="258" shipping_days="5" shipping_days_offset_warning="5"/>
	"""
	_expiretime = 10
	_get_root = _set_root = 'PROGRAM'
	_unique_keys = ['id']
	_keys = [GenericAttrib(str,'id','aff_program_id')
			, GenericAttrib(unicode,'name','name')
			, GenericAttrib(str,'aff_net','aff_net')
			, GenericAttrib(int,'default_shippingdays','shipping_days')
			, GenericAttrib(int,'default_shippingdays_warnlimit','shipping_days_offset_warning')]


class AffiliateConfig(DBMappedObject):
	_expiretime = 10
	_get_root = None
	_set_root = 'PRODUCT_SEARCH'
	_unique_keys = ['country']
	_get_proc = 'imp.get_programs_and_categories'
	_keys = [ GenericAttrib(str, 'country', 'country')
			, DBMapper(AffCategory,'categories','CATEGORY', is_list = True)
			, DBMapper(AffProgram,'programs','PROGRAM', is_list = True)
			]
	def get_program_settings(self, id):
		return dict([(p.id, p) for p in self.programs]).get(id, None)
	
	def __init__(self, **kwargs):
		super(self.__class__, self).__init__(**kwargs)
		self._affprogdict = AutoVivification()
	
	def fromDB(self, xml):
		for p in self.programs:
			self._affprogdict[p.aff_net][p.id] ={ 'shippingdays':p.default_shippingdays, 'shippingdays_warn':p.default_shippingdays_warnlimit }
		self.categories = dict([(cat.id , cat) for cat in self.categories])
