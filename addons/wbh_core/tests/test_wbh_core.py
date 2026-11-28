# -*- coding: utf-8 -*-
from psycopg2 import IntegrityError
from werkzeug.datastructures import MultiDict

from odoo.addons.website_sale.tests.common import MockRequest
from odoo.fields import Command
from odoo.tests import HttpCase, TransactionCase, tagged
from odoo.tools import mute_logger

from odoo.addons.wbh_core.controllers.shop import WbhWebsiteSale


@tagged('post_install', '-at_install', 'wbh_core')
class TestWbhCore(TransactionCase):
    """Kiểm thử toàn diện hạ tầng lõi Multi-Website của module wbh_core (G1, G2, G3)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website_gift = cls.env.ref('wbh_core.website_gift_store')
        cls.website_fashion = cls.env.ref('wbh_core.website_fashion_store')
        cls.ProductTemplate = cls.env['product.template']
        cls.ProductTag = cls.env['product.tag']
        cls.WbhPriceRange = cls.env['wbh.price.range']

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
        """Kiểm tra wbh_store_scope tự động đồng bộ website_id khi create, write và unlink."""
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

        # Tạo sản phẩm không truyền wbh_store_scope -> tự đồng bộ default='gift'
        default_product = self.ProductTemplate.create({
            'name': 'Móc Khóa Mặc Định Web 1',
        })
        self.assertEqual(default_product.wbh_store_scope, 'gift')
        self.assertEqual(default_product.website_id, self.website_gift)

        # Kiểm tra CRUD Delete (unlink)
        default_product.unlink()
        self.assertFalse(default_product.exists())

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

        self.assertEqual(
            self.env.ref('wbh_core.pub_cat_gift_occasion_valentine').parent_id,
            self.env.ref('wbh_core.pub_cat_gift_occasion'),
        )
        self.assertEqual(
            self.env.ref('wbh_core.pub_cat_fashion_tops_tshirt').parent_id,
            self.env.ref('wbh_core.pub_cat_fashion_tops'),
        )

    def test_07_discount_percent_compute_and_search(self):
        """Kiểm tra tính toán wbh_discount_percent và tìm kiếm wbh_has_discount."""
        discounted = self.ProductTemplate.create({
            'name': 'Standee Acrylic Giảm Giá',
            'wbh_store_scope': 'gift',
            'list_price': 160000.0,
            'compare_list_price': 200000.0,
        })
        regular = self.ProductTemplate.create({
            'name': 'Móc Khóa Giá Gốc',
            'wbh_store_scope': 'gift',
            'list_price': 120000.0,
            'compare_list_price': 0.0,
        })
        invalid_compare = self.ProductTemplate.create({
            'name': 'Sản Phẩm Giá So Sánh Thấp Hơn',
            'wbh_store_scope': 'gift',
            'list_price': 150000.0,
            'compare_list_price': 100000.0,
        })

        self.assertEqual(discounted.wbh_discount_percent, 20)
        self.assertTrue(discounted.wbh_has_discount)
        self.assertEqual(regular.wbh_discount_percent, 0)
        self.assertFalse(regular.wbh_has_discount)
        self.assertEqual(invalid_compare.wbh_discount_percent, 0)
        self.assertFalse(invalid_compare.wbh_has_discount)

        on_sale_records = self.ProductTemplate.search([('wbh_has_discount', '=', True)])
        self.assertIn(discounted, on_sale_records)
        self.assertNotIn(regular, on_sale_records)
        self.assertNotIn(invalid_compare, on_sale_records)

        not_on_sale_records = self.ProductTemplate.search([('wbh_has_discount', '=', False)])
        self.assertNotIn(discounted, not_on_sale_records)
        self.assertIn(regular, not_on_sale_records)

    def test_08_product_tag_wbh_fields(self):
        """Kiểm tra mở rộng product.tag cho bộ lọc động Giai đoạn 2."""
        tag = self.ProductTag.create({
            'name': 'Ưu Đãi Mới Test',
            'wbh_show_in_filter': True,
            'wbh_filter_group': 'promo',
            'wbh_badge_hex': '#D9483B',
        })
        self.assertTrue(tag.wbh_show_in_filter)
        self.assertEqual(tag.wbh_filter_group, 'promo')
        self.assertEqual(tag.wbh_badge_hex, '#D9483B')

    def test_09_price_range_model_and_constraints(self):
        """Kiểm tra model wbh.price.range, dữ liệu mẫu và ràng buộc CHECK."""
        under_100k = self.env.ref('wbh_core.wbh_price_range_under_100k')
        above_500k = self.env.ref('wbh_core.wbh_price_range_above_500k')
        self.assertEqual(under_100k.min_price, 0.0)
        self.assertEqual(under_100k.max_price, 100000.0)
        self.assertEqual(above_500k.min_price, 500000.0)
        self.assertEqual(above_500k.max_price, 0.0)

        # Chặn min_price âm
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            with self.env.cr.savepoint():
                self.WbhPriceRange.create({
                    'name': 'Khoảng giá âm',
                    'min_price': -5000.0,
                    'max_price': 100000.0,
                })

        # Chặn max_price > 0 nhưng nhỏ hơn min_price
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            with self.env.cr.savepoint():
                self.WbhPriceRange.create({
                    'name': 'Khoảng giá đảo ngược',
                    'min_price': 300000.0,
                    'max_price': 100000.0,
                })

    def test_10_website_three_channel_contact_fields(self):
        """Kiểm tra các trường kênh liên hệ & cấu hình thương hiệu mới trên Web 1 và Web 2."""
        self.assertEqual(
            self.website_gift.name,
            'Manh Dao Dao - Boku no Hero Academia Anime Goods Shop',
        )
        self.assertEqual(self.website_gift.wbh_brand_tagline, 'Tiền trao tay, quýt về ngay')
        self.assertFalse(self.website_gift.wbh_support_hotline)
        self.assertFalse(self.website_gift.wbh_support_zalo_url)
        self.assertTrue(self.website_gift.wbh_support_facebook_url)
        self.assertEqual(
            self.website_gift.wbh_support_facebook_url,
            self.website_gift.wbh_fb_messenger_url,
        )
        self.assertTrue(self.website_gift.wbh_livechat_enabled)
        self.assertEqual(
            self.website_gift.wbh_contact_prompt,
            'Cần vid check hoặc tư vấn chọn hàng?',
        )
        self.assertTrue(self.website_gift.wbh_packaging_fee_enabled)
        self.assertEqual(self.website_gift.wbh_packaging_fee, 5000.0)
        self.assertFalse(self.website_fashion.wbh_packaging_fee_enabled)

        self.website_gift.write({
            'wbh_support_facebook_url': 'https://m.me/wbh.gift.test',
            'wbh_livechat_enabled': False,
            'wbh_contact_prompt': 'Nhắn tin ngay để xem ảnh thực tế!',
        })
        self.assertEqual(self.website_gift.wbh_fb_messenger_url, 'https://m.me/wbh.gift.test')
        self.assertEqual(self.website_gift.wbh_support_facebook_url, 'https://m.me/wbh.gift.test')
        self.assertFalse(self.website_gift.wbh_livechat_enabled)
        self.assertEqual(self.website_gift.wbh_contact_prompt, 'Nhắn tin ngay để xem ảnh thực tế!')
        # Đảm bảo không ảnh hưởng Web 2
        self.assertTrue(self.website_fashion.wbh_livechat_enabled)
        self.assertFalse(self.website_fashion.wbh_fb_messenger_url)

    def test_10b_goods_type_attribute_and_packaging_fee_order_math(self):
        """Kiểm tra thuộc tính Loại goods (9 giá trị) và Phí gói 5.000đ trên đơn hàng Web 1 vs Web 2."""
        goods_attr = self.env.ref('wbh_core.attr_goods_type')
        self.assertEqual(goods_attr.name, 'Loại goods')
        self.assertEqual(goods_attr.create_variant, 'no_variant')
        self.assertEqual(goods_attr.visibility, 'visible')
        expected_goods_vals = {
            'CARD', 'POSTCARD (PC)', 'STANDEE', 'KEY',
            'FIGURE', 'BADGE', 'CLEAR FILE', 'DOLL', 'KHÁC',
        }
        self.assertTrue(expected_goods_vals.issubset(set(goods_attr.value_ids.mapped('name'))))

        pkg_product = self.env.ref('wbh_core.wbh_product_packaging_fee')
        self.assertEqual(pkg_product.type, 'service')
        self.assertFalse(pkg_product.sale_ok)
        self.assertFalse(pkg_product.is_published)
        self.assertFalse(pkg_product.taxes_id)

        vnd = self.env.ref('base.VND')
        vnd.active = True
        self.env.company.currency_id = vnd

        partner = self.env['res.partner'].create({'name': 'Khách Web 1 Test Phí Gói'})
        item = self.env['product.product'].create({
            'name': 'Standee Bakugo Test',
            'type': 'consu',
            'list_price': 150000.0,
            'taxes_id': [Command.clear()],
            'wbh_store_scope': 'gift',
        })
        order_gift = self.env['sale.order'].create({
            'website_id': self.website_gift.id,
            'partner_id': partner.id,
            'order_line': [
                Command.create({
                    'product_id': item.id,
                    'product_uom_qty': 1.0,
                    'price_unit': 150000.0,
                    'tax_ids': [Command.clear()],
                }),
            ],
        })
        pkg_lines = order_gift.order_line.filtered('wbh_is_packaging_fee')
        self.assertEqual(len(pkg_lines), 1)
        self.assertEqual(pkg_lines.price_unit, 5000.0)
        self.assertFalse(pkg_lines.tax_ids)
        self.assertEqual(order_gift.wbh_amount_products, 150000.0)
        self.assertEqual(order_gift.wbh_packaging_fee_amount, 5000.0)
        self.assertEqual(order_gift.amount_total, 155000.0)
        self.assertEqual(order_gift.cart_quantity, 1)
        self.assertNotIn(pkg_lines, order_gift.website_order_line)

        # Xóa sản phẩm cuối -> tự gỡ dòng Phí gói
        order_gift.order_line.filtered(lambda l: not l.wbh_is_packaging_fee).unlink()
        self.assertFalse(order_gift.order_line)
        self.assertEqual(order_gift.amount_total, 0.0)

        # Web 2 Thời trang KHÔNG cộng Phí gói
        order_fashion = self.env['sale.order'].create({
            'website_id': self.website_fashion.id,
            'partner_id': partner.id,
            'order_line': [
                Command.create({
                    'product_id': item.id,
                    'product_uom_qty': 1.0,
                    'price_unit': 150000.0,
                    'tax_ids': [Command.clear()],
                }),
            ],
        })
        self.assertFalse(order_fashion.order_line.filtered('wbh_is_packaging_fee'))
        self.assertEqual(order_fashion.wbh_packaging_fee_amount, 0.0)
        self.assertEqual(order_fashion.amount_total, 150000.0)


@tagged('post_install', '-at_install', 'wbh_core')
class TestWbhShopDynamicFilters(HttpCase):
    """Kiểm thử controller /shop lọc động 100%, auto-appear/auto-hide và kết hợp bộ lọc."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website_gift = cls.env.ref('wbh_core.website_gift_store')
        cls.website_fashion = cls.env.ref('wbh_core.website_fashion_store')
        cls.ProductTemplate = cls.env['product.template']
        cls.ProductTag = cls.env['product.tag']
        cls.ProductAttribute = cls.env['product.attribute']
        cls.ProductAttributeValue = cls.env['product.attribute.value']
        cls.WbhPriceRange = cls.env['wbh.price.range']

        # Tạo thuộc tính no_variant động (không hardcode trong module)
        cls.attr_character = cls.ProductAttribute.create({
            'name': 'Nhân Vật Test',
            'display_type': 'pills',
            'create_variant': 'no_variant',
            'visibility': 'visible',
        })
        cls.val_char_a = cls.ProductAttributeValue.create({
            'name': 'Nhân Vật A',
            'attribute_id': cls.attr_character.id,
        })
        cls.val_char_b = cls.ProductAttributeValue.create({
            'name': 'Nhân Vật B',
            'attribute_id': cls.attr_character.id,
        })
        cls.val_char_empty = cls.ProductAttributeValue.create({
            'name': 'Nhân Vật Rỗng',
            'attribute_id': cls.attr_character.id,
        })
        cls.attr_empty = cls.ProductAttribute.create({
            'name': 'Thuộc Tính Rỗng Test',
            'display_type': 'pills',
            'create_variant': 'no_variant',
            'visibility': 'visible',
            'value_ids': [Command.create({'name': 'Giá trị chưa gán'})],
        })

        # Tags động
        cls.tag_hot = cls.ProductTag.create({
            'name': 'Hot Dynamic Test',
            'wbh_show_in_filter': True,
            'wbh_filter_group': 'promo',
            'wbh_badge_hex': '#D9483B',
        })
        cls.tag_hidden_flag = cls.ProductTag.create({
            'name': 'Internal Hidden Tag',
            'wbh_show_in_filter': False,
        })
        cls.tag_zero_products = cls.ProductTag.create({
            'name': 'Empty Zero Tag',
            'wbh_show_in_filter': True,
        })
        cls.tag_fashion_only = cls.ProductTag.create({
            'name': 'Fashion Only Tag',
            'wbh_show_in_filter': True,
            'wbh_filter_group': 'collection',
        })

        # Khoảng giá động riêng cho test
        cls.range_under_200 = cls.WbhPriceRange.create({
            'name': 'Dưới 200K Test',
            'website_id': cls.website_gift.id,
            'min_price': 0.0,
            'max_price': 200000.0,
            'sequence': 5,
        })
        cls.range_empty = cls.WbhPriceRange.create({
            'name': 'Trên 99 Triệu Rỗng',
            'website_id': cls.website_gift.id,
            'min_price': 99000000.0,
            'max_price': 0.0,
            'sequence': 99,
        })

        # Sản phẩm mẫu trên Web 1 & Web 2
        cls.prod_gift_sale = cls.ProductTemplate.create({
            'name': 'Doll Nhân Vật A Sale',
            'wbh_store_scope': 'gift',
            'is_published': True,
            'list_price': 150000.0,
            'compare_list_price': 200000.0,
            'product_tag_ids': [Command.set([cls.tag_hot.id, cls.tag_hidden_flag.id])],
            'attribute_line_ids': [Command.create({
                'attribute_id': cls.attr_character.id,
                'value_ids': [Command.set([cls.val_char_a.id])],
            })],
        })
        cls.prod_gift_regular = cls.ProductTemplate.create({
            'name': 'Goods Nhân Vật B Thường',
            'wbh_store_scope': 'gift',
            'is_published': True,
            'list_price': 350000.0,
            'compare_list_price': 0.0,
            'attribute_line_ids': [Command.create({
                'attribute_id': cls.attr_character.id,
                'value_ids': [Command.set([cls.val_char_b.id])],
            })],
        })
        cls.prod_gift_unpublished = cls.ProductTemplate.create({
            'name': 'Goods Nháp Chưa Đăng',
            'wbh_store_scope': 'gift',
            'is_published': False,
            'list_price': 120000.0,
            'product_tag_ids': [Command.set([cls.tag_zero_products.id])],
        })
        cls.prod_fashion = cls.ProductTemplate.create({
            'name': 'Áo Thời Trang Web 2',
            'wbh_store_scope': 'fashion',
            'is_published': True,
            'list_price': 420000.0,
            'product_tag_ids': [Command.set([cls.tag_fashion_only.id])],
        })

    def _call_shop(self, website, query_params=None, **kwargs):
        args = MultiDict(query_params or [])
        captured = {}
        public_env = self.env(user=website.user_id.id)
        with MockRequest(
            public_env,
            website=website,
            path='/shop',
            context={'website_id': website.id},
        ) as req:
            req.session['force_website_id'] = website.id
            req.httprequest.args = args
            req.httprequest.query_string = b''

            def _capture_render(template, qcontext):
                captured.update(qcontext)
                return ''

            req.render = _capture_render
            WbhWebsiteSale.shop.original_endpoint(WbhWebsiteSale(), **kwargs)
        return captured

    def test_11_dynamic_tags_and_price_ranges_auto_appear_and_auto_hide(self):
        """Tag & khoảng giá chỉ hiện khi có sản phẩm đang đăng bán trên website hiện tại."""
        ctx_gift = self._call_shop(self.website_gift)
        filter_ctx = ctx_gift['wbh_filter_ctx']

        tag_ids = {t['id'] for t in filter_ctx['tags']}
        self.assertIn(self.tag_hot.id, tag_ids)
        self.assertNotIn(self.tag_hidden_flag.id, tag_ids, 'Tag tắt wbh_show_in_filter phải ẩn.')
        self.assertNotIn(self.tag_zero_products.id, tag_ids, 'Tag chỉ gắn vào SP chưa đăng phải ẩn.')
        self.assertNotIn(self.tag_fashion_only.id, tag_ids, 'Tag của Web 2 không được hiện trên Web 1.')

        range_ids = {r['id'] for r in filter_ctx['price_ranges']}
        self.assertIn(self.range_under_200.id, range_ids)
        self.assertNotIn(self.range_empty.id, range_ids, 'Khoảng giá có count=0 phải tự ẩn.')

        # Kiểm tra thuộc tính & giá trị thuộc tính rỗng bị ẩn trên Web 1
        avail_val_ids = ctx_gift['wbh_available_attr_value_ids']
        self.assertIn(self.val_char_a.id, avail_val_ids)
        self.assertIn(self.val_char_b.id, avail_val_ids)
        self.assertNotIn(self.val_char_empty.id, avail_val_ids, 'Giá trị thuộc tính rỗng phải tự ẩn.')
        self.assertNotIn(self.attr_empty, ctx_gift['attributes'], 'Thuộc tính 0 sản phẩm phải tự ẩn.')

        # Kiểm tra trên Web 2 chỉ thấy tag của Web 2 và không thấy Nhân Vật Test của Web 1
        ctx_fashion = self._call_shop(self.website_fashion)
        fashion_tag_ids = {t['id'] for t in ctx_fashion['wbh_filter_ctx']['tags']}
        self.assertIn(self.tag_fashion_only.id, fashion_tag_ids)
        self.assertNotIn(self.tag_hot.id, fashion_tag_ids)
        self.assertNotIn(self.attr_character, ctx_fashion['attributes'])

    def test_12_combined_filters_and_active_chips(self):
        """Lọc kết hợp tags + attrib (no_variant) + min_price/max_price + wbh_on_sale=1 + search."""
        query = [
            ('tags', str(self.tag_hot.id)),
            ('attrib', f'{self.attr_character.id}-{self.val_char_a.id}'),
            ('min_price', '100000'),
            ('max_price', '200000'),
            ('wbh_on_sale', '1'),
        ]
        ctx = self._call_shop(
            self.website_gift,
            query_params=query,
            search='Doll',
            min_price=100000.0,
            max_price=200000.0,
            tags=str(self.tag_hot.id),
            wbh_on_sale='1',
        )
        products = ctx['search_product']
        self.assertIn(self.prod_gift_sale, products)
        self.assertNotIn(self.prod_gift_regular, products)
        self.assertNotIn(self.prod_gift_unpublished, products)
        self.assertNotIn(self.prod_fashion, products)

        filter_ctx = ctx['wbh_filter_ctx']
        chip_kinds = {c['kind'] for c in filter_ctx['active_chips']}
        self.assertEqual(chip_kinds, {'search', 'on_sale', 'price', 'tag', 'attrib'})
        self.assertEqual(filter_ctx['total_active_filters'], 5)
        self.assertEqual(filter_ctx['clear_all_url'], '/shop')

    def test_13_shop_http_endpoint_renders_cleanly(self):
        """Kiểm tra HTTP GET /shop với tổ hợp bộ lọc trả về 200 OK."""
        response = self.url_open(
            f'/shop?tags={self.tag_hot.id}&wbh_on_sale=1&min_price=100000&max_price=300000'
        )
        self.assertEqual(response.status_code, 200)

    def test_14_hidden_card_pattern_attr_and_integer_vnd_format(self):
        """Kiểm tra ẩn thuộc tính 'Mẫu Thẻ Sưu Tầm' trên Web 1 và bỏ ',00' thập phân VNĐ."""
        hidden_card_attr = self.ProductAttribute.create({
            'name': 'Mẫu Thẻ Sưu Tầm',
            'display_type': 'select',
            'create_variant': 'no_variant',
            'visibility': 'visible',
        })
        hidden_val = self.ProductAttributeValue.create({
            'name': 'Card Bo Góc Test',
            'attribute_id': hidden_card_attr.id,
        })
        self.ProductTemplate.create({
            'name': 'Card Test Ẩn Thuộc Tính Cũ',
            'wbh_store_scope': 'gift',
            'is_published': True,
            'list_price': 20000.0,
            'attribute_line_ids': [Command.create({
                'attribute_id': hidden_card_attr.id,
                'value_ids': [Command.set([hidden_val.id])],
            })],
        })

        ctx_gift = self._call_shop(
            self.website_gift,
            query_params=[('min_price', '15000'), ('max_price', '380000')],
            min_price=15000.0,
            max_price=380000.0,
        )
        self.assertNotIn(hidden_card_attr, ctx_gift['attributes'])
        self.assertNotIn(hidden_val.id, ctx_gift['wbh_available_attr_value_ids'])
        self.assertEqual(WbhWebsiteSale._wbh_format_vnd(15000.0), '15.000₫')
        self.assertEqual(ctx_gift['wbh_filter_ctx']['min_price_display'], '15.000₫')
        self.assertEqual(ctx_gift['wbh_filter_ctx']['max_price_display'], '380.000₫')
        self.assertNotIn(',00', ctx_gift['wbh_filter_ctx']['min_price_display'])
        self.assertNotIn(',00', ctx_gift['wbh_filter_ctx']['max_price_display'])
