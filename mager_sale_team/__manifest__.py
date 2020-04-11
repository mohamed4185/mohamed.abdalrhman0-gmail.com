# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Manager sales Teams',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Manager Sales Team',
    'description': """
Using this application you can manage Sales Team  with CRM and/or Sales 
=======================================================================
 """,
    'website': 'https://www.BusinessBorderlines.com/',
    'depends': ['base','sales_team','sale'],
    'data': [ 
             'views/sales_team_dashboard.xml',
			 'secuirty/user_group_rights.xml'
             ],
    
   
    'demo': [],
    'installable': True,
    'auto_install': False,
}
