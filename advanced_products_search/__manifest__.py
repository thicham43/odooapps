# -*- coding: utf-8 -*-

{
    'name': "Advanced Products Search",
    'version': '1.0',
    'category': 'tools',
    'author': 'HichamTAROQ',
    'depends': ['sale'],
    'data': [
             'security/ir.model.access.csv',
             'views/assets.xml',
             'views/product_search_view.xml',
            ],
    'qweb': [
             "static/src/xml/m2m_selectable.xml"
            ],
    'installable': True,
    'application': True,
}
