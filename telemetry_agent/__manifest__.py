{
    'name': 'Telemetry Agent',
    'author': 'TuEmpresa',
    'version': '1.0',
    'category': 'Tools',
    'summary': 'Report installed module versions to HQ',
    'depends': ['base', 'base_setup'],
    'data': [
        'views/res_config_settings_views.xml',
        'data/cron.xml',
    ],
    'installable': True,
    'application': False,
}
