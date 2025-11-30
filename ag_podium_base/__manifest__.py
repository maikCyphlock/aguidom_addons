{
    "name": "Aguidom Podium",
    "version": "18.0",
    "summary": "Module to manage podiums for sport clubs",
    "description": """
        This module allows sport clubs to manage podiums for their events.
        Features include:
        - Podium creation and management
        - Athlete ranking and statistics
        - Event scheduling and results tracking
    """,
    "author": "Maikol Aguilar",
    "website": "https://www.aguidom.me",
    "category": "Sports",
    "depends": ["base", "mail", "website"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "security/ir_rule.xml",
        "data/system_parameters.xml",
        "views/club_view.xml",
        "views/partner_view.xml",
        "views/category_view.xml",
        "views/athlete_view.xml",
        "views/payment_view.xml",
        "views/attendance_view.xml",
        "views/report_payment.xml",
        "views/menuitem.xml",
        "views/portal_templates.xml",
        "views/website_templates.xml",
        "views/layout_templates.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ag_podium_base/static/src/components/**/*",
        ],
        "web.assets_frontend": [
            "ag_podium_base/static/src/css/style.css",
        ],
    },
    "installable": True,
}