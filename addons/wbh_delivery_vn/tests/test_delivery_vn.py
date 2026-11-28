# -*- coding: utf-8 -*-
import json
from unittest.mock import MagicMock, patch

import requests

from odoo.exceptions import ValidationError
from odoo.fields import Command
from odoo.tests import Form, HttpCase, TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestWbhDeliveryVn(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env.ref('wbh_core.website_gift_store')
        cls.vnd = cls.env.ref('base.VND')
        cls.vnd.active = True
        cls.env.company.currency_id = cls.vnd

        cls.pricelist_vnd = cls.env['product.pricelist'].create({
            'name': 'Bảng giá VNĐ Test',
            'currency_id': cls.vnd.id,
        })

        cls.province_hcm = cls.env.ref('wbh_delivery_vn.vn_province_hcm')
        cls.district_q1 = cls.env.ref('wbh_delivery_vn.vn_district_hcm_q1')
        cls.ward_ben_nghe = cls.env.ref('wbh_delivery_vn.vn_ward_hcm_q1_ben_nghe')
        cls.province_hn = cls.env.ref('wbh_delivery_vn.vn_province_hn')
        cls.district_hk = cls.env.ref('wbh_delivery_vn.vn_district_hn_hoan_kiem')

        cls.carrier_vtp = cls.env.ref('wbh_delivery_vn.carrier_wbh_viettel_post')
        cls.carrier_std = cls.env.ref('wbh_delivery_vn.carrier_wbh_standard')
        cls.carrier_hold = cls.env.ref('wbh_delivery_vn.carrier_wbh_hold_order')
        cls.carrier_ghn = cls.env.ref('wbh_delivery_vn.carrier_wbh_ghn')
        cls.province_ct = cls.env.ref('wbh_delivery_vn.vn_province_ct')
        cls.province_dn = cls.env.ref('wbh_delivery_vn.vn_province_dn')

        cls.partner = cls.env['res.partner'].create({
            'name': 'Khách Hàng Test WBH',
            'street': '12 Lê Lợi',
            'phone': '0901234567',
            'email': 'khachhang@wbh.test',
            'country_id': cls.env.ref('base.vn').id,
            'wbh_vn_province_id': cls.province_hcm.id,
            'wbh_vn_district_id': cls.district_q1.id,
            'wbh_vn_ward_id': cls.ward_ben_nghe.id,
        })

        cls.product_100k = cls.env['product.product'].create({
            'name': 'Móc khóa Anime Test 100k',
            'type': 'consu',
            'list_price': 100000.0,
            'weight': 0.3,
        })

    def _create_order(self, qty=1):
        return self.env['sale.order'].create({
            'website_id': self.website.id,
            'partner_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'pricelist_id': self.pricelist_vnd.id,
            'order_line': [
                Command.create({
                    'product_id': self.product_100k.id,
                    'product_uom_qty': qty,
                    'price_unit': 100000.0,
                }),
            ],
        })

    def test_01_seeded_data_and_hidden_delivery_products(self):
        """Kiểm tra đủ 5 thành phố mẫu, chỉ bật ĐVVC VIETTEL POST và ẩn sản phẩm dịch vụ ship."""
        provinces = self.env['wbh.vn.province'].search([
            ('code', 'in', ['HCM', 'HN', 'DN', 'HP', 'CT']),
        ])
        self.assertEqual(len(provinces), 5)
        self.assertTrue(self.carrier_vtp.is_published)
        self.assertFalse(self.carrier_std.is_published)
        self.assertFalse(self.carrier_hold.is_published)
        self.assertFalse(self.carrier_ghn.is_published)
        for carrier in (self.carrier_vtp, self.carrier_std, self.carrier_hold, self.carrier_ghn):
            self.assertEqual(carrier.product_id.type, 'service')
            self.assertFalse(carrier.product_id.sale_ok)
            self.assertFalse(carrier.product_id.is_published)

    def test_02_local_flat_rate_and_freeship_threshold(self):
        """Đơn < 300k tính đồng giá 30.000đ; đơn >= 300k được Freeship 0đ."""
        order_under = self._create_order(qty=2)  # 200.000đ
        rate_under = self.carrier_std.rate_shipment(order_under)
        self.assertTrue(rate_under['success'])
        self.assertEqual(rate_under['price'], 30000.0)

        order_over = self._create_order(qty=3)  # 300.000đ
        rate_over = self.carrier_std.rate_shipment(order_over)
        self.assertTrue(rate_over['success'])
        self.assertEqual(rate_over['price'], 0.0)
        self.assertTrue(rate_over['warning_message'])

    def test_03_hold_order_zero_shipping_and_flag(self):
        """Gom đơn / Giữ hàng tại shop tính 0đ ship và bật wbh_is_hold_order trên sale.order."""
        order = self._create_order(qty=1)
        rate_hold = self.carrier_hold.rate_shipment(order)
        self.assertTrue(rate_hold['success'])
        self.assertEqual(rate_hold['price'], 0.0)

        order._set_delivery_method(self.carrier_hold)
        self.assertEqual(order.carrier_id, self.carrier_hold)
        self.assertTrue(order.wbh_is_hold_order)
        self.assertEqual(order.amount_delivery, 0.0)

        order.action_confirm()
        self.assertTrue(order.wbh_is_hold_order)

        # Đổi lại giao hàng tiêu chuẩn phải tắt cờ Gom đơn
        order_2 = self._create_order(qty=1)
        order_2._set_delivery_method(self.carrier_hold)
        self.assertTrue(order_2.wbh_is_hold_order)
        order_2._set_delivery_method(self.carrier_std)
        self.assertFalse(order_2.wbh_is_hold_order)
        self.assertEqual(order_2.amount_delivery, 30000.0)

    def test_04_vn_address_cascade_onchange_and_constraints(self):
        """Kiểm tra cascade 3 cấp Tỉnh/TP -> Quận/Huyện -> Phường/Xã trên res.partner."""
        writable = self.env['res.partner']._get_frontend_writable_fields()
        self.assertTrue(
            {'wbh_vn_province_id', 'wbh_vn_district_id', 'wbh_vn_ward_id'}.issubset(writable)
        )

        cascade_partner = self.env['res.partner'].create({
            'name': 'Khách Hàng Cascade Test',
            'country_id': self.env.ref('base.vn').id,
            'wbh_vn_province_id': self.province_hcm.id,
            'wbh_vn_district_id': self.district_q1.id,
            'wbh_vn_ward_id': self.ward_ben_nghe.id,
        })

        with Form(cascade_partner) as partner_form:
            self.assertEqual(partner_form.wbh_vn_district_id, self.district_q1)
            self.assertEqual(partner_form.wbh_vn_ward_id, self.ward_ben_nghe)
            partner_form.wbh_vn_province_id = self.province_hn
            self.assertFalse(partner_form.wbh_vn_district_id)
            self.assertFalse(partner_form.wbh_vn_ward_id)

        with self.assertRaises(ValidationError):
            cascade_partner.write({
                'wbh_vn_province_id': self.province_hcm.id,
                'wbh_vn_district_id': self.district_hk.id,
            })

    def test_05_ghn_rate_mocked_and_fallback(self):
        """Kiểm tra tính cước GHN (mock JSON + fallback an toàn khi thiếu token/offline)."""
        order = self._create_order(qty=1)

        # Trường hợp 1: Chưa có token -> fallback an toàn 35.000đ
        self.carrier_ghn.sudo().wbh_ghn_token = False
        res_no_token = self.carrier_ghn.rate_shipment(order)
        self.assertTrue(res_no_token['success'])
        self.assertEqual(res_no_token['price'], 35000.0)
        self.assertTrue(res_no_token['warning_message'])

        # Trường hợp 2: Có token, mock GHN trả về cước 42.500đ
        self.carrier_ghn.sudo().wbh_ghn_token = 'test-ghn-token-sandbox'
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'{"code": 200}'
        mock_response.json.return_value = {
            'code': 200,
            'message': 'Success',
            'data': {'total': 42500},
        }
        with patch(
            'odoo.addons.wbh_delivery_vn.models.delivery_carrier.requests.post',
            return_value=mock_response,
        ) as mock_post:
            res_mocked = self.carrier_ghn.rate_shipment(order)
            self.assertTrue(res_mocked['success'])
            self.assertEqual(res_mocked['price'], 42500.0)
            mock_post.assert_called_once()
            self.assertEqual(mock_post.call_args.kwargs.get('timeout'), 8)
            sent_json = mock_post.call_args.kwargs.get('json', {})
            self.assertEqual(sent_json.get('to_district_id'), self.district_q1.ghn_district_id)
            self.assertEqual(sent_json.get('to_ward_code'), self.ward_ben_nghe.ghn_ward_code)

        # Trường hợp 3: Lỗi mạng / timeout -> fallback an toàn
        with patch(
            'odoo.addons.wbh_delivery_vn.models.delivery_carrier.requests.post',
            side_effect=requests.Timeout('GHN timeout'),
        ):
            res_offline = self.carrier_ghn.rate_shipment(order)
            self.assertTrue(res_offline['success'])
            self.assertEqual(res_offline['price'], 35000.0)
            self.assertTrue(res_offline['warning_message'])

    def test_06_viettel_post_dynamic_rate_by_province(self):
        """Kiểm tra ĐVVC VIETTEL POST tính cước động 12.000đ - 20.000đ theo tỉnh/vùng miền."""
        # Nội tỉnh HCM (origin mặc định HCM) -> 12.000đ
        order_hcm = self._create_order(qty=1)
        rate_hcm = self.carrier_vtp.rate_shipment(order_hcm)
        self.assertTrue(rate_hcm['success'])
        self.assertEqual(rate_hcm['price'], 12000.0)

        # Cùng miền Nam (Cần Thơ) -> 15.000đ
        partner_ct = self.partner.copy({
            'wbh_vn_province_id': self.province_ct.id,
            'wbh_vn_district_id': False,
            'wbh_vn_ward_id': False,
        })
        order_ct = self._create_order(qty=1)
        order_ct.partner_shipping_id = partner_ct
        rate_ct = self.carrier_vtp.rate_shipment(order_ct)
        self.assertTrue(rate_ct['success'])
        self.assertEqual(rate_ct['price'], 15000.0)

        # Liên miền (Hà Nội / Đà Nẵng) -> 20.000đ
        partner_hn = self.partner.copy({
            'wbh_vn_province_id': self.province_hn.id,
            'wbh_vn_district_id': self.district_hk.id,
            'wbh_vn_ward_id': False,
        })
        order_hn = self._create_order(qty=1)
        order_hn.partner_shipping_id = partner_hn
        rate_hn = self.carrier_vtp.rate_shipment(order_hn)
        self.assertTrue(rate_hn['success'])
        self.assertEqual(rate_hn['price'], 20000.0)

        # Chủ shop chỉnh cấu hình giá trên delivery.carrier
        self.carrier_vtp.write({
            'wbh_vtp_inner_price': 13000.0,
            'wbh_vtp_inter_region_price': 19000.0,
        })
        self.assertEqual(self.carrier_vtp.rate_shipment(order_hcm)['price'], 13000.0)
        self.assertEqual(self.carrier_vtp.rate_shipment(order_hn)['price'], 19000.0)

    def test_07_partner_and_order_fb_shipping_sync(self):
        """Kiểm tra đồng bộ wbh_fb_link & wbh_shipping_info_note lên res.partner và sale.order."""
        fb_partner = self.env['res.partner'].create({
            'name': 'Manh Dao Test',
            'wbh_fb_link': 'https://facebook.com/manhdaodao.test',
            'wbh_shipping_info_note': 'Anh An, 0909888777, 12 Lê Lợi, Q1',
            'country_id': self.env.ref('base.vn').id,
        })
        order = self.env['sale.order'].create({
            'website_id': self.website.id,
            'partner_id': fb_partner.id,
            'partner_shipping_id': fb_partner.id,
            'pricelist_id': self.pricelist_vnd.id,
            'order_line': [Command.create({'product_id': self.product_100k.id, 'product_uom_qty': 1})],
        })
        self.assertEqual(order.wbh_fb_link, 'https://facebook.com/manhdaodao.test')
        self.assertEqual(order.wbh_shipping_info_note, 'Anh An, 0909888777, 12 Lê Lợi, Q1')


@tagged('post_install', '-at_install')
class TestWbhVnAddressHttp(HttpCase):

    def test_01_vn_address_json_endpoints(self):
        """Kiểm tra endpoint GET /wbh/vn/districts/<id> và /wbh/vn/wards/<id>."""
        province_hcm = self.env.ref('wbh_delivery_vn.vn_province_hcm')
        district_q1 = self.env.ref('wbh_delivery_vn.vn_district_hcm_q1')

        resp_dist = self.url_open(f'/wbh/vn/districts/{province_hcm.id}')
        self.assertEqual(resp_dist.status_code, 200)
        districts = json.loads(resp_dist.content.decode('utf-8'))
        self.assertIsInstance(districts, list)
        self.assertTrue(any(item['id'] == district_q1.id for item in districts))
        self.assertEqual(set(districts[0].keys()), {'id', 'name'})

        resp_ward = self.url_open(f'/wbh/vn/wards/{district_q1.id}')
        self.assertEqual(resp_ward.status_code, 200)
        wards = json.loads(resp_ward.content.decode('utf-8'))
        self.assertIsInstance(wards, list)
        self.assertGreaterEqual(len(wards), 1)
        self.assertEqual(set(wards[0].keys()), {'id', 'name'})

    def test_02_simplified_gift_address_submit_with_fb_url(self):
        """Kiểm tra /shop/address trên Web 1 cho phép nhập Link FB (URL) và Thông tin ship không lỗi @."""
        import re as _re
        website_gift = self.env.ref('wbh_core.website_gift_store')
        website_gift.domain = 'localhost'
        product = self.env['product.product'].create({
            'name': 'Card Bakugo HTTP Test',
            'type': 'consu',
            'list_price': 50000.0,
            'is_published': True,
            'website_id': website_gift.id,
        })
        # Thêm vào giỏ hàng để mở /shop/address
        resp_shop = self.url_open('/shop')
        csrf_match = _re.search(r'csrf_token:\s*"([^"]+)"', resp_shop.text) or _re.search(
            r'name="csrf_token"\s+value="([^"]+)"', resp_shop.text
        )
        if csrf_match:
            csrf_token = csrf_match.group(1)
            self.url_open(
                '/shop/cart/update',
                data={
                    'product_id': product.id,
                    'add_qty': 1,
                    'csrf_token': csrf_token,
                },
            )
            addr_page = self.url_open('/shop/address')
            self.assertEqual(addr_page.status_code, 200)
            self.assertIn('Tên fb', addr_page.text)
            self.assertIn('Link fb', addr_page.text)
            self.assertIn('Thông tin ship', addr_page.text)
            submit_csrf = _re.search(r'name="csrf_token"\s+value="([^"]+)"', addr_page.text)
            if submit_csrf:
                province_hcm = self.env.ref('wbh_delivery_vn.vn_province_hcm')
                resp_submit = self.url_open(
                    '/shop/address/submit',
                    data={
                        'csrf_token': submit_csrf.group(1),
                        'name': 'Khách FB Test',
                        'email': 'https://facebook.com/manhdaodao.buyer',
                        'phone': 'Nguyễn Bảo, 0901234567, 12 Lê Lợi, Phường Bến Nghé',
                        'wbh_vn_province_id': province_hcm.id,
                        'address_type': 'billing',
                        'use_delivery_as_billing': 'True',
                        'required_fields': 'name,email,phone',
                    },
                )
                self.assertEqual(resp_submit.status_code, 200)
                payload = json.loads(resp_submit.content.decode('utf-8'))
                self.assertIn('redirectUrl', payload)
                partner = self.env['res.partner'].search(
                    [('wbh_fb_link', '=', 'https://facebook.com/manhdaodao.buyer')],
                    limit=1,
                )
                self.assertTrue(partner)
                self.assertEqual(partner.phone, '0901234567')
                self.assertEqual(partner.country_id, self.env.ref('base.vn'))
                self.assertIn('@fb.wbh.local', partner.email)
