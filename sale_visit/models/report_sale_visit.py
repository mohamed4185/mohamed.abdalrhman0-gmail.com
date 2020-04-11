from odoo import api, models
import logging 
from datetime import datetime, timedelta,date
import datetime as dt
import calendar
_logger = logging.getLogger(__name__)
class ParticularReport(models.AbstractModel):
    _name = 'report.sale_visit.sales_visit_printing'
    @api.model
    def _get_report_values(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('sale_visit.sales_visit_printing')
        _logger.info('dsfsdfsdfsd')
        docs = self.env['sale.visit'].searvh[('id','=',1)]
        _logger.info(docids)
        docargs = {
            'doc_ids': docids,
            'doc_model': 'sale.visit',
            'docs': docs,
            'Day':data['form']['date_from']
        }
        return docargs

     