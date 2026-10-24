from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class TournamentRegistration(models.Model):
    _name = 'tournament.registration'
    _description = 'Tournament Registration'
    _rec_name = 'team_id'

    tournament_id = fields.Many2one(
        'tournament.tournament',
        string='Tournament',
        required=True
    )

    team_id = fields.Many2one(
        'tournament.team',
        string='Team',
        required=True
    )

    registration_date = fields.Datetime(
        string='Registration Date',
        default=fields.Datetime.now,
        readonly=True
    )

    status = fields.Selection(
        [
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('rejected', 'Rejected'),
            ('withdrawn', 'Withdrawn'),
        ],
        string='Status',
        default='pending',
        required=True,
        readonly=True
    )

    roster_ids = fields.Many2many(
        'tournament.player',
        string='Tournament Roster',
        domain="[('team_id', '=', team_id)]"
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            tournament = self.env['tournament.tournament'].browse(
                vals.get('tournament_id')
            )

            if tournament and tournament.status != 'registration_open':
                raise UserError(
                    'You can only register a team when registration is open.'
                )

            existing_registration = self.search_count([
                ('tournament_id', '=', tournament.id),
                ('team_id', '=', vals.get('team_id'))
            ])

            if existing_registration:
                raise UserError(
                    'This team is already registered for this tournament.'
                )

        return super().create(vals_list)

    @api.constrains('team_id', 'roster_ids', 'tournament_id')
    def _check_roster(self):
        for record in self:
            for player in record.roster_ids:
                if player.team_id != record.team_id:
                    raise ValidationError(
                        'All roster players must belong to the selected team.'
                    )

            if (
                record.tournament_id
                and len(record.roster_ids) > record.tournament_id.max_players_per_team
            ):
                raise ValidationError(
                    'The tournament roster cannot exceed the maximum '
                    'players allowed per team.'
                )

    def action_accept(self):
        for record in self:
            if record.status != 'pending':
                raise UserError(
                    'Only pending registrations can be accepted.'
                )

            if not record.roster_ids:
                raise UserError(
                    'You must select at least one player.'
                )

            accepted_count = self.search_count([
                ('tournament_id', '=', record.tournament_id.id),
                ('status', '=', 'accepted')
            ])

            max_teams = int(record.tournament_id.max_teams)

            if accepted_count >= max_teams:
                record.tournament_id._close_registration()
                raise UserError(
                    'The maximum number of teams has already been reached.'
                )

            record.status = 'accepted'
            accepted_count += 1

            if accepted_count >= max_teams:
                record.tournament_id._close_registration()

        return True

    def action_reject(self):
        for record in self:
            if record.status != 'pending':
                raise UserError(
                    'Only pending registrations can be rejected.'
                )

            record.status = 'rejected'
        return True


    def action_withdraw(self):

        for record in self:

            if record.tournament_id.status != 'registration_open':
                raise UserError(
                    'You can only withdraw while registration is open.'
                )

            if record.status not in ('pending', 'accepted'):
                raise UserError(
                    'Only pending or accepted registrations can be withdrawn.'
                )

            record.status = 'withdrawn'

    def write(self, vals):
        protected_fields = {
            'tournament_id',
            'team_id',
            'registration_date',
            'status',
            'roster_ids',
        }

        for record in self:
            if (
                    record.tournament_id.status == 'registration_closed'
                    and protected_fields.intersection(vals)
            ):
                raise UserError(
                    'These registration fields cannot be modified after registration is closed.'
                )

        return super().write(vals)

    def unlink(self):

        for record in self:

            if record.tournament_id.status == 'registration_closed':

                raise UserError(
                    'Closed registrations cannot be deleted.'
                )

        return super().unlink()

    def _write(self, vals):
        protected_fields = [
            'tournament_id',
            'team_id',
            'status',
        ]
        for registration in self:
          if registration.tournament_id.status in [
            'registration_closed',
            'in_progress',
            'finished',
        ]:
            for field_name in protected_fields:
                if field_name in vals:
                    raise UserError(
                        'You cannot modify a registration '
                        'after registration has closed.'
                    )

        return super().write(vals)

