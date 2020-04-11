# -*- coding: utf-8 -*-

import datetime



from odoo import tools
from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class receipt_cash_check(models.AbstractModel):
    _name = 'report.check_managementtttt.receipt_check_cash_payment'


    @api.model
    def _get_report_values(self, docids, data=None):
        _logger.info('docids')
        _logger.info(docids)

        report_obj = self.env['ir.actions.report']
        report = report_obj._get_report_from_name('check_managementtttt.receipt_check_cash_payment')
        docargs = {
            'doc_ids': docids,
            'doc_model': 'normal.payments',
            'docs': self.env['normal.payments'].browse(docids),
            #'payment_info':self._payment_info,
            #'convert':self._convert,
        }

        return docargs


