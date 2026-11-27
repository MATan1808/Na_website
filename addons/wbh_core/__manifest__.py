# -*- coding: utf-8 -*-
{
    'name': 'WBH Core — Hạ Tầng Đa Cửa Hàng Quà Tặng & Thời Trang',
    'version': '19.0.1.1.3',
    'category': 'Website/Website',
    'summary': 'Hạ tầng lõi Multi-Website thuần Odoo 19.0 Community cho 2 cửa hàng Quà tặng & Thời trang.',
    'description': """
WBH Core — Hạ Tầng Đa Cửa Hàng Quà Tặng & Thời Trang — Changelog
================================================================

v19.0.1.1.3 (2026-11-28)
------------------------
- [FIX] Việt hóa triệt để các nhãn core còn lẫn tiếng Anh trên Breadcrumb & Trang chi tiết sản phẩm (`Tất cả sản phẩm`, `Thêm vào giỏ hàng`, `So sánh sản phẩm`) qua `views/website_sale_vi_templates.xml`.

v19.0.1.1.2 (2026-11-27)
------------------------
- [FIX] Kích hoạt mặc định tiền tệ `VND (₫)` trong `data/website_data.xml` và bổ sung bước chuyển Công ty + Bảng giá sang `VNĐ (₫)` trong `scripts/import_fb_products.py` để khắc phục hiển thị `$ USD` trên `/shop`.
- [IMPROVE] Tự động dọn sản phẩm test rác (`T1`), ẩn sản phẩm dịch vụ trên `/shop`, cô lập đúng `website_id` giữa Web 1 & Web 2 và ưu tiên `website_sequence` đưa 15 sản phẩm thật Anime Goods lên đầu Trang 1 `/shop`.

v19.0.1.1.1 (2026-11-27)
------------------------
- [NEW] Bổ sung bộ dữ liệu thật 10 lô sản phẩm (37 biến thể) & 49 ảnh từ Facebook Manh Dao Dao (`data/fb_manhdaodao_products.json`/`.csv`, `static/src/img/fb_manhdaodao/`) cùng script import idempotent `scripts/import_fb_products.py`.

v19.0.1.1.0 (2026-11-27)
------------------------
- [NEW] Đóng gói self-hosted GSAP v3.15.1 (kèm ScrollTrigger) và Lucide Icons v1.82.0 vào static/lib/ và đăng ký trong web.assets_frontend dùng chung cho cả 2 storefront (Web 1 & Web 2).

v19.0.1.0.1 (2026-11-27)
------------------------
- [FIX] Bổ sung compute_sudo=True khi tính toán nhãn sắp hết hàng (wbh_is_low_stock) giúp khách vãng lai xem trang /shop an toàn không cần mở quyền đọc trực tiếp stock.move.

v19.0.1.0.0 (2026-11-26)
------------------------
- [NEW] Khởi tạo hạ tầng 2 Website độc lập (Web 1 Quà tặng & Web 2 Thời trang) với specific_user_account=True tách biệt tài khoản khách hàng.
- [NEW] Mở rộng model website (wbh_store_type, wbh_brand_tagline, wbh_support_hotline, wbh_support_zalo_url) kèm models.Index chuẩn Odoo 19.0.
- [NEW] Mở rộng model product.template (wbh_store_scope, wbh_short_highlight, wbh_care_note, wbh_low_stock_threshold, wbh_is_low_stock) tự động đồng bộ website_id theo phạm vi cửa hàng và models.Constraint kiểm soát ngưỡng tồn kho.
- [NEW] Khởi tạo dữ liệu mẫu noupdate=1 gồm cây danh mục cho 2 website và bộ 7 thuộc tính biến thể chuẩn (Màu sắc swatch, Size Quần Áo, Kích thước Gấu Bông, Chất liệu, Form dáng, Dịp tặng quà, Phiên bản Blind Box).
- [NEW] Xây dựng bộ Backend Views tối ưu upload sản phẩm nhanh và menu điều phối "2 Cửa Hàng (WBH)".
- [NEW] Thiết lập phân quyền chuẩn Odoo 19.0 (res.groups.privilege, group_wbh_catalog_user, group_wbh_manager), ir.model.access.csv và ir.rule cô lập sản phẩm Public/Portal theo website và công ty.
    """,
    'author': '360org',
    'website': 'https://360.org.vn',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'website',
        'website_sale',
        'website_sale_wishlist',
        'website_sale_comparison',
        'website_sale_stock',
        'sale_management',
        'stock',
        'product',
        'contacts',
        'portal',
    ],
    'data': [
        'security/wbh_security.xml',
        'security/ir.model.access.csv',
        'data/website_data.xml',
        'data/product_public_category_data.xml',
        'data/product_attribute_data.xml',
        'views/website_views.xml',
        'views/product_template_views.xml',
        'views/wbh_menus.xml',
        'views/website_sale_vi_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'wbh_core/static/lib/gsap/gsap.min.js',
            'wbh_core/static/lib/gsap/ScrollTrigger.min.js',
            'wbh_core/static/lib/lucide/lucide.min.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'uninstall_hook': 'uninstall_hook',
}
