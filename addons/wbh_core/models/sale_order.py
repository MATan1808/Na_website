# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.fields import Command


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    wbh_is_packaging_fee = fields.Boolean(
        string='Là dòng Phí gói WBH',
        default=False,
        copy=False,
        help='Đánh dấu dòng phụ phí đóng gói cố định do WBH Core tự động quản lý trên đơn hàng.',
    )

    _wbh_is_packaging_fee_idx = models.Index('(wbh_is_packaging_fee)')

    def _show_in_cart(self):
        self.ensure_one()
        return super()._show_in_cart() and not self.wbh_is_packaging_fee

    def unlink(self):
        orders = (
            self.filtered(lambda sol: not sol.wbh_is_packaging_fee).mapped('order_id')
            if not self.env.context.get('_wbh_syncing_packaging_fee')
            else self.env['sale.order']
        )
        res = super().unlink()
        if orders:
            orders.exists()._wbh_sync_packaging_fee_line()
        return res


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    wbh_packaging_fee_amount = fields.Monetary(
        string='Phí gói',
        compute='_compute_wbh_packaging_fee_amount',
        help='Tổng phí đóng gói cố định đang áp dụng trên đơn hàng.',
    )
    wbh_amount_products = fields.Monetary(
        string='Thành tiền sản phẩm',
        compute='_compute_wbh_amount_products',
        help='Tổng tiền hàng hóa trong giỏ, tách biệt khỏi Phí gói và Phí giao hàng.',
    )

    @api.depends(
        'order_line.price_total',
        'order_line.price_subtotal',
        'order_line.wbh_is_packaging_fee',
        'website_id.show_line_subtotals_tax_selection',
    )
    def _compute_wbh_packaging_fee_amount(self):
        for order in self:
            pkg_lines = order.order_line.filtered('wbh_is_packaging_fee')
            if order.website_id and order.website_id.show_line_subtotals_tax_selection == 'tax_excluded':
                order.wbh_packaging_fee_amount = sum(pkg_lines.mapped('price_subtotal'))
            else:
                order.wbh_packaging_fee_amount = sum(pkg_lines.mapped('price_total'))

    @api.depends(
        'order_line.price_total',
        'order_line.price_subtotal',
        'order_line.is_delivery',
        'order_line.wbh_is_packaging_fee',
        'website_id.wbh_packaging_fee_enabled',
        'website_id.show_line_subtotals_tax_selection',
    )
    def _compute_wbh_amount_products(self):
        for order in self:
            product_lines = order.order_line.filtered(
                lambda sol: not sol.display_type and not sol.is_delivery and not sol.wbh_is_packaging_fee
            )
            if (
                order.website_id
                and order.website_id.wbh_packaging_fee_enabled
            ) or not (
                order.website_id
                and order.website_id.show_line_subtotals_tax_selection == 'tax_excluded'
            ):
                order.wbh_amount_products = sum(product_lines.mapped('price_total'))
            else:
                order.wbh_amount_products = sum(product_lines.mapped('price_subtotal'))

    def _get_update_prices_lines(self):
        lines = super()._get_update_prices_lines()
        return lines.filtered(lambda line: not line.wbh_is_packaging_fee)

    def _get_zero_priced_lines(self):
        lines = super()._get_zero_priced_lines()
        return lines.filtered(lambda line: not line.wbh_is_packaging_fee)

    def _wbh_sync_packaging_fee_line(self):
        """Đồng bộ đúng 1 dòng Phí gói cố định trên đơn hàng Web 1 khi giỏ có sản phẩm."""
        if self.env.context.get('_wbh_syncing_packaging_fee'):
            return
        packaging_product = self.env.ref(
            'wbh_core.wbh_product_packaging_fee',
            raise_if_not_found=False,
        )
        SaleOrderLineSudo = self.env['sale.order.line'].sudo().with_context(
            _wbh_syncing_packaging_fee=True
        )
        for order in self:
            if order.state not in ('draft', 'sent'):
                continue
            pkg_lines = order.order_line.filtered('wbh_is_packaging_fee')
            website = order.website_id
            should_apply = bool(
                website
                and website.wbh_packaging_fee_enabled
                and website.wbh_packaging_fee > 0
                and packaging_product
            )
            real_lines = order.order_line.filtered(
                lambda sol: (
                    not sol.display_type
                    and not sol.is_delivery
                    and not sol.wbh_is_packaging_fee
                )
            )
            if not should_apply or not real_lines:
                if pkg_lines:
                    pkg_lines.sudo().with_context(_wbh_syncing_packaging_fee=True).unlink()
                continue

            fee_amount = float(website.wbh_packaging_fee)
            if len(pkg_lines) == 1:
                line = pkg_lines[0]
                updates = {}
                if line.product_id.id != packaging_product.id:
                    updates['product_id'] = packaging_product.id
                if line.product_uom_qty != 1.0:
                    updates['product_uom_qty'] = 1.0
                if order.currency_id.compare_amounts(line.price_unit, fee_amount) != 0:
                    updates['price_unit'] = fee_amount
                if line.tax_ids:
                    updates['tax_ids'] = [Command.clear()]
                if updates:
                    line.sudo().with_context(_wbh_syncing_packaging_fee=True).write(updates)
            else:
                if pkg_lines:
                    pkg_lines.sudo().with_context(_wbh_syncing_packaging_fee=True).unlink()
                SaleOrderLineSudo.create({
                    'order_id': order.id,
                    'name': 'Phí gói',
                    'product_id': packaging_product.id,
                    'product_uom_id': packaging_product.uom_id.id,
                    'product_uom_qty': 1.0,
                    'price_unit': fee_amount,
                    'tax_ids': [Command.clear()],
                    'wbh_is_packaging_fee': True,
                    'sequence': 9990,
                })

    def _verify_cart(self):
        res = super()._verify_cart()
        self._wbh_sync_packaging_fee_line()
        return res

    def _verify_cart_after_update(self):
        self._wbh_sync_packaging_fee_line()
        return super()._verify_cart_after_update()

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        if not self.env.context.get('_wbh_syncing_packaging_fee'):
            orders._wbh_sync_packaging_fee_line()
        return orders

    def write(self, vals):
        res = super().write(vals)
        if not self.env.context.get('_wbh_syncing_packaging_fee') and any(
            key in vals for key in ('order_line', 'website_id')
        ):
            self._wbh_sync_packaging_fee_line()
        return res

    def unlink(self):
        return super(
            SaleOrder,
            self.with_context(_wbh_syncing_packaging_fee=True),
        ).unlink()
