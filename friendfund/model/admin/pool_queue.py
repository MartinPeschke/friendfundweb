from friendfund.lib import helpers as h
from friendfund.model.mapper import DBMappedObject, GenericAttrib, DBMapper, DBMapping
from friendfund.model.poolsettings import ShippingAddress
from datetime import datetime, timedelta

class ClosedPoolResult(DBMappedObject):
	_cacheable = False
	_get_root = None
	_get_proc = _set_proc = 'adi.get_closed_pool'
	_no_params = True
	_keys = [GenericAttrib(str,'p_url','p_url')
			,GenericAttrib(datetime,'expiry_date','expiry_date')
			,GenericAttrib(unicode,'external_link','tracking_link')
			,DBMapper(ShippingAddress, 'address', 'ADDRESS')]


class GetClosedPoolProc(DBMappedObject):
	"""
		 exec adi.get_closed_pool;
		<RESULT status="0" proc_name="get_closed_pool"><POOL p_url="UC0xMTMyOQ~~" expiry_date="2010-09-12" tracking_link="http://www.amazon.com/gp/gc/ref=topnav_giftcert"><ADDRESS/></POOL></RESULT>
	"""
	_cacheable = False
	_get_root = None
	_get_proc = _set_proc = 'adi.get_closed_pool'
	_no_params = True
	_keys = [DBMapper(ClosedPoolResult,'pools','POOL', is_list = True)]

class SetPoolCompleteProc(DBMappedObject):
	"""
		exec [adi].[set_pool_complete]'<POOL p_url ="UC0xMTEzMw~~"/>' -- completes pool when order is made by purchasing person.
	"""
	_cacheable = False
	_get_root = _set_root = 'POOL'
	_get_proc = _set_proc = 'adi.set_pool_complete'
	_no_params = False
	_keys = [GenericAttrib(str,'p_url','p_url')]
