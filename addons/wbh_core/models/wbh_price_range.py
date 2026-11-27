# -*- coding: utf-8 -*-
from odoo import fields, models


class WbhPriceRange(models.Model):
    _name = 'wbh.price.range'
    _description = 'Khoảng giá lọc nhanh WBH'
    _order = 'sequence, min_price, id'

    name = fields.Char(
        string='Tên khoảng giá',
        required=True,
        translate=True,
        help='Nhãn hiển thị trên bộ lọc giá (VD: Dưới 100.000₫, 100.000₫ – 300.000₫).',
    )
    website_id = fields.Many2one(
        comodel_name='website',
        string='Website áp dụng',
        ondelete='cascade',
        help='Để trống nếu áp dụng chung cho tất cả website.',
    )
    min_price = fields.Float(
        string='Giá tối thiểu',
        default=0.0,
        required=True,
    )
    max_price = fields.Float(
        string='Giá tối đa (0 = Không giới hạn)',
        default=0.0,
        required=True,
        help='Nhập 0 nếu không giới hạn mức giá trần.',
    )
    sequence = fields.Integer(
        string='Thứ tự',
        default=10,
    )
    active = fields.Boolean(
        string='Kích hoạt',
        default=True,
    )

    _check_wbh_price_range_bounds = models.Constraint(
        'CHECK(min_price >= 0 AND (max_price = 0 OR max_price >= min_price))',
        'Giá tối thiểu phải >= 0 và Giá tối đa phải bằng 0 (không giới hạn) hoặc >= Giá tối thiểu.',
    )
    _wbh_website_active_seq_idx = models.Index('(website_id, active, sequence)')
