# -*- coding: utf-8 -*-
from odoo import api, fields, models


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
        help='Mã theo dõi vận đơn từ GHN, Viettel Post hoặc vận chuyển nội bộ WBH.',
    )
    wbh_tracking_url = fields.Char(
        string='Link tra cứu vận đơn',
        copy=False,
        help='Đường dẫn tra cứu hành trình giao hàng hiển thị trên Portal.',
    )
    wbh_fb_link = fields.Char(
        string='Link Facebook khách hàng',
        compute='_compute_wbh_customer_contact_info',
        store=True,
        copy=False,
        help='Tự động đồng bộ Link Facebook từ khách hàng / địa chỉ giao hàng.',
    )
    wbh_shipping_info_note = fields.Text(
        string='Thông tin ship (Tên, SĐT, địa chỉ cũ)',
        compute='_compute_wbh_customer_contact_info',
        store=True,
        copy=False,
        help='Tự động đồng bộ thông tin nhận hàng chi tiết từ form đặt hàng Web 1.',
    )

    _wbh_hold_order_idx = models.Index('(wbh_is_hold_order)')

    @api.depends(
        'partner_id.wbh_fb_link',
        'partner_shipping_id.wbh_fb_link',
        'partner_id.wbh_shipping_info_note',
        'partner_shipping_id.wbh_shipping_info_note',
    )
    def _compute_wbh_customer_contact_info(self):
        for order in self:
            ship_partner = order.partner_shipping_id
            main_partner = order.partner_id
            order.wbh_fb_link = (
                (ship_partner and ship_partner.wbh_fb_link)
                or (main_partner and main_partner.wbh_fb_link)
                or False
            )
            order.wbh_shipping_info_note = (
                (ship_partner and ship_partner.wbh_shipping_info_note)
                or (main_partner and main_partner.wbh_shipping_info_note)
                or False
            )

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
