{
    'name': "Customer Annual Sales Report",
    'summary': """Customer Annual Sales Report""",
    'author': 'BBL',
    'website': '',
    'category': 'Sale Custimization',
    'version': '12.0.1.0.8',
    'depends': ['sale','account','sales_regions','cst_attributes','Sales_Vs_Forecast Report'],
    'data': ['views/consolidate_menu.xml','views/consolidate_action.xml','secuirty/ir.model.access.csv','views/customer_annual_templete.xml','views/report_customer_annual_templete.xml'],
    'demo': [
    ],
    'qweb': [
        
    ],
    'auto-install':True,
	'Sequence':101
     
}