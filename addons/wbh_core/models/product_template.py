# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    wbh_store_scope = fields.Selection(
        selection=[
            ('gift', 'Web 1 — Quà tặng'),
            ('fashion', 'Web 2 — Thời trang'),
            ('both', 'Hiển thị Cả 2 Website'),
        ],
        string='Cửa hàng đăng bán',
        default='gift',
        required=True,
        help='Chọn website hiển thị sản phẩm. Hệ thống tự động đồng bộ trường Website tương ứng.',
    )
    wbh_short_highlight = fields.Char(
        string='Điểm nổi bật ngắn',
        translate=True,
        help='Tóm tắt 1 dòng hiển thị ngay dưới tên sản phẩm trên trang chi tiết.',
    )
    wbh_care_note = fields.Text(
        string='Hướng dẫn bảo quản / Lưu ý',
        translate=True,
        help='Hiển thị trong mục accordion gọn trên trang chi tiết sản phẩm.',
    )
    wbh_low_stock_threshold = fields.Float(
        string='Ngưỡng cảnh báo sắp hết hàng',
        default=5.0,
        help='Ngưỡng tồn kho tối thiểu để cảnh báo nhập hàng đối với sản phẩm theo dõi tồn kho.',
    )
    wbh_is_low_stock = fields.Boolean(
        string='Sắp hết hàng',
        compute='_compute_wbh_is_low_stock',
        search='_search_wbh_is_low_stock',
        store=False,
        help='Bật khi sản phẩm thuộc loại hàng lưu kho (is_storable=True) và tồn kho khả dụng nhỏ hơn hoặc bằng ngưỡng cảnh báo.',
    )

    _check_wbh_low_stock_threshold = models.Constraint(
        'CHECK(wbh_low_stock_threshold >= 0)',
        'Ngưỡng cảnh báo tồn kho phải lớn hơn hoặc bằng 0.',
    )
    _wbh_store_scope_published_idx = models.Index('(wbh_store_scope, is_published)')

    @api.depends('type', 'is_storable', 'qty_available', 'wbh_low_stock_threshold')
    def _compute_wbh_is_low_stock(self):
        for product in self:
            product.wbh_is_low_stock = bool(
                product.type == 'consu'
                and product.is_storable
                and product.qty_available <= product.wbh_low_stock_threshold
            )

    def _search_wbh_is_low_stock(self, operator, value):
        # Chuẩn Odoo 19.0: operator có thể là 'in', 'not in', '=', '!=' và value có thể là OrderedSet/bool
        if operator == 'in':
            want_low_stock = True in value
        elif operator == 'not in':
            want_low_stock = True not in value
        elif operator == '=':
            want_low_stock = bool(value)
        elif operator == '!=':
            want_low_stock = not bool(value)
        else:
            return [('id', '=', 0)]

        self.env.flush_all()
        storable_products = self.sudo().search([
            ('is_storable', '=', True),
        ])
        low_stock_ids = [
            p.id for p in storable_products
            if p.type == 'consu' and p.qty_available <= p.wbh_low_stock_threshold
        ]
        if want_low_stock:
            return [('id', 'in', low_stock_ids)]
        return [('id', 'not in', low_stock_ids)]

    @api.model
    def _wbh_resolve_website_id(self, scope, company_id=False):
        """Tra cứu an toàn website_id tương ứng với wbh_store_scope, tôn trọng công ty."""
        xmlid_map = {
            'gift': 'wbh_core.website_gift_store',
            'fashion': 'wbh_core.website_fashion_store',
        }
        xmlid = xmlid_map.get(scope)
        if not xmlid:
            return False

        website = self.env.ref(xmlid, raise_if_not_found=False)
        if not website:
            return False

        if website.company_id:
            if company_id and website.company_id.id != company_id:
                return False
            allowed_company_ids = self.env.context.get('allowed_company_ids')
            if allowed_company_ids and website.company_id.id not in allowed_company_ids:
                return False

        return website.id

    @api.onchange('wbh_store_scope')
    def _onchange_wbh_store_scope(self):
        for product in self:
            product.website_id = product._wbh_resolve_website_id(
                product.wbh_store_scope,
                company_id=product.company_id.id,
            )

    @api.model_create_multi
    def create(self, vals_list):
        default_scope = self.env.context.get('default_wbh_store_scope')
        prepared_vals_list = []
        for vals in vals_list:
            new_vals = dict(vals)
            if 'website_id' not in new_vals:
                if 'wbh_store_scope' in new_vals:
                    scope = new_vals['wbh_store_scope']
                elif default_scope:
                    scope = default_scope
                    new_vals['wbh_store_scope'] = scope
                elif new_vals.get('sale_ok', True):
                    scope = 'gift'
                    new_vals['wbh_store_scope'] = scope
                else:
                    scope = False
                if scope:
                    new_vals['website_id'] = self._wbh_resolve_website_id(
                        scope,
                        company_id=new_vals.get('company_id', False),
                    )
            prepared_vals_list.append(new_vals)
        return super().create(prepared_vals_list)

    def write(self, vals):
        if 'wbh_store_scope' in vals and 'website_id' not in vals:
            scope = vals['wbh_store_scope']
            if scope == 'both':
                updated_vals = dict(vals, website_id=False)
                return super().write(updated_vals)

            companies = self.mapped('company_id')
            if len(companies) <= 1:
                company_id = companies.id if len(companies) == 1 else False
                updated_vals = dict(
                    vals,
                    website_id=self._wbh_resolve_website_id(scope, company_id=company_id),
                )
                return super().write(updated_vals)

            # Tách nhóm theo công ty để tôn trọng ràng buộc đa công ty mà không lặp từng bản ghi
            result = True
            for company_id in set(self.mapped('company_id.id')) | {False}:
                subset = self.filtered(lambda r, cid=company_id: (r.company_id.id or False) == cid)
                if not subset:
                    continue
                updated_vals = dict(
                    vals,
                    website_id=self._wbh_resolve_website_id(scope, company_id=company_id),
                )
                result = super(ProductTemplate, subset).write(updated_vals) and result
            return result

        return super().write(vals)
