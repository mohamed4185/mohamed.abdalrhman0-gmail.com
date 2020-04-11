{
    'name': 'Sales Regions',
    'version': '10.0.1.0.0',
    "category": "Generic Modules/Sales",
 
    'author': 'BBL',
    'company': 'BusinessBorderlines',
    'website': 'www.BusinessBorderlines.com',
    'data':['views/region_menu.xml','views/region_view.xml','secuirty/ir.model.access.csv','secuirty/user_group_rights.xml'],
    'depends': ['sale','base','cst_attributes','sales_team'],
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
