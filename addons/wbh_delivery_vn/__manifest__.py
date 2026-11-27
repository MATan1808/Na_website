# -*- coding: utf-8 -*-
{
    'name': 'WBH Giao Hàng Việt Nam & Địa Chỉ 3 Cấp',
    'version': '19.0.1.0.0',
    'category': 'Website/Delivery',
    'summary': 'Địa giới hành chính Việt Nam 3 cấp, Ship đồng giá / Freeship / Gom đơn 0đ và Giao Hàng Nhanh (GHN) thuần Odoo 19.0 Community.',
    'description': """
WBH Giao Hàng Việt Nam & Địa Chỉ 3 Cấp — Changelog
==================================================

v19.0.1.0.0 (2026-11-28)
------------------------
- [NEW] Xây dựng 3 model địa giới hành chính Việt Nam (`wbh.vn.province`, `wbh.vn.district`, `wbh.vn.ward`) kèm mã đối chiếu GHN, index, constraint chuẩn Odoo 19.0 và dữ liệu mẫu 5 thành phố lớn (TP.HCM, Hà Nội, Đà Nẵng, Hải Phòng, Cần Thơ).
- [NEW] Mở rộng `res.partner` với 3 cấp Tỉnh/TP – Quận/Huyện – Phường/Xã (`@api.onchange` reset tầng dưới và đồng bộ `city`/`state_id`) cùng endpoint `/wbh/vn/districts/<id>` & `/wbh/vn/wards/<id>` và bộ chọn địa chỉ 3 cấp trên checkout `/shop/address`.
- [NEW] Mở rộng `delivery.carrier` với `'wbh_local'` (Đồng giá 30.000đ, Freeship từ 300.000đ, Gom đơn / Giữ hàng tại shop 0đ) và `'wbh_ghn'` (Giao Hàng Nhanh API/Sandbox kèm fallback an toàn và hook mở rộng GHTK/Viettel Post).
- [NEW] Bổ sung theo dõi Gom đơn & mã vận đơn (`wbh_is_hold_order`, `wbh_tracking_code`, `wbh_tracking_url`) trên `sale.order` tại Backend và Portal `/my/orders/<id>`, kèm bộ unit test `tests/test_delivery_vn.py`.
    """,
    'author': '360org',
    'website': 'https://360.org.vn',
    'license': 'LGPL-3',
    'depends': [
        'wbh_core',
        'delivery',
        'stock_delivery',
        'website_sale',
        'portal',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rules.xml',
        'data/vn_address_data.xml',
        'data/delivery_carrier_data.xml',
        'views/vn_address_views.xml',
        'views/delivery_carrier_views.xml',
        'views/sale_order_views.xml',
        'views/checkout_vn_address_templates.xml',
        'views/portal_tracking_templates.xml',
        'views/wbh_delivery_menus.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'wbh_delivery_vn/static/src/css/wbh_delivery_vn.css',
            'wbh_delivery_vn/static/src/js/wbh_vn_address_checkout.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
