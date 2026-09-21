from docutils.nodes import note
from pytz import reference

from odoo import api, fields, models

class HospitalAppointment(models.Model):
    _name = 'hospital.appointment'  # Must be exact
    _description = 'Hospital Appointment'
    _inherit = ['mail.thread']
    _rec_name = 'patient_id'

    reference=fields.Char(string="Reference",default='New')
    patient_id = fields.Many2one('hospital.patient', string="Patient")
    date_appointment = fields.Datetime(string="Appointment Date")
    note = fields.Text(string="Note")
    # Add ('ongoing', 'Ongoing') to the selection options
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('ongoing', 'Ongoing'),  # <--- Ensure key 'ongoing' is defined here
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # CORRECT: call next_by_code with parentheses ()
            if vals.get('reference', 'New') == 'New':
                vals['reference'] = self.env['ir.sequence'].next_by_code('hospital.appointment') or 'New'
        return super().create(vals_list)

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirmed'

    def action_ongoing(self):
        for rec in self:
            rec.state = 'ongoing'

    def action_done(self):
        for rec in self:
            rec.state = 'done'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'