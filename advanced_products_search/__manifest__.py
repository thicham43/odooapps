# -*- coding: utf-8 -*-

{
    'name': "Advanced Products Search for Sales",
    'version': '1.0',
    'summary': "Advanced way to search products inside sale quotations/orders",
    'description': """ 
                    Enhanced products search
                    ========================
                    Advanced way to search products in large catalogs or databases.
                    User friendly and saves you precious time when working on your sales quotations or orders 
                   """,
    'category': 'tools',
    'author': 'HichamTAROQ',
    'website': 'https://github.com/thicham43',
    'depends': ['sale'],
    'data': [
             'security/ir.model.access.csv',
             'views/assets.xml',
             'views/product_search_view.xml',
             'views/sale_order_view.xml',
            ],
    'qweb': ['static/src/xml/m2m_selectable.xml'],
    'images': ['static/src/description/banner.png'],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
