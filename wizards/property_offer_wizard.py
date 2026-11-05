# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import models, fields, api
from odoo.exceptions import UserError


class PropertyOfferWizard(models.TransientModel):
    _name = 'property.offer.wizard'
    _description = 'Wizard Ajukan Penawaran Properti'

    property_id = fields.Many2one(
        'estate.property',
        string='Properti',
        required=True,
        default=lambda self: self.env.context.get('active_id')
    )
    partner_id = fields.Many2one('res.partner', string='Calon Pembeli', required=True)
    price = fields.Float(string='Nominal Penawaran', required=True)
    validity_days = fields.Integer(string='Masa Berlaku (Hari)', default=7)
    date_deadline = fields.Date(
        string='Batas Waktu',
        compute='_compute_date_deadline',
        readonly=False,
        store=True
    )
    notes = fields.Text(string='Catatan / Keterangan')

    @api.depends('validity_days')
    def _compute_date_deadline(self):
        for record in self:
            record.date_deadline = fields.Date.today() + timedelta(days=record.validity_days or 7)

    def action_submit_offer(self):
        self.ensure_one()
        if self.price <= 0:
            raise UserError("Nominal penawaran harus lebih dari 0!")

        # 1. Buat record penawaran baru
        self.env['estate.property.offer'].create({
            'property_id': self.property_id.id,
            'partner_id': self.partner_id.id,
            'price': self.price,
        })

        # 2. Update status properti jika masih 'new'
        if self.property_id.state == 'new':
            self.property_id.state = 'offer_received'

        # 3. Otomatis kirim pesan log ke Chatter
        note_text = f"Penawaran baru diajukan oleh <b>{self.partner_id.name}</b> sebesar <b>{self.price:,.2f}</b>."
        if self.notes:
            note_text += f"<br/><em>Catatan:</em> {self.notes}"
        self.property_id.message_post(body=note_text, subtype_xmlid='mail.mt_note')

        # Tutup dialog modal popup
        return {'type': 'ir.actions.act_window_close'}

