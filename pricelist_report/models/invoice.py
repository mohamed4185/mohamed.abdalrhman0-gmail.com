from odoo import models, fields, api
from odoo.exceptions import ValidationError
from num2words import num2words


class invoices(models.Model):
    _inherit = 'account.invoice'

    residual_to_text = fields.Char(compute='_amount_in_words', string='In Words', help="The amount in words")
    amount_to_text = fields.Char(compute='_amount_in_words', string='amount In Words', help="The amount in words")
    # total_inv_payment = fields.float('total payments')
    @api.one
    @api.depends('residual','amount_total')
    def _amount_in_words(self):
        # for line in self.payment_ids:
        #     total_inv_payment = total_inv_payment+line.amount
  

        self.residual_to_text = num2words(round(self.residual,2), lang='ar')
        self.amount_to_text = num2words(round(self.amount_total,2), lang='ar')
