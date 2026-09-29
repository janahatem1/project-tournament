from odoo import models, fields, api
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