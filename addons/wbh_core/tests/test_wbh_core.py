# -*- coding: utf-8 -*-
from psycopg2 import IntegrityError

from odoo.tests import TransactionCase, tagged
from odoo.tools import mute_logger


@tagged('post_install', '-at_install', 'wbh_core')
class TestWbhCore(TransactionCase):
    """Kiểm thử toàn diện hạ tầng lõi Multi-Website của module wbh_core."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website_gift = cls.env.ref('wbh_core.website_gift_store')
        cls.website_fashion = cls.env.ref('wbh_core.website_fashion_store')
        cls.ProductTemplate = cls.env['product.template']

    def test_01_websites_exist_with_specific_user_account(self):
        """Kiểm tra 2 website WBH tồn tại, đúng loại cửa hàng và bật tách tài khoản."""
        self.assertTrue(self.website_gift.exists())
        self.assertTrue(self.website_fashion.exists())
        self.assertEqual(self.website_gift.wbh_store_type, 'gift')
        self.assertEqual(self.website_fashion.wbh_store_type, 'fashion')
        self.assertTrue(
            self.website_gift.specific_user_account,
            'Web 1 Quà tặng bắt buộc bật specific_user_account=True.',
        )
        self.assertTrue(
            self.website_fashion.specific_user_account,
            'Web 2 Thời trang bắt buộc bật specific_user_account=True.',
        )
        self.assertEqual(self.website_gift.shop_default_sort, 'website_sequence asc')
        self.assertEqual(self.website_fashion.shop_default_sort, 'website_sequence asc')

    def test_02_product_store_scope_syncs_website_id(self):
        """Kiểm tra wbh_store_scope tự động đồng bộ website_id khi create và write."""
        product = self.ProductTemplate.create({
            'name': 'Gấu Bông Capybara 40cm',
            'type': 'consu',
            'is_storable': True,
            'list_price': 185000.0,
            'wbh_store_scope': 'gift',
            'wbh_short_highlight': 'Bông PP siêu mềm, tặng kèm túi rút',
        })
        self.assertEqual(
            product.website_id,
            self.website_gift,
            "Tạo sản phẩm với wbh_store_scope='gift' phải tự gán website_gift_store.",
        )

        # Đổi sang Web 2 Thời trang -> tự đồng bộ sang website_fashion_store
        product.write({'wbh_store_scope': 'fashion'})
        self.assertEqual(
            product.website_id,
            self.website_fashion,
            "Đổi wbh_store_scope='fashion' phải tự cập nhật website_fashion_store.",
        )

        # Đổi sang hiển thị cả 2 website -> website_id = False
        product.write({'wbh_store_scope': 'both'})
        self.assertFalse(
            product.website_id,
            "Đổi wbh_store_scope='both' phải đặt website_id=False.",
        )

        # Nếu truyền tường minh website_id thì giữ nguyên giá trị được truyền
        explicit_product = self.ProductTemplate.create({
            'name': 'Áo Thun Cotton 250gsm',
            'wbh_store_scope': 'gift',
            'website_id': self.website_fashion.id,
        })
        self.assertEqual(explicit_product.website_id, self.website_fashion)

        # Tạo sản phẩm không truyền wbh_store_scope và không có default context -> tự đồng bộ default='gift' & website_gift_store
        default_product = self.ProductTemplate.create({
            'name': 'Móc Khóa Mặc Định Web 1',
        })
        self.assertEqual(default_product.wbh_store_scope, 'gift')
        self.assertEqual(
            default_product.website_id,
            self.website_gift,
            "create({'name': ...}) phải tự gán wbh_store_scope='gift' và website_id=website_gift_store.",
        )

    def test_03_low_stock_threshold_constraint_rejects_negative(self):
        """Kiểm tra models.Constraint chặn giá trị wbh_low_stock_threshold < 0."""
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            with self.env.cr.savepoint():
                self.ProductTemplate.create({
                    'name': 'Sản phẩm ngưỡng âm không hợp lệ',
                    'wbh_store_scope': 'gift',
                    'wbh_low_stock_threshold': -1.0,
                })

    def test_04_low_stock_compute_and_search(self):
        """Kiểm tra tính toán và tìm kiếm wbh_is_low_stock trên hàng lưu kho vs dịch vụ."""
        storable = self.ProductTemplate.create({
            'name': 'Blind Box Series 1',
            'type': 'consu',
            'is_storable': True,
            'wbh_store_scope': 'gift',
            'wbh_low_stock_threshold': 5.0,
        })
        service = self.ProductTemplate.create({
            'name': 'Phí gói quà thủ công',
            'type': 'service',
            'wbh_store_scope': 'gift',
            'wbh_low_stock_threshold': 5.0,
        })
        self.assertTrue(storable.wbh_is_low_stock)
        self.assertFalse(service.wbh_is_low_stock)

        self.env.flush_all()
        low_stock_products = self.ProductTemplate.search([('wbh_is_low_stock', '=', True)])
        self.assertIn(storable, low_stock_products)
        self.assertNotIn(service, low_stock_products)

    def test_05_sample_attributes_and_values_exist(self):
        """Kiểm tra tồn tại đủ 7 thuộc tính mẫu chuẩn theo SPEC."""
        expected_attrs = {
            'wbh_core.attr_color_swatch': ('color', 'always', 8),
            'wbh_core.attr_fashion_size': ('pills', 'always', 7),
            'wbh_core.attr_gift_plush_size': ('pills', 'always', 7),
            'wbh_core.attr_material': ('pills', 'no_variant', 7),
            'wbh_core.attr_fashion_fit': ('pills', 'no_variant', 4),
            'wbh_core.attr_gift_occasion': ('pills', 'no_variant', 6),
            'wbh_core.attr_blindbox_edition': ('radio', 'always', 2),
        }
        for xmlid, (display_type, create_variant, min_values) in expected_attrs.items():
            attr = self.env.ref(xmlid)
            self.assertEqual(attr.display_type, display_type, f'Sai display_type cho {xmlid}')
            self.assertEqual(attr.create_variant, create_variant, f'Sai create_variant cho {xmlid}')
            self.assertGreaterEqual(
                len(attr.value_ids),
                min_values,
                f'Thiếu giá trị mẫu cho thuộc tính {xmlid}',
            )

        black = self.env.ref('wbh_core.attr_val_color_black')
        self.assertEqual(black.html_color, '#1A1A1A')

    def test_06_public_categories_tree_for_both_websites(self):
        """Kiểm tra cây danh mục mẫu thuộc đúng Web 1 và Web 2."""
        gift_cats = [
            'wbh_core.pub_cat_gift_plush',
            'wbh_core.pub_cat_gift_keychain',
            'wbh_core.pub_cat_gift_blindbox',
            'wbh_core.pub_cat_gift_occasion',
            'wbh_core.pub_cat_gift_occasion_birthday',
            'wbh_core.pub_cat_gift_occasion_valentine',
            'wbh_core.pub_cat_gift_occasion_graduation',
            'wbh_core.pub_cat_gift_occasion_womens_day',
            'wbh_core.pub_cat_gift_combo',
        ]
        for xmlid in gift_cats:
            cat = self.env.ref(xmlid)
            self.assertEqual(cat.website_id, self.website_gift, f'Sai website_id cho {xmlid}')

        fashion_cats = [
            'wbh_core.pub_cat_fashion_tops',
            'wbh_core.pub_cat_fashion_tops_tshirt',
            'wbh_core.pub_cat_fashion_tops_shirt',
            'wbh_core.pub_cat_fashion_tops_jacket',
            'wbh_core.pub_cat_fashion_bottoms',
            'wbh_core.pub_cat_fashion_bottoms_jeans',
            'wbh_core.pub_cat_fashion_bottoms_wide',
            'wbh_core.pub_cat_fashion_bottoms_shorts',
            'wbh_core.pub_cat_fashion_dresses',
            'wbh_core.pub_cat_fashion_sets',
            'wbh_core.pub_cat_fashion_accessories',
        ]
        for xmlid in fashion_cats:
            cat = self.env.ref(xmlid)
            self.assertEqual(cat.website_id, self.website_fashion, f'Sai website_id cho {xmlid}')

        # Kiểm tra quan hệ cha - con mẫu
        self.assertEqual(
            self.env.ref('wbh_core.pub_cat_gift_occasion_valentine').parent_id,
            self.env.ref('wbh_core.pub_cat_gift_occasion'),
        )
        self.assertEqual(
            self.env.ref('wbh_core.pub_cat_fashion_tops_tshirt').parent_id,
            self.env.ref('wbh_core.pub_cat_fashion_tops'),
        )
