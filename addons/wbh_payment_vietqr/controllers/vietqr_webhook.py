# -*- coding: utf-8 -*-
import base64
import hmac
import json
import logging
import os
import re

from markupsafe import Markup, escape

from odoo import _, fields
from odoo.exceptions import ValidationError
from odoo.http import Controller, request, route

from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment.controllers import post_processing as payment_post_processing
from odoo.addons.wbh_payment_vietqr.models.vietqr_emvco import sanitize_vietqr_text
from odoo.addons.website_sale.controllers.payment import PaymentPortal as WebsiteSalePaymentPortal

_logger = logging.getLogger(__name__)


class PaymentPortalVietQR(WebsiteSalePaymentPortal):
    """Kiểm tra điều kiện COD tại bước tạo giao dịch eCommerce để chống giả mạo RPC."""

    def _validate_transaction_for_order(self, transaction, sale_order):
        super()._validate_transaction_for_order(transaction, sale_order)
        if transaction.provider_code == 'wbh_cod':
            eligible, reason = sale_order._wbh_is_cod_eligible()
            if not eligible:
                raise ValidationError(reason)


class VietQRController(Controller):

    @staticmethod
    def _json_response(payload, status=200):
        return request.make_response(
            json.dumps(payload, ensure_ascii=False),
            headers=[('Content-Type', 'application/json; charset=utf-8')],
            status=status,
        )

    @staticmethod
    def _extract_bearer_or_apikey():
        headers = request.httprequest.headers
        auth_header = (headers.get('Authorization') or '').strip()
        if auth_header:
            lowered = auth_header.lower()
            if lowered.startswith('apikey '):
                return auth_header[7:].strip()
            if lowered.startswith('bearer '):
                return auth_header[7:].strip()
            return auth_header
        for header_name in ('X-API-Key', 'X-Webhook-Secret'):
            val = (headers.get(header_name) or '').strip()
            if val:
                return val
        return ''

    @staticmethod
    def _authenticate_provider(provided_token, gateway=None):
        """Xác thực API Key / Bearer Token bằng hmac.compare_digest chống timing attack."""
        if not provided_token:
            return None
        domain = [('code', '=', 'vietqr'), ('state', 'in', ('enabled', 'test'))]
        if gateway:
            domain.append(('wbh_vietqr_gateway', '=', gateway))
        providers = request.env['payment.provider'].sudo().search(domain)
        matched_provider = None
        for provider in providers:
            secret = (provider.wbh_vietqr_webhook_secret or '').strip()
            if not secret:
                continue
            if hmac.compare_digest(provided_token, secret):
                matched_provider = provider
        return matched_provider

    @staticmethod
    def _match_transaction(provider, clean_content):
        """Khớp giao dịch VietQR dựa trên mã nội dung chuyển khoản ASCII, tránh trùng tiền tố."""
        if not clean_content:
            return request.env['payment.transaction']

        token_content = re.sub(r'[^A-Z0-9]+', ' ', clean_content).strip()
        compact_content = re.sub(r'[^A-Z0-9]', '', clean_content)

        candidates = request.env['payment.transaction'].sudo().search([
            ('provider_id', '=', provider.id),
            ('provider_code', '=', 'vietqr'),
            ('state', 'in', ('draft', 'pending', 'done')),
            ('wbh_vietqr_reference', '!=', False),
        ], order='id desc', limit=200)

        # Ưu tiên chuỗi dài hơn trước để WBH10 không bị khớp nhầm thành WBH1.
        sorted_candidates = sorted(
            candidates,
            key=lambda t: len(t.wbh_vietqr_reference or ''),
            reverse=True,
        )
        for tx in sorted_candidates:
            ref = re.sub(r'[^A-Z0-9]', '', (tx.wbh_vietqr_reference or '').upper())
            if not ref:
                continue
            if re.search(rf'(?<![A-Z0-9]){re.escape(ref)}(?![A-Z0-9])', token_content):
                return tx
            if re.search(rf'{re.escape(ref)}(?![0-9])', compact_content):
                return tx
        return request.env['payment.transaction']

    @route('/payment/vietqr/process', type='http', auth='public', methods=['POST'], csrf=False)
    def vietqr_process_transaction(self, **post):
        request.env['payment.transaction'].sudo()._process('vietqr', post)
        return request.redirect('/payment/status')

    @route('/payment/wbh_cod/process', type='http', auth='public', methods=['POST'], csrf=False)
    def wbh_cod_process_transaction(self, **post):
        request.env['payment.transaction'].sudo()._process('wbh_cod', post)
        return request.redirect('/payment/status')

    @route('/payment/vietqr/webhook/sepay', type='http', auth='public', methods=['POST'], csrf=False)
    def vietqr_webhook_sepay(self, **kwargs):
        """Nhận webhook biến động số dư từ SePay Free (hoặc PayOS/Casso theo cấu hình provider)."""
        token = self._extract_bearer_or_apikey()
        provider = self._authenticate_provider(token)
        if not provider:
            _logger.warning("Từ chối webhook VietQR do thiếu hoặc sai API Key / Bearer token.")
            return self._json_response({'success': False, 'error': 'Unauthorized'}, status=401)

        raw_body = request.httprequest.get_data(as_text=True) or ''
        try:
            payload = json.loads(raw_body)
        except (ValueError, TypeError):
            _logger.warning("Webhook VietQR nhận JSON không hợp lệ.")
            return self._json_response({'success': False, 'error': 'Invalid JSON payload'}, status=400)

        if not isinstance(payload, dict):
            return self._json_response({'success': False, 'error': 'Payload must be a JSON object'}, status=400)

        entries = provider._wbh_parse_webhook_payload(payload)
        if not entries:
            return self._json_response({'success': True, 'matched': False, 'reason': 'empty_entries'}, status=200)

        results = []
        for entry in entries:
            if not entry.get('is_incoming'):
                results.append({'ignored': True, 'reason': 'not_incoming'})
                continue

            gateway_tx_id = entry.get('gateway_tx_id') or ''
            if gateway_tx_id:
                dup_tx = request.env['payment.transaction'].sudo().search([
                    ('provider_id', '=', provider.id),
                    ('wbh_gateway_tx_id', '=', gateway_tx_id),
                ], limit=1)
                if dup_tx:
                    results.append({
                        'duplicate': True,
                        'reference': dup_tx.reference,
                        'state': dup_tx.state,
                    })
                    continue

            clean_content = entry.get('clean_content') or sanitize_vietqr_text(entry.get('content', ''), max_len=250).upper()
            tx = self._match_transaction(provider, clean_content)
            if not tx:
                _logger.info("Webhook VietQR không tìm thấy giao dịch khớp nội dung: %s", clean_content)
                results.append({'matched': False})
                continue

            if tx.state == 'done':
                results.append({
                    'already_done': True,
                    'reference': tx.reference,
                    'state': tx.state,
                })
                continue

            paid_amount = float(entry.get('amount') or 0.0)
            if tx.currency_id.compare_amounts(paid_amount, tx.amount) < 0:
                audit_warn = Markup(
                    "<p><strong>[VietQR Webhook]</strong> Nhận tiền chưa đủ cho giao dịch "
                    "<code>%s</code>: nhận <strong>%s</strong> / cần <strong>%s</strong> (Mã GD: %s).</p>"
                ) % (
                    escape(tx.reference),
                    escape(f"{int(round(paid_amount)):,}"),
                    escape(f"{int(round(tx.amount)):,}"),
                    escape(gateway_tx_id or '-'),
                )
                for order in tx.sale_order_ids:
                    order.sudo().message_post(body=audit_warn)
                tx.sudo().write({
                    'state_message': _(
                        "Số tiền chuyển khoản chưa đủ (%s / %s)."
                    ) % (int(round(paid_amount)), int(round(tx.amount))),
                })
                results.append({
                    'matched': True,
                    'underpaid': True,
                    'reference': tx.reference,
                    'paid_amount': paid_amount,
                    'expected_amount': tx.amount,
                })
                continue

            tx.sudo().write({
                'wbh_gateway_tx_id': gateway_tx_id or tx.wbh_vietqr_reference,
                'provider_reference': gateway_tx_id or tx.wbh_vietqr_reference,
            })
            tx.sudo()._set_done(
                state_message=_(
                    "Đã xác nhận thanh toán VietQR qua %(gateway)s (Mã GD: %(tx_id)s)."
                ) % {
                    'gateway': (entry.get('gateway') or 'sepay').upper(),
                    'tx_id': gateway_tx_id or '-',
                }
            )
            tx.sudo()._post_process()

            audit_body = Markup(
                "<p><strong>[VietQR %s]</strong> Đã đối soát thành công giao dịch <code>%s</code> "
                "— Số tiền: <strong>%s</strong> — Mã GD: <code>%s</code> — Nội dung: <em>%s</em>.</p>"
            ) % (
                escape((entry.get('gateway') or 'sepay').upper()),
                escape(tx.reference),
                escape(f"{int(round(paid_amount)):,}"),
                escape(gateway_tx_id or '-'),
                escape(entry.get('content') or tx.wbh_vietqr_reference or ''),
            )
            for order in tx.sale_order_ids:
                order.sudo().message_post(body=audit_body)

            results.append({
                'matched': True,
                'reference': tx.reference,
                'state': tx.state,
                'gateway_tx_id': gateway_tx_id,
            })

        return self._json_response({'success': True, 'results': results}, status=200)

    @route('/payment/vietqr/status/<string:reference>', type='http', auth='public', methods=['GET'], website=True, sitemap=False)
    def vietqr_transaction_status(self, reference, access_token=None, **kwargs):
        """API JSON trả về trạng thái giao dịch VietQR có kiểm tra quyền truy cập."""
        tx = request.env['payment.transaction'].sudo().search([
            '|',
            ('reference', '=', reference),
            ('wbh_vietqr_reference', '=', reference),
        ], limit=1)
        if not tx:
            return self._json_response({'error': 'Transaction not found'}, status=404)

        if not self._can_access_transaction(tx, access_token=access_token):
            return self._json_response({'error': 'Forbidden'}, status=403)

        return self._json_response({
            'reference': tx.reference,
            'wbh_vietqr_reference': tx.wbh_vietqr_reference or tx.reference,
            'state': tx.state,
            'is_done': tx.state == 'done',
            'amount': tx.amount,
            'landing_route': tx.landing_route or '/shop/confirmation',
        }, status=200)

    @staticmethod
    def _can_access_transaction(tx, access_token=None):
        """Kiểm tra phiên trình duyệt, access_token hoặc chủ sở hữu giao dịch."""
        monitored_key = payment_post_processing.PaymentPostProcessing.MONITORED_TX_ID_KEY
        if tx.id in (
            request.session.get(monitored_key),
            request.session.get('__website_sale_last_tx_id'),
        ):
            return True

        user = request.env.user
        if not user._is_public():
            if user._is_internal():
                return True
            if tx.partner_id.commercial_partner_id == user.partner_id.commercial_partner_id:
                return True

        if access_token:
            if payment_utils.check_access_token(access_token, tx.partner_id.id, tx.amount, tx.currency_id.id):
                return True
            for order in tx.sale_order_ids:
                if order.access_token and hmac.compare_digest(str(access_token), str(order.access_token)):
                    return True

        return False

    MAX_PROOF_IMAGE_BYTES = 5 * 1024 * 1024  # 5MB

    @staticmethod
    def _detect_proof_image_type(raw_bytes):
        """Kiểm tra magic bytes của ảnh (chỉ cho phép PNG, JPEG, WEBP)."""
        if not raw_bytes:
            return None, None
        if raw_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
            return '.png', 'image/png'
        if raw_bytes.startswith(b'\xff\xd8\xff'):
            return '.jpg', 'image/jpeg'
        if len(raw_bytes) >= 12 and raw_bytes[:4] == b'RIFF' and raw_bytes[8:12] == b'WEBP':
            return '.webp', 'image/webp'
        return None, None

    @staticmethod
    def _sanitize_proof_filename(raw_name, order_name, ext):
        base = os.path.basename(raw_name or 'bill_ck')
        stem = os.path.splitext(base)[0]
        clean_stem = re.sub(r'[^A-Za-z0-9._-]+', '_', stem).strip('._-') or 'bill_ck'
        clean_order = re.sub(r'[^A-Za-z0-9_-]+', '_', order_name or 'order')
        return f"bill_ck_{clean_order}_{clean_stem[:40]}{ext}"

    def _can_access_sale_order(self, order_sudo, access_token=None):
        """Kiểm tra phiên đặt hàng, access_token hoặc chủ đơn hàng chống IDOR."""
        if not order_sudo or not order_sudo.exists():
            return False

        cart = getattr(request, 'cart', False)
        if order_sudo.id in (
            request.session.get('sale_order_id'),
            request.session.get('sale_last_order_id'),
            cart.id if cart else None,
        ):
            return True

        user = request.env.user
        if not user._is_public():
            if user._is_internal():
                return True
            if order_sudo.partner_id.commercial_partner_id == user.partner_id.commercial_partner_id:
                return True

        if access_token:
            token_str = str(access_token).strip()
            if order_sudo.access_token and hmac.compare_digest(token_str, str(order_sudo.access_token)):
                return True
            if payment_utils.check_access_token(
                token_str,
                order_sudo.partner_invoice_id.id,
                order_sudo.amount_total,
                order_sudo.currency_id.id,
            ):
                return True
            for tx in order_sudo.transaction_ids:
                if self._can_access_transaction(tx, access_token=token_str):
                    return True

        return False

    @route('/payment/vietqr/upload_proof', type='http', auth='public', methods=['POST'], website=True, sitemap=False)
    def vietqr_upload_payment_proof(self, order_id=None, access_token=None, **kwargs):
        """Nhận ảnh chụp màn hình chuyển khoản ('cap màn hình ck'), kiểm tra chặt magic bytes & <= 5MB."""
        try:
            parsed_order_id = int(order_id)
        except (TypeError, ValueError):
            return self._json_response({'success': False, 'error': 'Mã đơn hàng không hợp lệ.'}, status=400)

        order_sudo = request.env['sale.order'].sudo().browse(parsed_order_id).exists()
        if not order_sudo or order_sudo.state == 'cancel':
            return self._json_response({'success': False, 'error': 'Không tìm thấy đơn hàng hợp lệ.'}, status=404)

        if not self._can_access_sale_order(order_sudo, access_token=access_token):
            return self._json_response({'success': False, 'error': 'Không có quyền tải bill cho đơn hàng này.'}, status=403)

        upload_file = request.httprequest.files.get('proof_file')
        if not upload_file:
            return self._json_response({'success': False, 'error': 'Vui lòng chọn ảnh chụp màn hình chuyển khoản.'}, status=400)

        raw_bytes = upload_file.stream.read(self.MAX_PROOF_IMAGE_BYTES + 1)
        if not raw_bytes:
            return self._json_response({'success': False, 'error': 'Tệp ảnh trống, vui lòng chọn lại.'}, status=400)
        if len(raw_bytes) > self.MAX_PROOF_IMAGE_BYTES:
            return self._json_response({'success': False, 'error': 'Dung lượng ảnh vượt quá giới hạn 5MB.'}, status=400)

        ext, detected_mime = self._detect_proof_image_type(raw_bytes)
        if not ext or not detected_mime:
            return self._json_response(
                {'success': False, 'error': 'Chỉ hỗ trợ ảnh định dạng PNG, JPG/JPEG hoặc WEBP.'},
                status=400,
            )

        safe_filename = self._sanitize_proof_filename(upload_file.filename, order_sudo.name, ext)
        attachment = request.env['ir.attachment'].sudo().create({
            'name': safe_filename,
            'datas': base64.b64encode(raw_bytes),
            'res_model': 'sale.order',
            'res_id': order_sudo.id,
            'mimetype': detected_mime,
            'description': _('Ảnh chụp màn hình chuyển khoản khách hàng gửi từ trang thanh toán.'),
        })

        uploaded_at = fields.Datetime.now()
        order_sudo.sudo().write({
            'wbh_payment_proof_attachment_id': attachment.id,
            'wbh_payment_proof_uploaded_at': uploaded_at,
        })
        size_kb = max(1, (len(raw_bytes) + 1023) // 1024)
        order_sudo.sudo().message_post(
            body=Markup(
                "<p><strong>[Bill Chuyển Khoản]</strong> Khách hàng đã tải lên ảnh xác nhận chuyển khoản "
                "<code>%s</code> (%s KB).</p>"
            ) % (escape(safe_filename), escape(str(size_kb))),
            attachment_ids=[attachment.id],
        )

        return self._json_response({
            'success': True,
            'attachment_id': attachment.id,
            'filename': safe_filename,
            'size_kb': size_kb,
            'message': 'Đã gửi ảnh bill chuyển khoản thành công! Shop sẽ kiểm tra và xác nhận đơn cho bạn.',
        }, status=200)
