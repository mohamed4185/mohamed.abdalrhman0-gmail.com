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
    
class sale_custom(models.Model):
    _inherit="sale.order.line"
    note_sale=fields.Char('ملاحظات')

class purchase_custom(models.Model):
    _inherit="purchase.order.line"
    note_purchase=fields.Char('ملاحظات')

    