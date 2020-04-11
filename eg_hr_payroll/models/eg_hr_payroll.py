
# -*- coding: utf-8 -*-

##############################################################################
#
#
#    Copyright (C) 2018-TODAY .
#    Author: Eng.Ramadan Khalil (<rkhalil1990@gmail.com>)
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
##############################################################################



from odoo import models, fields, api
from odoo.addons import decimal_precision as dp
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from odoo import tools, _
import time
import babel
import logging


class Department(models.Model):
    _name = "hr.department"

    _inherit = "hr.department"

    name = fields.Char('Department Name', required=True, translate=True)


class Employee(models.Model):
    _name = "hr.employee"
    _inherit = "hr.employee"


    religion = fields.Selection([('mus', 'Muslem'), ('chris', 'Christian'), ('other', 'Others')], string="Religion")
    military_status = fields.Selection(
        [('not_req', 'Not Required'), ('post', 'Postponed'), ('complete', 'complete'), ('exemption', 'Exemption'),
         ('current', 'Currently serving ')], string="Military Status")
    age = fields.Integer(string="Age", compute="_calculate_age", readonly=True)
    start_date = fields.Date(string="Start Working At")
    edu_phase = fields.Many2one(comodel_name="hr.eg.education", string="Education")
    edu_school = fields.Many2one(comodel_name="hr.eg.school", string="School/University/Institute")
    edu_major = fields.Char(string="major")
    edu_grad = fields.Selection([('ex', 'Excellent'), ('vgod', 'Very Good'), ('god', 'Good'), ('pas', 'Pass')],
                                string="Grad")
    edu_note = fields.Text("Education Notes")
    experience_y = fields.Integer(compute="_calculate_experience", string="Experience",
                                  help="experience in our company", store=True)
    experience_m = fields.Integer(compute="_calculate_experience", string="Experience monthes", store=True)
    experience_d = fields.Integer(compute="_calculate_experience", string="Experience dayes", store=True)

    @api.depends("birthday")
    def _calculate_age(self):
        for emp in self.search([]):
            if emp.birthday:
                dob = emp.birthday
                print('birth day is',dob)
                emp.age = int((datetime.today().date() - dob).days / 365)

    @api.depends("start_date")
    def _calculate_experience(self):
        for emp in self.search([]):
            if emp.start_date:
                date_format = '%Y-%m-%d'
                current_date = (datetime.today()).strftime(date_format)
                d1 = emp.start_date
                d2 = datetime.strptime(current_date, date_format).date()
                r = relativedelta(d2, d1)
                emp.experience_y = r.years
                emp.experience_m = r.months
                emp.experience_d = r.days








    @api.model
    def _cron_employee_age(self):
        self._calculate_age()

    @api.model
    def _cron_employee_exp(self):
        self._calculate_experience()





class hr_education(models.Model):
    _name = "hr.eg.education"

    name = fields.Char(string="Education", translate=True)
    note = fields.Char(string="Note", required=False, )


class hr_eg_school(models.Model):
    _name = "hr.eg.school"

    name = fields.Char(string="School name", translate=True)
    note = fields.Char(string="Note", required=False, )


class HrSalaryRuleCategory(models.Model):
    _name = 'hr.salary.rule.category'
    _inherit = 'hr.salary.rule.category'

    name = fields.Char(required=True, translate=True)


class HrSalaryRule(models.Model):
    _name = 'hr.salary.rule'
    _inherit = 'hr.salary.rule'

    name = fields.Char(required=True, translate=True)


class HrRuleInput(models.Model):
    _name = 'hr.rule.input'
    _inherit = 'hr.rule.input'

    name = fields.Char(string='Description', required=True, translate=True)


class ResourceResource(models.Model):
    _name = "resource.resource"
    _inherit = "resource.resource"

    name = fields.Char(required=True, translate=True)

