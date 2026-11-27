# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    wbh_allow_cod = fields.Boolean(
        string='Cho phép thanh toán COD',
        default=True,
        help='Tắt tùy chọn này đối với hàng Pre-order / Đặt cọc trước hoặc sản phẩm giá trị cao không hỗ trợ COD.',
    )
