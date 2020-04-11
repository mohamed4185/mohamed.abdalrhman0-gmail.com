# -*- coding: utf-8 -*-

from odoo import api ,models, fields
from odoo.exceptions import ValidationError 
class cst_attribute(models.Model):
 _name = 'cst.attribute'
 attribute_name = fields.Selection([('Broiler','Broiler'),('Breeders','Breeders'),('Layers','Layers'),('Grandparents','Grandparents')])
 attribute_value = fields.Char('Attribute Value',Required=True)
 customer = fields.Many2one('res.partner',string='Customer' ,Required=True)
 @api.constrains('attribute_value')
 def get_attribute_value(self):
     if self.attribute_value:
         if self.attribute_value.isdigit()==False:
             raise ValidationError('Attribute Value must be digits')

