# -*- coding: utf-8 -*-
{
    'name': "Check Management",

    'summary': """ Check Management  """,

    'description': """
        This Module is used for check \n
        It includes creation of check receipt ,check cycle ,Holding ....... \n

    """,

    'author': "BBL",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'native',
    'version': '12.0.1.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account','sales_regions'],#' 'account_accountant', 'sale'

    # always loaded
    'data': [
         #'security/check_security.xml',
        
        'views/account_journal_view.xml',
        'views/checks_fields_view.xml',
        'views/check_payment.xml',
        'views/check_menus.xml',
        'wizard/check_cycle_wizard_view.xml',
        'views/payment_report.xml',
        'views/report_check_cash_payment_receipt_templates.xml',
        'security/ir.model.access.csv'

         

    ],
    'qweb': [],
    # only loaded in demonstration mode
    'demo': [],
    'application': True,

}
