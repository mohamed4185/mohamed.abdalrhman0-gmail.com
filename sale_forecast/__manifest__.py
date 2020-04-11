 
{
    'name': 'Sale Forecast',
    'category': 'sales',
    'summary': 'Sales Forecasting',
    'version': '1.0',
    'description': """
    """,
    'author': 'BBL',
    "website": "",
    "license": "AGPL-3",
    'depends': ['product','sales_regions','product'],
    'data': [
        'views/sale_forecast_view.xml',
        'security/ir.model.access.csv',
        'security/user_group.xml',


    ],
    'installable': True,
    'auto_install': True,
}
