# -*- coding: utf-8 -*-

from odoo import api, fields ,models
from odoo.exceptions import ValidationError 
import logging
import pytz
_logger = logging.getLogger(__name__)
ADDRESS_FIELDS = ('street', 'street2', 'zip', 'city', 'state_id', 'country_id')
_tzs = [(tz, tz) for tz in sorted(pytz.all_timezones, key=lambda tz: tz if not tz.startswith('Etc/') else '_')]
def _tz_get(self):
    return _tzs
@api.model
def _lang_get(self):
    return self.env['res.lang'].get_installed()
class ResPartner(models.Model):
    _name="res.partner.commerical"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description="Non Commerical Customer"
    def _default_category(self):
        return self.env['res.partner.category'].browse(self._context.get('category_id'))

    def _default_company(self):
        return self.env['res.company']._company_default_get('res.partner')

    def _split_street_with_params(self, street_raw, street_format):
        return {'street': street_raw}

    name = fields.Char(index=True)
    display_name = fields.Char(compute='_compute_display_name', store=True, index=True)
    date = fields.Date(index=True)
    title = fields.Many2one('res.partner.title')
    
    ref = fields.Char(string='Internal Reference', index=True)
    lang = fields.Selection(_lang_get, string='Language', default=lambda self: self.env.lang,
                            help="All the emails and documents sent to this contact will be translated in this language.")
    tz = fields.Selection(_tz_get, string='Timezone', default=lambda self: self._context.get('tz'),
                          help="The partner's timezone, used to output proper date and time values "
                               "inside printed reports. It is important to set a value for this field. "
                               "You should use the same timezone that is otherwise used to pick and "
                               "render date and time values: your computer's timezone.")
    tz_offset = fields.Char(compute='_compute_tz_offset', string='Timezone offset', invisible=True)
    user_id = fields.Many2one('res.users', string='Salesperson',
      help='The internal user in charge of this contact.')
    vat = fields.Char(string='Tax ID', help="The Tax Identification Number. Complete it if the contact is subjected to government taxes. Used in some legal statements.")
    
    website = fields.Char()
    comment = fields.Text(string='Notes')

    category_id = fields.Many2many('res.partner.category', column1='partner_id',
                                    column2='category_id', string='Tags', default=_default_category)
    credit_limit = fields.Char(string='Credit Limit')
    barcode = fields.Char(oldname='ean13', help="Use a barcode to identify this contact from the Point of Sale.")
    active = fields.Boolean(default=True)
    customer = fields.Boolean(string='Is a Customer', default=True,
                               help="Check this box if this contact is a customer. It can be selected in sales orders.")
    
    
    
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    email = fields.Char()
   
    email_formatted = fields.Char(
        'Formatted Email', compute='_compute_email_formatted',
        help='Format email address "Name <email@domain>"')
    phone = fields.Char()
    mobile = fields.Char()
    is_company = fields.Boolean(string='Is a Company', default=False,
        help="Check if the contact is a company, otherwise it is a person")
     
    company_type = fields.Selection(string='Company Type',
        selection=[('person', 'Individual'), ('company', 'Company')],
        compute='_compute_company_type', inverse='_write_company_type')
    company_id = fields.Many2one('res.company', 'Company', index=True, default=_default_company)
    color = fields.Integer(string='Color Index', default=0)
    user_ids = fields.Many2one('res.users', string='Sales Rep')
   
    contact_address = fields.Char(compute='_compute_contact_address', string='Complete Address')
    
    # technical field used for managing commercial fields
 
    company_name = fields.Char('Company Name')

    # image: all image fields are base64 encoded and PIL-supported
    image = fields.Binary("Image", attachment=True,
        help="This field holds the image used as avatar for this contact, limited to 1024x1024px",)
    image_medium = fields.Binary("Medium-sized image", attachment=True,
        help="Medium-sized image of this contact. It is automatically "\
             "resized as a 128x128px image, with aspect ratio preserved. "\
             "Use this field in form views or some kanban views.")
    image_small = fields.Binary("Small-sized image", attachment=True,
        help="Small-sized image of this contact. It is automatically "\
             "resized as a 64x64px image, with aspect ratio preserved. "\
             "Use this field anywhere a small image is required.")
    
    arabic_name=fields.Char('Arabic Name',size=100)
    customer_Type=fields.Selection([('key Account','key Account'),('Consultant','Consultant'),('Doctor','Doctor'),('Pharmacy','Pharmacy'),('Farm','Farm'),('Distributor','Distributor'),('Other','Other')] ,'Type',required=True)
    customer_class=fields.Selection([('A','A'),('B','B'),('C','C'),('D','D')],'Class')
    region=fields.Many2one('sale.region',string="Region",required=True)
    # hack to allow using plain browse record in qweb views, and used in ir.qweb.field.contact
    customer_code=fields.Char('Customer Code',size=10)
    credit_limit=fields.Char('Credit Limit')
    credit_duration=fields.Selection([('cash','cash'),('3 Months','3 Months'),('Stopped Deals','Stopped Deals'),('Unknown','Unknown')] ,'Customer Payment term')
    credit_duration_from=fields.Date('Credit Duration From')
    credit_duration_to=fields.Date('Credit Duration To')
    property_account_payable_id = fields.Many2one('account.account', company_dependent=True,
        string="Account Payable", oldname="property_account_payable",
        domain="[('internal_type', '=', 'payable'), ('deprecated', '=', False)]",
        help="This account will be used instead of the default one as the payable account for the current partner",
        )
    property_account_receivable_id = fields.Many2one('account.account', company_dependent=True,
        string="Account Receivable", oldname="property_account_receivable",
        domain="[('internal_type', '=', 'receivable'), ('deprecated', '=', False)]",
        help="This account will be used instead of the default one as the receivable account for the current partner",
        )
    reason=fields.Text("Reason")
    reason_reject=fields.Text("Reason for Reject")
    state=fields.Selection([('draft','Draft'),('sale_manager_con','Sales Manager Confrim'),('account_manager_con','Account Manager Confirm')],string="State",default='draft')
    national_id=fields.Text("National ID")
    tax_file=fields.Text("Tax File")
    discount=fields.Many2one('sales.discount',string='Discount')
     
    _sql_constraints = [
        ('check_name', "CHECK( (type='contact' AND name IS NOT NULL) or (type!='contact') )", 'Contacts require a name.'),
    ]
    _sql_constraints = [('customer_code_unique', 'unique(customer_code)', 'customer code already exists!')]

    # @api.constrains('customer_code')
    # def get_unique_customer_code(self):
    #     for rec in self.search([]):
    #         if rec.customer_code==self.customer_code and rec.id!=self.id:
    #             raise ValidationError('customer code is unique')
    @api.onchange('name')
    def get_user(self):
        if not self.user_ids:
            self.user_ids=self.env.uid
        self.display_name=self.name
    @api.depends('name', 'email')
    def _compute_email_formatted(self):
        for partner in self:
            if partner.email:
                partner.email_formatted = formataddr((partner.name or u"False", partner.email or u"False"))
            else:
                partner.email_formatted = ''
    
    @api.constrains('name')
    def get_display_name(self):
        self.display_name=self.name
    @api.depends('is_company')
    def _compute_company_type(self):
        for partner in self:
            partner.company_type = 'company' if partner.is_company else 'person'
    def _write_company_type(self):
        for partner in self:
            partner.is_company = partner.company_type == 'company'
    def set_confirm1(self):
        
        if not self.property_account_payable_id :
                raise ValidationError('please add payable account.......')
        if not self.property_account_receivable_id:
            raise ValidationError('please add receivable account.......')
        if not self.credit_limit :
            raise ValidationError('please add Credit Limit.......')
        if not self.credit_duration_from:
            raise ValidationError('please add Credit Duration From.......')
        if not self.credit_duration:
            raise ValidationError('please add Credit Duration .......')
        if not self.credit_duration_to:
            raise ValidationError('please add Credit Duration To.......')
        if not self.customer_code:
            raise ValidationError('please add Customer Code.......')
        if not self.vat:
            raise ValidationError('please add Vat.......')    
        elif self.state=='sale_manager_con':
           

            self.state='account_manager_con'
            values={}
            partner=self.env['res.partner'].search([])
            for rec in partner:
               if rec.customer_code==self.customer_code and rec.id!=self.id:
                raise ValidationError('customer code is unique')
            values={'name':self.name,'title':self.title.id,'lang':self.lang,'tz':self.tz,'user_id':self.user_ids.id,'vat':self.vat,'website':self.website,'comment':self.comment,'category_id':self.category_id.id,
            'credit_limit':self.credit_limit,'barcode':self.barcode,'customer':self.customer,'street':self.street,'street2':self.street2,'zip':self.zip,'city':self.city,'state_id':self.state_id.id,'country_id':self.country_id.id,'email':self.email,'phone':self.phone,
            'mobile':self.mobile,'is_company':self.is_company,'company_type':self.company_type,'company_id':self.company_id.id,'company_name':self.company_name,'arabic_name':self.arabic_name,'customer_Type':self.customer_Type,'customer_class':self.customer_class,'region':self.region.id,'customer_code':self.customer_code,'credit_duration':self.credit_duration,'credit_duration_from':self.credit_duration_from,'credit_duration_to':self.credit_duration_to,'property_account_payable_id':self.property_account_payable_id.id,'property_account_receivable_id':self.property_account_receivable_id.id}
            customer_new=self.env['res.partner']
            customer_new.create(values)
        for record in self:
            if not self.env['ir.attachment'].search([('res_model','=', self._name), ('res_id','=', record.id)], limit = 1):
                raise ValidationError("Please attach document" )

    def set_confirm(self):
        
        if not self.credit_limit :
                raise ValidationError('please add Credit Limit.......')
        if not self.credit_duration_from:
            raise ValidationError('please add Credit Duration From.......')
        if not self.credit_duration:
            raise ValidationError('please add Credit Duration .......')
        if not self.credit_duration_to:
            raise ValidationError('please add Credit Duration To.......')    
        
        for record in self:
            if not self.env['ir.attachment'].search([('res_model','=', self._name), ('res_id','=', record.id)], limit = 1):
                raise ValidationError("Please attach document" )
        if self.state=='draft':
            self.state='sale_manager_con'

    def set_return(self):
         
        if self.state=='sale_manager_con':
            self.state='draft'
        elif self.state=='account_manager_con':
            self.state='sale_manager_con'
        non_commerical=self.env['res.partner.commerical'].search([('id','=',self.id)])
        return { 'name':'Reason for Return',
         'view_type': 'form',
        'view_mode': 'form',
        'res_model': 'res.partner.commerical',
        'target': 'new',
         'view_type': 'form',
        'view_id':self.env.ref('non_commerical.view_partner_form_non_commerical_pop').id ,
        'target': 'new',
        'context':{'default_reason': self.reason},
        'nodestroy': True,
        'res_id':non_commerical.id,
        'flags': {'form': {'action_buttons': True}} ,
        'type': 'ir.actions.act_window', }
        
    @api.constrains('reason')
    def get_reason(self):
        if self.reason:
            value={
                'body':"Reason return :"+self.reason,
                'res_id':self.id,
                'model':'res.partner.commerical',
                'message_type':'notification',
                'subject':self.reason,
                 

                }
            
        
            self.message_ids.create(value)
    @api.constrains('reason_reject')
    def get__reject_reason(self):
        if self.reason_reject:
            value={
                'body':"Reason Reject:"+self.reason_reject,
                'res_id':self.id,
                'model':'res.partner.commerical',
                'message_type':'notification',
                'subject':self.reason_reject,
                 

                }
            
        
            self.message_ids.create(value)
     
    def set_reject(self):
        
        self.active=False
        return { 'name':'Reason for reject',
         'view_type': 'form',
        'view_mode': 'form',
        'res_model': 'res.partner.commerical',
        'target': 'new',
         'view_type': 'form',
        'view_id':self.env.ref('non_commerical.view_partner_form_non_commerical_pop_reject').id ,
        'target': 'new',
        'context':{'default_reason': self.reason},
        'nodestroy': True,
        'res_id':self.id,
        'flags': {'form': {'action_buttons': True}} ,
        'type': 'ir.actions.act_window', }


    @api.constrains('state')
    def get_state(self):
        user_id=self.env['res.users'].search([('id','=',self.env.uid)])
        region=self.env['sale.region'].search([('id','=',self.region.id)])
        manager=0
        if region.area_check==True:
            manager=region.sale_manager.id
        else:
            
            manager=region.sale_manager_id

        parent_id=False
        for rec in self.message_ids:
            _logger.info(rec)
            
            parent_id=rec.id
            break
        _logger.info("manager")
        _logger.info(manager)
        
        partner_list=[] 
        if self.state=='draft' and manager and self.name: 
             

            value={
                'body':"create New commerical customer "+self.name,
                'res_id':self.id,
                'parent':parent_id,
                'model':'res.partner.commerical',
                'message_type':'notification',
                'subject':'create commerical customer',
                'needaction_partner_ids':[(4,manager)]

                }
            
            
        
            self.message_ids.create(value)
        elif self.state=='sale_manager_con':

            manager=self.env['res.users'].search([('id','=',manager)]).partner_id.id
            group_id=self.env['ir.model.data'].search([('name','=','group_account_manager')])
            group_user = self.env['res.groups'].search([('id','=',group_id.res_id)]) 
            _logger.info("SALES CONFRIM")
            
            _logger.info(group_id)
            _logger.info(group_user.id)
            partner_list=[] 
            users=self.env['res.users'].search([('groups_id','=',group_user.id)])

            for rec in users:
                _logger.info(rec)
                partner_user=rec.partner_id.id
                
                partner_list.append(partner_user)
            _logger.info("PARTNER USER")
            _logger.info(partner_list)
            value={
                'body':"Sales Manager confrim commerical customer "+self.name+"  by:"+ user_id.name,
                'res_id':self.id,
                'parent':parent_id,
                'model':'res.partner.commerical',
                'message_type':'notification',
                'subject':'confrim commerical customer',
                'needaction_partner_ids':[(6,0,partner_list)]
                 

                }
           
            _logger.info(value)
            self.message_ids.create(value)
class Partner_user(models.Model):
    _inherit='res.partner'
    national_id=fields.Text("National ID" ,required=True)
    tax_file=fields.Text("Tax File",required=True)
    comment = fields.Text(string='Notes')