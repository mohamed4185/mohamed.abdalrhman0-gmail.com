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



class HrContract(models.Model):
    _inherit = 'hr.contract'
    _description = 'Employee Contract'

    sin_exist = fields.Boolean("Has Social Insurance")
    sin_no = fields.Char("Social Insurance No", )
    sin_date = fields.Date("Social Insurance Date")
    sin_end_date = fields.Date("Social Insurance  end Date")
    mi_exist = fields.Boolean("Has Medical Insurance")
    mi_no = fields.Char(string="Medical Insurance NO", help='Medical  Insurance No')
    mi_date = fields.Date(string="Medical Insurance Date", help='Medical  Insurance Date')
    basic_salary = fields.Float(string="Basic Salary", digits=dp.get_precision('Payroll'))
    variable_salary = fields.Float(string="Variable Salary", digits=dp.get_precision('Payroll'))
    allowances = fields.Float(string="Allowances", digits=dp.get_precision('Payroll'))
    prev_raise = fields.Float(string="previous Annual Raises", digits=dp.get_precision('Payroll'))
    other_alw_ids = fields.One2many(comodel_name="hr.other_alw_line", inverse_name="contract_id",
                                    string="Other Allowances")

    def get_alw(self, alw_code):
        alw_id = self.other_alw_ids.filtered(lambda x: x.code == alw_code)
        return alw_id


class hr_other_alw_line(models.Model):
    _name = "hr.other_alw_line"
    alw_id = fields.Many2one(comodel_name="hr.other_alw",string="name", required=True, translate=True)
    code = fields.Char(string="Code", required=True)
    amount = fields.Float(string="Amount", required=True)
    contract_id = fields.Many2one(comodel_name="hr.contract", string="Contract")

    @api.onchange('alw_id')
    def onchange_parts(self):
        self.code = self.alw_id.code
        self.amount = self.alw_id.amount




class hr_other_alw(models.Model):
    _name = "hr.other_alw"
    name = fields.Char(string="name", required=True, translate=True)
    code = fields.Char(string="Code", required=True)
    amount = fields.Float(string="Amount")
    # employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee")
    @api.model
    def create(self, values):
        # type: (object) -> object
        res = super(hr_other_alw, self).create(values)
        cat_id=self.env['hr.salary.rule.category'].search([('code','=','ALW')],limit=1)
        rule_obj=self.env['hr.salary.rule']
        condition_exp='result = contract.get_alw("%s") and contract.get_alw("%s").amount > 0 or False'%(values['code'],values['code'])
        amount_exp='result = contract.get_alw("%s").amount'%values['code']
        vals={
            'name':values['name'],
            'category_id':cat_id.id,
            'code': values['code'],
            'condition_select':'python',
            'condition_python':condition_exp,
            'amount_select':'code',
            'amount_python_compute':amount_exp,
            'sequence':35

        }
        rule_obj.create(vals)



        return res

    @api.multi
    def unlink(self):

        for rule in self.env['hr.salary.rule'].search([('code','=',self.code)]):
            rule.unlink()
        return super(hr_other_alw, self).unlink()
