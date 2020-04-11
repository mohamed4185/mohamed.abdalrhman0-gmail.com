from odoo import api ,models, fields
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError,UserError
import logging 
from datetime import datetime, timedelta,date
import datetime as dt
import calendar
_logger = logging.getLogger(__name__)
class journal(models.Model):
    _inherit='res.users'
    journal=fields.Many2many('account.journal','journal_account_user','id','journal')
    @api.onchange('journal')
    def get_changes(self):
        self.env['ir.cron'].clear_caches() 
