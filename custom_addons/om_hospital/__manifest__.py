{
    'name': 'Hospital Management System',
    'author': 'Walnut Software Solutions ',
    'license': 'LGPL-3',
    'version': '17.0.1.0',
    'summary': 'Hospital Management System',
    'depends': ['base','mail'],
    'installable': True,
    'application': True,
    'data': [
    'security/ir.model.access.csv',
     'data/sequence.xml',
     'views/patient_view.xml',
     'views/patient_readonly_view.xml',
     'views/appointment_view.xml',
     'views/menu.xml',          # Loads last
],
}