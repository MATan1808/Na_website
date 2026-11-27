# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductTag(models.Model):
    _inherit = 'product.tag'

    wbh_show_in_filter = fields.Boolean(
        string='Hiển thị trên bộ lọc Shop',
        default=True,
        help='Tự động hiển thị nhãn này trong bộ lọc /shop khi có ít nhất 1 sản phẩm đang bán gắn nhãn.',
    )
    wbh_filter_group = fields.Selection(
        selection=[
            ('promo', 'Ưu đãi & Trạng thái'),
            ('collection', 'Chủ đề / Bộ sưu tập'),
            ('other', 'Nhãn khác'),
        ],
        string='Nhóm bộ lọc WBH',
        default='promo',
        required=True,
        help='Phân nhóm hiển thị nhãn trong bộ lọc trang cửa hàng.',
    )
    wbh_badge_hex = fields.Char(
        string='Màu Badge (Hex)',
        help='Mã màu Hex tùy chỉnh trên Storefront (VD: #D9483B). Nếu để trống sẽ dùng màu mặc định của nhãn.',
    )

    _wbh_show_in_filter_idx = models.Index('(wbh_show_in_filter, wbh_filter_group)')
