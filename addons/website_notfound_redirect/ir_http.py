# -*- coding: utf-8 -*-
import logging
import urllib2

from openerp.http import request
from openerp.osv import orm

logger = logging.getLogger(__name__)


class ir_http(orm.AbstractModel):
    _inherit = 'ir.http'

    def _handle_exception(self, exception, code=500):
        code = getattr(exception, 'code', code)
        if code == 404:
            page = request.httprequest.path
            logger.info("Resolving 404 error code... %s" % (page))
            url_conf = request.registry['ir.config_parameter']
            url = url_conf.get_param(request.cr,
                                     request.uid,
                                     'website.notfound_redirect_url')
            url_request = "%s%s" % (url, page)
            if url:
                logger.info("Checking remote url: %s" % (url_request))
                try:
                    req = urllib2.Request(url_request)
                    request_old = urllib2.urlopen(req)
                except (urllib2.HTTPError, urllib2.URLError):
                    request_old = False
            else:
                logger.info("No url to redirect defined")
                return super(ir_http, self)._handle_exception(exception, code)

            if url and request_old:
                logger.info("Redirect to %s" % (url_request))
                return request.redirect(url_request, code=302)
            else:
                logger.info("URL remote not found: %s" % (url_request))
                return super(ir_http, self)._handle_exception(exception, code)

        return super(ir_http, self)._handle_exception(exception, code)
