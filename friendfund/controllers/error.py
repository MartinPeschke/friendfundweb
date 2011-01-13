import cgi

from paste.urlparser import PkgResourcesParser
from webhelpers.html.builder import literal

from pylons import config
from friendfund.lib.base import BaseController

errorf = open(config['error_template'], 'rb')
error_document = errorf.read()
errorf.close()
errorf = open(config['error_template_404'], 'rb')
error_document_404 = errorf.read()
errorf.close()
import logging
log = logging.getLogger(__name__)

class ErrorController(BaseController):
	"""Generates error documents as and when they are required.

	The ErrorDocuments middleware forwards to ErrorController when error
	related status codes are returned from the application.

	This behaviour can be altered by changing the parameters to the
	ErrorDocuments middleware in your config/middleware.py file.

	"""
	def __before__(self, action, environ):
		pass
	def __after__(self, action, environ):
		pass
	def document(self):
		"""Render the error document"""
		request = self._py_object.request
		resp = request.environ.get('pylons.original_response')
		content = literal(resp.body) or cgi.escape(request.GET.get('message', ''))
		if resp.status_int == 404:
			log.error("PAGE_NOT_FOUND:%s", getattr( request.environ.get('pylons.original_request'), 'path_qs', '[N/A]' ) )
			page = error_document_404 % \
				dict(prefix=request.environ.get('SCRIPT_NAME', ''),
					 code=cgi.escape(request.GET.get('code', str(resp.status_int))),
					 message=content)
		else:
			page = error_document % \
				dict(prefix=request.environ.get('SCRIPT_NAME', ''),
					 code=cgi.escape(request.GET.get('code', str(resp.status_int))),
					 message=content)
		return page
