# -*- coding: utf-8 -*-
import logging

from markupsafe import Markup
import requests

from odoo import _, fields, models

_logger = logging.getLogger(__name__)

GHN_SANDBOX_BASE_URL = 'https://dev-online-gateway.ghn.vn/shiip/public-api'
GHN_PROD_BASE_URL = 'https://online-gateway.ghn.vn/shiip/public-api'
GHN_TRACKING_BASE_URL = 'https://donhang.ghn.vn/?order_code='


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(
        selection_add=[
            ('wbh_local', 'WBH — Giao hàng Nội bộ / Đồng giá / Gom đơn'),
            ('wbh_ghn', 'WBH — Giao Hàng Nhanh (GHN)'),
        ],
        ondelete={
            'wbh_local': 'set default',
            'wbh_ghn': 'set default',
        },
    )

    wbh_flat_price = fields.Float(
        string='Phí ship đồng giá (VNĐ)',
        default=30000.0,
        help='Phí vận chuyển mặc định (hoặc phí dự phòng khi GHN ngoại tuyến).',
    )
    wbh_free_over_amount = fields.Float(
        string='Ngưỡng Freeship (VNĐ)',
        default=300000.0,
        help='Miễn phí ship khi tổng tiền hàng (chưa gồm phí ship) đạt từ ngưỡng này. Đặt 0 để tắt.',
    )
    wbh_is_hold_order = fields.Boolean(
        string='Gom đơn / Giữ hàng tại shop — 0đ ship',
        default=False,
        help='Khi bật, phương thức luôn tính phí 0đ và tự động gắn cờ Gom đơn lên đơn hàng.',
    )

    wbh_ghn_token = fields.Char(
        string='GHN API Token',
        groups='base.group_system,wbh_core.group_wbh_manager',
        help='Token xác thực API Giao Hàng Nhanh.',
    )
    wbh_ghn_shop_id = fields.Integer(
        string='GHN Shop ID',
        help='Mã cửa hàng (ShopId) trên hệ thống GHN.',
    )
    wbh_ghn_from_district_id = fields.Integer(
        string='Mã Quận/Huyện kho gửi (GHN)',
        default=1442,
        help='DistrictID nơi shop gửi hàng (mặc định 1442 — Quận 1, TP.HCM).',
    )
    wbh_ghn_service_type_id = fields.Integer(
        string='Mã loại dịch vụ GHN',
        default=2,
        help='2: Hàng nhẹ / Chuyển phát chuẩn; 5: Hàng nặng.',
    )
    wbh_ghn_sandbox = fields.Boolean(
        string='Chế độ Sandbox GHN',
        default=True,
        help='Bật để gọi môi trường dev-online-gateway.ghn.vn.',
    )
    wbh_provider_note = fields.Text(
        string='Ghi chú vận chuyển',
        translate=True,
        help='Mô tả ngắn hiển thị tại bước chọn vận chuyển ở Checkout và Portal.',
    )

    def _wbh_local_compute_price(self, order):
        """Tính cước nội bộ: 0đ cho Gom đơn, 0đ khi đạt ngưỡng Freeship, ngược lại đồng giá."""
        self.ensure_one()
        if self.wbh_is_hold_order:
            return 0.0, _('Đơn hàng được giữ tại cửa hàng (Gom đơn — Phí vận chuyển 0đ).')

        amount_without_delivery = order._compute_amount_total_without_delivery()
        order_amount_company = self._compute_currency(
            order, amount_without_delivery, 'pricelist_to_company'
        )
        if self.wbh_free_over_amount > 0 and order_amount_company >= self.wbh_free_over_amount:
            return 0.0, _(
                'Miễn phí vận chuyển cho đơn hàng đạt từ %(threshold).0f đ.',
                threshold=self.wbh_free_over_amount,
            )

        price = self._compute_currency(order, self.wbh_flat_price, 'company_to_pricelist')
        return price, False

    def wbh_local_rate_shipment(self, order):
        """Tính phí vận chuyển cho provider nội bộ (Đồng giá / Freeship / Gom đơn)."""
        self.ensure_one()
        if not self._match_address(order.partner_shipping_id):
            return {
                'success': False,
                'price': 0.0,
                'error_message': _('Phương thức giao hàng này không áp dụng cho khu vực đã chọn.'),
                'warning_message': False,
            }
        price, warning_msg = self._wbh_local_compute_price(order)
        return {
            'success': True,
            'price': price,
            'error_message': False,
            'warning_message': warning_msg,
        }

    def wbh_local_send_shipping(self, pickings):
        """Xác nhận giao nội bộ hoặc giữ hàng tại shop và gán mã theo dõi WBH."""
        self.ensure_one()
        results = []
        for picking in pickings:
            order = picking.sale_id
            if self.wbh_is_hold_order:
                exact_price = 0.0
                tracking_number = f'WBH-HOLD-{picking.name or picking.id}'
            else:
                exact_price = (
                    self._wbh_local_compute_price(order)[0]
                    if order
                    else self.wbh_flat_price
                )
                tracking_number = f'WBH-{picking.name or picking.id}'

            if order:
                order.sudo().write({
                    'wbh_tracking_code': tracking_number,
                    'wbh_tracking_url': self.wbh_local_get_tracking_link(
                        picking.new({'carrier_tracking_ref': tracking_number})
                    ) or False,
                    'wbh_is_hold_order': bool(self.wbh_is_hold_order),
                })
            results.append({
                'exact_price': exact_price,
                'tracking_number': tracking_number,
            })
        return results

    def wbh_local_get_tracking_link(self, picking):
        """Trả về link tra cứu nội bộ nếu cấu hình tracking_url."""
        self.ensure_one()
        if self.tracking_url and picking.carrier_tracking_ref:
            return self.tracking_url.replace('<shipmenttrackingnumber>', picking.carrier_tracking_ref)
        return False

    def _wbh_ghn_base_url(self):
        self.ensure_one()
        return GHN_SANDBOX_BASE_URL if self.wbh_ghn_sandbox else GHN_PROD_BASE_URL

    def _wbh_ghn_headers(self):
        self.ensure_one()
        carrier_sudo = self.sudo()
        headers = {
            'Content-Type': 'application/json',
            'Token': (carrier_sudo.wbh_ghn_token or '').strip(),
        }
        if carrier_sudo.wbh_ghn_shop_id:
            headers['ShopId'] = str(carrier_sudo.wbh_ghn_shop_id)
        return headers

    def _wbh_ghn_order_weight_grams(self, order):
        """Quy đổi tổng khối lượng đơn hàng sang gram (tối thiểu 200g theo chuẩn GHN)."""
        weight_kg = order._get_estimated_weight() or 0.5
        return max(200, int(round(weight_kg * 1000)))

    def wbh_ghn_rate_shipment(self, order):
        """Gọi API GHN tính phí vận chuyển, có fallback an toàn khi thiếu token hoặc ngoại tuyến."""
        self.ensure_one()
        if not self._match_address(order.partner_shipping_id):
            return {
                'success': False,
                'price': 0.0,
                'error_message': _('Giao Hàng Nhanh không áp dụng cho địa chỉ này.'),
                'warning_message': False,
            }

        fallback_company_price = self.wbh_flat_price or 35000.0
        fallback_price = self._compute_currency(
            order, fallback_company_price, 'company_to_pricelist'
        )

        token = (self.sudo().wbh_ghn_token or '').strip()
        if not token:
            return {
                'success': True,
                'price': fallback_price,
                'error_message': False,
                'warning_message': _('Chưa cấu hình GHN Token — đang áp dụng cước tạm tính.'),
            }

        partner = order.partner_shipping_id
        to_district_id = partner.wbh_vn_district_id.ghn_district_id or self.wbh_ghn_from_district_id or 1442
        to_ward_code = partner.wbh_vn_ward_id.ghn_ward_code or ''
        payload = {
            'from_district_id': self.wbh_ghn_from_district_id or 1442,
            'service_type_id': self.wbh_ghn_service_type_id or 2,
            'to_district_id': to_district_id,
            'to_ward_code': to_ward_code,
            'weight': self._wbh_ghn_order_weight_grams(order),
            'insurance_value': int(round(max(0.0, order._compute_amount_total_without_delivery()))),
        }

        url = f'{self._wbh_ghn_base_url()}/v2/shipping-order/fee'
        try:
            response = requests.post(
                url,
                json=payload,
                headers=self._wbh_ghn_headers(),
                timeout=8,
            )
            data = response.json() if response.content else {}
            if (
                response.status_code == 200
                and data.get('code') == 200
                and isinstance(data.get('data'), dict)
                and data['data'].get('total') is not None
            ):
                fee_company = float(data['data']['total'])
                fee_order = self._compute_currency(order, fee_company, 'company_to_pricelist')
                return {
                    'success': True,
                    'price': fee_order,
                    'error_message': False,
                    'warning_message': False,
                }
            _logger.warning(
                'GHN rate_shipment phản hồi không hợp lệ (status=%s, body=%s)',
                response.status_code,
                data,
            )
        except (requests.RequestException, ValueError, TypeError) as exc:
            _logger.warning('GHN rate_shipment ngoại tuyến/lỗi kết nối: %s', exc)

        return {
            'success': True,
            'price': fallback_price,
            'error_message': False,
            'warning_message': _('Không kết nối được GHN — đang áp dụng cước tạm tính.'),
        }

    def wbh_ghn_send_shipping(self, pickings):
        """Tạo vận đơn Giao Hàng Nhanh (GHN) từ phiếu xuất kho, fallback sạch ở Sandbox."""
        self.ensure_one()
        results = []
        token = (self.sudo().wbh_ghn_token or '').strip()
        fallback_price = self.wbh_flat_price or 35000.0

        for picking in pickings:
            order = picking.sale_id
            partner = picking.partner_id or (order.partner_shipping_id if order else False)
            tracking_number = f'GHN-SANDBOX-{picking.id}'
            exact_price = fallback_price

            if token and partner:
                payload = {
                    'payment_type_id': 2,
                    'note': (order.name if order else picking.name) or 'Đơn hàng WBH',
                    'required_note': 'CHOXEMHANGKHONGTHU',
                    'to_name': partner.name or 'Khách hàng',
                    'to_phone': partner.phone or '0900000000',
                    'to_address': partner.street or 'Địa chỉ giao hàng',
                    'to_ward_code': partner.wbh_vn_ward_id.ghn_ward_code or '',
                    'to_district_id': partner.wbh_vn_district_id.ghn_district_id or self.wbh_ghn_from_district_id or 1442,
                    'weight': self._wbh_ghn_order_weight_grams(order) if order else 500,
                    'service_type_id': self.wbh_ghn_service_type_id or 2,
                }
                url = f'{self._wbh_ghn_base_url()}/v2/shipping-order/create'
                try:
                    response = requests.post(
                        url,
                        json=payload,
                        headers=self._wbh_ghn_headers(),
                        timeout=8,
                    )
                    data = response.json() if response.content else {}
                    if (
                        response.status_code == 200
                        and data.get('code') == 200
                        and isinstance(data.get('data'), dict)
                        and data['data'].get('order_code')
                    ):
                        tracking_number = str(data['data']['order_code'])
                        if data['data'].get('total_fee') is not None:
                            exact_price = float(data['data']['total_fee'])
                except (requests.RequestException, ValueError, TypeError) as exc:
                    _logger.warning('GHN send_shipping lỗi kết nối: %s', exc)

            tracking_url = f'{GHN_TRACKING_BASE_URL}{tracking_number}'
            if order:
                order.sudo().write({
                    'wbh_tracking_code': tracking_number,
                    'wbh_tracking_url': tracking_url,
                })
                order.message_post(
                    body=Markup(
                        '<p>Đã tạo vận đơn GHN: <strong>%s</strong> '
                        '(<a href="%s" target="_blank" rel="noopener noreferrer">Tra cứu</a>)</p>'
                    )
                    % (tracking_number, tracking_url)
                )

            results.append({
                'exact_price': exact_price,
                'tracking_number': tracking_number,
            })
        return results

    def wbh_ghn_get_tracking_link(self, picking):
        """Trả về URL tra cứu đơn hàng Giao Hàng Nhanh."""
        self.ensure_one()
        if picking.carrier_tracking_ref:
            return f'{GHN_TRACKING_BASE_URL}{picking.carrier_tracking_ref}'
        return False

    # ------------------------------------------------------------------ #
    # Hook mở rộng cho các đơn vị vận chuyển VN khác (GHTK / Viettel Post) #
    # ------------------------------------------------------------------ #

    def _wbh_get_provider_adapter(self, provider_code):
        """Điểm mở rộng adapter cho GHTK / Viettel Post ở các đợt tích hợp sau."""
        self.ensure_one()
        adapters = {
            'wbh_local': self._wbh_local_adapter_info,
            'wbh_ghn': self._wbh_ghn_adapter_info,
            'ghtk': self._wbh_ghtk_adapter_hook,
            'vtp': self._wbh_vtp_adapter_hook,
        }
        handler = adapters.get(provider_code)
        return handler() if handler else {}

    def _wbh_local_adapter_info(self):
        return {'code': 'wbh_local', 'name': 'Nội bộ / Đồng giá / Gom đơn', 'active': True}

    def _wbh_ghn_adapter_info(self):
        return {'code': 'wbh_ghn', 'name': 'Giao Hàng Nhanh (GHN)', 'active': True}

    def _wbh_ghtk_adapter_hook(self):
        """Hook chuẩn bị tích hợp Giao Hàng Tiết Kiệm (GHTK)."""
        return {'code': 'ghtk', 'name': 'Giao Hàng Tiết Kiệm (GHTK)', 'active': False}

    def _wbh_vtp_adapter_hook(self):
        """Hook chuẩn bị tích hợp Viettel Post (VTP)."""
        return {'code': 'vtp', 'name': 'Viettel Post (VTP)', 'active': False}
