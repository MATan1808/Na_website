# -*- coding: utf-8 -*-
from urllib.parse import urlencode

from odoo import fields
from odoo.addons.website_sale.controllers.cart import Cart
from odoo.addons.website_sale.controllers.delivery import Delivery
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.fields import Domain
from odoo.http import request, route


TAG_GROUP_LABELS = {
    'promo': 'Ưu đãi & Trạng thái',
    'collection': 'Chủ đề / Bộ sưu tập',
    'other': 'Nhãn khác',
}

WBH_GIFT_HIDDEN_ATTRIBUTE_NAMES = {
    'mẫu thẻ sưu tầm',
}


class WbhWebsiteSale(WebsiteSale):
    """Mở rộng /shop cho lọc động 100% (tags, khoảng giá, đang giảm giá, thuộc tính biến thể & no_variant)."""

    def _wbh_parse_tag_ids(self, raw_tags=''):
        """Phân tích tham số `tags` từ cả `getlist('tags')` và chuỗi phân tách bởi dấu phẩy."""
        tokens = []
        if request and request.httprequest:
            tokens.extend(request.httprequest.args.getlist('tags'))
        if raw_tags and isinstance(raw_tags, str):
            tokens.append(raw_tags)

        seen = set()
        tag_ids = []
        ir_http = request.env['ir.http']
        for item in tokens:
            if not item:
                continue
            for part in str(item).split(','):
                part = part.strip()
                if not part:
                    continue
                tid = None
                if part.isdigit():
                    tid = int(part)
                else:
                    _, unslug_id = ir_http._unslug(part)
                    if unslug_id:
                        tid = int(unslug_id)
                if tid and tid not in seen:
                    seen.add(tid)
                    tag_ids.append(tid)
        return tag_ids

    @staticmethod
    def _wbh_merge_attribute_value_dict(raw_values):
        """Gộp an toàn danh sách chuỗi `attr_id-val1,val2` từ cả `attribute_values` và `attrib`."""
        merged = {}
        for item in raw_values or []:
            if not item or '-' not in str(item):
                continue
            parts = str(item).split('-', 1)
            try:
                attr_id = int(parts[0].strip())
            except ValueError:
                continue
            bucket = merged.setdefault(attr_id, [])
            for raw_vid in parts[1].split(','):
                raw_vid = raw_vid.strip()
                if not raw_vid:
                    continue
                try:
                    vid = int(raw_vid)
                except ValueError:
                    continue
                if vid not in bucket:
                    bucket.append(vid)
        return {k: v for k, v in merged.items() if v}

    @staticmethod
    def _wbh_format_attribute_values(attrib_dict):
        return [
            f"{attr_id}-{','.join(str(vid) for vid in val_ids)}"
            for attr_id, val_ids in sorted((attrib_dict or {}).items())
            if val_ids
        ]

    @staticmethod
    def _wbh_is_on_sale_param(value):
        if value in (None, False, '', 0, '0'):
            return False
        return str(value).strip().lower() in ('1', 'true', 'yes', 'on')

    @staticmethod
    def _wbh_format_vnd(amount):
        return f"{int(round(amount)):,}₫".replace(',', '.')

    def _wbh_build_shop_url(
        self,
        category=None,
        search='',
        tag_ids=None,
        attrib_dict=None,
        min_price=0.0,
        max_price=0.0,
        wbh_on_sale=False,
        order='',
    ):
        path = self._get_shop_path(category)
        params = []
        if search:
            params.append(('search', search))
        if tag_ids:
            params.append(('tags', ','.join(str(tid) for tid in tag_ids)))
        for av_str in self._wbh_format_attribute_values(attrib_dict):
            params.append(('attribute_values', av_str))
        if min_price and min_price > 0:
            val = int(min_price) if float(min_price).is_integer() else round(min_price, 2)
            params.append(('min_price', str(val)))
        if max_price and max_price > 0:
            val = int(max_price) if float(max_price).is_integer() else round(max_price, 2)
            params.append(('max_price', str(val)))
        if wbh_on_sale:
            params.append(('wbh_on_sale', '1'))
        if order:
            params.append(('order', order))
        if not params:
            return path
        return f"{path}?{urlencode(params)}"

    def _get_shop_domain(self, search, category, attribute_value_dict, search_in_description=True):
        wbh_params = getattr(request, '_wbh_shop_params', None) or {}
        effective_attrib = dict(attribute_value_dict or {})
        if not effective_attrib and wbh_params.get('attrib_dict'):
            effective_attrib = wbh_params['attrib_dict']
        return super()._get_shop_domain(
            search, category, effective_attrib, search_in_description=search_in_description
        )

    def _get_search_options(
        self,
        category=None,
        attribute_value_dict=None,
        tags=None,
        min_price=0.0,
        max_price=0.0,
        conversion_rate=1,
        **post,
    ):
        wbh_params = getattr(request, '_wbh_shop_params', None) or {}
        effective_attrib = dict(attribute_value_dict or {})
        if not effective_attrib and wbh_params.get('attrib_dict'):
            effective_attrib = wbh_params['attrib_dict']

        options = super()._get_search_options(
            category=category,
            attribute_value_dict=effective_attrib,
            tags=tags,
            min_price=min_price,
            max_price=max_price,
            conversion_rate=conversion_rate,
            **post,
        )
        if wbh_params.get('tag_ids'):
            options['wbh_tag_ids'] = wbh_params['tag_ids']
            if not options.get('tags'):
                options['tags'] = set(wbh_params['tag_ids'])
        if wbh_params.get('wbh_on_sale'):
            options['wbh_on_sale'] = True
        return options

    def _shop_get_query_url_kwargs(
        self, search, min_price, max_price, order=None, tags=None, **kwargs
    ):
        res = super()._shop_get_query_url_kwargs(
            search, min_price, max_price, order=order, tags=tags, **kwargs
        )
        wbh_params = getattr(request, '_wbh_shop_params', None) or {}
        if not res.get('attribute_values') and wbh_params.get('attrib_values_list'):
            res['attribute_values'] = wbh_params['attrib_values_list']
        if wbh_params.get('wbh_on_sale') or self._wbh_is_on_sale_param(kwargs.get('wbh_on_sale')):
            res['wbh_on_sale'] = '1'
        if not res.get('tags') and wbh_params.get('tags_str'):
            res['tags'] = wbh_params['tags_str']
        return res

    def _wbh_compute_filter_ctx(self, values, **kwargs):
        website = request.env['website'].get_current_website()
        wbh_params = getattr(request, '_wbh_shop_params', None) or {}

        category = values.get('category')
        search = values.get('search') or ''
        order = values.get('order') or ''
        attrib_dict = dict(values.get('attrib_values') or {})
        if not attrib_dict and wbh_params.get('attrib_dict'):
            attrib_dict = dict(wbh_params['attrib_dict'])
        attrib_set = {vid for vids in attrib_dict.values() for vid in vids}

        active_tag_ids = list(wbh_params.get('tag_ids') or [])
        if not active_tag_ids and values.get('tags'):
            active_tag_ids = sorted(int(tid) for tid in values['tags'] if tid)

        cur_min_price = float(wbh_params.get('min_price') or 0.0)
        cur_max_price = float(wbh_params.get('max_price') or 0.0)
        wbh_on_sale = bool(wbh_params.get('wbh_on_sale'))

        company_currency = website.company_id.sudo().currency_id
        conversion_rate = request.env['res.currency']._get_conversion_rate(
            company_currency, website.currency_id, website.company_id, fields.Date.today()
        ) or 1.0

        ProductTemplate = request.env['product.template']
        ProductTag = request.env['product.tag']
        ProductAttribute = request.env['product.attribute']
        ProductAttributeValue = request.env['product.attribute.value']
        WbhPriceRange = request.env['wbh.price.range']

        base_domain = self._get_shop_domain(search, category, {})
        on_sale_domain_clause = ProductTemplate._search_wbh_has_discount('=', True)

        def _compose_domain(
            include_tags=True,
            include_attrib=True,
            include_price=True,
            include_on_sale=True,
        ):
            doms = [base_domain]
            if include_tags and active_tag_ids:
                doms.append(Domain.OR([
                    Domain('product_tag_ids', 'in', active_tag_ids),
                    Domain('product_variant_ids.additional_product_tag_ids', 'in', active_tag_ids),
                ]))
            if include_attrib and attrib_dict:
                doms.extend(ProductTemplate._get_attribute_value_domain(attrib_dict))
            if include_price:
                if cur_min_price > 0:
                    doms.append(Domain('list_price', '>=', cur_min_price / conversion_rate))
                if cur_max_price > 0:
                    doms.append(Domain('list_price', '<=', cur_max_price / conversion_rate))
            if include_on_sale and wbh_on_sale:
                doms.append(Domain(on_sale_domain_clause))
            return Domain.AND(doms)

        # 1. Thống kê số lượng theo Tag (1 truy vấn SQL duy nhất, chống N+1)
        tag_tmpl_ids = list(ProductTemplate._search(_compose_domain(include_tags=False)))
        tag_counts = {}
        if tag_tmpl_ids:
            tmpl_tag_field = ProductTemplate._fields['product_tag_ids']
            var_tag_field = request.env['product.product']._fields['additional_product_tag_ids']
            cr = request.env.cr
            cr.execute(f"""
                SELECT tag_id, COUNT(DISTINCT tmpl_id)
                FROM (
                    SELECT {tmpl_tag_field.column2} AS tag_id,
                           {tmpl_tag_field.column1} AS tmpl_id
                    FROM {tmpl_tag_field.relation}
                    WHERE {tmpl_tag_field.column1} = ANY(%s)
                    UNION
                    SELECT vrel.{var_tag_field.column2} AS tag_id,
                           pp.product_tmpl_id AS tmpl_id
                    FROM {var_tag_field.relation} vrel
                    JOIN product_product pp ON pp.id = vrel.{var_tag_field.column1}
                    WHERE pp.active = true
                      AND pp.product_tmpl_id = ANY(%s)
                ) pairs
                GROUP BY tag_id
            """, (tag_tmpl_ids, tag_tmpl_ids))
            tag_counts = {row[0]: int(row[1]) for row in cr.fetchall() if row[1]}

        tags_data = []
        matched_tags = ProductTag
        if tag_counts:
            matched_tags = ProductTag.search([
                ('id', 'in', list(tag_counts.keys())),
                ('wbh_show_in_filter', '=', True),
                ('visible_to_customers', '=', True),
                '|',
                ('website_id', '=', False),
                ('website_id', '=', website.id),
            ], order='sequence, id')
            active_tag_set = set(active_tag_ids)
            for tag in matched_tags:
                cnt = tag_counts.get(tag.id, 0)
                if cnt <= 0:
                    continue
                is_active = tag.id in active_tag_set
                next_tags = (
                    [tid for tid in active_tag_ids if tid != tag.id]
                    if is_active
                    else active_tag_ids + [tag.id]
                )
                group_key = tag.wbh_filter_group or 'promo'
                tags_data.append({
                    'id': tag.id,
                    'name': tag.name,
                    'count': cnt,
                    'group': group_key,
                    'group_label': TAG_GROUP_LABELS.get(group_key, 'Nhãn khác'),
                    'hex_color': tag.wbh_badge_hex or tag.color or '#3C3C3C',
                    'color_index': ((tag.id - 1) % 11) + 1,
                    'active': is_active,
                    'toggle_url': self._wbh_build_shop_url(
                        category=category,
                        search=search,
                        tag_ids=next_tags,
                        attrib_dict=attrib_dict,
                        min_price=cur_min_price,
                        max_price=cur_max_price,
                        wbh_on_sale=wbh_on_sale,
                        order=order,
                    ),
                })

        # 2. Thống kê "Đang giảm giá" (1 truy vấn SQL)
        sale_tmpl_ids = list(ProductTemplate._search(_compose_domain(include_on_sale=False)))
        on_sale_count = 0
        if sale_tmpl_ids:
            request.env.cr.execute("""
                SELECT COUNT(*)
                FROM product_template
                WHERE id = ANY(%s)
                  AND COALESCE(compare_list_price, 0) > list_price
                  AND list_price > 0
            """, (sale_tmpl_ids,))
            on_sale_count = int(request.env.cr.fetchone()[0] or 0)

        on_sale_data = {
            'count': on_sale_count,
            'active': wbh_on_sale,
            'toggle_url': self._wbh_build_shop_url(
                category=category,
                search=search,
                tag_ids=active_tag_ids,
                attrib_dict=attrib_dict,
                min_price=cur_min_price,
                max_price=cur_max_price,
                wbh_on_sale=not wbh_on_sale,
                order=order,
            ),
        }

        # 3. Thống kê khoảng giá động từ wbh.price.range (1 truy vấn SQL)
        ranges = WbhPriceRange.search([
            ('active', '=', True),
            '|',
            ('website_id', '=', False),
            ('website_id', '=', website.id),
        ], order='sequence, min_price, id')
        price_ranges_data = []
        matched_range_name = None
        if ranges:
            price_tmpl_ids = list(ProductTemplate._search(_compose_domain(include_price=False)))
            prices = []
            if price_tmpl_ids:
                request.env.cr.execute("""
                    SELECT list_price * %s
                    FROM product_template
                    WHERE id = ANY(%s)
                """, (conversion_rate, price_tmpl_ids))
                prices = [float(row[0] or 0.0) for row in request.env.cr.fetchall()]

            has_price_filter = cur_min_price > 0 or cur_max_price > 0
            for pr in ranges:
                cnt = sum(
                    1 for price in prices
                    if price >= pr.min_price and (pr.max_price == 0 or price <= pr.max_price)
                )
                is_active = (
                    has_price_filter
                    and abs(cur_min_price - pr.min_price) < 1e-6
                    and abs(cur_max_price - pr.max_price) < 1e-6
                )
                if is_active:
                    matched_range_name = pr.name
                if cnt <= 0:
                    continue
                price_ranges_data.append({
                    'id': pr.id,
                    'name': pr.name,
                    'min_price': pr.min_price,
                    'max_price': pr.max_price,
                    'count': cnt,
                    'active': is_active,
                    'url': self._wbh_build_shop_url(
                        category=category,
                        search=search,
                        tag_ids=active_tag_ids,
                        attrib_dict=attrib_dict,
                        min_price=0.0 if is_active else pr.min_price,
                        max_price=0.0 if is_active else pr.max_price,
                        wbh_on_sale=wbh_on_sale,
                        order=order,
                    ),
                })

        # 4. Lọc danh sách Thuộc tính & Giá trị Thuộc tính có sản phẩm thật trên Website hiện tại
        attr_tmpl_ids = list(ProductTemplate._search(_compose_domain(include_attrib=False)))
        available_attr_ids = set()
        available_val_ids = set()
        if attr_tmpl_ids:
            ptal_val_field = request.env['product.template.attribute.line']._fields['value_ids']
            request.env.cr.execute(f"""
                SELECT DISTINCT ptal.attribute_id, rel.{ptal_val_field.column2}
                FROM product_template_attribute_line ptal
                JOIN {ptal_val_field.relation} rel
                  ON rel.{ptal_val_field.column1} = ptal.id
                JOIN product_attribute pa ON pa.id = ptal.attribute_id
                WHERE ptal.active = true
                  AND pa.visibility = 'visible'
                  AND ptal.product_tmpl_id = ANY(%s)
            """, (attr_tmpl_ids,))
            for attr_id, val_id in request.env.cr.fetchall():
                available_attr_ids.add(attr_id)
                available_val_ids.add(val_id)

        wbh_available_attr_value_ids = available_val_ids | attrib_set
        visible_attr_ids = available_attr_ids | set(attrib_dict.keys())
        filtered_attributes = (
            ProductAttribute.search([('id', 'in', list(visible_attr_ids))], order='sequence, id')
            if visible_attr_ids
            else ProductAttribute
        )
        if website and website.wbh_store_type == 'gift' and filtered_attributes:
            hidden_attrs = filtered_attributes.filtered(
                lambda attr: (attr.name or '').strip().lower() in WBH_GIFT_HIDDEN_ATTRIBUTE_NAMES
            )
            if hidden_attrs:
                filtered_attributes = filtered_attributes - hidden_attrs
                hidden_val_ids = set(hidden_attrs.mapped('value_ids').ids)
                wbh_available_attr_value_ids -= hidden_val_ids

        # 5. Active Filter Chips
        active_chips = []
        if category:
            active_chips.append({
                'label': f"Danh mục: {category.name}",
                'remove_url': self._wbh_build_shop_url(
                    category=None,
                    search=search,
                    tag_ids=active_tag_ids,
                    attrib_dict=attrib_dict,
                    min_price=cur_min_price,
                    max_price=cur_max_price,
                    wbh_on_sale=wbh_on_sale,
                    order=order,
                ),
                'kind': 'category',
            })
        if search:
            active_chips.append({
                'label': f'Tìm: "{search}"',
                'remove_url': self._wbh_build_shop_url(
                    category=category,
                    search='',
                    tag_ids=active_tag_ids,
                    attrib_dict=attrib_dict,
                    min_price=cur_min_price,
                    max_price=cur_max_price,
                    wbh_on_sale=wbh_on_sale,
                    order=order,
                ),
                'kind': 'search',
            })
        if wbh_on_sale:
            active_chips.append({
                'label': 'Đang giảm giá',
                'remove_url': self._wbh_build_shop_url(
                    category=category,
                    search=search,
                    tag_ids=active_tag_ids,
                    attrib_dict=attrib_dict,
                    min_price=cur_min_price,
                    max_price=cur_max_price,
                    wbh_on_sale=False,
                    order=order,
                ),
                'kind': 'on_sale',
            })
        if cur_min_price > 0 or cur_max_price > 0:
            if matched_range_name:
                price_label = matched_range_name
            elif cur_min_price > 0 and cur_max_price > 0:
                price_label = f"{self._wbh_format_vnd(cur_min_price)} – {self._wbh_format_vnd(cur_max_price)}"
            elif cur_min_price > 0:
                price_label = f"Từ {self._wbh_format_vnd(cur_min_price)}"
            else:
                price_label = f"Dưới {self._wbh_format_vnd(cur_max_price)}"
            active_chips.append({
                'label': price_label,
                'remove_url': self._wbh_build_shop_url(
                    category=category,
                    search=search,
                    tag_ids=active_tag_ids,
                    attrib_dict=attrib_dict,
                    min_price=0.0,
                    max_price=0.0,
                    wbh_on_sale=wbh_on_sale,
                    order=order,
                ),
                'kind': 'price',
            })
        if active_tag_ids:
            active_tags_recs = ProductTag.browse(active_tag_ids).exists()
            for tag in active_tags_recs:
                active_chips.append({
                    'label': tag.name,
                    'remove_url': self._wbh_build_shop_url(
                        category=category,
                        search=search,
                        tag_ids=[tid for tid in active_tag_ids if tid != tag.id],
                        attrib_dict=attrib_dict,
                        min_price=cur_min_price,
                        max_price=cur_max_price,
                        wbh_on_sale=wbh_on_sale,
                        order=order,
                    ),
                    'kind': 'tag',
                })
        if attrib_set:
            active_vals = ProductAttributeValue.browse(sorted(attrib_set)).exists()
            for val in active_vals:
                next_dict = {
                    aid: [vid for vid in vids if not (aid == val.attribute_id.id and vid == val.id)]
                    for aid, vids in attrib_dict.items()
                }
                next_dict = {aid: vids for aid, vids in next_dict.items() if vids}
                active_chips.append({
                    'label': f"{val.attribute_id.name}: {val.name}",
                    'remove_url': self._wbh_build_shop_url(
                        category=category,
                        search=search,
                        tag_ids=active_tag_ids,
                        attrib_dict=next_dict,
                        min_price=cur_min_price,
                        max_price=cur_max_price,
                        wbh_on_sale=wbh_on_sale,
                        order=order,
                    ),
                    'kind': 'attrib',
                })

        wbh_filter_ctx = {
            'tags': tags_data,
            'on_sale': on_sale_data,
            'price_ranges': price_ranges_data,
            'active_chips': active_chips,
            'clear_all_url': '/shop',
            'total_active_filters': len(active_chips),
            'available_attribute_value_ids': sorted(wbh_available_attr_value_ids),
            'min_price_display': self._wbh_format_vnd(cur_min_price) if cur_min_price > 0 else '',
            'max_price_display': self._wbh_format_vnd(cur_max_price) if cur_max_price > 0 else '',
        }
        grouped_attributes_values = (
            ProductAttributeValue.browse(sorted(attrib_set)).sorted().grouped('attribute_id')
            if attrib_set
            else values.get('grouped_attributes_values', ProductAttributeValue.grouped('attribute_id'))
        )
        return {
            'wbh_filter_ctx': wbh_filter_ctx,
            'wbh_available_attr_value_ids': wbh_available_attr_value_ids,
            'attributes': filtered_attributes,
            'attrib_values': attrib_dict,
            'attrib_set': attrib_set,
            'grouped_attributes_values': grouped_attributes_values,
            'all_tags': matched_tags,
            'tags': set(active_tag_ids),
        }

    def _get_additional_shop_values(self, values, **kwargs):
        res = super()._get_additional_shop_values(values, **kwargs)
        merged_values = dict(values)
        merged_values.update(res)
        res.update(self._wbh_compute_filter_ctx(merged_values, **kwargs))
        website = request.env['website'].get_current_website()
        if website and website.currency_id and website.currency_id.decimal_places == 0:
            for price_key in ('min_price', 'max_price', 'available_min_price', 'available_max_price'):
                if price_key in merged_values and merged_values[price_key] is not None:
                    res[price_key] = float(int(round(merged_values[price_key])))
        return res

    @route()
    def shop_checkout(self, try_skip_step=None, **query_params):
        order_sudo = request.cart
        if order_sudo and order_sudo.state in ('draft', 'sent'):
            order_sudo._wbh_sync_packaging_fee_line()
        return super().shop_checkout(try_skip_step=try_skip_step, **query_params)

    @route()
    def shop_payment(self, **post):
        order_sudo = request.cart
        if order_sudo and order_sudo.state in ('draft', 'sent'):
            order_sudo._wbh_sync_packaging_fee_line()
        return super().shop_payment(**post)

    @route()
    def shop(self, page=0, category=None, search='', min_price=0.0, max_price=0.0, tags='', **post):
        request_args = request.httprequest.args
        tag_ids = self._wbh_parse_tag_ids(tags)
        tags_str = ','.join(str(tid) for tid in tag_ids)

        raw_attr_values = list(request_args.getlist('attribute_values'))
        raw_attrib = list(request_args.getlist('attrib'))
        attrib_dict = self._wbh_merge_attribute_value_dict(raw_attr_values + raw_attrib)
        attrib_values_list = self._wbh_format_attribute_values(attrib_dict)

        wbh_on_sale = self._wbh_is_on_sale_param(post.get('wbh_on_sale'))
        if wbh_on_sale:
            post['wbh_on_sale'] = '1'
        else:
            post.pop('wbh_on_sale', None)
        post.pop('attrib', None)

        try:
            parsed_min = float(min_price) if min_price else 0.0
        except (TypeError, ValueError):
            parsed_min = 0.0
        try:
            parsed_max = float(max_price) if max_price else 0.0
        except (TypeError, ValueError):
            parsed_max = 0.0

        request._wbh_shop_params = {
            'tag_ids': tag_ids,
            'tags_str': tags_str,
            'attrib_dict': attrib_dict,
            'attrib_values_list': attrib_values_list,
            'wbh_on_sale': wbh_on_sale,
            'min_price': parsed_min,
            'max_price': parsed_max,
        }
        try:
            return super().shop(
                page=page,
                category=category,
                search=search,
                min_price=min_price,
                max_price=max_price,
                tags=tags_str,
                **post,
            )
        finally:
            if hasattr(request, '_wbh_shop_params'):
                delattr(request, '_wbh_shop_params')


class WbhWebsiteSaleCart(Cart):
    """Đảm bảo Phí gói cố định được đồng bộ mỗi khi mở trang Giỏ hàng /shop/cart."""

    @route()
    def cart(self, id=None, access_token=None, revive_method='', **post):
        order_sudo = request.cart
        if order_sudo and order_sudo.state in ('draft', 'sent'):
            order_sudo._wbh_sync_packaging_fee_line()
        return super().cart(
            id=id,
            access_token=access_token,
            revive_method=revive_method,
            **post,
        )


class WbhWebsiteSaleDelivery(Delivery):
    """Đồng bộ số liệu Thành tiền sản phẩm & Phí gói khi cập nhật phương thức vận chuyển."""

    def _order_summary_values(self, order, **kwargs):
        res = super()._order_summary_values(order, **kwargs)
        if (
            order
            and order.website_id
            and order.website_id.wbh_store_type == 'gift'
            and order.website_id.wbh_packaging_fee_enabled
        ):
            Monetary = request.env['ir.qweb.field.monetary']
            currency = order.currency_id
            res['amount_untaxed'] = Monetary.value_to_html(
                order.wbh_amount_products,
                {'display_currency': currency},
            )
            res['wbh_packaging_fee_amount'] = Monetary.value_to_html(
                order.wbh_packaging_fee_amount,
                {'display_currency': currency},
            )
        return res
