################################################################################ -*- coding: utf-8 -*-

###############################################################################
#
#    Periodical Sales Report
#
#    Copyright (C) 2019 Aminia Technology
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from odoo import api, models
from dateutil.relativedelta import relativedelta
import datetime
import logging
_logger = logging.getLogger(__name__)

class ReportPeriodicalSale(models.AbstractModel):
    _name = 'report.total_size_sales.report_total_size_sales'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        customer=data['form']['customer'] 
        total_sale = 0.0
        period_value = ''
        domain=[]
         
        if date_from  :
            domain.append(('date_order', '>=', date_from))
        if  date_to:
            domain.append(('date_order', '<=', date_to))
        if customer:
            domain.append(('partner_id','=',customer))


         
        sale_orders = []
        order_line=[]
        orders = self.env['sale.order'].search(domain)
        
        
        for rec in orders:
            total_sale=0
            count_invoice=0
            quantity=0
            total_price=0
            
            if rec.state=='sale' or rec.state == "done":
                count_invoice=len(rec.invoice_ids)
                _logger.info(rec.name)
                _logger.info(count_invoice)
                for line in rec.order_line:
                    quantity=quantity+line.product_uom_qty
                    total_price=total_price+line.price_total
                 
                sale_orders.append({
                    'name': rec.name,
                    'partner' : rec.partner_id.name,
                    'quantity':quantity,
                    'count_invoice':count_invoice,
                  
                    'total':total_price,   
                    })       
        _logger.info(sale_orders)
        if len(sale_orders)!=0:
            return {
                    'doc_ids': data['ids'],
                    'doc_model': data['model'],
                    'period' : period_value,
                    'date_from': date_from,
                    'date_to': date_to,
                    'sale_orders' : sale_orders,
                    'total_sale' : total_sale,
                    'customer_name':self.env['res.partner'].search([('id','=',customer)]).name,
                    'data_check':False,
                    'name_report':"بيان بحجم المبيعات خلال فتره علي مستوي العملاء"

                }
        else:
            return {
                    'doc_ids': data['ids'],
                    'doc_model': data['model'],
                    'period' : period_value,
                    'date_from': date_from,
                    'date_to': date_to,
                    'sale_orders' : sale_orders,
                    'total_sale' : total_sale,
                    'customer_name':self.env['res.partner'].search([('id','=',customer)]).name,
                    'data_check':True,
                    'name_report':"بيان بحجم المبيعات خلال فتره علي مستوي العملاء"
                }
        # return {
        #     'doc_ids': data['ids'],
        #     'doc_model': data['model'],
        #     'period': period_value,
        #     'date_from': date_from,
        #     'date_to': date_to,
        #     'sale_orders': sale_orders,
        #     'total_sale': total_sale,
        #     'data_check': False
        # }



        



