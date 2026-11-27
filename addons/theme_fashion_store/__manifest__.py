# -*- coding: utf-8 -*-
# Part of 360org WBH Multi-Store. See LICENSE file for full copyright and licensing details.

{
    'name': 'Theme Web 2 — Cửa Hàng Thời Trang (Quần Áo & Lookbook)',
    'version': '19.0.1.2.1',
    'category': 'Theme/eCommerce',
    'summary': 'Giao diện tối giản phong cách Editorial & Lookbook dành riêng cho Web 2 Thời trang (Odoo 19.0 Community)',
    'description': """
Theme Web 2 — Cửa Hàng Thời Trang (Quần Áo & Lookbook) — Changelog
==================================================================

v19.0.1.2.1 (2026-11-28)
------------------------
- [FIX] Ghi đè SVG arrow của `select.form-select.css_attribute_select`, bọc toolbar `/shop` trên mobile (`< 768px`) và tắt `website.header_text_element` / `website.header_call_to_action`.

v19.0.1.2.0 (2026-11-28)
------------------------
- [IMPROVE] Áp dụng chuẩn heydamir/unslop: gỡ bỏ bẫy GSAP opacity:0 khi tải/cuộn nhanh, ẩn .oe_subdescription trên thẻ lưới /shop để đồng đều chiều cao, thêm nền trắng cho nút Wishlist và tabular-nums cho giá bán.
- [FIX] Chuẩn hóa <select class="form-select"> (triệt tiêu lỗi lặp 2 mũi tên & cắt chữ) và căn giữa dọc mọi nút bấm Editorial bằng inline-flex.

v19.0.1.1.0 (2026-11-27)
------------------------
- [IMPROVE] Tích hợp Lucide Icons & GSAP + ScrollTrigger (theme_fashion_motion.js) phong cách Editorial mượt mà với 3 chốt bảo vệ (scope .wbh-store-fashion, Website Builder edit mode, prefers-reduced-motion).
- [IMPROVE] Đánh bóng UI/UX theo chuẩn Impeccable & Front-End Checklist: hiệu ứng phóng ảnh hover scale(1.04) cho Lookbook & /shop 3:4, bỏ inline onclick và inline style, bổ sung preconnect font, theme-color, focus-visible và IntersectionObserver cho sticky bar mobile.

v19.0.1.0.1 (2026-11-27)
------------------------
- [FIX] Tắt footer tiếng Anh mẫu mặc định (website.footer_custom) và đưa .wbh-fashion-footer-band lên trước #footer để không lặp 2 footer và không che nút scrolltop.

v19.0.1.0.0 (2026-11-26)
------------------------
- [NEW] Khởi tạo Custom Theme Upgrade-Safe cho Web 2 Thời trang chuẩn Odoo 19.0 Community (LGPL-3, 0% Enterprise).
- [NEW] Cô lập tuyệt đối Multi-Website bằng phạm vi `website.wbh_store_type == 'fashion'` và class `.wbh-store-fashion`.
- [NEW] Xây dựng bảng màu SCSS tối giản Editorial (#111111, #C8B6A6, #F5F5F3, #FFFFFF, #222222) cùng bộ font tiếng Việt Plus Jakarta Sans & Inter.
- [NEW] Bổ sung 3 Building Blocks kéo-thả chuẩn Odoo 19.0: `s_fashion_lookbook_hero`, `s_fashion_category_strip`, `s_fashion_editorial_grid`.
- [NEW] Tối ưu trang Shop & Chi tiết sản phẩm: khung ảnh dọc 3:4 (`object-fit: cover`), Color Swatch rõ nét, Size pills lớn dễ chạm mobile, `wbh_short_highlight`, accordion `wbh_care_note`, thanh sticky bottom Add-to-Cart trên mobile.
- [NEW] Mở sẵn 4 Extension Slots cho Milestone 2 & 3: `wbh_fashion_size_advisor_slot`, `wbh_fashion_video_gallery_slot`, `wbh_fashion_shop_the_look_slot`, `wbh_flash_sale_banner_slot`.
    """,
    'author': '360org',
    'website': 'https://360.org.vn',
    'license': 'LGPL-3',
    'depends': [
        'wbh_core',
        'theme_default',
    ],
    'data': [
        'data/presets.xml',
        'views/layout.xml',
        'views/snippets/s_fashion_lookbook_hero.xml',
        'views/snippets/s_fashion_category_strip.xml',
        'views/snippets/s_fashion_editorial_grid.xml',
        'views/snippets/snippets.xml',
        'views/pages/home.xml',
        'views/shop_templates.xml',
    ],
    'assets': {
        'web._assets_primary_variables': [
            'theme_fashion_store/static/src/scss/primary_variables.scss',
        ],
        'web.assets_frontend': [
            'theme_fashion_store/static/src/scss/theme_fashion.scss',
            'theme_fashion_store/static/src/js/theme_fashion_motion.js',
        ],
        'website.assets_wysiwyg': [
            'theme_fashion_store/static/src/scss/theme_fashion_editor.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
