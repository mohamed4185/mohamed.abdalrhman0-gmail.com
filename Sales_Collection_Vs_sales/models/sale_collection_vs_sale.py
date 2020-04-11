from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError,UserError
import logging
import datetime as dt
from datetime import datetime, timedelta
import calendar
import re
import itertools
import operator
from operator import itemgetter
_logger = logging.getLogger(__name__)
class user(models.Model):
    _inherit='res.users'
    customer_related=fields.One2many('res.partner','user_id',string="customer")
class sale_collection_vs_forecast(models.Model):
    _name='sale.collection.vs.sales'
    _description = "Sales  and Collection report"
    name=fields.Char('name',default='Sales  and Collection report') 
    #_inherit="sale.order.line"
    user_id=fields.Many2one('res.users','Sale rep')
    
    customer=fields.Many2one('res.partner','Customer',domain="[('customer','=',True)]")
    Date_from=fields.Date('Date From')
    Date_to=fields.Date('Date To')
    #product_id = fields.Many2one('product.product', string='Product')

    def search_report(self):
        _logger.info('Date from')
        _logger.info(self.Date_from)
        order_line=self.env['account.move.line'].search([],order='id asc')
        ids=[]
        res=[]
        sql = "delete from customer_account_move"
  
        self.env.cr.execute(sql)
         
        
        if   self.Date_from:
            order_line=order_line.search(['&',('id','in',order_line.ids),('create_date','>=',self.Date_from)],order='id asc') 
        if   self.Date_to:
            order_line=order_line.search(['&',('id','in',order_line.ids),('create_date','<=',self.Date_to)],order='id asc')
        """if self.user_id:
            order_line=order_line.search(['&',('id','in',order_line.ids),('sale_rep','=',self.user_id.id)],order='id asc')"""
        if self.customer:
            order_line=order_line.search(['&',('id','in',order_line.ids),('partner_id','=',self.customer.id)],order='id asc')
       
        for rec in order_line:
            ids.append(rec.id)
        
        records=[]
        for rec in order_line:
            addition=0
            return_value=0
            discount,discount_value=0,0
            if rec.invoice_id and rec.invoice_id.state!='draft' and  rec.account_id.id ==rec.partner_id.property_account_receivable_id.id :
                credit_note=self.env['account.invoice'].search(['&',('id','=',rec.invoice_id.id),('type','=','out_refund')])
                invoice_id=self.env['account.invoice'].search(['&',('id','=',rec.invoice_id.id),('type','=','out_invoice')])
                if invoice_id.invoice_line_ids:
                    for record in invoice_id.invoice_line_ids:
                       if record.discount!=0 :
                            discount_value+=(record.discount/100)*(record.price_unit*record.quantity)
                    
               
                if credit_note :
                    addition=1
                    return_value=credit_note.amount_total
            


            value_emp={
                 'id':rec.id,
                 'partner_id':rec.partner_id,
                 'debit':rec.debit,
                 'credit':rec.credit,
                 'account_id':rec.account_id,
                 'cheques':rec.cheques,
                 'invoice_id':rec.invoice_id,
                 'customer':rec.partner_id.id,
                 'state':rec.invoice_id.state,
                 'addition':addition,
                 'total_return':return_value,
                 'discount':discount_value,
                 'last_move':rec.move_id.id
                 
               }
            records.append(value_emp)
        records.sort(key=operator.itemgetter('customer'))
        grouped_tasks = []
        Records_sorted=[]
        counter=0 
        for key, items in itertools.groupby(records, operator.itemgetter('customer')):
            grouped_tasks.append(list(items))
            Records_sorted.append(key)
        _logger.info('sort and group By')
        _logger.info(grouped_tasks)
         
        for item in grouped_tasks:
            size = len(item)
            addition_customer=0
            cheques,cash,debit,credit,totalsale,begin_debit,begin_credit,begin_balance,total_return=0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0
            partner_id=0
            discount,last_id=0,0
             
            for k in range(size):
                
                partner_id=item[k]['partner_id'].id
                if  item[k]['addition']==1:
                    addition_customer+=1

                if item[k]['account_id'].id==item[k]['partner_id'].property_account_receivable_id.id or item[k]['account_id'].id==item[k]['partner_id'].property_account_payable_id.id:
                    if item[k]['cheques']==True:
                        _logger.info('TRUEEEEE')
                        cheques+=item[k]['credit']
                        
                    else:
                        if item[k]['total_return']==0:
                            cash+=item[k]['credit']
                    if item[k]['total_return']!=0:
                        total_return+=item[k]['total_return']
                    if item[k]['invoice_id']:
                           
                            _logger.info('Invoice_id')
                            _logger.info(item[k]['invoice_id'])
                            if item[k]['invoice_id'].state!='draft' and item[k]['invoice_id'].type=='out_invoice' :
                                totalsale+=item[k]['debit']
                    debit += item[k]['debit']
                    credit+=item[k]['credit']
                    discount+=item[k]['discount']
                    if item[k]['last_move']>last_id:
                        begin_debit=item[k]['debit']
                        begin_credit=item[k]['credit']
                    last_id=item[k]['last_move']
                    
            _logger.info('LASTTTTTTTTTTTTTTTtt')
            _logger.info(begin_debit)
            _logger.info(begin_credit)        
            begin_balance=debit-credit-begin_debit+begin_credit
            customer_move=self.env['customer.account.move'].search([('customer','=',partner_id)])
            collection_net=0
            if totalsale-total_return >0:
                collection_net=((cash+cheques)/(totalsale-total_return))*100

            if partner_id:
                if not customer_move:
                    customer_move.create({
                             'customer':partner_id,
                             'total_sale':totalsale,
                             'cash':cash,
                             'cheque':cheques,
                             'begin_balance':begin_balance,
                             'addition':addition_customer,
                             'total_return':total_return,
                             'net_sale':totalsale-total_return,
                             'collection':cash+cheques,
                             'collection_net':collection_net,
                             'discount':discount,
                             'current_balance':begin_balance+totalsale-total_return-(cash+cheques-discount)
                              
                              })
                else:
                    customer_move.update({
                             'customer':partner_id,
                             'total_sale':totalsale,
                             'cash':cash,
                             'cheque':cheques,
                             'begin_balance':begin_balance,
                             'addition':addition_customer,
                             'total_return':total_return,
                             'net_sale':totalsale-total_return,
                             'collection':cash+cheques,
                             'collection_net':collection_net,
                             'discount':discount,
                             'current_balance':begin_balance+totalsale-total_return-(cash+cheques-discount)
                              
                    
                              })      
            _logger.info(debit)  
            _logger.info(credit)
            _logger.info(cheques)
            _logger.info(cash)
            _logger.info(totalsale)
            _logger.info(begin_balance)
            _logger.info(begin_debit)
            _logger.info(begin_credit)
            _logger.info(debit-credit-begin_debit-begin_credit)
             
            
        view_id_tree=self.env.ref('Sales_Collection_Vs_sales.view_customer_move_tree').id
        
        _logger.info('LLLLLLLLLLLLLLLLLLLLLLL')
        _logger.info(order_line)
        if self.customer:
            return { 'name':'/',
                'view_mode': 'tree', 
                'view_mode': 'tree', 
                'views': [(view_id_tree, 'tree')], 
                
                'res_model': 'customer.account.move',
                'target': 'current',
                'domain':"[('customer','=',%s)]"%(self.customer.id),
                'type': 'ir.actions.act_window',
                   } 
        else:
            return { 'name':'/',
                    'view_mode': 'tree', 
                    'view_mode': 'tree', 
                    'views': [(view_id_tree, 'tree')], 
                    
                    'res_model': 'customer.account.move',
                    'target': 'current',
                    'type': 'ir.actions.act_window',
                   } 
 

class account_line_customer(models.Model):
    _inherit='account.move.line'
    state=fields.Selection(related="move_id.state",string="state")
    

class move_account(models.Model):
     _name='customer.account.move'
     customer=fields.Many2one('res.partner','Customer')
     #cudtomer_id=fields.Integer(related="customer.id",string="Customer ID")
     
     #sale_rep_id=fields.Integer(related="customer.user_id.id",string="Sales Rep ID")
     begin_balance=fields.Float('Beging Balance')
     total_sale=fields.Float('Total Sale')
     cash=fields.Float('Cash')
     cheque=fields.Float('Cheque')
     total_return=fields.Float("Total Return")
     net_sale=fields.Float("Net Sales")
     current_balance=fields.Float('Current Balance')
     addition=fields.Float('Addition')
     collection=fields.Float('Total Collection')
     collection_net=fields.Float('Collections to net sales')
     discount=fields.Float('discount')
     sale_rep=fields.Many2one(related='customer.user_id',string='Sales Rep')
     cst_id=fields.Char(string='Customer ID')
     region=fields.Many2one(related='customer.region',string="Region")
     region_parent=fields.Many2one(related='customer.region.parent_region',string="Region")
     @api.constrains("customer")
     def get_code(self):
         if self.customer.customer_code:
             self.cst_id=self.customer.customer_code
      
     #region=fields.Many2one(related="customer.region",string="Region")
     #parent_region=fields.Many2one(related="customer.region.parent_region",string="Parent Region")
     #parent_region_id=fields.Integer(related="customer.region.parent_region.id",string="Parent Region ID")
     #parent_region_team_leader=fields.Many2one(related="customer.region.parent_region.user_id",string=" Parent Region Sales Rep Team Leader")
     #region_id=fields.Integer(related="customer.region.id",string="Region ID")
     @api.model
     def create(self,vals):
         
        return super(move_account,self).create(vals)
