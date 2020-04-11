from odoo import api ,models, fields,_
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError,UserError
import logging 
from datetime import datetime, timedelta,date
import datetime as dt
import calendar
_logger = logging.getLogger(__name__)
from num2words import num2words
class payment_reciept(models.Model):
    _inherit='account.payment'

    logo=fields.Binary(related="partner_id.company_id.logo")
    payment_related_journal=fields.Boolean('Payment related journal' ,default=False)
    name_check=fields.Char(default='')
    recieve_text=fields.Text("رقــــم الحافــظه")
   
    customer=fields.Many2one('res.partner',string="Customer Name",domain="[('customer','=',True)]")
    sales_rep=fields.Many2one('res.users',string="Sales Rep")
    others=fields.Char("Others")
    analytical_account=fields.Many2one("account.analytic.account",string="Analytical Account")
    ref_number=fields.Char("Ref.Number")
    account_id=fields.Many2one("account.account",string="Account",domain="[('user_type_id.type','!=','view')]")
    partner_type = fields.Selection([('customer', 'Customer'), ('supplier', 'Vendor'),('miscellaneous','Miscellaneous')])
    amount_to_text = fields.Char(compute='_amount_in_words', string='amount In Words', help="The amount in words")
    sales_rep_or_other=fields.Boolean("check" ,default=False)
    # total_inv_payment = fields.float('total payments')
    

    @api.onchange("others")
    def get_sales_rep(self):
        if  self.others:
            self.sales_rep_or_other=True
        else:
            self.sales_rep_or_other=False
    @api.constrains("others")
    def save_sales_rep(self):
        if  self.others:
            self.sales_rep_or_other=True
        else:
            self.sales_rep_or_other=False


    @api.onchange("sales_rep","partner_id")
    def get_domain(self):
        user=self.env['res.users'].search([('id','=',self.env.uid)])
        domain=[]
        if self.partner_id.user_id and not self.sales_rep :
            self.sales_rep=self.partner_id.user_id.id
        if user.lang=='ar_AA' or user.lang=='ar_SY':
            domain.append(('groups_id.name','=','مستخدم: مبيعاته فقط'))
        if user.lang=="en_US":
            domain.append(('groups_id.name','=','User: Own Documents Only'))
          
        return {'domain':{'sales_rep':domain}}
        
    @api.one
    @api.depends('amount')
    def _amount_in_words(self):
        
        self.amount_to_text = num2words(self.amount, lang='ar')
    _sql_constraints = [('ref_number_unique', 'unique(ref_number)', 'Ref.Number already exists!')]

    def _get_shared_move_line_vals(self, debit, credit, amount_currency, move_id, invoice_id=False):
        """ Returns values common to both move lines (except for debit, credit and amount_currency which are reversed)
        """
        if self.analytical_account:

            return {
                'partner_id': self.payment_type in ('inbound', 'outbound') and self.env['res.partner']._find_accounting_partner(self.partner_id).id or False,
                'invoice_id': invoice_id and invoice_id.id or False,
                'move_id': move_id,
                'debit': debit,
                'credit': credit,
                'amount_currency': amount_currency or False,
                'payment_id': self.id,
                'journal_id': self.journal_id.id,
                'analytic_account_id':self.analytical_account.id
            }
        else:
            return {
                'partner_id': self.payment_type in ('inbound', 'outbound') and self.env['res.partner']._find_accounting_partner(self.partner_id).id or False,
                'invoice_id': invoice_id and invoice_id.id or False,
                'move_id': move_id,
                'debit': debit,
                'credit': credit,
                'amount_currency': amount_currency or False,
                'payment_id': self.id,
                'journal_id': self.journal_id.id,

            }
    @api.onchange('partner_type','payment_type')
    def _onchange_partner_type(self):
        if self.payment_type == 'inbound':
            if self.partner_type=='miscellaneous':
                raise ValidationError(_("you can't choose miscellaneous when the payment type is Receive money ."))
    @api.onchange('ref_number')
    def get_unique_ref_number(self):
        if self.ref_number:
          for rec in self.search([]):
            if rec.ref_number==self.ref_number and rec.id!=self.id:
                raise ValidationError('_ Referance Number is unique')
    @api.constrains('payment_type')
    def get_payment_type(self):
        _logger.info('dddddddddddddddddddddd')
        self.name_check=''
        id=9999
        
         
        if len(str( self.id))>=4:
                self.name_check=+str( self.id)
        else:
            for i in range(0,4-len(str(abs(self.id)))):
                self.name_check+='0'
            self.receipt_number=self.name_check+str(self.id)
            self.name_check=self.name_check+str(self.id)
        _logger.info('CHECK NAME')
        _logger.info(type(self.id))
        _logger.info(4-len(str(abs(self.id))))
        _logger.info(self.name_check)

    def _get_counterpart_move_line_vals(self, invoice=False):
        if self.payment_type == 'transfer':
            name = self.name
        else:
            name = ''
            if self.partner_type == 'customer':
                if self.payment_type == 'inbound':
                    name += _("Customer Payment")
                elif self.payment_type == 'outbound':
                    name += _("Customer Credit Note")
            elif self.partner_type == 'supplier':
                if self.payment_type == 'inbound':
                    name += _("Vendor Credit Note")
                elif self.payment_type == 'outbound':
                    name += _("Vendor Payment")
            if invoice:
                name += ': '
                for inv in invoice:
                    if inv.move_id:
                        name += inv.number + ', '
                name = name[:len(name)-2]
        if not self.destination_account_id:
            self.destination_account_id=self.account_id

        return {
            'name': name,
            'account_id': self.destination_account_id.id,
            'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
        }
    
    @api.multi
    def post(self):
        """ Create the journal items for the payment and update the payment's state to 'posted'.
            A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
            and another in the destination reconcilable account (see _compute_destination_account_id).
            If invoice_ids is not empty, there will be one reconcilable move line per invoice to reconcile with.
            If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
        """
        for rec in self:

            if rec.state != 'draft':
                raise UserError(_("Only a draft payment can be posted."))

            if any(inv.state != 'open' for inv in rec.invoice_ids):
                raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))

            # keep the name in case of a payment reset to draft
            if not rec.name:
               
                # Use the right sequence to set the name
                if rec.payment_type == 'transfer':
                    sequence_code = 'account.payment.transfer'
                else:
                    if rec.partner_type == 'customer':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.customer.invoice'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.customer.refund'
                    if rec.partner_type == 'supplier':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.supplier.refund'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.supplier.invoice'

                    if rec.partner_type=='miscellaneous':
                        sequence_code = 'account.payment.supplier.refund'
                       
                rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(sequence_code)
                if not rec.name and rec.payment_type != 'transfer':
                    raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))

            # Create the journal entry
            amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
            move = rec._create_payment_entry(amount)

            # In case of a transfer, the first journal entry created debited the source liquidity account and credited
            # the transfer account. Now we debit the transfer account and credit the destination liquidity account.
            if rec.payment_type == 'transfer':
                transfer_credit_aml = move.line_ids.filtered(lambda r: r.account_id == rec.company_id.transfer_account_id)
                transfer_debit_aml = rec._create_transfer_entry(amount)
                (transfer_credit_aml + transfer_debit_aml).reconcile()

            rec.write({'state': 'posted', 'move_name': move.name})
        return True
    def _get_liquidity_move_line_vals(self, amount):
        name = self.name
        if self.payment_type == 'transfer':
            name = _('Transfer to %s') % self.destination_journal_id.name
        vals = {
            'name': name,
            'account_id': self.payment_type in ('outbound','transfer') and self.journal_id.default_debit_account_id.id or self.journal_id.default_credit_account_id.id,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
        }

        # If the journal has a currency specified, the journal item need to be expressed in this currency
        if self.journal_id.currency_id and self.currency_id != self.journal_id.currency_id:
            amount = self.currency_id._convert(amount, self.journal_id.currency_id, self.company_id, self.payment_date or fields.Date.today())
            debit, credit, amount_currency, dummy = self.env['account.move.line'].with_context(date=self.payment_date)._compute_amount_fields(amount, self.journal_id.currency_id, self.company_id.currency_id)
            vals.update({
                'amount_currency': amount_currency,
                'currency_id': self.journal_id.currency_id.id,
            })

        return vals

    @api.constrains('state','name')
    def get_state(self):
        parent_id=''
        for rec in self.message_ids:
            _logger.info(rec)
            
            parent_id=rec.id
            break
                
        channel_ids=self.env['mail.channel'].search([('name','=','Accountant Notification')])
        adv_channel=self.env['mail.channel'].search([('name','=','Advisor Notification')])
        user=self.env['res.users'].search([('id','=',self.env.uid)])
        group_id=self.env['ir.model.data'].search([('name','=','group_account_manager')])
        group_user = self.env['res.groups'].search([('id','=',group_id.res_id)]) 
        _logger.info("Group User")
        _logger.info(group_user.users)
        partner_list=[]
        if self.state=='draft' :
            # self.name="payment is draft  "+str(self.id)
            for rec in group_user.users:
                partner_user=self.env['res.users'].search([('id','=',rec.id)]).partner_id.id
                
                _logger.info(partner_user)
                if rec.id!=self.env.uid:
                   partner_list.append(partner_user)
        if  partner_list:
            value={
            'body':"create new payment :"+str(self.id) +"   by "+str(user.name),
            'res_id':self.id,
            'model':'account.payment',
            'message_type':'notification',
            'parent_id':parent_id,
            'needaction_partner_ids':[(6,0,partner_list)]
            
            }
            self.message_ids.create(value)
class move_line(models.Model):
     _inherit='account.move.line'
   
     @api.onchange('partner_id')
     def _get_account_id(self):
        _logger.info("7877")
        if self.partner_id:
                _logger.info("7777")
                if self.partner_id.property_account_receivable_id and self.partner_id.customer==True:
                     _logger.info(self.partner_id.property_account_receivable_id.name)
                     self.account_id=self.partner_id.property_account_receivable_id.id
                     #return {'domain':{'account_id':[('id','=',self.partner_id.property_account_receivable_id.id)]}}
        


        
        
        