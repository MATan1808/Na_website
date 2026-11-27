# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Theme Web 1 — Cửa Hàng Quà Tặng (Móc Khóa, Gấu Bông & Blind Box)',
    'version': '19.0.1.0.0',
    'category': 'Theme/eCommerce',
    'summary': 'Giao diện cửa hàng quà tặng, móc khóa, gấu bông và Blind Box chuẩn Upgrade-Safe Odoo 19.0 Community',
    'description': """
Theme Web 1 — Cửa Hàng Quà Tặng — Changelog
===========================================

v19.0.1.0.0 (2026-11-26)
------------------------
- [NEW] Khởi tạo module giao diện `theme_gift_store` thuần Odoo 19.0 Community (LGPL-3), chuẩn Theme Upgrade-Safe.
- [NEW] Bảng màu quà tặng ấm áp (`$o-color-1..5`: Hồng san hô, Vàng mật ong, Kem ấm, Trắng, Nâu cacao) kèm typography tiếng Việt `Be Vietnam Pro` / `Quicksand`.
- [NEW] Cô lập tuyệt đối Multi-Website bằng class `.wbh-store-gift` và điều kiện `website.wbh_store_type == 'gift'` (không ghi đè sang Web 2 `theme_fashion_store`).
- [NEW] Cấu hình `data/presets.xml` và `theme.utils._theme_gift_store_post_copy` bật bộ lọc thuộc tính, danh mục Shop, Wishlist và nút cuộn đầu trang.
- [NEW] Xây dựng trang chủ mẫu `views/pages/home.xml` và 3 Building Blocks kéo-thả (`s_gift_hero`, `s_gift_occasion_bar`, `s_gift_featured_grid`).
- [NEW] Tùy biến trang Shop & Chi tiết sản phẩm (tỷ lệ ảnh 1:1, bo góc 16px, badge `wbh_short_highlight`, accordion `wbh_care_note`, sticky bottom bar mobile) kèm 3 QWeb extension slots cho Milestone 2 & 3 (`wbh_gift_options_slot`, `wbh_gift_size_compare_slot`, `wbh_flash_sale_banner_slot`).
    """,
    'author': '360org',
    'license': 'LGPL-3',
    'depends': [
        'wbh_core',
        'theme_default',
    ],
    'data': [
        'data/presets.xml',
        'views/layout.xml',
        'views/snippets/s_gift_hero.xml',
        'views/snippets/s_gift_occasion_bar.xml',
        'views/snippets/s_gift_featured_grid.xml',
        'views/snippets/snippets.xml',
        'views/pages/home.xml',
        'views/shop_templates.xml',
    ],
    'assets': {
        'web._assets_primary_variables': [
            'theme_gift_store/static/src/scss/primary_variables.scss',
        ],
        'web.assets_frontend': [
            'theme_gift_store/static/src/scss/theme_gift.scss',
        ],
        'website.assets_wysiwyg': [
            'theme_gift_store/static/src/scss/theme_gift_editor.scss',
        ],
    },
    'installable': True,
    'auto_install': False,
}
