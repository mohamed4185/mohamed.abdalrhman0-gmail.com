from odoo import api, models
from dateutil.relativedelta import relativedelta
import datetime
import logging
_logger = logging.getLogger(__name__)

class ReportPeriodicalSale(models.AbstractModel):
    _name="report.Customer_Annual_Sales_Report.report_sale_line_doc"
    @api.model
    def _get_report_values(self, docids, data=None):
        report_obj = self.env['ir.actions.report']
        report = report_obj._get_report_from_name('Customer_Annual_Sales_Report.report_sale_line_doc')
        model = self.env.context.get('active_model')
        docs = self.env['sale.order.line'].search([('id','in',docids)])
      
         

        docargs = {
            'doc_ids': docids,
            'doc_model': self.env.context.get('active_model'),
            'docs': docs,
             
        }
        return docargs