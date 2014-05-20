import logging

from routes.mapper import Mapper
from webob.exc import status_map


log = logging.getLogger('friendfund.lib.routes_middleware')

class VersionedMapper(Mapper):
    def generate(self, *args, **kargs):
        # environ = kargs.get('_environ', self.environ)
        # prefix = environ.get('HTTP_X_VERSION')
        # if prefix: path = '/%s%s' % (prefix, path)
        # if kargs.get("controller") == "content":
        # lang = environ.get("beaker.session", {}).get("lang")
        # if lang: path = str('/%s%s' % (lang, path))
        path = super(VersionedMapper, self).generate(*args, **kargs)
        return path

def abort(status_code=None, detail="", headers=None, comment=None):
    """Aborts the request immediately by returning an HTTP exception

    In the event that the status_code is a 300 series error, the detail
    attribute will be used as the Location header should one not be
    specified in the headers attribute.

    """
    exc = status_map[status_code](detail=detail, headers=headers,
                                  comment=comment)
    log.debug("Aborting request, status: %s, detail: %r, headers: %r, "
              "comment: %r", status_code, detail, headers, comment)
    raise exc

def redirect(url, code=302):
    """Raises a redirect exception to the specified URL

    Optionally, a code variable may be passed with the status code of
    the redirect, ie::

        redirect(url(controller='home', action='index'), code=303)

    """
    log.debug("Generating %s redirect" % code)
    exc = status_map[code]
    raise exc(location=url)
