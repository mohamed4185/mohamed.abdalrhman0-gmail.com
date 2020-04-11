# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Sales Access  Rights',
    'version': '1.0',
    'category':'base',
    'summary': 'Sales Access  Rights',
     
    'author':'BBL',
    'website': 'https://www.BusinessBorderlines.com/',
    'depends': ['sale','stock','hr','base'],
    'data': [ 
             'secuirty/user_group_rights.xml','secuirty/ir.model.access.csv'
             ],
    
    
    'demo': [],
    'installable': True,
    'auto_install': False,
}
