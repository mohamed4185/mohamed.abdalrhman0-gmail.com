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


class ReportProductmove(models.AbstractModel):
    _name = "report.move_product_in_to_out.report_move_in_out_product"

    @api.model
    def _get_report_values(self, docids, data=None):
        date_from = data["form"]["date_from"]
        date_to = data["form"]["date_to"]
        pro = data["form"]["product"]
        vendor = data["form"]["vendor"]
        customer = data["form"]["customer"]

        total_sale = 0.0
        period_value = ""
        domain = []
        domain_purchase = []
        if date_from and date_to:
            domain = [("date_order", ">=", date_from), ("date_order", "<=", date_to)]
            domain_purchase = [
                ("date_order", ">=", date_from),
                ("date_order", "<=", date_to),
            ]
        elif date_from:
            domain = [("date_order", ">=", date_from)]
            domain_purchase = [("date_order", ">=", date_from)]
        elif date_to:
            domain = [("date_order", ">=", date_to)]
            domain_purchase = [("date_order", ">=", date_to)]

        if vendor:
            domain_purchase.append(("partner_id", "=", vendor))
        if customer:
            domain.append(("partner_id", "=", customer))

        sale_orders = []
        purchase_orders = []
        order_line = []
        purchases = self.env["purchase.order"].search(domain_purchase)

        for rec in purchases:
            total_sale = 0
            count_invoice = 0

            if rec.state == "purchase" or rec.state == "done":
                count_invoice = len(rec.invoice_ids)
                for order in rec.order_line:
                    _logger.info(type(order.product_id.id))
                    _logger.info(pro)

                    if pro:
                        if pro == order.product_id.id:
                            purchase_orders.append(
                                {
                                    "name": rec.name,
                                    "product_id": order.product_id.name,
                                    "date_one": rec.date_order,
                                    "partner": order.order_id.partner_id.name,
                                    "amount_total": order.price_total,
                                    "order_id": order.order_id.name,
                                    "quantity": order.product_qty,
                                    "price_unit": order.price_unit,
                                    "count_invoice": count_invoice,
                                    "total": order.price_total,
                                    "pro_id": order.product_id,
                                    "category": order.product_id.categ_id,
                                    "id": order.product_id.id,
                                }
                            )
                    else:
                        purchase_orders.append(
                            {
                                "name": rec.name,
                                "product_id": order.product_id.name,
                                "date_one": rec.date_order,
                                "partner": order.order_id.partner_id.name,
                                "amount_total": order.price_total,
                                "order_id": order.order_id.name,
                                "quantity": order.product_qty,
                                "price_unit": order.price_unit,
                                "count_invoice": count_invoice,
                                "total": order.price_total,
                                "pro_id": order.product_id,
                                "category": order.product_id.categ_id,
                                "id": order.product_id.id,
                            }
                        )

        orders = self.env["sale.order"].search(domain)

        for rec in orders:
            total_sale = 0
            count_invoice = 0
            if rec.state == "sale" or rec.state == "done":
                # if   rec.picking_ids.date_done:
                count_invoice = len(rec.invoice_ids)
                for order in rec.order_line:
                    _logger.info(type(order.product_id.id))
                    _logger.info(pro)

                    if pro:
                        if pro == order.product_id.id:
                            sale_orders.append(
                                {
                                    "name": rec.name,
                                    "product_id": order.product_id.name,
                                    "date_one": rec.date_order,
                                    "partner": order.order_id.partner_id.name,
                                    "amount_total": order.price_total,
                                    "order_id": order.order_id.name,
                                    "quantity": order.product_uom_qty,
                                    "price_unit": order.price_unit,
                                    "count_invoice": count_invoice,
                                    "total": order.price_total,
                                    "pro_id": order.product_id,
                                    "category": order.product_id.categ_id,
                                    "id": order.product_id.id,
                                }
                            )
                    else:
                        sale_orders.append(
                            {
                                "name": rec.name,
                                "product_id": order.product_id.name,
                                "date_one": rec.date_order,
                                "partner": order.order_id.partner_id.name,
                                "amount_total": order.price_total,
                                "order_id": order.order_id.name,
                                "quantity": order.product_uom_qty,
                                "price_unit": order.price_unit,
                                "count_invoice": count_invoice,
                                "total": order.price_total,
                                "pro_id": order.product_id,
                                "category": order.product_id.categ_id,
                                "id": order.product_id.id,
                            }
                        )
        if len(purchase_orders) != 0:
            return {
                "doc_ids": data["ids"],
                "doc_model": data["model"],
                "period": period_value,
                "date_from": date_from,
                "date_to": date_to,
                "purchase_orders": purchase_orders,
                "sale_orders": sale_orders,
                "total_sale": total_sale,
                "customer_name": self.env["res.partner"].search([("id", "=", customer)]).name,
                "vendor_name": self.env["res.partner"].search([("id", "=", vendor)]).name,
                "product_name": self.env["product.product"].search([("id", "=", pro)]).name,
                "data_check": False,
                'name_report':'بيان حركه صنف لمورد مقابل العملاء'
            }
        else:
            return {
                "doc_ids": data["ids"],
                "doc_model": data["model"],
                "period": period_value,
                "date_from": date_from,
                "date_to": date_to,
                "purchase_orders": purchase_orders,
                "sale_orders": sale_orders,
                "total_sale": total_sale,
                "customer_name": self.env["res.partner"].search([("id", "=", customer)]).name,
                "vendor_name": self.env["res.partner"].search([("id", "=", vendor)]).name,
                "product_name": self.env["product.product"].search([("id", "=", pro)]).name,
                "data_check": True,
                'name_report':'بيان حركه صنف لمورد مقابل العملاء'
            }

