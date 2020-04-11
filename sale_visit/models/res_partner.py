# -*- coding: utf-8 -*-

from odoo import fields ,models

class cst_segmentation(models.Model):
    _inherit="res.partner"

    customer_Segment = fields.Selection([('Key Account','Key Account'),('Farm','Farm'),('Distributor','Distributor'),('Pharmacy','Pharmacy'),('Doctors','Doctors'),('Consultant','Consultant')])
