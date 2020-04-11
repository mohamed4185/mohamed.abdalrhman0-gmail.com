{
    'name': 'Bank Cheques Report',
    'version': '12.0.1.0.8',
    'summary': 'Module all Cheques of Bank .',
    'sequence': 16,
    'category': 'Account',
    'author': 'BBl',
    "license": "AGPL-3",
    'depends': ['account', 'sales_regions', 'sale'],
    'data': [
             'wizard/wiz_bank_cheques_view.xml',
             'views/bank_cheques_view.xml',
             'views/report_bank_cheques.xml',
             ],

    'installable': True,
}
