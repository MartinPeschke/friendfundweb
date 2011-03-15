import logging, formencodefrom pylons import request, app_globals as gfrom friendfund.lib.base import BaseController, render, _from friendfund.model.contribution import AsyncDBPaymentInitializationpaymentlog = logging.getLogger('payment.service')log = logging.getLogger(__name__)from friendfund.services.pool_service import MissingPermissionsExceptionclass PaymentServiceController(BaseController):	def service(self):		"""basic auth: adyen/4epayeguka7ew43frEst5b4u"""		if request.method != 'POST':			return ['rejected']				params = request.POST		strbool = formencode.validators.StringBoolean(if_missing=False)		if str(params['eventCode']) in ['AUTHORISATION', 'REFUND', 'CANCELLATION', 'CAPTURE', 'CHARGEBACK', 'CHARGEBACK_REVERSED', 'CANCEL_OR_REFUND']:			paymentlog.info( '-'*40 )			paymentlog.info( 'headers=%s', request.headers )			paymentlog.info( 'post_params=%s', request.params )			paymentlog.info( '-'*40 )		else:			paymentlog.info( '-'*40 )			paymentlog.warning( request.headers )			paymentlog.warning( request.params )			paymentlog.info( '-'*40 )			return '[accepted]'		if str(params['eventCode']) in ['AUTHORISATION']:			transl = {  'merchantReference':'ref'\						,'pspReference':'tx_id'\						,'eventCode':'type'\						,'success':'success'					}		else:			transl = {  'merchantReference':'ref'\						,'originalReference':'tx_id'\						,'pspReference':'msg_id'\						,'eventCode':'type'\						,'success':'success'					}		noticeparams = dict([k for k in filter(lambda x: x[1], [(transl[k],v) for k,v in params.iteritems() if k in transl])])		noticeparams['success'] = strbool.to_python(noticeparams.get('success', False))		try:			notice = AsyncDBPaymentInitialization(**noticeparams)			g.dbm.set(notice)		except SProcException, e:			paymentlog.error(e)		except Exception, e:			paymentlog.error(e)		finally:			paymentlog.info( '-'*40 )			return '[accepted]'