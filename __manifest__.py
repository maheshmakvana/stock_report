{
    'name': 'Product Stock Location and Category Wise Report',
    'summary': 'Product Stock Report',
    'description': """
    Report
    """,
    'category': 'Report',
    'version': '12.0',
    'author': 'JP',
    'website': ' ',
    'depends': ['stock','purchase','sale'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/location_wise_report_view.xml',
    ],
    "sequence": 1,
    'installable': True,
    'application': False,
    'price': 5,
    'currency': "EUR",
}
