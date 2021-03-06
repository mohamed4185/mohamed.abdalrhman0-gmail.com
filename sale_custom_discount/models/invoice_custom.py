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
class invoice_discount(models.Model):
    _inherit='account.invoice'
    discount=fields.Many2one('sales.discount',string='Discount')
    discount_type=fields.Selection([('Precentage','Precentage'),('Amount','Amount')],string="Discount Type")
    precentge_value=fields.Float("Precentage")
    amount_value=fields.Float("Amount")
    global_discount=fields.Float(compute='_compute_amount',string="Global Discount")
    serial_invoice=fields.Integer('Serial Invoice')
    serial_statment=fields.Integer('Serial Statemnt')
    type_invoice=fields.Selection([('invoice','Invoice'),('statment','Statment')],string="Type",default='statment')
    confrimed_user=fields.Many2one('res.users',string="confrimed_user")
    @api.onchange('partner_id')
    def get_partner_discount(self):
        self.discount=self.partner_id.discount.id
    @api.constrains('discount')
    def get_line_discount(self):
        
        if self.discount:
            for rec in self.invoice_line_ids:
                if rec.discount_change==False:
                     rec.discount2=self.discount.id
    @api.onchange('discount')
    def get_line_discount_change(self):
        if self.discount:
            for rec in self.invoice_line_ids:
                if rec.discount_change==False:
                       rec.discount2=self.discount.id
     
    @api.constrains('discount_type','invoice_line_ids')
    def get_global_discount(self):
            
            if self.discount_type=='Amount':
                
                self.precentge_value=0
               
            if self.discount_type=='Precentage':

                self.amount_value=0
                 
    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'tax_line_ids.amount_rounding',
                 'currency_id', 'company_id', 'date_invoice', 'type','amount_value','precentge_value')
    def _compute_amount(self):
        round_curr = self.currency_id.round
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(round_curr(line.amount_total) for line in self.tax_line_ids)
        self.amount_total = self.amount_untaxed + self.amount_tax
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id
            amount_total_company_signed = currency_id._convert(self.amount_total, self.company_id.currency_id, self.company_id, self.date_invoice or fields.Date.today())
            amount_untaxed_signed = currency_id._convert(self.amount_untaxed, self.company_id.currency_id, self.company_id, self.date_invoice or fields.Date.today())
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign
        if self.discount_type=='Amount':
                
                self.precentge_value=0
                self.global_discount=self.amount_value
                self.amount_total-=self.amount_value
        if self.discount_type=='Precentage' :

            self.amount_value=0
            prec=(self.precentge_value/100)*self.amount_total
            self.global_discount=prec
            self.amount_total-=self.global_discount


            

    @api.constrains('state')
    def get_state(self):
        if self.state=='open':
            self.confrimed_user=self.env.uid
    @api.constrains('type_invoice')
    def get_serial(self):
        self.serial_invoice=0
        self.serial_statment=0
        if self.type_invoice=='invoice':
            self._cr.execute('select max(serial_invoice) from account_invoice') 
            account = self._cr.dictfetchall()
            account=account[0]['max']
            
            self.serial_invoice=account+1
             
            now = datetime.now()
            x="000"
            if len(str(self.serial_invoice))==2:
                x='00'
            if len(str(self.serial_invoice))==3:
                x='0'


            self.name="INV/"+str(now.year)+"/"+x+str(self.serial_invoice)
        else:
            self._cr.execute('select  max(serial_statment) from account_invoice') 
            account = self._cr.dictfetchall()
            account=account[0]['max']
            
             
            self.serial_statment=account+1
            now = datetime.now()
            x="000"
            if len(str(self.serial_statment))==2:
                x='00'
            if len(str(self.serial_statment))==3:
                x='0'


            self.name="STAT/"+str(now.year)+"/"+x+str(self.serial_statment)
  
    
   
    @api.onchange('discount_type')
    def get_global_discount_changes(self):
            
            if self.discount_type=='Amount':
                self.precentge_value=0
                 
            if self.discount_type=='Precentage':

                self.amount_value=0
              
            

    """@api.multi
    def get_taxes_values(self):
        tax_grouped = {}
        round_curr = self.currency_id.round
        for line in self.invoice_line_ids:
            if not line.account_id:
                continue
            price_unit = line.price_unit 
            if line.discount2:
                    if line.discount2.discount_1:
                                 price_unit=  price_unit-((price_unit*line.discount2.discount_1)/100)
                    if line.discount2.discount_2:
                                price_unit=price_unit-((price_unit*line.discount2.discount_2)/100)
                    if line.discount2.discount_3:
                        price_unit= price_unit-((price_unit*line.discount2.discount_3)/100)
            if line.discount:
                 price_unit= price_unit-((price_unit*line.discount)/100)
            taxes = line.invoice_line_tax_ids.compute_all(price_unit, self.currency_id, line.quantity, line.product_id, self.partner_id)['taxes']
            for tax in taxes:
                val = self._prepare_tax_line_vals(line, tax)
                key = self.env['account.tax'].browse(tax['id']).get_grouping_key(val)

                if key not in tax_grouped:
                    tax_grouped[key] = val
                    tax_grouped[key]['base'] = round_curr(val['base'])
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += round_curr(val['base'])
        return tax_grouped"""
      
    @api.multi
    def action_move_create(self):
        _logger.info('action_move_create')
        """ Creates invoice related analytics and financial move lines """
        account_move = self.env['account.move']

        for inv in self:
            if not inv.journal_id.sequence_id:
                raise UserError(_('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line_ids.filtered(lambda line: line.account_id):
                raise UserError(_('Please add at least one invoice line.'))
            if inv.move_id:
                continue


            if not inv.date_invoice:
                inv.write({'date_invoice': fields.Date.context_today(self)})
            if not inv.date_due:
                inv.write({'date_due': inv.date_invoice})
            company_currency = inv.company_id.currency_id

            # create move lines (one per invoice line + eventual taxes and analytic lines)
            iml = inv.invoice_line_move_line_get()
            iml += inv.tax_line_move_line_get()
            _logger.info('IML')
            _logger.info(iml)

            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.compute_invoice_totals(company_currency, iml)

            name = inv.name or ''
            if inv.payment_term_id:
                totlines = inv.payment_term_id.with_context(currency_id=company_currency.id).compute(total, inv.date_invoice)[0]
                res_amount_currency = total_currency
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency._convert(t[1], inv.currency_id, inv.company_id, inv._get_currency_rate_date() or fields.Date.today())
                    else:
                        amount_currency = False

                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency
                    _logger.info('TOTAL PAYEMrnt')
                    _logger.info(t[1])
                    _logger.info(inv.global_discount)
                    _logger.info(self.global_discount)
                    if self.type in ['in_invoice', 'out_invoice']:
                        total_price=t[1]-self.global_discount
                    elif self.type in ['out_refund','in_refund']:
                        total_price=t[1]+self.global_discount
                    
                    
                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': total_price,
                        'account_id': inv.account_id.id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
            else:
                _logger.info('TOTAL After Valdition')
                _logger.info(total)
                _logger.info(type(total))
                _logger.info(self.global_discount)
                _logger.info(inv.global_discount)
                if self.type in ['in_invoice', 'out_invoice']:
                      total_price=total-self.global_discount
                elif self.type in ['out_refund','in_refund']:
                    total_price=total+self.global_discount

                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total_price,
                    'account_id': inv.account_id.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'invoice_id': inv.id
                })
            _logger.info("IMLLLLLLLLLLLL")

            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
            line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
            line = inv.group_lines(iml, line)

            line = inv.finalize_invoice_move_lines(line)
            _logger.info("LINE LINE")
            check='invoice'
            _logger.info(self.type)
            if self.type in ['in_invoice', 'out_invoice']:
                for record in line :
                     
                        if record[2]['credit']:
                                _logger.info(record[2]['credit'])
                                record[2]['credit']=record[2]['credit']-self.global_discount
                                _logger.info(record[2]['credit'])
                                break

            elif self.type in ['out_refund','in_refund']:
                for record in line :
                     
                        if record[2]['debit']:
                                _logger.info(record[2]['debit'])
                                record[2]['debit']=record[2]['debit']-self.global_discount
                                _logger.info(record[2]['debit'])
                                break
                         


                    
               

             
            date = inv.date or inv.date_invoice
            move_vals = {
                'ref': inv.reference,
                'line_ids': line,
                'journal_id': inv.journal_id.id,
                'date': date,
                'narration': inv.comment,
            }
            _logger.info("LINEEEEEEEE")
            _logger.info(line)
            move = account_move.create(move_vals)
            
            """if self.global_discount!=0:
                discount_account=self.env['res.config.settings'].search([])
                 if not discount_account.discount_account:
                    raise ValidationError('Please add discount account from configuration')

                if discount_account.discount_account:
                    obj=self.env['account.move.line']
                    writeoff_line={}
                    writeoff_line['name'] = "Discount Differance"
                    writeoff_line['account_id'] = discount_account.discount_account.id
                    writeoff_line['debit'] = self.global_discount
                    writeoff_line['credit'] = 0
                    writeoff_line['move_id'] = move.id
                    obj.create(writeoff_line)"""

            # Pass invoice in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post(invoice = inv)
            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'date': date,
                'move_name': move.name,
            }
            inv.write(vals)
        return True
    @api.multi
    def action_invoice_open(self):
        group_id=self.env['ir.model.data'].search([('name','=','group_account_manager')])
        group_user = self.env['res.groups'].search([('id','=',group_id.res_id)]) 
         
        partner_list=[]
        parent_id=False
        _logger.info("NOTEEEE")  
        _logger.info(group_user)
        if  self.message_ids:
            if self.name:
                for rec in self.message_ids:
                    _logger.info(rec)
                    
                    parent_id=rec.id
           
                
            for rec in group_user.users:
                partner_user=self.env['res.users'].search([('id','=',rec.id)]).partner_id.id
                _logger.info(partner_user)
                if rec.id!=self.env.uid:
                     partner_list.append(partner_user)
            if  partner_list:
                value={
                'body':"Validate new Ivoice: ",
                'res_id':self.id,
                'model':'account.invoice',
                'message_type':'notification',
                'parent_id':parent_id,
                'needaction_partner_ids':[(6,0,partner_list)]
                
                }
                self.message_ids.create(value)
            sales_manager_id=self.partner_id.region.sale_manager_id
           
            area_manager_id=self.partner_id.region.area_manager_id
            if sales_manager_id:
                value={
                'body':"Validate new Ivoice: "+self.name ,
                'res_id':self.id,
                'model':'account.invoice',
                'message_type':'notification',
                'parent_id':parent_id,
                'needaction_partner_ids':[(4,sales_manager_id)]
                
                }
                self.message_ids.create(value)
            
            if area_manager_id:
                value={
                'body':"Validate new Ivoice:  "+self.name ,
                'res_id':self.id,
                'model':'account.invoice',
                'message_type':'notification',
                'parent_id':parent_id,
                'needaction_partner_ids':[(4,area_manager_id)]
                
                }
                self.message_ids.create(value)
        return super(invoice_discount, self).action_invoice_open()
    @api.constrains('invoice_line_ids')
    def get_exclude_changes(self):
        """sql='delete from  account_invoice_line  where (excluded_check=True or price_subtotal=0)  and invoice_id=%s'%(self.id)
        self._cr.execute(sql)"""
        _logger.info("DElete 777")
        _logger.info(self.invoice_line_ids)
        for line in self.invoice_line_ids:    
            if line.foc_type=='excluded':
                if line.foc_discount:
                    order_lines=self.env['account.invoice.line']
                    
                    result=line.foc_discount/100
                    quantity=round(line.quantity*result,0)
                    
                    x=0
                    dis_list=self.env['sales.discount'].search([('discount_1','=',100)])
                    if not dis_list:
                        dis_list=self.env['sales.discount']
                        dis_list.create({'discount_1':100,'discount_2':0,'discount_3':0,'name':'Discount 100%'})


                    dis_list=self.env['sales.discount'].search([('discount_1','=',100)])
                    other_product=self.env['account.invoice.line'].search([('product_id','=',line.product_id.id),('invoice_id','=',line.invoice_id.id),('discount2','=',dis_list.id)])
                    prod_name="'"+line.product_id.name+"'"
                    if other_product:
                        sql='update  account_invoice_line set discount2=%s ,quantity=%s where id=%s'%(dis_list.id,quantity,other_product.id)
                        self._cr.execute(sql)
                    else:
                        sql='insert into account_invoice_line(product_id,invoice_id,name,price_unit,quantity,uom_id,excluded_check,discount2,discount_change,account_id) values(%s,%s,%s,%s,%s,%s,true,%s,true,%s)'%(line.product_id.id,self.id,prod_name,line.price_unit,quantity,line.uom_id.id,dis_list.id,line.product_id.property_account_income_id.id)
                        self._cr.execute(sql)
class invoice_line_discount(models.Model):
    _inherit='account.invoice.line'
    discount2=fields.Many2one('sales.discount',string='Discount')
    foc_type=fields.Selection([('included','Included'),('excluded','Excluded')],string="FOC Type")
    foc_discount=fields.Float("FOC Discount")
    discount_change=fields.Boolean("Dis change")
    excluded_check=fields.Boolean("excluded Check",default=False)

    #price_untaxes_discount=fields.Float('subtotal',compute="_compute_price")
    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
        'invoice_id.date_invoice', 'invoice_id.date','discount2')
    def _compute_price(self):
        _logger.info('COMPUTE PRICE')
        currency = self.invoice_id and self.invoice_id.currency_id or None
        price = self.price_unit 
        if self.discount2:
            if self.discount2.discount_1:
                         price=  price-((price*self.discount2.discount_1)/100)
            if self.discount2.discount_2:
                        price=price-((price*self.discount2.discount_2)/100)
            if self.discount2.discount_3:
                price= price-((price*self.discount2.discount_3)/100)
        if self.discount:
             price= price-((price*self.discount)/100)
        if self.foc_type=='included':
                 
                _logger.info((price*100)/(self.foc_discount+10))
                if self.foc_discount:  
                    result=self.foc_discount+100
                    price=(price*100)/(result)
         

        taxes = False
        if self.invoice_line_tax_ids:
            taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
        self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price
        self.price_total = taxes['total_included'] if taxes else self.price_subtotal
         
        _logger.info('DISCOUNT')
        _logger.info(self.price_subtotal)
        if self.invoice_id.currency_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
            currency = self.invoice_id.currency_id
            date = self.invoice_id._get_currency_rate_date()
            price_subtotal_signed = currency._convert(price_subtotal_signed, self.invoice_id.company_id.currency_id, self.company_id or self.env.user.company_id, date or fields.Date.today())
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign
         
    
