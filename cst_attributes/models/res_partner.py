# -*- coding: utf-8 -*-

from odoo import api, fields ,models
from odoo.exceptions import ValidationError 
import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit="res.partner"
    cst_attributes_target = fields.One2many('cst.attribute','customer',string='Customer Attributes')
    customer_code=fields.Char('Customer Code',size=10)
    arabic_name=fields.Char('Arabic Name',size=100)
    customer_Type=fields.Selection([('key Account','key Account'),('Consultant','Consultant'),('Doctor','Doctor'),('Pharmacy','Pharmacy'),('Farm','Farm'),('Distributor','Distributor'),('Other','Other')] ,'Type')
    customer_class=fields.Selection([('A','A'),('B','B'),('C','C'),('D','D')],'Class')
    region=fields.Many2one('sale.region',string="Region")
    is_blacklist=fields.Boolean('Is Blacklisted',default=False,store=True)
    discount=fields.Many2one('sales.discount',string='Discount')
    #sale_pricelist=fields.Many2one('product.pricelist')
    credit_limit=fields.Integer('Credit Limit')
    credit_duration=fields.Selection([('cash','cash'),('3 Months','3 Months'),('Stopped Deals','Stopped Deals'),('Unknown','Unknown')] ,'Credit Duration')
    credit_duration_from=fields.Date('Credit Duration From')
    credit_duration_to=fields.Date('Credit Duration To')
   
    
    @api.constrains('customer_code')
    def get_code(self):
        if self.customer_code:
            for rec in self.search([]) :
                if self.customer_code == rec.customer_code and self.id != rec.id:
                   raise ValidationError("Error: Customer Code must be unique")
 
 
     
class User(models.Model):
    _inherit='res.users'
    """@api.constrains('groups_id')
    def get_manager_user(self):
        
        list_ids=[]
        manager_sale=self.env['ir.model.data'].search([('name','=','group_sale_manager')])
        group_manager_sale = self.env['res.groups'].search([('id','=',manager_sale.res_id)])
        all_document_sale=self.env['ir.model.data'].search([('name','=','group_sale_salesman_all_leads')])
        only_document_sale=self.env['ir.model.data'].search([('name','=','group_sale_salesman')])
        contant=self.env['ir.model.data'].search([('name','=','group_partner_manager')])
        group_manager_sale = self.env['res.groups'].search([('id','=',manager_sale.res_id)])
        group_all_document_sale = self.env['res.groups'].search([('id','=',all_document_sale.res_id)])
        group_only_document_sale = self.env['res.groups'].search([('id','=',only_document_sale.res_id)])
        list_ids.append(group_only_document_sale.id)
        list_ids.append(group_all_document_sale.id)
        list_ids.append(group_manager_sale.id)
        group_contant = self.env['res.groups'].search([('id','=',contant.res_id)])

        internal_user_group=self.env['ir.model.data'].search([('name','=','group_user')])
        internal_user_group = self.env['res.groups'].search([('id','=',internal_user_group.res_id)])
        list_ids.append(internal_user_group.id)
        group_private_addresses=self.env['ir.model.data'].search([('name','=','group_private_addresses')])
        group_private_addresses = self.env['res.groups'].search([('id','=',group_private_addresses.res_id)])
        list_ids.append(group_private_addresses.id)
        group_no_one=self.env['ir.model.data'].search([('name','=','group_no_one')])
        group_no_one = self.env['res.groups'].search([('id','=',group_no_one.res_id)])
        list_ids.append(group_no_one.id)
        group_show_line_subtotals_tax_excluded=self.env['ir.model.data'].search([('name','=','group_show_line_subtotals_tax_excluded')])
        group_show_line_subtotals_tax_excluded = self.env['res.groups'].search([('id','=',group_show_line_subtotals_tax_excluded.res_id)])
        list_ids.append(group_show_line_subtotals_tax_excluded.id)
        group_products_in_bills=self.env['ir.model.data'].search([('name','=','group_products_in_bills')])
        group_products_in_bills = self.env['res.groups'].search([('id','=',group_products_in_bills.res_id)])
        list_ids.append(group_products_in_bills.id)
        list_ids.append(group_contant.id)
        create_customer=False
        only_document=False
       
        list_groups=self.groups_id.search([('id','not in',list_ids)])
        _logger.info('List')
        _logger.info(list_ids)
        _logger.info(self.groups_id)
        
        for rec in self.groups_id:
            if rec.id  not in list_ids:
                 create_customer=True
                    
                    
                    
                
                   

        _logger.info("BOOLEAN")
        _logger.info(create_customer)
        if create_customer==False:  
                  group_contant.users=[(2,self.id)]        
         """
    