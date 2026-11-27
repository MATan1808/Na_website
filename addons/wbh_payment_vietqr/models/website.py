# -*- coding: utf-8 -*-
from odoo import fields, models


class Website(models.Model):
    _inherit = 'website'

    wbh_cod_max_amount = fields.Float(
        string='Hạn mức tối đa cho phép COD (VNĐ)',
        default=0.0,
        help='Đơn hàng có tổng tiền lớn hơn hạn mức này sẽ ẩn COD và yêu cầu thanh toán VietQR / đặt cọc. Nhập 0 nếu không giới hạn.',
    )
    wbh_cod_deposit_percent = fields.Float(
        string='Tỷ lệ đặt cọc yêu cầu (%)',
        default=0.0,
        help='Phần trăm giá trị đơn hàng gợi ý đặt cọc qua VietQR khi đơn hàng không đủ điều kiện COD (0 - 100%).',
    )

    _check_wbh_cod_max_amount = models.Constraint(
        'CHECK(wbh_cod_max_amount >= 0)',
        'Hạn mức COD tối đa phải lớn hơn hoặc bằng 0.',
    )
    _check_wbh_cod_deposit_percent = models.Constraint(
        'CHECK(wbh_cod_deposit_percent >= 0 AND wbh_cod_deposit_percent <= 100)',
        'Tỷ lệ đặt cọc COD phải nằm trong khoảng từ 0 đến 100%.',
    )
