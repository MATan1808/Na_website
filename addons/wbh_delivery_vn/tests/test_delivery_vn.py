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

        cls.carrier_std = cls.env.ref('wbh_delivery_vn.carrier_wbh_standard')
        cls.carrier_hold = cls.env.ref('wbh_delivery_vn.carrier_wbh_hold_order')
        cls.carrier_ghn = cls.env.ref('wbh_delivery_vn.carrier_wbh_ghn')

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
        """Kiểm tra đủ 5 thành phố mẫu và sản phẩm dịch vụ ship không lộ ra /shop."""
        provinces = self.env['wbh.vn.province'].search([
            ('code', 'in', ['HCM', 'HN', 'DN', 'HP', 'CT']),
        ])
        self.assertEqual(len(provinces), 5)
        for carrier in (self.carrier_std, self.carrier_hold, self.carrier_ghn):
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
