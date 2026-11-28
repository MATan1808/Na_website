# -*- coding: utf-8 -*-
{
    'name': 'WBH Payment VietQR & COD Rules',
    'version': '19.0.1.1.0',
    'category': 'Accounting/Payment Providers',
    'sequence': 355,
    'summary': 'Chuyển khoản trước VietQR / QR riêng chủ shop, Upload ảnh bill CK bảo mật và tắt COD trên Web 1 thuần Odoo 19.0 Community.',
    'description': """
WBH Payment VietQR & COD Rules — Changelog
==========================================

v19.0.1.1.0 (2026-11-28)
------------------------
- [IMPROVE] Bật sẵn `payment_provider_vietqr` (`state='enabled'`, `is_published=True`) & `payment_method_vietqr` (`active=True`), tắt hoàn toàn COD trên Web 1 (`wbh_store_type == 'gift'`) theo `CR-09` & `CR-10`.
- [NEW] Bổ sung `wbh_custom_qr_image` (`Binary`) trên `payment.provider` (kèm view Backend): ưu tiên hiển thị ảnh QR chủ shop ngay trên `/shop/payment` và trang xác nhận, tự fallback về QR động EMVCo khi chưa upload.
- [NEW] Thêm tính năng Upload ảnh chụp màn hình chuyển khoản (`'cap màn hình ck'`) ngay tại `/shop/payment` và trang xác nhận qua route `POST /payment/vietqr/upload_proof` (kiểm tra session/`access_token`, magic bytes PNG/JPEG/WEBP, giới hạn `<= 5MB`, lưu `ir.attachment` gắn `sale.order`, hiển thị ảnh trên form Backend `sale.order` và ghi chatter `markupsafe.Markup`).

v19.0.1.0.0 (2026-11-28)
------------------------
- [NEW] Khởi tạo module thuần Odoo 19.0 Community (`LGPL-3`) sinh mã QR chuyển khoản VietQR chuẩn EMVCo / Napas 247 offline 100% qua `ir.actions.report.barcode` và CRC16-CCITT (`0x1021`).
- [NEW] Tích hợp cổng đối soát Webhook miễn phí SePay Free (`POST /payment/vietqr/webhook/sepay`) xác thực khóa bí mật bằng `hmac.compare_digest`, kiểm tra idempotency theo mã giao dịch ngân hàng, tự động xác nhận đơn hàng và ghi nhật ký `markupsafe.Markup`. Sẵn sàng adapter mở rộng PayOS & Casso.
- [NEW] Thêm API kiểm tra trạng thái giao dịch thời gian thực (`GET /payment/vietqr/status/<reference>`) kèm thẻ hướng dẫn thanh toán VietQR hỗ trợ sao chép nhanh & giao diện theo `DESIGN.md` cho cả Web 1 (Quà tặng) và Web 2 (Thời trang).
- [NEW] Bổ sung phương thức Thanh toán khi nhận hàng (COD) cùng quy tắc giới hạn COD theo sản phẩm (`wbh_allow_cod`), hạn mức tối đa (`wbh_cod_max_amount`) và tỷ lệ đặt cọc (`wbh_cod_deposit_percent`) theo từng website.
    """,
    'author': '360org',
    'website': 'https://360.org.vn',
    'license': 'LGPL-3',
    'depends': [
        'payment',
        'payment_custom',
        'website_payment',
        'website_sale',
        'wbh_core',
    ],
    'data': [
        'security/wbh_payment_vietqr_security.xml',
        'security/ir.model.access.csv',
        'views/payment_vietqr_templates.xml',
        'views/payment_provider_views.xml',
        'views/payment_transaction_views.xml',
        'views/product_website_cod_views.xml',
        'data/payment_method_data.xml',
        'data/payment_provider_data.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'wbh_payment_vietqr/static/src/scss/vietqr.scss',
            'wbh_payment_vietqr/static/src/js/vietqr_checkout.js',
        ],
    },
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
}
