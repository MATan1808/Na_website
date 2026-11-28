# -*- coding: utf-8 -*-
from odoo import fields, models


class Website(models.Model):
    _inherit = 'website'

    wbh_store_type = fields.Selection(
        selection=[
            ('gift', 'Web 1 — Quà tặng'),
            ('fashion', 'Web 2 — Thời trang'),
        ],
        string='Loại Cửa hàng WBH',
        index=False,
        help='Định danh loại cửa hàng để các theme và module nghiệp vụ phân nhánh sạch không phụ thuộc ID cố định.',
    )
    wbh_brand_tagline = fields.Char(
        string='Khẩu hiệu Thương hiệu',
        translate=True,
        help='Hiển thị trên header/footer và tiêu đề SEO mặc định của từng website.',
    )
    wbh_support_hotline = fields.Char(
        string='Hotline CSKH',
        help='Số điện thoại chăm sóc khách hàng hiển thị riêng cho từng cửa hàng.',
    )
    wbh_support_zalo_url = fields.Char(
        string='Link Zalo CSKH',
        help='Đường dẫn liên hệ nhanh qua Zalo hiển thị riêng cho từng cửa hàng.',
    )
    wbh_fb_messenger_url = fields.Char(
        string='Link Facebook Messenger',
        help='Đường dẫn nhắn tin Facebook Messenger riêng cho từng cửa hàng (VD: https://m.me/tenpage).',
    )
    wbh_support_facebook_url = fields.Char(
        string='Link Facebook CSKH / Shop',
        related='wbh_fb_messenger_url',
        readonly=False,
        help='Đường dẫn Facebook / Messenger hiển thị trên storefront và hộp tư vấn của cửa hàng.',
    )
    wbh_livechat_enabled = fields.Boolean(
        string='Bật Chat trực tiếp trên Web',
        default=True,
        help='Hiển thị kênh Chat trực tiếp tại Web trên trang sản phẩm, giỏ hàng và nút hỗ trợ nổi.',
    )
    wbh_contact_prompt = fields.Char(
        string='Lời nhắc tư vấn',
        translate=True,
        default='Cần vid check hoặc tư vấn chọn hàng?',
        help='Câu gợi ý hiển thị trong hộp tư vấn trên trang chi tiết sản phẩm và giỏ hàng.',
    )
    wbh_packaging_fee = fields.Float(
        string='Phí gói mặc định (VNĐ)',
        default=5000.0,
        help='Khoản phí đóng gói cố định trên mỗi đơn hàng khi bật Áp dụng Phí gói.',
    )
    wbh_packaging_fee_enabled = fields.Boolean(
        string='Áp dụng Phí gói theo đơn',
        default=False,
        help='Tự động cộng Phí gói cố định theo đơn hàng thay cho dòng Thuế trên Storefront.',
    )

    _check_wbh_packaging_fee = models.Constraint(
        'CHECK(wbh_packaging_fee >= 0)',
        'Phí gói mặc định phải lớn hơn hoặc bằng 0.',
    )
    _wbh_store_type_idx = models.Index('(wbh_store_type)')
