from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError,UserError
import logging
import datetime as dt
from datetime import datetime, timedelta
import calendar
import re
_logger = logging.getLogger(__name__)

class consildate_report(models.Model):
    #_name='consildate.sale.report'
    _inherit="sale.order.line"

     
    customer=fields.Many2one('res.partner','Customer')
    region=fields.Many2one('sale.region','Region')
    order_date=fields.Date('Order Date')
    pro_code=fields.Char('Product Code')
    attribute_name = fields.Selection([('Broiler','Broiler'),('Breeders','Breeders'),('Layers','Layers'),('Grandparents','Grandparents')])
     

    
    @api.constrains('product_id')
    def get_data_line(self):
        _logger.info(self.order_id)
        sale_order=self.env['sale.order.line'].search([])
        _logger.info(sale_order)
        for rec in sale_order:

            rec.region=rec.order_id.partner_id.region
            rec.customer=rec.order_id.partner_id
            #self.order_date=  datetime.strftime(sale_order.create_date,'%Y-%m-%d')
            rec.pro_code=rec.product_id.code_product
        
    
         

class consildate_report(models.Model):
    _name='consildate.sale.report'
    name=fields.Char('name',default="Consildate Sale Report")
    #_inherit="sale.order.line"
    user_id=fields.Many2one('res.users','Sale rep')
    customer=fields.Many2one('res.partner','Customer',domain="[('customer','=',True)]")
    region=fields.Many2one('sale.region','Region')
    Date_from=fields.Date('Date From')
    Date_to=fields.Date('Date To')
    attribute_name = fields.Selection([('Broiler','Broiler'),('Breeders','Breeders'),('Layers','Layers'),('Grandparents','Grandparents')])
    product_id=fields.Many2one('product.product',string='Product')

    def search_report(self):
        _logger.info('Date from')
        _logger.info(self.Date_from)
         
        ids=[]
        str_domain=""
        if self.Date_from and self.Date_to and self.Date_to<=self.Date_from:
            raise ValidationError('Date To must be greater than Date From')
            return True
          
        visits=self.env['sale.order.line'].search([]) 
        res=[] 

        for record in visits:
            res.append((record.id))
        if   self.Date_from:
            _logger.info(visits)
            
            visits=visits.search(['&',('id','in',visits.ids),('create_date','>=',self.Date_from)]) 
        
        if   self.Date_to:
            _logger.info(visits)
            
            visits=visits.search(['&',('id','in',visits.ids),('create_date','<=',self.Date_to)])
        if self.customer  :
            _logger.info(visits)
           
            visits=visits.search(['&',('id','in',visits.ids),('order_partner_id','=',self.customer.id) ])
        
        if self.user_id:
            _logger.info(visits)
             
            visits=visits.search(['&',('id','in',visits.ids),('salesman_id','=',self.user_id.id)])
            
        if self.region:
            _logger.info(visits)
             
            visits=visits.search(['&',('id','in',visits.ids),('region','=',self.region.id)])
        
        if self.attribute_name:
            _logger.info(visits)
             
            visits=visits.search(['&',('id','in',visits.ids),('attribute_name','=',self.attribute_name)])
        if self.product_id:
            _logger.info(visits)
             
            visits=visits.search(['&',('id','in',visits.ids),('product_id','=',self.product_id.id)])
        

        for rec in visits:
            if rec.state=='sale' or rec.state=='done':
                
                     ids.append(rec.id)

        _logger.info(visits)
        pivot_id=self.env.ref('consolidated_sales_report.view_sales_consolidate_pivote').id
        tree_view=self.env.ref('consolidated_sales_report.view_sales_consolidate_tree_line').id


        return { 'name':'/',
          
        'view_mode': 'tree,pivot',
        'view_type': 'form',
        'view_id':False,
        'views':[(tree_view,'tree'),(pivot_id,'pivot')],
        'res_model': 'sale.order.line',
        'target': 'current',
         'domain':"[('id','in',%s)]"%(ids),
         'context':{'group_by':'order_partner_id'},
        'type': 'ir.actions.act_window',
         
                   }   
