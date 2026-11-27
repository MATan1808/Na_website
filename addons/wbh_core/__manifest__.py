# -*- coding: utf-8 -*-
{
    'name': 'WBH Core — Hạ Tầng Đa Cửa Hàng Quà Tặng & Thời Trang',
    'version': '19.0.1.0.1',
    'category': 'Website/Website',
    'summary': 'Hạ tầng lõi Multi-Website thuần Odoo 19.0 Community cho 2 cửa hàng Quà tặng & Thời trang.',
    'description': """
WBH Core — Hạ Tầng Đa Cửa Hàng Quà Tặng & Thời Trang — Changelog
================================================================

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
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'uninstall_hook': 'uninstall_hook',
}
