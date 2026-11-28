# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class ThemeUtils(models.AbstractModel):
    _inherit = 'theme.utils'

    def _theme_gift_store_post_copy(self, mod):
        """Áp dụng cấu hình preset Upgrade-Safe cho website chọn theme Web 1."""
        self.enable_view('website_sale.products_attributes')
        self.enable_view('website_sale.products_categories')
        self.enable_view('website_sale.option_collapse_products_categories')
        self.enable_view('website_sale_wishlist.add_to_wishlist')
        self.enable_view('website_sale_wishlist.product_add_to_wishlist')
        self.enable_view('website_sale.product_terms_and_conditions')
        self.enable_view('website.option_footer_scrolltop')
        self.disable_view('website.footer_custom')
        self.disable_view('website.header_text_element')
        self.disable_view('website.header_call_to_action')
        self.disable_view('website.template_header_hamburger')
        self.disable_view('website.footer_no_copyright')
