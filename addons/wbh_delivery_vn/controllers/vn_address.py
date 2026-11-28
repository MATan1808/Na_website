# -*- coding: utf-8 -*-
import hashlib
import re

from odoo import _, http
from odoo.http import request
from odoo.tools import single_email_re

from odoo.addons.website_sale.controllers.main import WebsiteSale

VN_PHONE_RE = re.compile(r'(?:\+?84|0)(?:[\s.\-]*\d){8,10}')


class WbhVnAddressController(http.Controller):

    @http.route(
        '/wbh/vn/districts/<int:province_id>',
        type='http',
        auth='public',
        methods=['GET'],
        website=True,
        readonly=True,
    )
    def get_vn_districts(self, province_id, **kwargs):
        """Trả về danh sách Quận/Huyện {id, name} đã làm sạch theo Tỉnh/Thành phố."""
        districts = request.env['wbh.vn.district'].sudo().search(
            [('province_id', '=', province_id), ('active', '=', True)],
            order='sequence, name, id',
        )
        payload = [
            {'id': int(district.id), 'name': str(district.name or '')}
            for district in districts
        ]
        return request.make_json_response(payload)

    @http.route(
        '/wbh/vn/wards/<int:district_id>',
        type='http',
        auth='public',
        methods=['GET'],
        website=True,
        readonly=True,
    )
    def get_vn_wards(self, district_id, **kwargs):
        """Trả về danh sách Phường/Xã {id, name} đã làm sạch theo Quận/Huyện."""
        wards = request.env['wbh.vn.ward'].sudo().search(
            [('district_id', '=', district_id), ('active', '=', True)],
            order='sequence, name, id',
        )
        payload = [
            {'id': int(ward.id), 'name': str(ward.name or '')}
            for ward in wards
        ]
        return request.make_json_response(payload)


class WbhWebsiteSaleAddress(WebsiteSale):
    """Tối giản form /shop/address cho Web 1 (gift), giữ nguyên hoàn toàn hành vi Web 2."""

    @staticmethod
    def _is_wbh_gift_store():
        website = getattr(request, 'website', False) if request else False
        return bool(website and website.wbh_store_type == 'gift')

    @staticmethod
    def _wbh_build_technical_fb_email(fb_link):
        digest = hashlib.sha256((fb_link or '').strip().lower().encode('utf-8')).hexdigest()[:12]
        return f'fb-{digest}@fb.wbh.local'

    @staticmethod
    def _wbh_extract_vn_phone(raw_text):
        if not raw_text:
            return ''
        match = VN_PHONE_RE.search(str(raw_text))
        if not match:
            return ''
        digits = re.sub(r'[\s.\-]+', '', match.group(0))
        if digits.startswith('84') and len(digits) >= 11:
            digits = f'+{digits}'
        return digits

    def _get_default_country(self, order_sudo=False, **kwargs):
        if self._is_wbh_gift_store():
            vn_country = request.env.ref('base.vn', raise_if_not_found=False)
            if vn_country:
                return vn_country
        return super()._get_default_country(order_sudo=order_sudo, **kwargs)

    def _prepare_address_form_values(self, *args, callback='', order_sudo=False, **kwargs):
        values = super()._prepare_address_form_values(
            *args, callback=callback, order_sudo=order_sudo, **kwargs
        )
        if self._is_wbh_gift_store():
            values['display_b2b_fields'] = False
            vn_country = request.env.ref('base.vn', raise_if_not_found=False)
            if vn_country and not values.get('country'):
                values['country'] = vn_country
                values['country_states'] = vn_country.state_ids
        return values

    def _get_mandatory_address_fields(self, country_sudo):
        if self._is_wbh_gift_store():
            return set()
        return super()._get_mandatory_address_fields(country_sudo)

    def _get_mandatory_billing_address_fields(self, country_sudo):
        if self._is_wbh_gift_store():
            return {'name', 'email', 'phone'}
        return super()._get_mandatory_billing_address_fields(country_sudo)

    def _get_mandatory_delivery_address_fields(self, country_sudo):
        if self._is_wbh_gift_store():
            return {'name', 'email', 'phone'}
        return super()._get_mandatory_delivery_address_fields(country_sudo)

    def _check_billing_address(self, partner_sudo):
        if self._is_wbh_gift_store():
            return bool(
                partner_sudo.name
                and partner_sudo.email
                and (partner_sudo.wbh_shipping_info_note or partner_sudo.phone or partner_sudo.street)
            )
        return super()._check_billing_address(partner_sudo)

    def _check_delivery_address(self, partner_sudo):
        if self._is_wbh_gift_store():
            return bool(
                partner_sudo.name
                and partner_sudo.email
                and (partner_sudo.wbh_shipping_info_note or partner_sudo.phone or partner_sudo.street)
            )
        return super()._check_delivery_address(partner_sudo)

    def _parse_form_data(self, form_data):
        address_values, extra_form_data = super()._parse_form_data(form_data)
        if not self._is_wbh_gift_store():
            return address_values, extra_form_data

        # Gán ngầm Việt Nam (base.vn) khi ẩn ô chọn quốc gia trên Web 1
        if not address_values.get('country_id'):
            vn_country = request.env.ref('base.vn', raise_if_not_found=False)
            if vn_country:
                address_values['country_id'] = vn_country.id

        # Xử lý Link fb (nhận cả URL Facebook lẫn email truyền thống mà không bị chặn @)
        raw_fb_or_email = (form_data.get('email') or form_data.get('wbh_fb_link') or '').strip()
        if raw_fb_or_email:
            if single_email_re.match(raw_fb_or_email):
                address_values['email'] = raw_fb_or_email
                if form_data.get('wbh_fb_link'):
                    address_values['wbh_fb_link'] = str(form_data.get('wbh_fb_link')).strip()
            else:
                address_values['wbh_fb_link'] = raw_fb_or_email
                address_values['email'] = self._wbh_build_technical_fb_email(raw_fb_or_email)

        # Xử lý Thông tin ship (Tên, sđt, địa chỉ cũ không ghi tắt)
        raw_ship_info = (
            form_data.get('phone') or form_data.get('wbh_shipping_info_note') or ''
        ).strip()
        if raw_ship_info:
            address_values['wbh_shipping_info_note'] = raw_ship_info
            if not address_values.get('street'):
                address_values['street'] = raw_ship_info
            extracted_phone = self._wbh_extract_vn_phone(raw_ship_info)
            address_values['phone'] = extracted_phone or False

        if not address_values.get('city'):
            province_id = address_values.get('wbh_vn_province_id')
            if province_id:
                province = request.env['wbh.vn.province'].sudo().browse(province_id).exists()
                if province:
                    address_values['city'] = province.name
            if not address_values.get('city'):
                address_values['city'] = 'Việt Nam'

        return address_values, extra_form_data

    def _validate_address_values(
        self,
        address_values,
        partner_sudo,
        address_type,
        use_delivery_as_billing,
        required_fields,
        **kwargs,
    ):
        invalid_fields, missing_fields, error_messages = super()._validate_address_values(
            address_values,
            partner_sudo,
            address_type,
            use_delivery_as_billing,
            required_fields,
            **kwargs,
        )
        if not self._is_wbh_gift_store():
            return invalid_fields, missing_fields, error_messages

        # Nếu khách đã điền Thông tin ship thì không báo thiếu 'phone' khi chuỗi không chứa SĐT tách riêng
        if 'phone' in missing_fields and address_values.get('wbh_shipping_info_note'):
            missing_fields.discard('phone')
            if not missing_fields:
                empty_msg = _('Some required fields are empty.')
                error_messages = [msg for msg in error_messages if msg != empty_msg]

        if not address_values.get('wbh_shipping_info_note') and not address_values.get('phone'):
            missing_fields.add('phone')
            empty_msg = _('Some required fields are empty.')
            if empty_msg not in error_messages:
                error_messages.append(empty_msg)

        if not address_values.get('email') and not address_values.get('wbh_fb_link'):
            missing_fields.add('email')
            empty_msg = _('Some required fields are empty.')
            if empty_msg not in error_messages:
                error_messages.append(empty_msg)

        return invalid_fields, missing_fields, error_messages
