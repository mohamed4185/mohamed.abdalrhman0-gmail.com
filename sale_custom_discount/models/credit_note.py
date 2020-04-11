from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError,UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import datetime as dt
from datetime import datetime, timedelta
import calendar
import time
import re
from odoo.addons import decimal_precision as dp
from dateutil import relativedelta
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)



class CreditNote(models.TransientModel):
    _inherit='account.invoice.refund'
    @api.multi
    def compute_refund(self, mode='refund'):
        inv_obj = self.env['account.invoice']
        inv_tax_obj = self.env['account.invoice.tax']
        inv_line_obj = self.env['account.invoice.line']
        context = dict(self._context or {})
        xml_id = False

        for form in self:
            created_inv = []
            date = False
            description = False
            _logger.info("Ffffffffffffffffffffffffffff")
            _logger.info(inv_obj.browse(context.get('active_ids')).global_discount)
            for inv in inv_obj.browse(context.get('active_ids')):
                _logger.info("Ffffffffffffffffffffffffffff")
                _logger.info(inv.precentge_value)
                _logger.info(inv.amount_value)
                _logger.info(inv.global_discount)

                if inv.state in ['draft', 'cancel']:
                    raise UserError(_('Cannot create credit note for the draft/cancelled invoice.'))
                if inv.reconciled and mode in ('cancel', 'modify'):
                    raise UserError(_('Cannot create a credit note for the invoice which is already reconciled, invoice should be unreconciled first, then only you can add credit note for this invoice.'))

                date = form.date or False
                description = form.description or inv.name
                refund = inv.refund(form.date_invoice, date, description, inv.journal_id.id)

                created_inv.append(refund.id)
                
                precentge_value=inv.precentge_value
                amount_value=inv.amount_value
                global_discount=inv.global_discount
                discount_type=inv.discount_type
                if mode in ('cancel', 'modify'):
                    movelines = inv.move_id.line_ids
                    to_reconcile_ids = {}
                    to_reconcile_lines = self.env['account.move.line']
                    for line in movelines:
                        if line.account_id.id == inv.account_id.id:
                            to_reconcile_lines += line
                            to_reconcile_ids.setdefault(line.account_id.id, []).append(line.id)
                        if line.reconciled:
                            line.remove_move_reconcile()
                    refund.action_invoice_open()
                    for tmpline in refund.move_id.line_ids:
                        if tmpline.account_id.id == inv.account_id.id:
                            to_reconcile_lines += tmpline
                    to_reconcile_lines.filtered(lambda l: l.reconciled == False).reconcile()
                    if mode == 'modify':
                        _logger.info("modify")
                        invoice = inv.read(inv_obj._get_refund_modify_read_fields())
                        invoice = invoice[0]
                        del invoice['id']
                        invoice_lines = inv_line_obj.browse(invoice['invoice_line_ids'])
                        invoice_lines = inv_obj.with_context(mode='modify')._refund_cleanup_lines(invoice_lines)
                        tax_lines = inv_tax_obj.browse(invoice['tax_line_ids'])
                        tax_lines = inv_obj._refund_cleanup_lines(tax_lines)
                        _logger.info("CREDIT NOTE")
                        
                        invoice.update({
                            'type': inv.type,
                            'date_invoice': form.date_invoice,
                            'state': 'draft',
                            'number': False,
                            'invoice_line_ids': invoice_lines,
                            'tax_line_ids': tax_lines,
                            'date': date,
                            'origin': inv.origin,
                            'fiscal_position_id': inv.fiscal_position_id.id,
                            'precentge_value':inv.precentge_value,
                            'amount_value':inv.amount_value,
                            'global_discount':inv.global_discount,
                            'discount_type':inv.discount_type

                        })
                        for field in inv_obj._get_refund_common_fields():
                            if inv_obj._fields[field].type == 'many2one':
                                invoice[field] = invoice[field] and invoice[field][0]
                            else:
                                invoice[field] = invoice[field] or False
                        _logger.info("INVOICE EEEE")
                        _logger.info(invoice)
                        inv_refund = inv_obj.create(invoice)
                        body = _('Correction of <a href=# data-oe-model=account.invoice data-oe-id=%d>%s</a><br>Reason: %s') % (inv.id, inv.number, description)
                        inv_refund.message_post(body=body)
                        if inv_refund.payment_term_id.id:
                            inv_refund._onchange_payment_term_date_invoice()
                        created_inv.append(inv_refund.id)
                xml_id = inv.type == 'out_invoice' and 'action_invoice_out_refund' or \
                         inv.type == 'out_refund' and 'action_invoice_tree1' or \
                         inv.type == 'in_invoice' and 'action_invoice_in_refund' or \
                         inv.type == 'in_refund' and 'action_invoice_tree2'
        if xml_id:
            _logger.info("xml_id")
            result = self.env.ref('account.%s' % (xml_id)).read()[0]
            if mode == 'modify':
                _logger.info("XML MODIFY")
                # When refund method is `modify` then it will directly open the new draft bill/invoice in form view
                if inv_refund.type == 'in_invoice':
                    view_ref = self.env.ref('account.invoice_supplier_form')
                else:
                    view_ref = self.env.ref('account.invoice_form')
                result['views'] = [(view_ref.id, 'form')]
                result['res_id'] = inv_refund.id
                _logger.info(result['views'])
                _logger.info(result['res_id'])
            else:
                _logger.info("ELSE")
                invoice_domain = safe_eval(result['domain'])
                invoice_domain.append(('id', 'in', created_inv))
                result['domain'] = invoice_domain
                _logger.info(result)
                _logger.info(created_inv)
                obj_invoice=self.env['account.invoice'].search([('id','=',created_inv[0])])
                obj_invoice.update({'precentge_value':precentge_value,
                            'amount_value':amount_value,
                            'global_discount':global_discount,
                            'discount_type':discount_type})
            return result
        return True