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

    _wbh_store_type_idx = models.Index('(wbh_store_type)')
