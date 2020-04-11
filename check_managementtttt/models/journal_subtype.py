from odoo import models, fields, api, _

class account_journal(models.Model):

    _inherit = 'account.journal'

    payment_subtype = fields.Selection([('issue_check',_('Issued Checks')),('rece_check',_('Received Checks'))],string="Payment Subtype")

