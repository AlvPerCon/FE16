# -*- coding: utf-8 -*-
from odoo import http, SUPERUSER_ID
import re
from odoo.tools import consteq, plaintext2html
from odoo.addons.portal.controllers.mail import _check_special_access, PortalChatter
from odoo.http import request
import logging
_logging = logging.getLogger(__name__)

class SolsePortalChatter(PortalChatter):

	@http.route(['/mail/chatter_post'], type='json', methods=['POST'], auth='public', website=True)
	def portal_chatter_post(self, res_model, res_id, message, **kw):
		result = super(SolsePortalChatter, self).portal_chatter_post(res_model, res_id, message, **kw)
		record = request.env[res_model].browse(res_id)
		record.sudo().leer_archivos()
		return result