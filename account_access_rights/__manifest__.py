# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Account Access  Rights',
    'version': '1.0',
    'category':'base',
    'summary': 'Account Access  Rights',
     
    'author':'BBL',
    'website': 'https://www.BusinessBorderlines.com/',
    'depends': ['account','hr_expense','sales_regions','account_parent','bi_import_chart_of_accounts','sale','check_managementtttt','account_budget','budget_customization','chart_account_customization','journal-account','payment_reciept'],
    'data': [ 
             'secuirty/user_group_rights.xml','secuirty/ir.model.access.csv','views/journal_enteries_parent_view.xml'
             ],
    
    
    'demo': [],
    'installable': True,
    'auto_install': False,
}
