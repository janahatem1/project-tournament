from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

class TournamentMatch(models.Model):
    _name = 'tournament.match'
    _description = 'Tournament Match'
    _order = 'scheduled_date, id'

    reference = fields.Char(
        string='Reference',
        required=True,
        readonly=True,
        copy=False,
        default='New'
    )
    tournament_id = fields.Many2one(
        'tournament.tournament',
        string='Tournament',
        required=True

    )

    round_number = fields.Integer(
        string='Round Number',
        required=True,
        default=1
    )

    team_a_id = fields.Many2one(
        'tournament.team',
        string='Team A',
        required=True
    )

    team_b_id = fields.Many2one(
        'tournament.team',
        string='Team B',
        required=True
    )

    scheduled_date = fields.Datetime(
        string='Scheduled Date & Time'

    )

    team_a_score = fields.Integer(
        string='Team A Score',
        default=0
    )

    team_b_score = fields.Integer(
        string='Team B Score',
        default=0
    )

    winner_id = fields.Many2one(
        'tournament.team',
        string='Winner'
    )

    status = fields.Selection(
        [
            ('scheduled', 'Scheduled'),
            ('in_progress', 'In Progress'),
            ('finished', 'Finished'),
        ],
        string='Status',
        required=True,
        default='scheduled'
    )

    @api.model_create_multi

    def create(self, vals_list):
        for vals in vals_list:

            if vals.get('reference', 'New') == 'New':
                vals['reference'] = self.env['ir.sequence'].next_by_code('tournament.match') or 'New'
        return super().create(vals_list)


@api.constrains('team_a_id', 'team_b_id')
def _check_teams(self):
    for match in self:
        if match.team_a_id == match.team_b_id:
            raise ValidationError(
                'Team A and Team B cannot be the same team.'
            )


@api.constrains('tournament_id', 'team_a_id', 'team_b_id')
def _check_accepted_teams(self):
    for match in self:
        accepted_registrations = self.env[
            'tournament.registration'
        ].search([
            ('tournament_id', '=', match.tournament_id.id),
            ('status', '=', 'accepted'),
        ])

        accepted_teams = accepted_registrations.mapped('team_id')

        if match.team_a_id not in accepted_teams:
            raise ValidationError(
                'Team A must be an accepted team in this tournament.'
            )

        if match.team_b_id not in accepted_teams:
            raise ValidationError(
                'Team B must be an accepted team in this tournament.'
            )


@api.constrains('team_a_score', 'team_b_score')
def _check_scores(self):
    for match in self:
        if match.team_a_score < 0 or match.team_b_score < 0:
            raise ValidationError(
                'Scores cannot be negative.'
            )


def action_start_match(self):
    for match in self:
        if match.status != 'scheduled':
            raise UserError(
                'Only scheduled matches can be started.'
            )

        match.status = 'in_progress'


def action_finish_match(self):
    for match in self:

        if match.status != 'in_progress':
            raise UserError(
                'Only matches in progress can be finished.'
            )

        if match.team_a_score == match.team_b_score:
            raise UserError(
                'A match cannot end in a draw.'
            )

        if match.team_a_score > match.team_b_score:
            match.winner_id = match.team_a_id
        else:
            match.winner_id = match.team_b_id

        match.status = 'finished'


def write(self, vals):
    for match in self:

        if match.status == 'finished':

            protected_fields = [
                'team_a_id',
                'team_b_id',
                'team_a_score',
                'team_b_score',
                'winner_id',
                'tournament_id',
                'round_number',
            ]

            for field_name in protected_fields:
                if field_name in vals:
                    raise UserError(
                        'You cannot change a finished match.'
                    )

            if 'status' in vals and vals['status'] != 'finished':
                raise UserError(
                    'A finished match cannot be started again.'
                )

    return super().write(vals)