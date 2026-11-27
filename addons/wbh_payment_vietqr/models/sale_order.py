# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    wbh_allow_cod = fields.Boolean(
        string='Đủ điều kiện COD',
        compute='_compute_wbh_cod_eligibility',
        compute_sudo=True,
        help='Cho biết đơn hàng hiện tại có được phép thanh toán khi nhận hàng (COD) hay không.',
    )
    wbh_cod_block_reason = fields.Char(
        string='Lý do hạn chế COD',
        compute='_compute_wbh_cod_eligibility',
        compute_sudo=True,
    )
    wbh_cod_deposit_amount = fields.Float(
        string='Số tiền đặt cọc gợi ý (VNĐ)',
        compute='_compute_wbh_cod_eligibility',
        compute_sudo=True,
    )

    @api.depends(
        'amount_total',
        'order_line.product_id',
        'order_line.product_id.product_tmpl_id.wbh_allow_cod',
        'website_id',
        'website_id.wbh_cod_max_amount',
        'website_id.wbh_cod_deposit_percent',
    )
    def _compute_wbh_cod_eligibility(self):
        for order in self:
            eligible, reason = order._wbh_is_cod_eligible()
            order.wbh_allow_cod = eligible
            order.wbh_cod_block_reason = reason or False
            deposit_pct = order.website_id.wbh_cod_deposit_percent if order.website_id else 0.0
            if not eligible and deposit_pct > 0 and order.amount_total > 0:
                order.wbh_cod_deposit_amount = round(order.amount_total * deposit_pct / 100.0)
            else:
                order.wbh_cod_deposit_amount = 0.0

    def _wbh_is_cod_eligible(self):
        """Kiểm tra điều kiện áp dụng COD trên đơn hàng.

        :return: tuple (eligible: bool, reason: str)
        """
        self.ensure_one()
        restricted_lines = self.order_line.filtered(
            lambda l: not l.display_type
            and l.product_id
            and not l.product_id.product_tmpl_id.wbh_allow_cod
        )
        if restricted_lines:
            product_names = ', '.join(restricted_lines[:2].mapped('product_id.display_name'))
            return False, _(
                "Sản phẩm (%s) không hỗ trợ COD (hàng đặt trước / pre-order). Vui lòng thanh toán qua VietQR."
            ) % product_names

        max_amount = self.website_id.wbh_cod_max_amount if self.website_id else 0.0
        if max_amount and max_amount > 0 and self.currency_id.compare_amounts(self.amount_total, max_amount) == 1:
            return False, _(
                "Đơn hàng vượt hạn mức COD tối đa (%s). Vui lòng chuyển khoản hoặc đặt cọc qua VietQR."
            ) % f"{int(round(max_amount)):,}".replace(',', '.')

        return True, ''
