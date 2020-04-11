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


class ReportProductSale(models.AbstractModel):
    _name = "report.customer_cheques.customer_cheques_report"

    @api.model
    def _get_report_values(self, docids, data=None):
        date_from = data["form"]["date_from"]
        date_to = data["form"]["date_to"]
        customer = data["form"]["customer"]
        state = data["form"]["state"]

        total_sale = 0.0
        period_value = ""
        domain = []
        if date_from:
            domain.append(("check_payment", ">=", date_from))
        if date_to:
            domain.append(("check_payment", "<=", date_to))
        if customer:
            domain.append(("investor_id", "=", customer))
        if state:
            domain.append(("state", "=", state))

        list = []
        order_line = []
        cheques = self.env["check.management"].search(domain, order="check_date asc")
        state_value=''
        user_log=self.env['res.users'].search([('id','=',self.env.uid)])
        for line in cheques:
            if line.investor_id.customer==True:
                if user_log.lang=='en_US':
                    state_value=line.state
                elif user_log.lang=='ar_SY' or user_log.lang=='ar_AA':
                    if line.state=='holding':
                        state_value='الخزنه'
                    elif line.state=='depoisted':
                        state_value='تحت التحصيل'
                    elif line.state=='approved':
                        state_value='معتـــــمدة'
                    elif line.state=='rejected':
                        state_value='المرفـــوضه'
                    elif line.state=='returned':
                        state_value='المرتجعه'
                    elif line.state=='handed':
                        state_value='الصـــادره'
                    elif line.state=='debited':
                        state_value='المــدينــه'
                    elif line.state=='canceled':
                        state_value=line.state
                    elif line.state=='cs_return':
                        state_value='المرتـــجعه للعميل'
                    
                list.append(
                    {
                        "cheque_number": line.check_number,
                        "cheque_date": line.check_date,
                        "check_payment": line.check_payment,
                        "partner": line.investor_id.name,
                        "state": state_value,
                        "check_bank": line.check_bank.name,
                        "dept_bank":line.dep_bank.name,
                        "total": line.amount,
                        "reff_number":self.env['native.payments.check.create'].search([('id','=',line.check_id)]).nom_pay_id.reff_number,
                        "Analytic_Account":self.env['native.payments.check.create'].search([('id','=',line.check_id)]).nom_pay_id.analyitc_id.name,
                        "safe_number":self.env['native.payments.check.create'].search([('id','=',line.check_id)]).nom_pay_id.safe_number,
                        "sales_rep":self.env['native.payments.check.create'].search([('id','=',line.check_id)]).nom_pay_id.sales_rep.name,
               
                    }
            )

        if len(cheques) != 0:
            return {
                "doc_ids": data["ids"],
                "doc_model": data["model"],
                "period": period_value,
                "date_from": date_from,
                "date_to": date_to,
                "cheques": list,
                "total_sale": total_sale,
                "state": state,
                "customer_name": self.env["res.partner"].search([("id", "=",customer)]).name,
                "data_check": False,
                "name_report":'بيــان بشيــكات عميـــل'
            }
        else:
            return {
                "doc_ids": data["ids"],
                "doc_model": data["model"],
                "period": period_value,
                "date_from": date_from,
                "date_to": date_to,
                "cheques": list,
                "total_sale": total_sale,
                "state": state,
                "customer_name": self.env["res.partner"].search([("id", "=", customer)]).name,
                "data_check": True,
                "name_report":'بيــان بشيــكات عميـــل'
            }

