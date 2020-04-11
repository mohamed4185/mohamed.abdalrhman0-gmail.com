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


class Discount_lis(models.Model):
    _name='sales.discount'
    name=fields.Char('Name')
    discount_1=fields.Integer('Discout 1')
    discount_2=fields.Integer('Discount 2')
    discount_3=fields.Integer('Discount 3')