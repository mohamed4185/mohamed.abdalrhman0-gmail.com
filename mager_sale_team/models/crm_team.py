# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)


class Crm_Team(models.Model):
    _inherit = 'crm.team'
     
    @api.onchange('member_ids')
    def get_member(self):
        _logger.info('ffffffffffffffff')
        self.env['ir.cron'].clear_caches()

