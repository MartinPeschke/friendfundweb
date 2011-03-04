from friendfund.model.mapper import DBMappedObject, GenericAttrib, DBMapper

class PaymentMethod(DBMappedObject):
	pass
	
class CreditCard(PaymentMethod):
	_keys = [	 GenericAttrib(int, 'ccType'        ,None)
				,GenericAttrib(str, 'ccHolder'      ,None)
				,GenericAttrib(bool,'ccNumber'      ,None)
				,GenericAttrib(str, 'ccCode'        ,None)
				,GenericAttrib(int, 'ccExpiresMonth',None)
				,GenericAttrib(int, 'ccExpiresYear' ,None)
			]

class Contribution(DBMappedObject):
	_keys = [	 GenericAttrib(int,      'amount'            ,None)
				,GenericAttrib(int,      'total'             ,None)
				,GenericAttrib(bool,     'agreedToS'         ,None)
				,GenericAttrib(bool,     'is_secret'         ,None)
				,GenericAttrib(unicode,  'message'           ,None)
				,GenericAttrib(str,      'paymentmethod_code',None)
				,DBMapper(PaymentMethod, 'methoddetails'     ,None)
				,GenericAttrib(str,      'currency'          ,None)
				,GenericAttrib(str,      'ref'               ,None)
				,GenericAttrib(int,      'user_id'           ,None)
				,GenericAttrib(bool,     'is_valid'          ,None)
			]
	def get_amount(self):
		return float(self.amount)/100
	def set_amount(self, value):
		self.amount = int(value*100)
	def get_total(self):
		return float(self.total)/100
	def set_total(self, value):
		self.total = int(value*100)
	def set_user(self, user):
		self.user_id = user.u_id
	def validate_user(self, user):
		return self.user_id == user.u_id
	def invalidate(self):
		self.is_valid = False
	def get_difference(self):
		return float(self.total - self.amount)/100
	def __repr__(self):
		return '<%s: %s>' % (self.__class__.__name__, ','.join(['%s:%s'%(k.pykey,getattr(self, k.pykey)) for k in self._keys[:3]]))

class DBContribution(DBMappedObject):
	_cachable = False
	_get_root = _set_root = 'CONTRIBUTION'
	_unique_keys = ['ref']
	_set_proc   = 'app.create_contribution'
	_keys = [	 GenericAttrib(str ,'ref'   ,'contribution_ref')
				,GenericAttrib(int ,'amount','amount')
				,GenericAttrib(int ,'total','total')
				,GenericAttrib(bool,'is_secret','secret')
				,GenericAttrib(unicode, 'message'    ,'message')
				,GenericAttrib(str ,'p_url' ,'p_url')
				,GenericAttrib(int ,'u_id'  ,'u_id')
				,GenericAttrib(str ,'network'  ,'network')
				,GenericAttrib(str ,'network_id'  ,'id')
				
				,GenericAttrib(str, 'paymentmethod'    ,"payment_method")
				,GenericAttrib(str ,'shopper_email'  ,'shopper_email')
				
				,GenericAttrib(str ,'shopper_ref'  ,'shopper_ref', persistable = False)
				,GenericAttrib(bool,'is_recurring'  ,'is_recurring', persistable = False)
				,GenericAttrib(int ,'total','total', persistable = False)
			]

class DBPaymentInitialization(DBMappedObject):
	_cachable = False
	_get_root = _set_root = 'NOTICE'
	_unique_keys = ['ref']
	_set_proc   = 'app.add_contribution_notice'
	_keys = [	 GenericAttrib(str, 'ref'      ,'contribution_ref')
				,GenericAttrib(int, 'tx_id'    ,'transaction_id')
				,GenericAttrib(int, 'msg_id'   ,'message_id')
				,GenericAttrib(str, 'type'     ,'type')
				,GenericAttrib(str, 'reason'     ,'reason')
				,GenericAttrib(bool, 'success'  ,'success')
			]
class DBPaymentNotice(DBMappedObject):
	_cachable = False
	_get_root = _set_root = 'NOTICE'
	_unique_keys = ['msg_id', 'ref']
	_set_proc = 'app.add_contribution_notice'
	_keys = [	GenericAttrib(str, 'ref','contribution_ref')
				,GenericAttrib(int, 'tx_id'    ,'transaction_id')
				,GenericAttrib(int, 'msg_id'   ,'message_id')
				,GenericAttrib(str, 'type'     ,'type')
				,GenericAttrib(bool, 'success'  ,'success')
				,GenericAttrib(str, 'reason'   ,'reason')
			]
			
class GlobalDBPaymentNotice(DBMappedObject):
	_cachable = False
	_get_root = _set_root = 'NOTICE'
	_unique_keys = ['msg_id', 'ref']
	_set_proc = _get_proc = 'dbo.exec_contribution_notice_db'
	_keys = [	GenericAttrib(str,  'ref','contribution_ref')
				,GenericAttrib(int, 'tx_id'    ,'transaction_id')
				,GenericAttrib(int, 'msg_id'   ,'message_id')
				,GenericAttrib(str, 'type'     ,'type')
				,GenericAttrib(bool,'success'  ,'success')
				,GenericAttrib(str, 'reason'   ,'reason')
			]
	
class GetDetailsFromContributionRefProc(DBMappedObject):
	"""
		[app].[get_details_from_contribution_ref]
		<CONTRIBUTION  contribution_ref="30DBFB7B-4DD2-4C70-9470-FA4B0F5AF10F"/>
	"""
	_cachable = False
	_get_root = _set_root = 'CONTRIBUTION'
	_unique_keys = ['msg_id']
	_set_proc =_get_proc = 'app.get_details_from_contribution_ref'
	_keys = [	GenericAttrib(unicode, 'contribution_ref','contribution_ref')
				,GenericAttrib(int, 'amount'      ,'amount')
				,GenericAttrib(bool, 'is_secret'  ,'is_secret')
				,GenericAttrib(unicode, 'message' ,'message')]
	def get_amount(self):
		return float(self.amount)/100