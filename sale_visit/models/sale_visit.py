# -*- coding: utf-8 -*-

from odoo import api ,models, fields
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError,UserError
import logging 
from datetime import datetime, timedelta,date
import datetime as dt
import calendar
_logger = logging.getLogger(__name__)
class sale_visit(models.Model):
    _name = 'sale.visit'
    Day = fields.Date(string="Visit Date")
    area = fields.Many2one(related='Customer.region', string="Area",readonly=True)
    reg = fields.Many2one('sale.region', string="Area",readonly=True)
    Customer = fields.Many2one('res.partner', string="Customer" ,domain="[('customer','=',True)]")
    customer_Type=fields.Selection(related="Customer.customer_Type",string="Customer Type",readonly=True,)
    Objective = fields.Many2many('objective.visit',string="Objective" )
    Description = fields.Char(string="Visit Desciption",size=500)
    Status = fields.Selection([('Planned','Planned'),('Canceled','Canceled'),('Completed','Completed')],string="Status",default="Planned")
    Feedback = fields.Char(string="Visit Feedback",size=150 )
    sale_visit_planned=fields.Many2one('sale.visit.planned',ondelete='cascade', index=True,)
    rep = fields.Many2one(related="sale_visit_planned.rep")
    name=fields.Char(related="sale_visit_planned.name")
    state=fields.Selection(related="sale_visit_planned.state")
    @api.onchange('Day')
    def check_date_onchange(self):
        visits=self.env['objective.visit'].search([])
        if not visits:
            vals={}
            vals['name']='Make Sales Order'
            objective=self.env['objective.visit'].create(vals)
            vals['name']='Promotion'
            objective=self.env['objective.visit'].create(vals)
            vals['name']='Collection'
            objective=self.env['objective.visit'].create(vals)

             
        if self.Day:
           if self.sale_visit_planned.date_from:
                if self.Day<self.sale_visit_planned.date_from or self.Day>self.sale_visit_planned.date_to:
                        raise ValidationError('Date of visit is out of Range')

    @api.constrains('Day')
    def check_date(self):
        _logger.info('dddddddddddd')
   
    @api.onchange('Customer')
    def check_customer_onchage(self):
        _logger.info('customer')
        if self.Customer:
            records=self.env['sale.visit'].search(['&',('Day','=',self.Day),('rep','=',self.rep.id)])
            _logger.info(records)
            _logger.info(self.rep)
            if records :
                for rec in records:
                    if rec.id!=self.id and rec.Customer==self.Customer and self.sale_visit_planned!=rec.sale_visit_planned:
                        raise ValidationError('Customer is selected before with sale rep')        
    
class sales_visit_planned(models.Model):
    _name='sale.visit.planned'
    name=fields.Char('name',default='Visits')
    date_from=fields.Date('From')
    date_to=fields.Date('To')
    sale_visit_activity=fields.One2many('sale.visit','sale_visit_planned',string="activity",copy=True,required=True) 
    rep = fields.Many2one('res.users',string="Sales Rep",default=lambda self: self.env.uid)
    state=fields.Selection([('Open','Open'),('Approve','Approve')],default="Open")
    def action_approve(self):
        group_id=self.env['ir.model.data'].search([('name','=','group_sale_manager')])
        group_user = self.env['res.groups'].search([('id','=',group_id.res_id)]) 
        user=self.env['res.users'].search(['&',('id','=',self.env.uid),('groups_id','in',group_user.id)])  
        if self.rep.id==self.env.uid and not user :
            raise ValidationError('Sales Manager will approve your plan.....')
        self.state='Approve'
    def action_open(self):
        self.state='Open'
    @api.onchange('date_from','date_to')
    def check_date_range(self):
        today = dt.datetime.today()
        month=int(today.strftime('%m'))
        year=int(today.strftime('%y'))
         
        num_days_next=0
        for i in range(0,3):
             
            if month==12:
                month=1
                year+=1
            num_days_next+=calendar.monthrange(year,month)[1]
            month+=i
        
        next_date=today+timedelta(days=num_days_next) 
        month=int(today.strftime('%m'))
        year=int(today.strftime('%y'))
        if month==1:
            year-=1
            month=12
        num_days_pre=calendar.monthrange(year,month-1)[1]
        pre_date=today-timedelta(days=num_days_pre) 

        if self.date_from:
            if self.date_to:
                if self.date_from>=self.date_to  :
                    raise ValidationError('Error : Date From must be  less than Date To')

            if datetime.combine(self.date_from, datetime.min.time())> next_date  or datetime.combine(self.date_from, datetime.min.time())< pre_date  :
                raise ValidationError('Error : Date From must be  a month or three months from now')
        if self.date_to:
            if self.date_from:
                if  self.date_to <= self.date_from :
                    raise ValidationError('Error : Date To must be  greater than Date From')
            if datetime.combine(self.date_to, datetime.min.time())> next_date  or datetime.combine(self.date_to, datetime.min.time())< pre_date  :
                raise ValidationError('Error : Date To must be  a month or three months from now')

    @api.constrains('date_from','date_to')
    def confrim_date_range(self):
        today = dt.datetime.today()
        month=int(today.strftime('%m'))
        year=int(today.strftime('%y'))
         
        num_days_next=0
        for i in range(0,3):
             
            if month==12:
                month=1
                year+=1
            num_days_next+=calendar.monthrange(year,month)[1]
            month+=i
        
        next_date=today+timedelta(days=num_days_next) 
        month=int(today.strftime('%m'))
        year=int(today.strftime('%y'))
        if month==1:
            year-=1
            month=12
        num_days_pre=calendar.monthrange(year,month-1)[1]
        pre_date=today-timedelta(days=num_days_pre) 

        if self.date_from:
            if self.date_to:
                if self.date_from>=self.date_to  :
                    raise ValidationError('Error : Date From must be  less than Date To')

            if datetime.combine(self.date_from, datetime.min.time())> next_date  or datetime.combine(self.date_from, datetime.min.time())< pre_date  :
                raise ValidationError('Error : Date From must be  a month or three months from now')
        if self.date_to:
            
            """if datetime.strftime(self.date_to,'%d-%m-%Y')<=datetime.strftime(self.date_from,'%d-%m-%Y') and self.date_to:
                raise ValidationError('Error : Date To must be  greater than Date From')"""
            if datetime.combine(self.date_to, datetime.min.time())> next_date  or datetime.combine(self.date_to, datetime.min.time())< pre_date  :
                raise ValidationError('Error : Date To must be  a month or three months from now')

    @api.constrains('rep')
    def get_duplication(self):
        records=self.env['sale.visit.planned'].search(['&',('date_from','>=',self.date_from),('date_to','<=',self.date_to)])
        for rec in records:
            if self.id!=rec.id and self.rep==rec.rep:
                raise ValidationError('Sale rep is selected at the same dates')
        if not self.sale_visit_activity:
            raise ValidationError('Please Add at the least one activity')

    @api.constrains('sale_visit_activity')
    def get_activity(self):
         
        if not self.sale_visit_activity:
            raise ValidationError('Please Add at the least one activity')

    