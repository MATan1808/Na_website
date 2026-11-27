# -*- coding: utf-8 -*-
# Part of 360org WBH Multi-Store. See LICENSE file for full copyright and licensing details.

from odoo import models


class ThemeUtils(models.AbstractModel):
    _inherit = 'theme.utils'

    def _theme_fashion_store_post_copy(self, mod):
        """Kích hoạt các preset Shop & Wishlist chuẩn Odoo 19.0 riêng cho website dùng theme_fashion_store."""
        self.enable_view('website_sale.products_categories')
        self.enable_view('website_sale.products_attributes')
        self.enable_view('website_sale.filter_products_price')
        self.enable_view('website_sale_wishlist.add_to_wishlist')
        self.enable_view('website_sale_wishlist.product_add_to_wishlist')
        # Tắt footer tiếng Anh mẫu mặc định, số +1 555 và Contact Us thừa trên navbar
        self.disable_view('website.footer_custom')
        self.disable_view('website.header_text_element')
        self.disable_view('website.header_call_to_action')
        # Tắt hiển thị danh mục dạng thanh cuộn ngang trên đầu trang khi đã bật sidebar danh mục
        self.disable_view('website_sale.products_categories_top')
