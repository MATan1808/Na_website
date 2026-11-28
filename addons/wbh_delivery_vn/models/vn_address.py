# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class WbhVnProvince(models.Model):
    _name = 'wbh.vn.province'
    _description = 'Tỉnh / Thành phố Việt Nam'
    _order = 'sequence, name, id'

    name = fields.Char(string='Tên Tỉnh / Thành phố', required=True, translate=True)
    code = fields.Char(string='Mã tỉnh', required=True)
    sequence = fields.Integer(string='Thứ tự', default=10)
    active = fields.Boolean(default=True)
    wbh_region = fields.Selection(
        selection=[
            ('north', 'Miền Bắc'),
            ('central', 'Miền Trung'),
            ('south', 'Miền Nam'),
        ],
        string='Khu vực (Vùng miền)',
        default='south',
        required=True,
        help='Phân vùng địa lý phục vụ tính cước nội tỉnh / cùng miền / liên miền cho ĐVVC Viettel Post.',
    )
    ghn_province_id = fields.Integer(
        string='Mã Tỉnh GHN',
        help='Mã ProvinceID đối chiếu với API Giao Hàng Nhanh (GHN).',
    )
    state_id = fields.Many2one(
        'res.country.state',
        string='Tỉnh/Bang Odoo',
        domain="[('country_id.code', '=', 'VN')]",
        ondelete='set null',
    )
    district_ids = fields.One2many(
        'wbh.vn.district',
        'province_id',
        string='Danh sách Quận / Huyện',
    )
    district_count = fields.Integer(
        string='Số Quận / Huyện',
        compute='_compute_district_count',
    )

    _code_uniq = models.Constraint(
        'UNIQUE(code)',
        'Mã Tỉnh / Thành phố phải là duy nhất.',
    )
    _ghn_province_idx = models.Index('(ghn_province_id)')
    _active_sequence_idx = models.Index('(active, sequence)')

    @api.depends('district_ids')
    def _compute_district_count(self):
        for province in self:
            province.district_count = len(province.district_ids)


class WbhVnDistrict(models.Model):
    _name = 'wbh.vn.district'
    _description = 'Quận / Huyện Việt Nam'
    _order = 'sequence, name, id'

    name = fields.Char(string='Tên Quận / Huyện', required=True, translate=True)
    code = fields.Char(string='Mã Quận / Huyện', required=True)
    sequence = fields.Integer(string='Thứ tự', default=10)
    active = fields.Boolean(default=True)
    province_id = fields.Many2one(
        'wbh.vn.province',
        string='Tỉnh / Thành phố',
        required=True,
        ondelete='cascade',
    )
    ghn_district_id = fields.Integer(
        string='Mã Quận/Huyện GHN',
        help='Mã DistrictID đối chiếu với API Giao Hàng Nhanh (GHN).',
    )
    ward_ids = fields.One2many(
        'wbh.vn.ward',
        'district_id',
        string='Danh sách Phường / Xã',
    )
    ward_count = fields.Integer(
        string='Số Phường / Xã',
        compute='_compute_ward_count',
    )

    _province_code_uniq = models.Constraint(
        'UNIQUE(province_id, code)',
        'Mã Quận / Huyện phải là duy nhất trong cùng Tỉnh / Thành phố.',
    )
    _province_active_idx = models.Index('(province_id, active, sequence)')
    _ghn_district_idx = models.Index('(ghn_district_id)')

    @api.depends('ward_ids')
    def _compute_ward_count(self):
        for district in self:
            district.ward_count = len(district.ward_ids)


class WbhVnWard(models.Model):
    _name = 'wbh.vn.ward'
    _description = 'Phường / Xã Việt Nam'
    _order = 'sequence, name, id'

    name = fields.Char(string='Tên Phường / Xã', required=True, translate=True)
    code = fields.Char(string='Mã Phường / Xã', required=True)
    sequence = fields.Integer(string='Thứ tự', default=10)
    active = fields.Boolean(default=True)
    district_id = fields.Many2one(
        'wbh.vn.district',
        string='Quận / Huyện',
        required=True,
        ondelete='cascade',
    )
    province_id = fields.Many2one(
        'wbh.vn.province',
        string='Tỉnh / Thành phố',
        related='district_id.province_id',
        store=True,
        readonly=True,
    )
    ghn_ward_code = fields.Char(
        string='Mã Phường/Xã GHN',
        help='Mã WardCode (chuỗi) đối chiếu với API Giao Hàng Nhanh (GHN).',
    )

    _district_code_uniq = models.Constraint(
        'UNIQUE(district_id, code)',
        'Mã Phường / Xã phải là duy nhất trong cùng Quận / Huyện.',
    )
    _district_active_idx = models.Index('(district_id, active, sequence)')
    _ghn_ward_idx = models.Index('(ghn_ward_code)')


class ResPartner(models.Model):
    _inherit = 'res.partner'

    wbh_vn_province_id = fields.Many2one(
        'wbh.vn.province',
        string='Tỉnh / Thành phố (VN)',
        ondelete='set null',
    )
    wbh_vn_district_id = fields.Many2one(
        'wbh.vn.district',
        string='Quận / Huyện (VN)',
        domain="[('province_id', '=', wbh_vn_province_id)]",
        ondelete='set null',
    )
    wbh_vn_ward_id = fields.Many2one(
        'wbh.vn.ward',
        string='Phường / Xã (VN)',
        domain="[('district_id', '=', wbh_vn_district_id)]",
        ondelete='set null',
    )
    wbh_fb_link = fields.Char(
        string='Link Facebook',
        copy=False,
        help='Đường dẫn tài khoản Facebook khách hàng nhập tại trang đặt hàng.',
    )
    wbh_shipping_info_note = fields.Text(
        string='Thông tin ship (Tên, SĐT, địa chỉ cũ)',
        copy=False,
        help='Thông tin nhận hàng chi tiết khách hàng nhập tại form tối giản Web 1.',
    )

    _wbh_vn_address_idx = models.Index('(wbh_vn_province_id, wbh_vn_district_id, wbh_vn_ward_id)')

    @api.model
    def _get_frontend_writable_fields(self):
        """Cho phép khách hàng chọn và lưu 3 cấp địa giới VN cùng Link FB & Thông tin ship trên form checkout/portal."""
        writable_fields = super()._get_frontend_writable_fields()
        return writable_fields | {
            'wbh_vn_province_id',
            'wbh_vn_district_id',
            'wbh_vn_ward_id',
            'wbh_fb_link',
            'wbh_shipping_info_note',
        }

    @api.onchange('wbh_vn_province_id')
    def _onchange_wbh_vn_province_id(self):
        for partner in self:
            if (
                partner.wbh_vn_district_id
                and partner.wbh_vn_district_id.province_id != partner.wbh_vn_province_id
            ):
                partner.wbh_vn_district_id = False
                partner.wbh_vn_ward_id = False
            if partner.wbh_vn_province_id:
                if not partner.city:
                    partner.city = partner.wbh_vn_province_id.name
                if partner.wbh_vn_province_id.state_id:
                    partner.state_id = partner.wbh_vn_province_id.state_id
                if not partner.country_id:
                    vn_country = self.env.ref('base.vn', raise_if_not_found=False)
                    if vn_country:
                        partner.country_id = vn_country

    @api.onchange('wbh_vn_district_id')
    def _onchange_wbh_vn_district_id(self):
        for partner in self:
            if (
                partner.wbh_vn_ward_id
                and partner.wbh_vn_ward_id.district_id != partner.wbh_vn_district_id
            ):
                partner.wbh_vn_ward_id = False
            if partner.wbh_vn_district_id and not partner.wbh_vn_province_id:
                partner.wbh_vn_province_id = partner.wbh_vn_district_id.province_id

    @api.onchange('wbh_vn_ward_id')
    def _onchange_wbh_vn_ward_id(self):
        for partner in self:
            if partner.wbh_vn_ward_id:
                if not partner.wbh_vn_district_id:
                    partner.wbh_vn_district_id = partner.wbh_vn_ward_id.district_id
                if not partner.wbh_vn_province_id:
                    partner.wbh_vn_province_id = partner.wbh_vn_ward_id.district_id.province_id

    @api.constrains('wbh_vn_province_id', 'wbh_vn_district_id', 'wbh_vn_ward_id')
    def _check_wbh_vn_hierarchy(self):
        for partner in self:
            if (
                partner.wbh_vn_district_id
                and partner.wbh_vn_province_id
                and partner.wbh_vn_district_id.province_id != partner.wbh_vn_province_id
            ):
                raise ValidationError(_(
                    'Quận/Huyện "%(district)s" không thuộc Tỉnh/Thành phố "%(province)s".',
                    district=partner.wbh_vn_district_id.name,
                    province=partner.wbh_vn_province_id.name,
                ))
            if (
                partner.wbh_vn_ward_id
                and partner.wbh_vn_district_id
                and partner.wbh_vn_ward_id.district_id != partner.wbh_vn_district_id
            ):
                raise ValidationError(_(
                    'Phường/Xã "%(ward)s" không thuộc Quận/Huyện "%(district)s".',
                    ward=partner.wbh_vn_ward_id.name,
                    district=partner.wbh_vn_district_id.name,
                ))

    def _normalize_wbh_vn_vals(self, vals):
        """Đồng bộ chuỗi Tỉnh/TP -> Quận/Huyện -> Phường/Xã khi ghi qua ORM hoặc checkout."""
        vals = dict(vals)
        province_id = vals.get('wbh_vn_province_id')
        district_id = vals.get('wbh_vn_district_id')
        ward_id = vals.get('wbh_vn_ward_id')

        if ward_id and not district_id:
            ward = self.env['wbh.vn.ward'].sudo().browse(ward_id).exists()
            if ward:
                district_id = ward.district_id.id
                vals['wbh_vn_district_id'] = district_id
        if district_id and not province_id:
            district = self.env['wbh.vn.district'].sudo().browse(district_id).exists()
            if district:
                province_id = district.province_id.id
                vals['wbh_vn_province_id'] = province_id
        if province_id and not vals.get('city'):
            province = self.env['wbh.vn.province'].sudo().browse(province_id).exists()
            if province:
                vals['city'] = province.name
                if province.state_id and 'state_id' not in vals:
                    vals['state_id'] = province.state_id.id
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        normalized = [self._normalize_wbh_vn_vals(vals) for vals in vals_list]
        return super().create(normalized)

    def write(self, vals):
        vals = self._normalize_wbh_vn_vals(vals)
        # Khi đổi Tỉnh/TP mà không truyền Quận/Huyện mới, reset tầng dưới nếu lệch
        if 'wbh_vn_province_id' in vals and 'wbh_vn_district_id' not in vals:
            new_prov_id = vals.get('wbh_vn_province_id')
            mismatched = self.filtered(
                lambda p: p.wbh_vn_district_id and p.wbh_vn_district_id.province_id.id != new_prov_id
            )
            if mismatched:
                super(ResPartner, mismatched).write({
                    'wbh_vn_district_id': False,
                    'wbh_vn_ward_id': False,
                })
        if 'wbh_vn_district_id' in vals and 'wbh_vn_ward_id' not in vals:
            new_dist_id = vals.get('wbh_vn_district_id')
            mismatched_ward = self.filtered(
                lambda p: p.wbh_vn_ward_id and p.wbh_vn_ward_id.district_id.id != new_dist_id
            )
            if mismatched_ward:
                super(ResPartner, mismatched_ward).write({
                    'wbh_vn_ward_id': False,
                })
        return super().write(vals)
