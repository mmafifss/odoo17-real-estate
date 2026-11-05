# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class EstateProperty(models.Model):
    _name = 'estate.property'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Real Estate Property'
    _order = 'id desc'

    # --- Basic Fields ---
    name = fields.Char(string='Title', required=True, tracking=True)
    description = fields.Text(string='Description')
    postcode = fields.Char(string='Postcode')
    date_availability = fields.Date(
        string='Available From',
        copy=False,
        default=lambda self: fields.Date.today()
    )
    expected_price = fields.Float(string='Expected Price', required=True, tracking=True)
    selling_price = fields.Float(string='Selling Price', readonly=True, copy=False, tracking=True)
    bedrooms = fields.Integer(string='Bedrooms', default=2)
    living_area = fields.Integer(string='Living Area (sqm)')
    facades = fields.Integer(string='Facades')
    garage = fields.Boolean(string='Garage')
    garden = fields.Boolean(string='Garden')
    garden_area = fields.Integer(string='Garden Area (sqm)')
    garden_orientation = fields.Selection(
        selection=[
            ('north', 'North'),
            ('south', 'South'),
            ('east', 'East'),
            ('west', 'West'),
        ],
        string='Garden Orientation'
    )
    active = fields.Boolean(string='Active', default=True)
    state = fields.Selection(
        selection=[
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('canceled', 'Canceled'),
        ],
        string='Status',
        required=True,
        copy=False,
        default='new',
        tracking=True
    )

    # --- Relational Fields ---
    property_type_id = fields.Many2one('estate.property.type', string='Property Type')
    tag_ids = fields.Many2many('estate.property.tag', string='Tags')
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string='Offers')
    buyer_id = fields.Many2one('res.partner', string='Buyer', copy=False, readonly=True, tracking=True)
    invoice_id = fields.Many2one('account.move', string='Invoice', readonly=True, copy=False)
    salesperson_id = fields.Many2one(
        'res.users',
        string='Salesperson',
        default=lambda self: self.env.user,
        tracking=True
    )

    # --- Computed Fields ---
    total_area = fields.Integer(
        string='Total Area (sqm)',
        compute='_compute_total_area',
        help='Luas bangunan + luas taman'
    )
    best_price = fields.Float(
        string='Best Offer',
        compute='_compute_best_price',
        help='Tawaran tertinggi yang masuk'
    )

    # --- Compute Methods ---
    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = (record.living_area or 0) + (record.garden_area or 0)

    @api.depends('offer_ids.price')
    def _compute_best_price(self):
        for record in self:
            offers = record.offer_ids.mapped('price')
            record.best_price = max(offers) if offers else 0.0

    # --- Onchange Method ---
    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = False

    # --- Python Constraints ---
    @api.constrains('expected_price')
    def _check_expected_price(self):
        for record in self:
            if record.expected_price <= 0:
                raise ValidationError("Harga ekspektasi (Expected Price) harus lebih dari 0!")

    # --- Action Buttons ---
    def action_set_sold(self):
        for record in self:
            if record.state == 'canceled':
                raise UserError("Properti yang dibatalkan tidak bisa dijual langsung!")
            record.state = 'sold'
        return True

    def action_set_canceled(self):
        for record in self:
            if record.state == 'sold':
                raise UserError("Properti yang sudah terjual tidak bisa dibatalkan!")
            record.state = 'canceled'
        return True

    def action_reset(self):
        for record in self:
            if record.invoice_id and record.invoice_id.state == 'posted':
                raise UserError("Tidak bisa mereset properti karena invoice sudah disahkan/diposting!")
            record.state = 'new'
            record.selling_price = 0.0
            record.buyer_id = False
            record.invoice_id = False
        return True

    def action_create_invoice(self):
        self.ensure_one()
        if not self.buyer_id:
            raise UserError("Pembeli belum ditentukan untuk membuat tagihan!")
        if self.invoice_id:
            raise UserError("Faktur tagihan untuk properti ini sudah pernah dibuat!")

        # Ambil nilai komisi dan admin fee dari pengaturan (Settings)
        config_param = self.env['ir.config_parameter'].sudo()
        commission_rate = float(config_param.get_param('real_estate.default_commission_rate', 6.0))
        admin_fee = float(config_param.get_param('real_estate.default_admin_fee', 1500000.0))

        commission = self.selling_price * (commission_rate / 100.0)

        invoice = self.env['account.move'].create({
            'partner_id': self.buyer_id.id,
            'move_type': 'out_invoice',
            'invoice_line_ids': [
                fields.Command.create({
                    'name': f"Komisi Agen ({commission_rate}%) Properti: {self.name}",
                    'quantity': 1,
                    'price_unit': commission,
                }),
                fields.Command.create({
                    'name': "Biaya Administrasi & Dokumen Legal",
                    'quantity': 1,
                    'price_unit': admin_fee,
                }),
            ],
        })
        self.invoice_id = invoice.id
        self.message_post(
            body=f"Faktur tagihan <b>{invoice.name or 'Draft Tagihan'}</b> sebesar <b>{(commission + admin_fee):,.2f}</b> berhasil dibuat untuk pembeli <b>{self.buyer_id.name}</b>.",
            subtype_xmlid='mail.mt_note'
        )
        return self.action_view_invoice()

    def action_view_invoice(self):
        self.ensure_one()
        return {
            'name': 'Faktur Tagihan',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': self.invoice_id.id,
        }


class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Property Type'
    _order = 'sequence, name'

    name = fields.Char(string='Type', required=True)
    sequence = fields.Integer(string='Sequence', default=1)
    property_ids = fields.One2many('estate.property', 'property_type_id', string='Properties')
    property_count = fields.Integer(string='Jumlah Properti', compute='_compute_property_count')

    @api.depends('property_ids')
    def _compute_property_count(self):
        for record in self:
            record.property_count = len(record.property_ids)


class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Property Tag'
    _order = 'name'

    name = fields.Char(string='Tag Name', required=True)
    color = fields.Integer(string='Color Index')

    _sql_constraints = [
        ('check_name_unique', 'unique(name)', 'Nama tag properti tidak boleh sama!')
    ]


class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Property Offer'
    _order = 'price desc'

    price = fields.Float(string='Price', required=True)
    status = fields.Selection(
        selection=[
            ('accepted', 'Accepted'),
            ('refused', 'Refused'),
        ],
        string='Status',
        copy=False
    )
    partner_id = fields.Many2one('res.partner', string='Buyer', required=True)
    property_id = fields.Many2one('estate.property', string='Property', required=True, ondelete='cascade')

    def action_accept(self):
        for record in self:
            accepted_offers = record.property_id.offer_ids.filtered(lambda o: o.status == 'accepted')
            if accepted_offers:
                raise UserError("Sudah ada tawaran yang diterima untuk properti ini!")

            record.status = 'accepted'
            record.property_id.selling_price = record.price
            record.property_id.buyer_id = record.partner_id
            record.property_id.state = 'offer_accepted'
        return True

    def action_refuse(self):
        for record in self:
            record.status = 'refused'
        return True
