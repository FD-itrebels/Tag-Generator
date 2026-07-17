{
    'name': 'Lageretiketten Generator',
    'version': '19.1.0',
    'category': 'Inventory',
    'summary': 'Generiert farbcodierte Batch-PDF-Etiketten aus Lagerexport mit QR-Codes',
    'author': 'Lager-IT',
    'website': 'https://github.com/yourgithub/taggenerator',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
    ],
    'data': [
        'data/config.xml',
        'views/menu.xml',
        'views/label_batch_views.xml',
    ],
    'external_dependencies': {
        'python': ['reportlab'],
    },
    'installable': True,
    'auto_install': False,
}
