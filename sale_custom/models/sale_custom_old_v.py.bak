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
from odoo.tools import email_re, email_split, email_escape_char, float_is_zero, float_compare, \
    pycompat, date_utils
    
class sale_custom(models.Model):
    _inherit="sale.order"
    date_valid=fields.Integer('validity ')
    user_id=fields.Many2one('res.users',string="Sales Rep")
    discount=fields.Selection(related='partner_id.discount',string='Discount')
    reason=fields.Selection([('A','A'),('B','B')],'Reason')
    comment_cancel=fields.Char('Comment')
    order_date=fields.Date('Order Date',default=dt.datetime.strftime(datetime.today(),'%Y-%m-%d'))
    #region=fields.Many2one(related='user_id.region',string='Region')
     
    @api.onchange('order_date')
    def get_order_date(self):
        self.order_date=dt.datetime.strftime(datetime.today(),'%Y-%m-%d')


    @api.onchange('partner_id')
    def get_blacklist(self):
        if self.partner_id.is_blacklist==True:
            raise ValidationError('you can not create sale order for this customer')
    @api.constrains('order_date')
    def get_date(self):
        _logger.info(type(self.order_date))
        _logger.info(type(datetime.today()))
        if self.order_date < dt.datetime.today().date():
            raise ValidationError('Order Date must be greater than Today')
    @api.constrains('reason','comment_cancel')
    def print_message_reason(self):
        message_body= "Customer :"+str(self.partner_id.name) +"<br>"+"  Cancelation Reason: "+str(self.reason) 
        if self.comment_cancel:
            message_body+="<br>"+"  Cancelation Comment: "+str(self.comment_cancel)
        _logger.info('Message')
        _logger.info(message_body)
        #sql="insert into mail_message(body,res_id,model,message_type,create_uid) values("+message_body+","+str(self.id)+",'sale.order','notification',"+ str(self.env.uid)+")"
        #_logger.info(sql)
        #self._cr.execute(sql)
        value={
        'body':message_body,
        'res_id':self.id,
        'model':'sale.order',
        'message_type':'notification',
        }
        if (self.reason and self.comment_cancel) or self.reason:
            self.message_ids.create(value)

    @api.multi
    def action_cancel_order(self):
        self.write({'state': 'cancel'})
        _logger.info('Cancel')
        _logger.info('idddd')
        _logger.info(self.id)
        

        cancel_oreder=self.env['sale.order.cancelled'].search([('cancelled_order','=',self.id)])
        self.env['ir.cron'].clear_caches() 
        res= { 'name':'',
         'view_type': 'form',
        'view_mode': 'form',
        'res_model': 'sale.order.cancelled',
        'target': 'new',
         'view_type': 'form',
        'view_id':self.env.ref('sale_custom.cancel_custom_order_from').id ,
        'tag': 'reload',
        'context':{'default_cancelled_order': self.id},
        'res_id':cancel_oreder.id,
        'flags': {'form': {'action_buttons': True}} ,
        'type': 'ir.actions.act_window', }
        
         
        return res
    @api.onchange('date_valid')
    def change_validity_date_vlid(self):
        _logger.info('Validation')
        if self.date_valid<0:
            raise ValidationError('validity date must be postive value')

 
        if self.date_valid>0:
            self.validity_date=datetime.strftime(dt.datetime.today() +timedelta(days=self.date_valid),'%Y-%m-%d %H:%M')
            _logger.info(self.validity_date)
        """if not self.date_valid and self.create_date:
            self.validity_date= datetime.strftime(self.create_date,'%Y-%m-%d %H:%M')"""
    @api.constrains('date_valid')
    def save_validity_date_vlid(self):
        _logger.info('Validation')
       
        if self.date_valid>0:
            self.validity_date=datetime.strftime(dt.datetime.today() +timedelta(days=self.date_valid),'%Y-%m-%d %H:%M')
            _logger.info(self.validity_date)
    @api.onchange('confirmation_date')
    def get_state_action(self):
        _logger.info('ssssssssssss')
        if self.state=='sale':
            _logger.info('777777777777')
            if self.partner_id.credit_limit<self.amount_total:
                warning_mess = {
                            'title': _('Customer Credit Limit!'),
                            'message' : 'Credit Limit for Customer is less than total sale order'
                        }
                        

                return {'warning': warning_mess}

    @api.multi
    @api.onchange('order_line','discount','amount_untaxed','amount_tax') 
    def get_discount_list(self):
        _logger.info('sdfsdfdsf')
        _logger.info(self.discount)
        self.amount_untaxed=0
        self.amount_tax=0
        dif=0
        for rec in self.order_line:
                rec.price_subtotal=rec.product_uom_qty*rec.price_unit
                if rec.discount2=='1':
                     rec.price_subtotal-=rec.price_subtotal*0.15
                if rec.discount2=='2':
                    rec.price_subtotal-=(rec.price_subtotal*0.15)+(rec.price_subtotal*0.15*0.05)
                if rec.discount2=='3':
                    dis_value=(rec.price_subtotal*0.15)+(rec.price_subtotal*0.15*0.05)+(rec.price_subtotal*0.15*0.05*0.05)
                    price_discount=rec.price_subtotal-dis_value
                    rec.price_subtotal-=(rec.price_subtotal*0.15)+(rec.price_subtotal*0.15*0.05)+(rec.price_subtotal*0.15*0.05*0.05)
                self.amount_untaxed+=rec.price_subtotal
                rec.price_total_discount=rec.price_subtotal
                if rec.tax_id :
                    _logger.info('TAXES')
                    _logger.info(rec.tax_id.amount)
                    _logger.info(self.amount_tax)
                    self.amount_tax+=rec.price_subtotal*(rec.tax_id.amount/100)
                    self.price_total_discount=rec.price_subtotal*(rec.tax_id.amount/100)+rec.price_subtotal

        dif= self.amount_untaxed
        if self.discount=='1':
            
            _logger.info('self.amount_untaxed*0.15')
            _logger.info(self.amount_untaxed*0.15)
            self.amount_untaxed-=self.amount_untaxed*0.15
            _logger.info(self.amount_untaxed)
        if self.discount=='2':
            self.amount_untaxed-=(self.amount_untaxed*0.15)+(self.amount_untaxed*0.15*0.05)
        if self.discount=='3':
            dis_value=(self.amount_untaxed*0.15)+(self.amount_untaxed*0.15*0.05)+(self.amount_untaxed*0.15*0.05*0.05)
            price_discount=self.amount_untaxed-dis_value
            self.amount_untaxed-=(self.amount_untaxed*0.15)+(self.amount_untaxed*0.15*0.05)+(self.amount_untaxed*0.15*0.05*0.05)
         
        self.update({'amount_untaxed':self.amount_untaxed})
        if self.amount_tax:
            self.update({'amount_total':self.amount_untaxed+self.amount_tax})
        else:
            self.update({'amount_total':self.amount_untaxed+self.amount_tax})
        dif-=self.amount_untaxed
        for rec in self.order_line:
            rec.price_total_discount-=(dif/len(self.order_line))
    @api.constrains('order_line') 
    def get_discount_list2(self):
        _logger.info('constrains')
        _logger.info(self.discount)
        self.amount_untaxed=0
        self.amount_tax=0
        dif=0
        for rec in self.order_line:
                rec.price_subtotal=rec.product_uom_qty*rec.price_unit
                if rec.discount2=='1':
                     rec.price_subtotal-=rec.price_subtotal*0.15
                if rec.discount2=='2':
                    rec.price_subtotal-=(rec.price_subtotal*0.15)+(rec.price_subtotal*0.15*0.05)
                if rec.discount2=='3':
                    dis_value=(rec.price_subtotal*0.15)+(rec.price_subtotal*0.15*0.05)+(rec.price_subtotal*0.15*0.05*0.05)
                    price_discount=rec.price_subtotal-dis_value
                    rec.price_subtotal-=(rec.price_subtotal*0.15)+(rec.price_subtotal*0.15*0.05)+(rec.price_subtotal*0.15*0.05*0.05)
                self.amount_untaxed+=rec.price_subtotal
                rec.price_total_discount=rec.price_subtotal
                if rec.tax_id :
                    _logger.info('TAXES')
                    _logger.info(rec.tax_id.amount)
                    _logger.info(self.amount_tax)
                    self.amount_tax+=rec.price_subtotal*(rec.tax_id.amount/100)
                    self.price_total_discount=rec.price_subtotal*(rec.tax_id.amount/100)+rec.price_subtotal

        dif= self.amount_untaxed
        if self.discount=='1':
            
            _logger.info('self.amount_untaxed*0.15')
            _logger.info(self.amount_untaxed*0.15)
            self.amount_untaxed-=self.amount_untaxed*0.15
            _logger.info(self.amount_untaxed)
        if self.discount=='2':
            self.amount_untaxed-=(self.amount_untaxed*0.15)+(self.amount_untaxed*0.15*0.05)
        if self.discount=='3':
            dis_value=(self.amount_untaxed*0.15)+(self.amount_untaxed*0.15*0.05)+(self.amount_untaxed*0.15*0.05*0.05)
            price_discount=self.amount_untaxed-dis_value
            self.amount_untaxed-=(self.amount_untaxed*0.15)+(self.amount_untaxed*0.15*0.05)+(self.amount_untaxed*0.15*0.05*0.05)
         
        self.update({'amount_untaxed':self.amount_untaxed})
        if self.amount_tax:
            self.update({'amount_total':self.amount_untaxed+self.amount_tax})
        else:
            self.update({'amount_total':self.amount_untaxed+self.amount_tax})
        dif-=self.amount_untaxed
        for rec in self.order_line:
            rec.price_total_discount-=(dif/len(self.order_line))



    
class cancel_order(models.Model):
    _name="sale.order.cancelled"
    reason=fields.Selection([('A','A'),('B','B')],'Reason',required=True)
    comment_cancel=fields.Char('Comment')
    cancelled_order=fields.Many2one('sale.order')
    @api.constrains('reason','comment_cancel')
    def get_reaon(self):
        _logger.info('Reason')
        self.cancelled_order.reason=self.reason
        self.cancelled_order.comment_cancel=self.comment_cancel
        _logger.info(self.cancelled_order)
        
    @api.model
    def create(self,vals):
        _logger.info('CREATE')
        _logger.info(self.reason)
        return super(cancel_order,self).create(vals)
    
class sale_order_line(models.Model):
    _inherit='sale.order.line'
    discount2=fields.Selection([('1','15%'),('2','%15,5%'),('3','%15,%5,5%')],'Discount',store=True)
    price_total_discount=fields.Float('Total price Discount')
    @api.constrains('product_uom_qty')
    def get_nagtive_value(self):
        if self.product_uom_qty<0:
            raise ValidationError('Order Quantity must be postive value')

    @api.multi
    def write(self,values):
        _logger.info('writeeee')
        return super(sale_order_line,self).write(values)
    @api.multi
    @api.onchange('discount2','price_subtotal','tax_id')
    def calculated_discount(self):
        _logger.info('Change')
        _logger.info(self.discount2)
        if self.discount2:
            self.price_subtotal=self.product_uom_qty*self.price_unit
            if self.discount2=='1':
                self.price_subtotal-=self.price_subtotal*0.15
            if self.discount2=='2':
                self.price_subtotal-=(self.price_subtotal*0.15)+(self.price_subtotal*0.15*0.05)
            if self.discount2=='3':
                dis_value=(self.price_subtotal*0.15)+(self.price_subtotal*0.15*0.05)+(self.price_subtotal*0.15*0.05*0.05)
                price_discount=self.price_subtotal-dis_value
                self.price_subtotal-=(self.price_subtotal*0.15)+(self.price_subtotal*0.15*0.05)+(self.price_subtotal*0.15*0.05*0.05)
            if not self.discount2:
                self.price_subtotal=self.product_uom_qty*self.price_unit
          
 
         
    
    @api.onchange('product_uom_qty', 'product_uom', 'route_id')
    def _onchange_product_id_check_availability(self):
        _logger.info('FFFFFFFFFFFFFFFFFFF')
        if not self.product_id or not self.product_uom_qty or not self.product_uom:
            self.product_packaging = False
            return {}
        if self.product_id.type == 'product':
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            product = self.product_id.with_context(
                warehouse=self.order_id.warehouse_id.id,
                lang=self.order_id.partner_id.lang or self.env.user.lang or 'en_US'
            )
            product_qty = self.product_uom._compute_quantity(self.product_uom_qty, self.product_id.uom_id)
            if float_compare(product.virtual_available, product_qty, precision_digits=precision) == -1:
                is_available = self._check_routing()
                if not is_available:
                    message =  _('You plan to sell %s %s of %s but you only have %s %s available in %s warehouse.') % \
                            (self.product_uom_qty, self.product_uom.name, self.product_id.name, product.virtual_available, product.uom_id.name, self.order_id.warehouse_id.name)
                    # We check if some products are available in other warehouses.
                    if float_compare(product.virtual_available, self.product_id.virtual_available, precision_digits=precision) == -1:
                        message += _('\nThere are %s %s available across all warehouses.\n\n') % \
                                (self.product_id.virtual_available, product.uom_id.name)
                        for warehouse in self.env['stock.warehouse'].search([]):
                            quantity = self.product_id.with_context(warehouse=warehouse.id).virtual_available
                            if quantity > 0:
                                message += "%s: %s %s\n" % (warehouse.name, quantity, self.product_id.uom_id.name)
                    warning_mess = {
                        'title': _('Not enough inventory!'),
                        'message' : message
                    }
                    if warning_mess:
                        return {}

                    #return {'warning': warning_mess}
        return {}


class invoice_discount(models.Model):
    _inherit='account.invoice'
    discount=fields.Selection(related='partner_id.discount',string='Discount')
    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'tax_line_ids.amount_rounding',
                 'currency_id', 'company_id', 'date_invoice', 'type')
    def _compute_amount(self):
        _logger.info('depends account invoice')
        round_curr = self.currency_id.round
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        _logger.info('UN TAXE')
        _logger.info(self.amount_untaxed)
        if self.discount=='1':
            self.amount_untaxed-=self.amount_untaxed*0.15
        if self.discount=='2':
            self.amount_untaxed-=(self.amount_untaxed*0.15)+(self.amount_untaxed*0.15*0.05)
        if self.discount=='3':
            dis_value=(self.amount_untaxed*0.15)+(self.amount_untaxed*0.15*0.05)+(self.amount_untaxed*0.15*0.05*0.05)
            price_discount=self.amount_untaxed-dis_value
            self.amount_untaxed-=(self.amount_untaxed*0.15)+(self.amount_untaxed*0.15*0.05)+(self.amount_untaxed*0.15*0.05*0.05)
        _logger.info(self.amount_untaxed)
        self.update({'amount_untaxed':self.amount_untaxed})
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
     
    """@api.multi
    def action_move_create(self):
        _logger.info('action_move_create SALE CUST')
        """ Creates invoice related analytics and financial move lines """
        account_move = self.env['account.move']
        desc=0
        total_line=0
        for line in self.invoice_line_ids:
            total_line+=line.price_subtotal
        _logger.info('VALUE OF DISCOUNT')
        desc=abs((self.amount_untaxed-total_line))
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
                    _logger.info(t[1]-desc)
                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1]-desc,
                        'account_id': inv.account_id.id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
            else:
                _logger.info('TOTAL After Valdition')
                
              
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total-desc,
                    'account_id': inv.account_id.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'invoice_id': inv.id
                })
                _logger.info(total)
                _logger.info(type(total))
            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
            line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
            line = inv.group_lines(iml, line)

            line = inv.finalize_invoice_move_lines(line)
            account_discount=self.env['res.config.settings'].search([])
            account_discount_id=0
            if self.discount:
                for rec in account_discount:
                    if not rec.discount_account_id:
                        raise ValidationError('Please Select Account Discount...')
                    else :
                        account_discount_id=rec.discount_account_id.id

                line.append((0, 0, { 'partner_id': part.id, 'name': 'Discount', 'debit':desc , 'credit':False , 'account_id':account_discount_id , 'analytic_line_ids': [], 'amount_currency': 0, 'currency_id': False, 'quantity': 1.0, 'product_id': False, 'product_uom_id': False, 'analytic_account_id': False, 'invoice_id': inv.id, 'tax_ids': False, 'tax_line_id': False, 'analytic_tag_ids': False}))

            date = inv.date or inv.date_invoice
            move_vals = {
                'ref': inv.reference,
                'line_ids': line,
                'journal_id': inv.journal_id.id,
                'date': date,
                'narration': inv.comment,
            }
            move = account_move.create(move_vals)
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
        return True"""
        
class invoice_line_discount(models.Model):
    _inherit='account.invoice.line'
    discount2=fields.Selection(related='sale_line_ids.discount2',string='Discount')
    price_untaxes_discount=fields.Float('subtotal',compute="_compute_price")
    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
        'invoice_id.date_invoice', 'invoice_id.date')
    def _compute_price(self):
        _logger.info('COMPUTE PRICE')
        currency = self.invoice_id and self.invoice_id.currency_id or None
        price = self.price_unit 
        if self.discount2:
            if self.discount2=='1':
                price-=price*0.15
            if self.discount2=='2':
                price-=(price*0.15)+(price*0.15*0.05)
            if self.discount2=='3':
                dis_value=(price*0.15)+(price*0.15*0.05)+(price*0.15*0.05*0.05)
                price_discount=price-dis_value
                price-=(price*0.15)+(price*0.15*0.05)+(price*0.15*0.05*0.05)
        
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
        self.price_untaxes_discount=self.price_subtotal
""""class inherite_confi_setting(models.TransientModel):
    _inherit='res.config.settings'
    discount_account_id=fields.Many2one('account.account',string='Sale Discount Account',related='company_id.discount_account_id',readonly=False)
class ResCompany_discount(models.Model):
    _inherit = "res.company"
    discount_account_id=fields.Many2one('account.account',string='Sale Discount Account')"""

   
    
    
 