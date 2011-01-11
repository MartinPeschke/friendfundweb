from friendfund.model.mapper import DBMappedObject, GenericAttrib, DBMapper


def SSPUserRole(DBMappedObject):
	_set_root = _get_root = "ROLE"
	_unique_keys = ['name']
	_cachable = False
	_keys = [GenericAttrib(unicode,'name','name')]



class SSPUserLogin(DBMappedObject):
	_set_root = _get_root = "USER"
	_get_proc = _set_proc = "ssp.web_login"
	_unique_keys = ['email', 'name']
	_cachable = False
	_keys = [	 GenericAttrib(unicode,'email','email')
				,GenericAttrib(str,'password','password')
				,GenericAttrib(int,'merchant_id','merchant_id')
				,GenericAttrib(unicode,'role','role')
			]
	def am_i_admin(action):
		return True
	@classmethod
	def login(email, password):
		user = SSPUserLogin(email = email, password = password)
		return user

class SSPOrderOverview(DBMappedObject):
	_set_root = _get_root = "ORDER"
	_unique_keys = ['p_url', 'expiry_date']
	_cachable = False
	_keys = [	 GenericAttrib(unicode,'p_url','p_url')
				,GenericAttrib(unicode,'admin_name','admin_name')
				,GenericAttrib(unicode,'admin_image','admin_image')
				,GenericAttrib(unicode,'product_name','product_name')
				,GenericAttrib(unicode,'product_name','product_name')
				,GenericAttrib(unicode,'product_image','product_image')
				,GenericAttrib(unicode,'product_image','product_image')
				,GenericAttrib(int,'product_amount','product_amount')
				,GenericAttrib(int,'product_shipping_amount','product_shipping_amount')
				,GenericAttrib(int,'pool_amount','pool_amount')
				,GenericAttrib(unicode,'voucher_code','voucher_code')
				,GenericAttrib(unicode,'merchant_order_ref','merchant_order_ref')
			]
class GetSSPOrderOverview(DBMappedObject):
	_set_root = _get_root = "ORDERS"
	_get_proc = _set_proc = "ssp.get_current_orders"
	_unique_keys = ['merchant_id']
	_cachable = False
	_keys = [	 GenericAttrib(unicode,'merchant_id','merchant_id')
				,DBMapper(SSPOrderOverview, 'orders', 'ORDERS', is_list = True)
			]

class SSPOrderComplete(DBMappedObject):
	_set_root = _get_root = "ORDER"
	_get_proc = _set_proc = "ssp.set_order_complete"
	_unique_keys = ['p_url']
	_cachable = False
	_keys = [	 GenericAttrib(unicode,'merchant_id','merchant_id')
				,GenericAttrib(unicode,'p_url','p_url')
				,GenericAttrib(unicode,'voucher_code','voucher_code')
				,GenericAttrib(unicode,'merchant_order_ref','merchant_order_ref')
			]
