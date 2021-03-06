{
 'name':'Spot Insight',
 'summary':'Explore smart media marketing',
 'description':'App for media marketing to explore spot data from Instar or any other source of spot data',
 'application':True,
 'author':'sshokot',
 'category':'Uncategorized',
 'version':'14.0.1',
 'email':'sshokot@gmail.com',
# 'depends': ['website'],
 'data':['security/groups.xml',
         'security/ir.model.access.csv',
         'views/raw_data.xml',
         'views/base_data.xml',
         'views/storage_data.xml',
         'views/analytic_data.xml',
 #        'views/templates.xml',
         'wizard/import_wizard.xml',
         'wizard/etl_wizard.xml'],
 'qweb':['static/src/xml/read_raw.xml',
         'static/src/xml/read_raw_js.xml',
         ],
}
