
from odoo import models, fields


class TournamentPlayer(models.Model):
    _name = 'tournament.player'
    _description = 'Tournament Player'
    _rec_name = 'full_name'

    full_name = fields.Char(
        string='Full Name',
        required=True
    )

    gamer_tag = fields.Char(
        string='Gamer Tag',
        required=True
    )

    email = fields.Char(
        string='Email'
    )

    team_id = fields.Many2one(
        'tournament.team',
        string='Team'
    )
