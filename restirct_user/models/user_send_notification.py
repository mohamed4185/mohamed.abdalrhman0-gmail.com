from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError,UserError
import logging
import datetime as dt
from datetime import datetime, timedelta
import calendar
import re
_logger = logging.getLogger(__name__)


class sale_vs_forecast(models.Model):
    _inherit="res.users"
    @api.constrains("groups_id")
    def send_notifation(self):
         
        group_id=self.env['ir.model.data'].search([('name','=','group_system')])
        group_user_broker = self.env['res.groups'].search([('id','=',group_id.res_id)]) 
        users=self.env['res.users'].search([('groups_id','=',group_user_broker.id)])
        _logger.info("USERS")
        _logger.info(users)
        
        template = False
         
        user_login=self.env['res.users'].search([('id','=',self.env.uid)])
        mail_mail_obj = self.env['mail.mail']

        _logger.info("MAIL")
        for line in users:

            values = {
                'email_from':user_login.login,
                'email_to': line.login,
                'email_cc': False,
                'auto_delete': True,
                'partner_to': False,
                'scheduled_date': False,
                'subject':'Create New User',
                'body_html':'Dear Admin \n Add new User \n Email'+self.login
            }
            _logger.info(values)
            msg_id = mail_mail_obj.create(values)
            _logger.info(msg_id)
            if msg_id:
               mail_mail_obj.send(msg_id)
        for user in users:
            if not user.email:
                raise UserError(_("Cannot send email: user %s has no email address.") % user.name)
            

