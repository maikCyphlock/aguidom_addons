{
    'name': 'Mecatec Management',
    'version': '1.0',
    'category': 'Services',
    'summary': 'Inventory, Maintenance, and Appointment Management for Mecatec',
    'description': """
        Mecatec Module for managing:
        - Inventory
        - Maintenance Requests
        - Appointments
        - Vehicles
        - Clients (Venezuelan Context)
    """,
    'author': 'Antigravity',
    'depends': ['base', 'stock', 'maintenance', 'fleet'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/inventory_views.xml',
        'views/maintenance_views.xml',
        'views/vehicle_views.xml',
        'views/appointment_views.xml',
        'views/client_views.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'application': True,
}
