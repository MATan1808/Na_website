# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


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
