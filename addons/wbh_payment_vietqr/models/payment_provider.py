# -*- coding: utf-8 -*-
import logging

from odoo import _, api, fields, models
from odoo.tools.image import image_data_uri

from odoo.addons.payment import utils as payment_utils
from odoo.addons.wbh_payment_vietqr.const import (
    COD_PAYMENT_METHOD_CODES,
    DEFAULT_PAYMENT_METHOD_CODES,
    VN_BANK_SELECTION,
)
from odoo.addons.wbh_payment_vietqr.models.vietqr_emvco import (
    build_vietqr_payload,
    generate_qr_png_base64,
    get_bank_display_name,
    sanitize_vietqr_text,
)

_logger = logging.getLogger(__name__)


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[
            ('vietqr', 'VietQR (Napas 24/7)'),
            ('wbh_cod', 'COD — Thanh toán khi nhận hàng'),
        ],
        ondelete={
            'vietqr': 'set default',
            'wbh_cod': 'set default',
        },
    )

    wbh_vietqr_bank_bin = fields.Selection(
        selection=VN_BANK_SELECTION,
        string='Ngân hàng nhận (BIN)',
        help='Mã BIN Napas 247 của ngân hàng nhận chuyển khoản VietQR.',
    )
    wbh_vietqr_account_no = fields.Char(
        string='Số tài khoản nhận',
        help='Số tài khoản ngân hàng hiển thị và mã hóa trực tiếp vào QR VietQR.',
    )
    wbh_vietqr_account_name = fields.Char(
        string='Tên chủ tài khoản',
        help='Tên chủ tài khoản ngân hàng hiển thị cho khách hàng đối chiếu khi chuyển khoản.',
    )
    wbh_vietqr_prefix = fields.Char(
        string='Tiền tố nội dung CK',
        default='WBH',
        help='Tiền tố đứng đầu mã nội dung chuyển khoản để tự động đối soát (VD: WBH -> WBHS00012).',
    )
    wbh_vietqr_gateway = fields.Selection(
        selection=[
            ('sepay', 'SePay Free'),
            ('payos', 'PayOS'),
            ('casso', 'Casso'),
            ('manual', 'Thủ công'),
        ],
        string='Cổng đối soát Webhook',
        default='sepay',
        required=True,
        help='Chọn cổng nhận thông báo biến động số dư tự động (mặc định SePay Free) hoặc đối soát thủ công.',
    )
    wbh_vietqr_webhook_secret = fields.Char(
        string='Webhook Secret / API Key',
        groups='base.group_system,wbh_core.group_wbh_manager',
        copy=False,
        help='Mã API Key / Secret dùng xác thực header Authorization gửi từ SePay, PayOS hoặc Casso.',
    )
    wbh_custom_qr_image = fields.Binary(
        string='Ảnh mã QR chuyển khoản riêng',
        attachment=True,
        help='Nếu chủ shop tải ảnh QR ngân hàng riêng lên đây, hệ thống ưu tiên hiển thị ảnh QR này tại /shop/payment; nếu để trống sẽ tự sinh QR động EMVCo.',
    )
    wbh_custom_qr_filename = fields.Char(
        string='Tên tệp ảnh QR riêng',
    )

    def _get_default_payment_method_codes(self):
        """Trả về mã phương thức thanh toán mặc định cho VietQR và COD."""
        self.ensure_one()
        if self.code == 'vietqr':
            return DEFAULT_PAYMENT_METHOD_CODES
        if self.code == 'wbh_cod':
            return COD_PAYMENT_METHOD_CODES
        return super()._get_default_payment_method_codes()

    def _get_reset_values(self):
        """Xóa khóa bí mật webhook khi reset thông tin xác thực của VietQR."""
        res = super()._get_reset_values()
        if self.code == 'vietqr':
            res['wbh_vietqr_webhook_secret'] = False
        return res

    def _should_build_inline_form(self, is_validation=False):
        """Cho phép hiển thị thẻ tóm tắt inline trên /shop/payment nhưng vẫn xử lý qua redirect form."""
        if self.code in ('vietqr', 'wbh_cod'):
            return True
        return super()._should_build_inline_form(is_validation=is_validation)

    @api.model
    def _get_compatible_providers(
        self, company_id, partner_id, amount, currency_id=None, force_tokenization=False,
        is_express_checkout=False, is_validation=False, report=None, **kwargs
    ):
        """Ẩn phương thức COD nếu đơn hàng có sản phẩm Pre-order hoặc vượt hạn mức COD của website."""
        providers = super()._get_compatible_providers(
            company_id,
            partner_id,
            amount,
            currency_id=currency_id,
            force_tokenization=force_tokenization,
            is_express_checkout=is_express_checkout,
            is_validation=is_validation,
            report=report,
            **kwargs,
        )
        sale_order_id = kwargs.get('sale_order_id')
        website_id = kwargs.get('website_id')
        order = self.env['sale.order'].sudo().browse(sale_order_id).exists() if sale_order_id else self.env['sale.order']
        website = (
            order.website_id
            if order and order.website_id
            else (self.env['website'].sudo().browse(website_id).exists() if website_id else self.env['website'])
        )
        cod_providers = providers.filtered(lambda p: p.code == 'wbh_cod')
        if cod_providers:
            if website and website.wbh_store_type == 'gift':
                providers -= cod_providers
                payment_utils.add_to_report(
                    report,
                    cod_providers,
                    available=False,
                    reason=_("Cửa hàng chỉ hỗ trợ Chuyển khoản trước rồi ship (không hỗ trợ COD)."),
                )
            elif order:
                eligible, reason = order._wbh_is_cod_eligible()
                if not eligible:
                    providers -= cod_providers
                    payment_utils.add_to_report(
                        report,
                        cod_providers,
                        available=False,
                        reason=reason,
                    )
        return providers

    def _wbh_get_bank_display_name(self):
        """Trả về tên ngân hàng dễ đọc cho template QWeb."""
        self.ensure_one()
        return get_bank_display_name(self.wbh_vietqr_bank_bin)

    def _wbh_get_vietqr_reference_for_order(self, order=None, reference=None):
        """Sinh mã nội dung chuyển khoản ASCII ngắn gọn dùng hiển thị trước tại /shop/payment."""
        self.ensure_one()
        raw_ref = reference or (order.name if order else 'WBH')
        return self.env['payment.transaction']._wbh_format_vietqr_reference(
            raw_ref,
            prefix=self.wbh_vietqr_prefix or 'WBH',
        )

    def _wbh_get_qr_data_uri_for_order(self, order=None, amount=None, reference=None):
        """Ưu tiên trả về ảnh QR riêng của chủ shop; nếu chưa có thì fallback về QR động EMVCo."""
        self.ensure_one()
        provider_sudo = self.sudo()
        if provider_sudo.wbh_custom_qr_image:
            return image_data_uri(provider_sudo.wbh_custom_qr_image)

        if not provider_sudo.wbh_vietqr_bank_bin or not provider_sudo.wbh_vietqr_account_no:
            return ''

        pay_amount = amount if amount is not None else (order.amount_total if order else 0.0)
        vietqr_ref = provider_sudo._wbh_get_vietqr_reference_for_order(order=order, reference=reference)
        payload = build_vietqr_payload(
            bank_bin=provider_sudo.wbh_vietqr_bank_bin,
            account_no=provider_sudo.wbh_vietqr_account_no,
            amount=pay_amount or 0.0,
            transfer_note=vietqr_ref,
        )
        qr_b64 = generate_qr_png_base64(self.env, payload)
        return image_data_uri(qr_b64) if qr_b64 else ''

    def _wbh_parse_webhook_payload(self, payload):
        """Chuẩn hóa payload webhook từ SePay Free, PayOS hoặc Casso về một cấu trúc thống nhất.

        :param dict payload: Dữ liệu JSON nhận được từ webhook.
        :return: list[dict] các giao dịch tiền vào đã chuẩn hóa.
        """
        self.ensure_one()
        if not isinstance(payload, dict):
            return []

        gateway = self.wbh_vietqr_gateway or 'sepay'
        if gateway == 'payos':
            return self._wbh_parse_payos_payload(payload)
        if gateway == 'casso':
            return self._wbh_parse_casso_payload(payload)
        return self._wbh_parse_sepay_payload(payload)

    @api.model
    def _wbh_parse_sepay_payload(self, payload):
        """Phân tích webhook chuẩn SePay Free."""
        transfer_type = str(payload.get('transferType') or 'in').strip().lower()
        gateway_tx_id = str(payload.get('id') or payload.get('referenceCode') or '').strip()
        try:
            amount = float(payload.get('transferAmount') or 0.0)
        except (TypeError, ValueError):
            amount = 0.0
        content_parts = [
            str(payload.get('code') or ''),
            str(payload.get('content') or ''),
            str(payload.get('description') or ''),
        ]
        content = ' '.join(p for p in content_parts if p).strip()
        return [{
            'gateway': 'sepay',
            'gateway_tx_id': gateway_tx_id,
            'amount': amount,
            'content': content,
            'clean_content': sanitize_vietqr_text(content, max_len=250).upper(),
            'account_no': str(payload.get('accountNumber') or '').strip(),
            'transfer_type': transfer_type,
            'is_incoming': transfer_type == 'in',
            'reference_code': str(payload.get('referenceCode') or '').strip(),
        }]

    @api.model
    def _wbh_parse_payos_payload(self, payload):
        """Adapter hook phân tích payload webhook PayOS."""
        data = payload.get('data')
        if not isinstance(data, dict):
            return []
        gateway_tx_id = str(data.get('reference') or data.get('orderCode') or '').strip()
        try:
            amount = float(data.get('amount') or 0.0)
        except (TypeError, ValueError):
            amount = 0.0
        content = str(data.get('description') or data.get('orderCode') or '').strip()
        is_success = str(payload.get('code') or '') == '00' or bool(payload.get('success'))
        return [{
            'gateway': 'payos',
            'gateway_tx_id': gateway_tx_id,
            'amount': amount,
            'content': content,
            'clean_content': sanitize_vietqr_text(content, max_len=250).upper(),
            'account_no': str(data.get('accountNumber') or '').strip(),
            'transfer_type': 'in' if is_success else 'other',
            'is_incoming': is_success and amount > 0,
            'reference_code': str(data.get('paymentLinkId') or '').strip(),
        }]

    @api.model
    def _wbh_parse_casso_payload(self, payload):
        """Adapter hook phân tích payload webhook Casso."""
        items = payload.get('data')
        if isinstance(items, dict):
            items = [items]
        if not isinstance(items, list):
            return []
        parsed = []
        for item in items:
            if not isinstance(item, dict):
                continue
            gateway_tx_id = str(item.get('id') or item.get('tid') or '').strip()
            try:
                amount = float(item.get('amount') or 0.0)
            except (TypeError, ValueError):
                amount = 0.0
            content = str(item.get('description') or '').strip()
            parsed.append({
                'gateway': 'casso',
                'gateway_tx_id': gateway_tx_id,
                'amount': amount,
                'content': content,
                'clean_content': sanitize_vietqr_text(content, max_len=250).upper(),
                'account_no': str(item.get('bankSubAccId') or '').strip(),
                'transfer_type': 'in' if amount > 0 else 'out',
                'is_incoming': amount > 0,
                'reference_code': str(item.get('tid') or '').strip(),
            })
        return parsed
