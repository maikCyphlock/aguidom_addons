{
    'name': "Avícola Management",
    'summary': "Gestión integral de granjas avícolas",
    'description': """
        Sistema de gestión para producción avícola con:
        - Dashboard en tiempo real con OWL
        - Control de galpones y lotes
        - Registro de mortalidad y recolección
        - Alertas críticas (temperatura, stock, mortalidad)
        - Gráficos de crecimiento y conversión alimenticia
    """,
    'author': "MAIKOL AGUILAR",
    'website': "https://github.com/maikol-aguilar",
    'category': 'Operations/Agriculture',
    'version': '1.0',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/menu_views.xml',
        'views/galpon_views.xml',
        'views/lote_views.xml',
        'views/alimento_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js',
            'https://cdn.jsdelivr.net/npm/fullcalendar@6.1.10/index.global.min.js',
            'https://cdn.jsdelivr.net/npm/driver.js@1.0.1/dist/driver.js.iife.js',
            'https://cdn.jsdelivr.net/npm/driver.js@1.0.1/dist/driver.css',
            'avicola_management/static/src/dashboard/*',
            'avicola_management/static/src/components/*',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
