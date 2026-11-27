# -*- coding: utf-8 -*-
import logging
import re

from odoo import _, api, fields, models
from odoo.tools.image import image_data_uri

from odoo.addons.wbh_payment_vietqr.models.vietqr_emvco import (
    build_vietqr_payload,
    generate_qr_png_base64,
    sanitize_vietqr_text,
)

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    wbh_vietqr_reference = fields.Char(
        string='Nội dung chuyển khoản VietQR',
        compute='_compute_wbh_vietqr_data',
        store=True,
        copy=False,
        help='Mã nội dung chuyển khoản ASCII không dấu dùng để nhận diện đơn hàng từ biến động số dư.',
    )
    wbh_vietqr_payload = fields.Text(
        string='Chuỗi EMVCo VietQR',
        compute='_compute_wbh_vietqr_data',
        store=True,
        copy=False,
    )
    wbh_vietqr_qr_base64 = fields.Binary(
        string='Ảnh QR VietQR',
        compute='_compute_wbh_vietqr_qr_base64',
        store=True,
        attachment=False,
        copy=False,
    )
    wbh_gateway_tx_id = fields.Char(
        string='Mã giao dịch ngân hàng / Cổng',
        copy=False,
        help='Mã giao dịch duy nhất từ SePay/PayOS/Casso dùng chống trùng lặp webhook (idempotency).',
    )

    _wbh_vietqr_reference_idx = models.Index('(wbh_vietqr_reference)')
    _wbh_gateway_tx_id_idx = models.Index('(provider_id, wbh_gateway_tx_id)')

    @api.model
    def _wbh_format_vietqr_reference(self, reference, prefix='WBH'):
        """Chuẩn hóa mã tham chiếu thành nội dung chuyển khoản ASCII ngắn gọn, không ký tự đặc biệt."""
        clean_prefix = re.sub(
            r'[^A-Za-z0-9]',
            '',
            sanitize_vietqr_text(prefix or 'WBH', max_len=12),
        ).upper() or 'WBH'
        clean_ref = re.sub(
            r'[^A-Za-z0-9]',
            '',
            sanitize_vietqr_text(reference or '', max_len=36),
        ).upper()
        if not clean_ref:
            return clean_prefix
        if clean_ref.startswith(clean_prefix):
            return clean_ref[:32]
        return f"{clean_prefix}{clean_ref}"[:32]

    @api.depends(
        'reference',
        'amount',
        'provider_id',
        'provider_id.code',
        'provider_id.wbh_vietqr_bank_bin',
        'provider_id.wbh_vietqr_account_no',
        'provider_id.wbh_vietqr_prefix',
    )
    def _compute_wbh_vietqr_data(self):
        for tx in self:
            if tx.provider_id.code != 'vietqr':
                tx.wbh_vietqr_reference = False
                tx.wbh_vietqr_payload = False
                continue

            vietqr_ref = tx._wbh_format_vietqr_reference(
                tx.reference,
                prefix=tx.provider_id.wbh_vietqr_prefix or 'WBH',
            )
            payload = build_vietqr_payload(
                bank_bin=tx.provider_id.wbh_vietqr_bank_bin or '',
                account_no=tx.provider_id.wbh_vietqr_account_no or '',
                amount=tx.amount or 0.0,
                transfer_note=vietqr_ref,
            )
            tx.wbh_vietqr_reference = vietqr_ref
            tx.wbh_vietqr_payload = payload or False

    @api.depends('wbh_vietqr_payload', 'provider_id.code')
    def _compute_wbh_vietqr_qr_base64(self):
        for tx in self:
            if tx.provider_id.code != 'vietqr' or not tx.wbh_vietqr_payload:
                tx.wbh_vietqr_qr_base64 = False
                continue
            tx.wbh_vietqr_qr_base64 = generate_qr_png_base64(tx.env, tx.wbh_vietqr_payload) or False

    def _wbh_get_qr_data_uri(self):
        """Trả về Data URI PNG an toàn để hiển thị trong QWeb."""
        self.ensure_one()
        if not self.wbh_vietqr_qr_base64:
            return ''
        return image_data_uri(self.wbh_vietqr_qr_base64)

    def _get_specific_processing_values(self, processing_values):
        """Bổ sung thông tin VietQR vào processing_values cho frontend."""
        res = super()._get_specific_processing_values(processing_values)
        if self.provider_code != 'vietqr':
            return res
        res.update({
            'wbh_vietqr_reference': self.wbh_vietqr_reference or '',
            'wbh_vietqr_payload': self.wbh_vietqr_payload or '',
            'wbh_vietqr_gateway': self.provider_id.wbh_vietqr_gateway or 'sepay',
        })
        return res

    def _get_specific_rendering_values(self, processing_values):
        """Trả về giá trị render redirect form cho VietQR và COD."""
        if self.provider_code == 'vietqr':
            return {
                'api_url': '/payment/vietqr/process',
                'reference': self.reference,
                'wbh_vietqr_reference': self.wbh_vietqr_reference or self.reference,
            }
        if self.provider_code == 'wbh_cod':
            return {
                'api_url': '/payment/wbh_cod/process',
                'reference': self.reference,
            }
        return super()._get_specific_rendering_values(processing_values)

    def _extract_amount_data(self, payment_data):
        """Bỏ qua đối chiếu số tiền ở bước redirect POST nội bộ (chỉ truyền reference)."""
        if self.provider_code in ('vietqr', 'wbh_cod') and 'amount' not in payment_data:
            return None
        return super()._extract_amount_data(payment_data)

    def _apply_updates(self, payment_data):
        """Chuyển trạng thái giao dịch sang pending khi khách xác nhận chọn VietQR hoặc COD."""
        if self.provider_code not in ('vietqr', 'wbh_cod'):
            return super()._apply_updates(payment_data)

        if self.state in ('done', 'authorized'):
            return
        if self.provider_code == 'vietqr':
            _logger.info(
                "Khởi tạo chờ thanh toán VietQR cho giao dịch %s (nội dung CK: %s).",
                self.reference,
                self.wbh_vietqr_reference,
            )
            self._set_pending(
                state_message=_("Đang chờ chuyển khoản VietQR với nội dung: %s")
                % (self.wbh_vietqr_reference or self.reference)
            )
        else:
            _logger.info("Khách hàng chọn thanh toán COD cho giao dịch %s.", self.reference)
            self._set_pending(
                state_message=_("Đơn hàng sẽ được thanh toán khi nhận hàng (COD).")
            )

    def _log_received_message(self):
        other_txs = self.filtered(lambda t: t.provider_code not in ('vietqr', 'wbh_cod'))
        super(PaymentTransaction, other_txs)._log_received_message()

    def _get_sent_message(self):
        message = super()._get_sent_message()
        if self.provider_code in ('vietqr', 'wbh_cod'):
            return _(
                "Khách hàng đã chọn phương thức %(provider_name)s.",
                provider_name=self.provider_id.name,
            )
        return message
