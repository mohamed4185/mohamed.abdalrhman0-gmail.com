from odoo import api ,models, fields
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError,UserError
import logging 
from datetime import datetime, timedelta,date
import datetime as dt
import calendar
_logger = logging.getLogger(__name__)
class objective_visit(models.Model):
    _name = 'objective.visit'
    name=fields.Char('Name')
    