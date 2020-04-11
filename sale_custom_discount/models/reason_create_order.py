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
import logging
_logger = logging.getLogger(__name__)
from odoo.tools import email_re, email_split, email_escape_char, float_is_zero, float_compare, \
    pycompat, date_utils
    



class cancel_order(models.Model):
    _name="sale.order.cancelled"
    reason=fields.Selection([('A','A'),('B','B')],'Reason',required=True)
    comment_cancel=fields.Char('Comment')
    cancelled_order=fields.Many2one('sale.order')
    @api.constrains('reason','comment_cancel')
    def get_reaon(self):
        _logger.info('Reason')
        self.cancelled_order.reason=self.reason
        self.cancelled_order.comment_cancel=self.comment_cancel
        if self.reason:
            self.cancelled_order.write({'state': 'cancel'})
        _logger.info(self.cancelled_order)
        
    @api.model
    def create(self,vals):
        _logger.info('CREATE')
        _logger.info(self.reason)
        return super(cancel_order,self).create(vals)
    
