# -*- coding: utf-8 -*-
import base64
import json

from odoo.fields import Command
from odoo.tests import HttpCase, TransactionCase, tagged

from odoo.addons.wbh_payment_vietqr.models.vietqr_emvco import (
    build_vietqr_payload,
    crc16_ccitt,
    generate_qr_png_base64,
    sanitize_vietqr_text,
)


@tagged('post_install', '-at_install')
class TestVietQRCore(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vnd = cls.env.ref('base.VND')
        cls.vnd.active = True
        cls.env.company.currency_id = cls.vnd

        cls.partner = cls.env['res.partner'].create({
            'name': 'Khách Hàng Test VietQR',
            'email': 'vietqr_test@example.com',
        })
        cls.website = cls.env.ref('wbh_core.website_gift_store')
        cls.vietqr_provider = cls.env.ref('wbh_payment_vietqr.payment_provider_vietqr')
        cls.vietqr_provider.write({
            'state': 'test',
            'is_published': True,
            'wbh_vietqr_bank_bin': '970422',
            'wbh_vietqr_account_no': '0123456789',
            'wbh_vietqr_account_name': '360 CORP TEST',
            'wbh_vietqr_prefix': 'WBH',
            'wbh_vietqr_gateway': 'sepay',
            'wbh_vietqr_webhook_secret': 'secret-sepay-test-key-123',
        })
        cls.vietqr_method = cls.env.ref('wbh_payment_vietqr.payment_method_vietqr')
        cls.vietqr_method.active = True

        cls.cod_provider = cls.env.ref('wbh_payment_vietqr.payment_provider_cod')
        cls.cod_provider.write({
            'state': 'test',
            'is_published': True,
        })
        cls.cod_method = cls.env.ref('wbh_payment_vietqr.payment_method_cod')
        cls.cod_method.active = True

    def test_01_crc16_ccitt_and_emvco_payload(self):
        """Kiểm tra chuẩn CRC16-CCITT (0x1021/0xFFFF) và cấu trúc EMVCo / Napas 247."""
        self.assertEqual(crc16_ccitt(b'123456789'), '29B1')

        clean = sanitize_vietqr_text('Thanh toán đơn hàng Đặng Châu #01')
        self.assertEqual(clean, 'Thanh toan don hang Dang Chau 01')

        payload = build_vietqr_payload(
            bank_bin='970422',
            account_no='0123456789',
            amount=150000,
            transfer_note='WBHSO001',
        )
        self.assertTrue(payload.startswith('000201010212'))
        self.assertIn('A000000727', payload)
        self.assertIn('QRIBFTTA', payload)
        self.assertIn('970422', payload)
        self.assertIn('0123456789', payload)
        self.assertIn('5303704', payload)
        self.assertIn('5406150000', payload)
        self.assertIn('5802VN', payload)
        self.assertIn('WBHSO001', payload)

        # Kiểm chứng CRC 4 ký tự cuối của payload
        body_with_crc_tag = payload[:-4]
        expected_crc = crc16_ccitt(body_with_crc_tag.encode('ascii'))
        self.assertEqual(payload[-4:], expected_crc)

    def test_02_offline_qr_generation(self):
        """Kiểm tra sinh ảnh PNG base64 offline bằng ir.actions.report.barcode."""
        payload = build_vietqr_payload('970422', '0123456789', 250000, 'WBHTEST02')
        qr_b64 = generate_qr_png_base64(self.env, payload)
        self.assertTrue(qr_b64)
        raw_png = base64.b64decode(qr_b64)
        self.assertTrue(raw_png.startswith(b'\x89PNG'))

    def test_03_cod_restriction_preorder_and_max_amount(self):
        """Kiểm tra quy tắc chặn COD cho hàng Pre-order và vượt hạn mức COD của website."""
        product_normal = self.env['product.product'].create({
            'name': 'Gấu Bông Sẵn Kho',
            'list_price': 200000.0,
            'wbh_allow_cod': True,
        })
        product_preorder = self.env['product.product'].create({
            'name': 'Figure Pre-order',
            'list_price': 200000.0,
            'wbh_allow_cod': False,
        })

        # Trường hợp 1: Hàng sẵn kho + dưới hạn mức -> được phép COD
        self.website.write({'wbh_cod_max_amount': 500000.0, 'wbh_cod_deposit_percent': 30.0})
        order_ok = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'website_id': self.website.id,
            'order_line': [Command.create({'product_id': product_normal.id, 'product_uom_qty': 1})],
        })
        self.assertTrue(order_ok.wbh_allow_cod)
        providers = self.env['payment.provider']._get_compatible_providers(
            self.env.company.id,
            self.partner.id,
            order_ok.amount_total,
            currency_id=self.vnd.id,
            sale_order_id=order_ok.id,
        )
        self.assertIn(self.cod_provider, providers)
        self.assertIn(self.vietqr_provider, providers)

        # Trường hợp 2: Có sản phẩm Pre-order (wbh_allow_cod=False) -> ẩn COD
        order_preorder = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'website_id': self.website.id,
            'order_line': [Command.create({'product_id': product_preorder.id, 'product_uom_qty': 1})],
        })
        self.assertFalse(order_preorder.wbh_allow_cod)
        providers_po = self.env['payment.provider']._get_compatible_providers(
            self.env.company.id,
            self.partner.id,
            order_preorder.amount_total,
            currency_id=self.vnd.id,
            sale_order_id=order_preorder.id,
        )
        self.assertNotIn(self.cod_provider, providers_po)
        self.assertIn(self.vietqr_provider, providers_po)

        # Trường hợp 3: Vượt hạn mức COD tối đa -> ẩn COD và tính tiền đặt cọc gợi ý
        order_over = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'website_id': self.website.id,
            'order_line': [Command.create({'product_id': product_normal.id, 'product_uom_qty': 3})],
        })
        self.assertFalse(order_over.wbh_allow_cod)
        self.assertGreater(order_over.wbh_cod_deposit_amount, 0)
        providers_over = self.env['payment.provider']._get_compatible_providers(
            self.env.company.id,
            self.partner.id,
            order_over.amount_total,
            currency_id=self.vnd.id,
            sale_order_id=order_over.id,
        )
        self.assertNotIn(self.cod_provider, providers_over)


@tagged('post_install', '-at_install')
class TestVietQRWebhookHttp(HttpCase):

    def setUp(self):
        super().setUp()
        self.vnd = self.env.ref('base.VND')
        self.vnd.active = True
        self.env.company.currency_id = self.vnd

        self.partner = self.env['res.partner'].create({
            'name': 'Khách Webhook SePay',
            'email': 'webhook@example.com',
        })
        self.vietqr_provider = self.env.ref('wbh_payment_vietqr.payment_provider_vietqr')
        self.vietqr_provider.write({
            'state': 'test',
            'is_published': True,
            'wbh_vietqr_bank_bin': '970422',
            'wbh_vietqr_account_no': '0123456789',
            'wbh_vietqr_account_name': '360 CORP',
            'wbh_vietqr_prefix': 'WBH',
            'wbh_vietqr_gateway': 'sepay',
            'wbh_vietqr_webhook_secret': 'sepay-super-secret-token',
        })
        self.vietqr_method = self.env.ref('wbh_payment_vietqr.payment_method_vietqr')
        self.vietqr_method.active = True

        self.product = self.env['product.product'].create({
            'name': 'Móc Khóa Anime',
            'list_price': 120000.0,
        })
        self.order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [Command.create({'product_id': self.product.id, 'product_uom_qty': 1})],
        })
        self.tx = self.env['payment.transaction'].create({
            'provider_id': self.vietqr_provider.id,
            'payment_method_id': self.vietqr_method.id,
            'amount': self.order.amount_total,
            'currency_id': self.vnd.id,
            'partner_id': self.partner.id,
            'reference': self.order.name,
            'sale_order_ids': [Command.set([self.order.id])],
        })
        self.tx._set_pending()

    def test_01_sepay_webhook_reject_401(self):
        """Từ chối HTTP 401 khi thiếu hoặc sai Authorization header."""
        payload = json.dumps({
            'id': 1001,
            'transferType': 'in',
            'transferAmount': self.tx.amount,
            'content': self.tx.wbh_vietqr_reference,
        })
        resp_missing = self.url_open(
            '/payment/vietqr/webhook/sepay',
            data=payload,
            headers={'Content-Type': 'application/json'},
        )
        self.assertEqual(resp_missing.status_code, 401)

        resp_wrong = self.url_open(
            '/payment/vietqr/webhook/sepay',
            data=payload,
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Apikey wrong-secret',
            },
        )
        self.assertEqual(resp_wrong.status_code, 401)
        self.tx.invalidate_recordset()
        self.assertEqual(self.tx.state, 'pending')

    def test_02_sepay_webhook_success_and_idempotency(self):
        """Webhook hợp lệ chuyển transaction -> done, xác nhận đơn hàng và chống trùng lặp."""
        payload = json.dumps({
            'id': 889900,
            'gateway': 'MBBank',
            'transferType': 'in',
            'transferAmount': int(round(self.tx.amount)),
            'content': f"CHUYEN KHOAN {self.tx.wbh_vietqr_reference} CAM ON",
            'accountNumber': '0123456789',
            'referenceCode': 'FT263320001',
        })
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Apikey sepay-super-secret-token',
        }
        resp = self.url_open('/payment/vietqr/webhook/sepay', data=payload, headers=headers)
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body.get('success'))

        self.tx.invalidate_recordset()
        self.order.invalidate_recordset()
        self.assertEqual(self.tx.state, 'done')
        self.assertEqual(self.tx.wbh_gateway_tx_id, '889900')
        self.assertEqual(self.order.state, 'sale')

        # Gửi lại webhook trùng mã GD ngân hàng -> idempotent 200 duplicate
        resp_dup = self.url_open('/payment/vietqr/webhook/sepay', data=payload, headers=headers)
        self.assertEqual(resp_dup.status_code, 200)
        dup_body = resp_dup.json()
        self.assertTrue(dup_body.get('success'))
        self.assertTrue(dup_body['results'][0].get('duplicate'))
