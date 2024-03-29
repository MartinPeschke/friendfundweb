import logging
import socket
import datetime

import simplejson
from pylons import request, response, session as websession, tmpl_context as c, app_globals
from pylons.decorators import jsonify
from pylons.templating import render_mako_def as render_def, render_mako as render
from pylons.i18n import ugettext as _

from friendfund.lib import helpers as h
from friendfund.lib.auth.decorators import logged_in, pool_available
from friendfund.lib.base import BaseController
from friendfund.model.pool import Pool, UpdatePoolProc, OccasionSearch
from friendfund.model.product import Product
from friendfund.tasks.celerytasks.photo_renderer import UnsupportedFileFormat
from friendfund.services.product_service import QueryMalformedException
from friendfund.lib.routes_middleware import abort

log = logging.getLogger(__name__)


class ProductController(BaseController):
    @jsonify
    def open_bounce(self):
        c.upload = bool(request.params.get("upload", False))
        try:
            query, product, img_list = app_globals.product_service.set_product_from_open_web(request.params.get('query'))
        except QueryMalformedException, e:
            log.warning(e)
            return {'success':False}
        except socket.timeout, e:
            return {'success':False}
        else:
            if img_list is None:
                return {'success':False}
            c.parser_values = {'url':query,
                               'display_url':h.word_truncate_by_letters(query, 40),
                               'name':product.name,
                               'display_name':h.word_truncate_by_letters(product.name, 40),
                               'description':product.description,
                               'display_description': h.word_truncate_by_letters(product.description, 180),
                               'img_list':img_list}
            html = render_def("/product/urlparser.html", "renderParser", values = c.parser_values, with_closer = True).strip()
        return {'success':True, 'html':html}

    def bouncev2(self):
        return self.bounce()

    def bounce(self):
        query=request.params.get("referer")
        c.product_list = app_globals.product_service.get_products_from_url(query)
        c.product = c.product_list[0]

        c.method = c.user.get_current_network() or 'facebook'
        c.olist = app_globals.dbm.get(OccasionSearch, date = h.format_date_internal(datetime.date.today()), country = websession['region']).occasions

        c.values = {"occasion_name":c.olist[0].get_display_name()}
        c.errors = {}
        return self.render('/partner/iframe.html')

    def picturepopup(self, pool_url):
        c.pool = app_globals.dbm.get(Pool, p_url = pool_url)
        if not c.pool:
            return abort(404)
        elif not c.pool.am_i_admin(c.user):
            response.headers['Content-Type'] = 'application/json'
            return simplejson.dumps({'message':'Not authorized!'})

        pool_picture = request.params.get('pool_picture')
        if pool_picture is None:
            response.headers['Content-Type'] = 'application/json'
            return simplejson.dumps({'popup':render('/product/picturepopup.html').strip()})
        try:
            picture_url = app_globals.pool_service.save_pool_picture(pool_picture)
            updater = UpdatePoolProc(p_url = c.pool.p_url)
            updater.product = c.pool.product or Product()
            updater.product.picture = picture_url
            app_globals.dbm.set(updater)
            app_globals.dbm.expire(Pool(p_url = c.pool.p_url))
            c.pool = updater
        except Exception, e:
            log.error(e)
            return '<html><body><textarea>{"message":%s}</textarea></body></html>' % _("FF_PICTUREUPLOAD_Some Error occured, please try again")
        return '<html><body><textarea>{"reload":true}</textarea></body></html>'

    def ulpicture(self):
        c.pool_picture = request.params.get('pool_picture')
        if c.pool_picture is None:
            response.headers['Content-Type'] = 'application/json'
            return simplejson.dumps({'popup':render('/product/ulpicture_popup.html').strip()})
        try:
            picture_url = app_globals.pool_service.save_pool_picture_sync(c.pool_picture, type="TMP")
        except UnsupportedFileFormat, e:
            result = {"data":{"success":False}}
        else:
            result = {"data":{"success":True, "rendered_picture_url":app_globals.statics_service.get_product_picture(picture_url, type="TMP")}}
        result = '<html><body><textarea>%s</textarea></body></html>'%simplejson.dumps(result)
        return result

    @logged_in()
    @pool_available(admin_only=True)
    def ulpoolpicture(self, pool_url):
        c.pool_picture = request.params.get('pool_picture')
        if c.pool_picture is None:
            response.headers['Content-Type'] = 'application/json'
            if c.pool.product:
                c.pool_picture = c.pool.product.picture
            return simplejson.dumps({'popup':render('/product/ulpicture_popup.html').strip()})
        try:
            picture_url = app_globals.pool_service.save_pool_picture_sync(c.pool_picture, type="TMP")
        except UnsupportedFileFormat, e:
            result = {"data":{"success":False}}
        else:
            result = {"data":{"success":True, "rendered_picture_url":app_globals.statics_service.get_product_picture(picture_url, type="TMP")}}
        result = '<html><body><textarea>%s</textarea></body></html>'%simplejson.dumps(result)
        return result
