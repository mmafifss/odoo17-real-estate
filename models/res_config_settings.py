# -*- coding: utf-8 -*-
from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    commission_rate = fields.Float(
        string="Komisi Agen Default (%)",
        default=6.0,
        config_parameter='real_estate.commission_rate',
        help="Persentase komisi standar untuk agen saat membuat tagihan."
    )
    admin_fee = fields.Float(
        string="Biaya Administrasi & Legal",
        default=1500000.0,
        config_parameter='real_estate.admin_fee',
        help="Biaya administrasi standar pengurusan dokumen properti."
    )
