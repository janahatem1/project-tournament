
from odoo import api, fields, models

class HospitalPatient(models.Model):
    _name = 'hospital.patient'
    _inherit = ['mail.thread.cc']
    _description = 'Patient Mater'

    name = fields.Char(string='Name', required=True , tracking=True)
    date_of_birth = fields.Date(string='DOB', required=True, tracking=True)
    gender = fields.Selection([('male', 'Male' ),('female','Female')],
                              string='Gender', required=True, tracking=True)