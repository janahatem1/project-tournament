
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class Tournament(models.Model):
    _name = 'tournament.tournament'
    _description = 'Tournament'

    name = fields.Char(
        string='Tournament Name',
        required=True
    )

    game_title = fields.Char(
        string='Game Title',
        required=True
    )

    registration_opening = fields.Datetime(
        string='Registration Opening',
        readonly=True
    )

    registration_closing = fields.Datetime(
        string='Registration Closing',
        required=True
    )

    tournament_start = fields.Datetime(
        string='Tournament Start',
        required=True
    )

    max_teams = fields.Selection(
        [
            ('4', '4'),
            ('8', '8'),
            ('16', '16'),
            ('32', '32'),
            ('64', '64'),
        ],
        string='Maximum Teams',
        required=True
    )

    max_players_per_team = fields.Integer(
        string='Maximum Players Per Team',
        required=True
    )

    match_duration = fields.Integer(
        string='Match Duration (Minutes)',
        required=True
    )

    status = fields.Selection(
        [
            ('draft', 'Draft'),
            ('registration_open', 'Registration Open'),
            ('registration_closed', 'Registration Closed'),
            ('in_progress', 'In Progress'),
            ('finished', 'Finished'),
        ],
        string='Status',
        default='draft',
        required=True,
        readonly=True
    )

    champion_id = fields.Many2one(
        'tournament.team',
        string='Champion'
    )

    registration_ids = fields.One2many(
        'tournament.registration',
        'tournament_id',
        string='Registrations'
    )


    @api.constrains('registration_closing', 'tournament_start')
    def _check_registration_dates(self):
        for record in self:
            if record.registration_closing >= record.tournament_start:
                raise ValidationError(
                    'Registration Closing must be before Tournament Start.'
                )

    @api.constrains('max_players_per_team')
    def _check_max_players_per_team(self):
        for record in self:
            if record.max_players_per_team <= 0:
                raise ValidationError(
                    'Maximum Players Per Team must be greater than 0.'
                )

    @api.constrains('match_duration')
    def _check_match_duration(self):
        for record in self:
            if record.match_duration <= 0:
                raise ValidationError(
                    'Match Duration must be greater than 0.'
                )



    def action_open_registration(self):
        for record in self:

            if record.status != 'draft':
                raise UserError(
                    'Only draft tournaments can open registration.'
                )

            record.status = 'registration_open'
            record.registration_opening = fields.Datetime.now()



    @api.model
    def _check_registration_closing(self):

        now = fields.Datetime.now()

        tournaments = self.search([
            ('status', '=', 'registration_open')
        ])

        for tournament in tournaments:

            if tournament.registration_closing <= now:
                tournament._close_registration()



    def _close_registration(self):

        for tournament in self:

            if tournament.status != 'registration_open':
                continue

            pending_registrations = self.env[
                'tournament.registration'
            ].search([
                ('tournament_id', '=', tournament.id),
                ('status', '=', 'pending')
            ])


            pending_registrations.write({
                'status': 'rejected'
            })


            tournament.status = 'registration_closed'
            tournament.registration_closing = fields.Datetime.now()

    def write(self, vals):
        for record in self:
            if 'max_teams' in vals and record.status != 'draft':
                raise UserError(
                    'Maximum Teams can only be changed while the tournament is in Draft.'
                )

        return super().write(vals)