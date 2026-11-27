# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Theme Web 1 — Cửa Hàng Quà Tặng (Móc Khóa, Gấu Bông & Blind Box)',
    'version': '19.0.1.3.0',
    'category': 'Theme/eCommerce',
    'summary': 'Giao diện cửa hàng quà tặng, móc khóa, gấu bông và Blind Box chuẩn Upgrade-Safe Odoo 19.0 Community',
    'description': """
Theme Web 1 — Cửa Hàng Quà Tặng — Changelog
===========================================

v19.0.1.3.0 (2026-11-28)
------------------------
- [NEW] Giai đoạn 1 UI: Hiển thị giá gốc gạch ngang `compare_list_price` (chống trùng với core) kèm huy hiệu giảm giá `-XX%` trên thẻ sản phẩm `/shop` và trang chi tiết sản phẩm (PDP).
- [NEW] Giai đoạn 2 UI: Tích hợp bộ lọc động 100% từ `wbh_filter_ctx` (Đang giảm giá, Khoảng giá, Nhãn & Chủ đề) cho cả Sidebar Desktop và Offcanvas Mobile; thêm thanh Active Filter Chips có nút `×` và `Xóa tất cả`, gắn tối đa 2 nhãn động lên thẻ `/shop`, nâng cấp nút `Bộ lọc` mobile đạt vùng chạm `>= 44px` kèm bộ đếm số lượng đang lọc.
- [NEW] Giai đoạn 3 UI: Nâng cấp hộp tư vấn 3 kênh trên PDP và thêm thanh tư vấn trên `/shop/cart` (`Chat tại Web` kích hoạt Livechat + chép tên & link SP, `Nhắn Facebook`, `Nhắn Zalo`, `Chép tên & link SP`); bổ sung Widget Liên hệ nổi 3 trong 1 dùng Lucide + GSAP (có đủ 3 chốt bảo vệ) đặt phía trên nút cuộn đầu trang và thanh sticky mobile.

v19.0.1.2.2 (2026-11-28)
------------------------
- [FIX] Sửa đúng selector `footer.o_footer, #bottom.o_footer` (thay cho `#footer.o_footer`) để nút cuộn đầu trang `#o_footer_scrolltop_wrapper` hiển thị tròn đầy không bị cắt nửa dưới; thêm `overflow-x: clip` và `table-layout: fixed` chống tràn ngang PDP mobile.

v19.0.1.2.1 (2026-11-28)
------------------------
- [FIX] Ghi đè triệt để SVG arrow mặc định của Odoo `select.form-select.css_attribute_select` và ép `max-width: 100%` tránh tràn mobile 416px.
- [FIX] Bọc 2 hàng cho toolbar `/shop` trên mobile (`< 768px`) để ô tìm kiếm đủ rộng và không cắt nút `Bộ lọc`; hiện nút Wishlist trên mobile; mở chiều cao `#o_footer_scrolltop_wrapper` hết bị che nửa dưới.
- [FIX] Tắt `website.header_text_element` (+1 555-555-5556) và `website.header_call_to_action` (nút Contact Us thừa) trong `presets.xml` và `theme.utils`.

v19.0.1.2.0 (2026-11-28)
------------------------
- [IMPROVE] Áp dụng 9 passes của heydamir/unslop (CC-BY-4.0) dựa trên kiểm định live: gỡ bỏ bẫy GSAP opacity:0 khi tải/cuộn nhanh, thay toàn bộ khối icon pastel "AI slop" bằng ảnh chụp sản phẩm thật (Cotton Doll 20cm, Card Bo Góc, Shikishi) trên nền Warm Paper (#F7F4EE).
- [FIX] Ẩn đoạn mô tả dài (.oe_subdescription) gây phình thẻ sản phẩm /shop (720-845px), giữ chiều cao card đồng đều, bọc nền trắng cho nút Wishlist và mũi tên slider ảnh PDP.
- [FIX] Sửa triệt để lỗi <select class="form-select"> bị lặp 2 mũi tên (double-caret) & cắt chữ; chuẩn hóa mọi nút bấm inline-flex căn giữa dọc, cố định topbar 1 dòng trên mobile 390px và nới ô tìm kiếm /shop.

v19.0.1.1.0 (2026-11-27)
------------------------
- [IMPROVE] Tích hợp Lucide Icons & GSAP + ScrollTrigger (theme_gift_motion.js) với 3 chốt bảo vệ (scope .wbh-store-gift, Website Builder edit mode, prefers-reduced-motion).
- [IMPROVE] Đánh bóng UI/UX theo chuẩn Impeccable & Front-End Checklist: tăng tương phản topbar/CTA đạt WCAG AA (>= 4.5:1), thay side-tab bằng full border, bỏ inline onclick, bổ sung preconnect font, theme-color, focus-visible và IntersectionObserver cho sticky bar mobile.

v19.0.1.0.2 (2026-11-27)
------------------------
- [FIX] Tắt khối footer tiếng Anh mẫu mặc định (website.footer_custom) để triệt tiêu lỗi lặp 2 footer.
- [FIX] Đặt dải .wbh-gift-footer-band lên trước #footer và nâng z-index cho #o_footer_scrolltop_wrapper giúp nút cuộn tròn hiển thị trọn vẹn không bị che trên mobile.
- [IMPROVE] Hiển thị dòng bản quyền động theo tên Website thay thế cho chuỗi mẫu "Company name".

v19.0.1.0.1 (2026-11-27)
------------------------
- [NEW] Bổ sung bộ nhận diện thương hiệu Manh Dao Dao Anime Goods Shop (logo.png ngang chuẩn eCommerce, logo_emblem_transparent.png tách nền trong suốt, favicon.ico).
- [IMPROVE] Tối ưu CSS chiều cao logo Navbar 60px (desktop) / 46px (mobile) trong scope .wbh-store-gift.
- [FIX] Đọc tồn kho qua product.sudo().qty_available trên thẻ sản phẩm /shop để tương thích quyền Public user.

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
            'theme_gift_store/static/src/js/theme_gift_motion.js',
        ],
        'website.assets_wysiwyg': [
            'theme_gift_store/static/src/scss/theme_gift_editor.scss',
        ],
    },
    'installable': True,
    'auto_install': False,
}
