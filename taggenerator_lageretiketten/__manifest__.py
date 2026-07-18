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
        'stock',
    ],
    'data': [
        'data/config.xml',
        'views/label_batch_views.xml',  # Muss VOR menu.xml kommen (definiert die Actions)
        'views/menu.xml',                # Referenziert die Actions
    ],
    'external_dependencies': {
        'python': ['reportlab'],
    },
    'installable': True,
    'auto_install': False,
}
