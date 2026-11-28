# -*- coding: utf-8 -*-
"""Script idempotent đồng bộ cấu hình & dữ liệu DB đang chạy theo yêu cầu Manh Dao Dao (CR-01..CR-10).

Hỗ trợ chạy theo 2 cách:
1. Qua Odoo shell:
   docker exec -i web-ban-hang-app odoo shell -c /etc/odoo/odoo.conf -d web_ban_hang_dev --no-http < /mnt/extra-addons/wbh_core/scripts/apply_cr_manhdaodao.py
2. Trực tiếp bằng python3 bên trong container Odoo:
   docker exec web-ban-hang-app python3 /mnt/extra-addons/wbh_core/scripts/apply_cr_manhdaodao.py
"""
import base64
import os

from odoo import Command, SUPERUSER_ID, api
from odoo.modules.registry import Registry
from odoo.tools.misc import file_path

GOODS_TYPE_VALUES = [
    'CARD',
    'POSTCARD (PC)',
    'STANDEE',
    'KEY',
    'FIGURE',
    'BADGE',
    'CLEAR FILE',
    'DOLL',
    'KHÁC',
]

GOODS_KEYWORD_RULES = [
    ('DOLL', ('doll', 'búp bê', 'plush', 'mochi', 'gấu bông', 'nui')),
    ('POSTCARD (PC)', ('postcard', 'shikishi', 'tranh ký', 'poster')),
    ('STANDEE', ('standee', 'std')),
    ('KEY', ('móc khóa', 'keychain', 'key')),
    ('FIGURE', ('figure', 'mô hình')),
    ('BADGE', ('badge', 'huy hiệu', 'pin balo')),
    ('CLEAR FILE', ('clear file', 'bìa hồ sơ', 'file')),
    ('CARD', ('card', 'photocard', 'snapmide', 'polaroid', 'instax', 'ticket', 'memo', 'thẻ')),
]


def _ensure_vnd_currency(env):
    Currency = env['res.currency'].with_context(active_test=False)
    vnd = Currency.search([('name', '=', 'VND')], limit=1)
    if vnd:
        vnd.write({'active': True, 'position': 'after', 'rounding': 1.0})
        print(f"[CURRENCY] VND ID={vnd.id} -> active=True, rounding=1.0, decimal_places={vnd.decimal_places}")


def _sync_websites(env):
    gift_website = env.ref('wbh_core.website_gift_store', raise_if_not_found=False)
    if not gift_website:
        gift_website = env['website'].search([('wbh_store_type', '=', 'gift')], limit=1)
    if gift_website:
        gift_vals = {
            'name': 'Manh Dao Dao - Boku no Hero Academia Anime Goods Shop',
            'wbh_brand_tagline': 'Tiền trao tay, quýt về ngay',
            'wbh_support_hotline': False,
            'wbh_support_zalo_url': False,
            'wbh_support_facebook_url': 'https://www.facebook.com/an.na.116565?locale=vi_VN',
            'wbh_contact_prompt': 'Cần vid check hoặc tư vấn chọn hàng?',
            'wbh_packaging_fee_enabled': True,
            'wbh_packaging_fee': 5000.0,
        }
        gift_website.write(gift_vals)
        print(f"[WEBSITE] Updated Web 1 ID={gift_website.id}: {gift_website.name}")

    fashion_website = env.ref('wbh_core.website_fashion_store', raise_if_not_found=False)
    if not fashion_website:
        fashion_website = env['website'].search([('wbh_store_type', '=', 'fashion')], limit=1)
    if fashion_website:
        fashion_website.write({
            'wbh_packaging_fee_enabled': False,
            'wbh_packaging_fee': 0.0,
        })
        print(f"[WEBSITE] Updated Web 2 ID={fashion_website.id}: packaging fee disabled")
    return gift_website


def _infer_goods_values(product, value_by_name):
    haystack = ' '.join([
        product.name or '',
        product.wbh_short_highlight or '',
        ' '.join(product.public_categ_ids.mapped('name')),
    ]).lower()
    matched = []
    for val_name, keywords in GOODS_KEYWORD_RULES:
        if any(kw in haystack for kw in keywords) and val_name in value_by_name:
            matched.append(value_by_name[val_name])
    if not matched and 'KHÁC' in value_by_name:
        matched.append(value_by_name['KHÁC'])
    return matched


def _sync_attributes(env, gift_website):
    Attr = env['product.attribute']
    AttrVal = env['product.attribute.value']

    # Ẩn các thuộc tính cũ khỏi sidebar lọc /shop nhưng vẫn giữ variant đang dùng
    for hidden_name in ('Mẫu Thẻ Sưu Tầm', 'Gói Phân Loại'):
        hidden_attrs = Attr.search([('name', '=ilike', hidden_name)])
        if hidden_attrs:
            hidden_attrs.write({'visibility': 'hidden'})
            print(f"[ATTR] Hidden '{hidden_name}' IDs={hidden_attrs.ids}")

    # Bảo đảm thuộc tính 'Loại goods' (no_variant) và đủ 9 giá trị chuẩn
    goods_attr = env.ref('wbh_core.attr_goods_type', raise_if_not_found=False)
    if not goods_attr:
        goods_attr = Attr.search([('name', '=ilike', 'Loại goods')], limit=1)
    if not goods_attr:
        goods_attr = Attr.create({
            'name': 'Loại goods',
            'display_type': 'pills',
            'create_variant': 'no_variant',
            'visibility': 'visible',
            'sequence': 5,
        })
    else:
        goods_attr.write({
            'name': 'Loại goods',
            'display_type': 'pills',
            'create_variant': 'no_variant',
            'visibility': 'visible',
            'sequence': 5,
        })

    value_by_name = {}
    for idx, val_name in enumerate(GOODS_TYPE_VALUES, start=1):
        val = AttrVal.search([
            ('attribute_id', '=', goods_attr.id),
            ('name', '=ilike', val_name),
        ], limit=1)
        if not val:
            val = AttrVal.create({
                'name': val_name,
                'attribute_id': goods_attr.id,
                'sequence': idx * 10,
            })
        else:
            val.write({'name': val_name, 'sequence': idx * 10})
        value_by_name[val_name] = val

    # Tự động gắn dòng 'Loại goods' cho các sản phẩm Web 1 chưa được phân loại
    if gift_website:
        gift_products = env['product.template'].search([
            ('sale_ok', '=', True),
            ('type', '!=', 'service'),
            '|',
            ('website_id', '=', gift_website.id),
            ('wbh_store_scope', 'in', ('gift', 'both')),
        ])
        assigned_count = 0
        for product in gift_products:
            has_goods_line = product.attribute_line_ids.filtered(
                lambda line: line.attribute_id.id == goods_attr.id
            )
            if has_goods_line:
                continue
            vals = _infer_goods_values(product, value_by_name)
            if vals:
                product.write({
                    'attribute_line_ids': [Command.create({
                        'attribute_id': goods_attr.id,
                        'value_ids': [Command.set([v.id for v in vals])],
                    })],
                })
                assigned_count += 1
        print(f"[ATTR] 'Loại goods' ID={goods_attr.id} ready (assigned to {assigned_count} products)")


def _sync_packaging_product_and_carts(env, gift_website):
    pkg_product = env.ref('wbh_core.wbh_product_packaging_fee', raise_if_not_found=False)
    if not pkg_product:
        pkg_product = env['product.product'].with_context(active_test=False).search([
            ('default_code', '=', 'WBH_PACKAGING_FEE'),
        ], limit=1)
    if pkg_product:
        pkg_product.write({
            'name': 'Phí gói',
            'type': 'service',
            'sale_ok': False,
            'purchase_ok': False,
            'is_published': False,
            'active': True,
            'list_price': 5000.0,
            'taxes_id': [Command.clear()],
            'invoice_policy': 'order',
        })
        print(f"[PACKAGING] Synced wbh_product_packaging_fee ID={pkg_product.id}")

    if gift_website:
        open_carts = env['sale.order'].search([
            ('website_id', '=', gift_website.id),
            ('state', 'in', ('draft', 'sent')),
        ])
        if open_carts:
            open_carts._wbh_sync_packaging_fee_line()
            print(f"[PACKAGING] Synced {len(open_carts)} open Web 1 draft orders")


def _sync_delivery_carriers(env):
    Carrier = env['delivery.carrier'].with_context(active_test=False)
    for xmlid in ('wbh_delivery_vn.carrier_wbh_standard', 'wbh_delivery_vn.carrier_wbh_hold_order'):
        rec = env.ref(xmlid, raise_if_not_found=False)
        if rec:
            rec.write({'is_published': False})
            print(f"[DELIVERY] Unpublished old carrier {xmlid} (ID={rec.id})")

    old_carriers = Carrier.search([
        '|',
        ('name', 'ilike', 'Đồng giá 30.000'),
        ('name', 'ilike', 'Gom đơn / Giữ hàng'),
    ])
    if old_carriers:
        old_carriers.write({'is_published': False})

    vtp = env.ref('wbh_delivery_vn.carrier_wbh_viettel_post', raise_if_not_found=False)
    if not vtp:
        vtp = Carrier.search([('name', 'ilike', 'VIETTEL POST')], limit=1)
    if vtp:
        vtp.write({
            'name': 'ĐVVC VIETTEL POST',
            'active': True,
            'is_published': True,
            'sequence': 10,
        })
        print(f"[DELIVERY] Enabled 'ĐVVC VIETTEL POST' ID={vtp.id}")
    else:
        print("[DELIVERY] Note: Viettel Post carrier not found yet (upgrade wbh_delivery_vn first).")


def _sync_payment_providers(env):
    cod_provider = env.ref('wbh_payment_vietqr.payment_provider_cod', raise_if_not_found=False)
    if not cod_provider:
        cod_provider = env['payment.provider'].search([('code', '=', 'wbh_cod')], limit=1)
    if cod_provider:
        cod_provider.write({'state': 'disabled', 'is_published': False})
        print(f"[PAYMENT] Disabled COD provider ID={cod_provider.id}")

    cod_method = env.ref('wbh_payment_vietqr.payment_method_cod', raise_if_not_found=False)
    if not cod_method:
        cod_method = env['payment.method'].with_context(active_test=False).search([
            ('code', '=', 'wbh_cod'),
        ], limit=1)
    if cod_method:
        cod_method.write({'active': False})
        print(f"[PAYMENT] Deactivated COD method ID={cod_method.id}")

    vietqr_method = env.ref('wbh_payment_vietqr.payment_method_vietqr', raise_if_not_found=False)
    if not vietqr_method:
        vietqr_method = env['payment.method'].with_context(active_test=False).search([
            ('code', '=', 'vietqr'),
        ], limit=1)
    if vietqr_method:
        vietqr_method.write({'active': True})
        print(f"[PAYMENT] Activated VietQR method ID={vietqr_method.id}")

    vietqr_provider = env.ref('wbh_payment_vietqr.payment_provider_vietqr', raise_if_not_found=False)
    if not vietqr_provider:
        vietqr_provider = env['payment.provider'].search([('code', '=', 'vietqr')], limit=1)
    if vietqr_provider:
        vals = {
            'state': 'enabled',
            'is_published': True,
        }
        if vietqr_method:
            vals['payment_method_ids'] = [Command.link(vietqr_method.id)]
        vietqr_provider.write(vals)
        print(f"[PAYMENT] Enabled VietQR provider ID={vietqr_provider.id}")


def _sync_website_branding_and_assets(env, gift_website):
    """Đồng bộ logo/favicon mới vào DB, bật view chính sách PDP và xóa cache asset cũ."""
    if gift_website:
        vals = {}
        for field_name, rel_path in (
            ('logo', 'theme_gift_store/static/src/img/logo.png'),
            ('favicon', 'theme_gift_store/static/src/img/favicon.ico'),
        ):
            try:
                abs_path = file_path(rel_path)
                with open(abs_path, 'rb') as fp:
                    vals[field_name] = base64.b64encode(fp.read())
            except FileNotFoundError:
                print(f"[BRANDING] Skip missing file: {rel_path}")
        if vals:
            gift_website.write(vals)
            print(f"[BRANDING] Synced logo/favicon into website ID={gift_website.id}")

        # Bảo đảm bật view chính sách dưới nút Mua trên PDP Web 1
        terms_view = env['website'].with_context(website_id=gift_website.id).viewref(
            'website_sale.product_terms_and_conditions', raise_if_not_found=False
        )
        if terms_view and not terms_view.active:
            terms_view.sudo().write({'active': True})
            print(f"[VIEW] Enabled product_terms_and_conditions ID={terms_view.id}")

    old_assets = env['ir.attachment'].sudo().search([('url', '=like', '/web/assets/%')])
    if old_assets:
        count = len(old_assets)
        old_assets.unlink()
        print(f"[ASSETS] Cleared {count} compiled /web/assets/* bundles")


def apply_cr_manhdaodao(env):
    """Thực thi toàn bộ cập nhật cấu hình & dữ liệu CR Manh Dao Dao theo chuẩn idempotent."""
    _ensure_vnd_currency(env)
    gift_website = _sync_websites(env)
    _sync_attributes(env, gift_website)
    _sync_packaging_product_and_carts(env, gift_website)
    _sync_delivery_carriers(env)
    _sync_payment_providers(env)
    _sync_website_branding_and_assets(env, gift_website)


if 'env' in globals():
    apply_cr_manhdaodao(env)
    env.cr.commit()
    print('=== HOAN TAT APPLY CR MANH DAO DAO (ODOO SHELL MODE) ===')
elif __name__ == '__main__':
    import odoo

    db_name = os.environ.get('ODOO_DB', 'web_ban_hang_dev')
    odoo.tools.config.parse_config(['-c', '/etc/odoo/odoo.conf', '-d', db_name])
    registry = Registry(db_name)
    with registry.cursor() as cr:
        local_env = api.Environment(cr, SUPERUSER_ID, {})
        apply_cr_manhdaodao(local_env)
        cr.commit()
    print(f'=== HOAN TAT APPLY CR MANH DAO DAO VAO DB {db_name} ===')
