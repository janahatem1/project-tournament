from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TournamentTeam(models.Model):
    _name = 'tournament.team'
    _description = 'Tournament Team'

    name = fields.Char(
        string='Team Name',
        required=True
    )

    captain_id = fields.Many2one(
        'tournament.player',
        string='Captain',
        domain="[('team_id', '=', id)]"
    )

    players = fields.One2many(
        'tournament.player',
        'team_id',
        string='Players'
    )

    @api.constrains('name')
    def _check_unique_name(self):
        for record in self:
            existing_team = self.search([
                ('name', '=', record.name),
                ('id', '!=', record.id)
            ])

            if existing_team:
                raise ValidationError(
                    'A team with this name already exists.'
                )



