# -*- coding: utf-8 -*-
from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    wbh_is_hold_order = fields.Boolean(
        string='Gom đơn / Giữ hàng tại shop',
        default=False,
        copy=False,
        help='Tự động bật khi khách chọn phương thức Gom đơn / Giữ hàng tại shop (0đ phí vận chuyển).',
    )
    wbh_tracking_code = fields.Char(
        string='Mã vận đơn',
        copy=False,
        help='Mã theo dõi vận đơn từ GHN hoặc vận chuyển nội bộ WBH.',
    )
    wbh_tracking_url = fields.Char(
        string='Link tra cứu vận đơn',
        copy=False,
        help='Đường dẫn tra cứu hành trình giao hàng hiển thị trên Portal.',
    )

    _wbh_hold_order_idx = models.Index('(wbh_is_hold_order)')

    def _remove_delivery_line(self):
        res = super()._remove_delivery_line()
        self.write({'wbh_is_hold_order': False})
        return res

    def set_delivery_line(self, carrier, amount):
        res = super().set_delivery_line(carrier, amount)
        for order in self:
            order.wbh_is_hold_order = bool(carrier and carrier.wbh_is_hold_order)
        return res

    def _action_confirm(self):
        res = super()._action_confirm()
        for order in self:
            if order.carrier_id:
                order.wbh_is_hold_order = bool(order.carrier_id.wbh_is_hold_order)
        return res


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def send_to_shipper(self):
        res = super().send_to_shipper()
        for picking in self:
            if picking.sale_id and picking.carrier_tracking_ref:
                picking.sale_id.sudo().write({
                    'wbh_tracking_code': picking.carrier_tracking_ref,
                    'wbh_tracking_url': picking.carrier_tracking_url or picking.sale_id.wbh_tracking_url,
                })
        return res
