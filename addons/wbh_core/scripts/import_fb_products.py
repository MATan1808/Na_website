# -*- coding: utf-8 -*-
"""Script import dữ liệu sản phẩm cào từ Facebook Manh Dao Dao vào Odoo 19.0 Community.

Hỗ trợ chạy theo 2 cách:
1. Qua Odoo shell:
   docker exec -i web-ban-hang-app odoo shell -c /etc/odoo/odoo.conf -d web_ban_hang_dev --no-http < /mnt/extra-addons/wbh_core/scripts/import_fb_products.py
2. Trực tiếp bằng python3 bên trong container Odoo:
   docker exec web-ban-hang-app python3 /mnt/extra-addons/wbh_core/scripts/import_fb_products.py
"""
import base64
import csv
import json
import os

from odoo import Command, SUPERUSER_ID, api
from odoo.modules.registry import Registry

MODULE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if "__file__" in globals() else "/mnt/extra-addons/wbh_core"
DATA_JSON_PATH = os.path.join(MODULE_DIR, "data", "fb_manhdaodao_products.json")
DATA_CSV_PATH = os.path.join(MODULE_DIR, "data", "fb_manhdaodao_products.csv")
IMG_DIR = os.path.join(MODULE_DIR, "static", "src", "img", "fb_manhdaodao")

SUB_CAT_NAMES = {
    "doll": "Búp Bê Bông Doll 20cm & Outfit",
    "card": "Card Bo Góc & Photocards",
    "badge": "Huy Hiệu (Can Badges) & Pin Balo",
    "mochi": "Mochi Bông Tròn & Túi Mù",
    "poster": "Tranh Ký & Standee Nhân Vật",
}


def read_img_base64(filename):
    """Đọc file ảnh từ thư mục local fb_manhdaodao sang chuỗi base64."""
    if not filename:
        return False
    path = os.path.join(IMG_DIR, filename)
    if os.path.exists(path) and os.path.getsize(path) > 0:
        with open(path, "rb") as f:
            return base64.b64encode(f.read())
    return False


def get_or_create_attr(env, name, display_type, create_variant):
    """Tìm hoặc tạo mới product.attribute chuẩn Odoo 19.0."""
    Attr = env["product.attribute"]
    attr = Attr.search([("name", "=", name)], limit=1)
    if not attr:
        attr = Attr.create({
            "name": name,
            "display_type": display_type,
            "create_variant": create_variant,
        })
    return attr


def get_or_create_attr_value(env, attr, value_name):
    """Tìm hoặc tạo mới product.attribute.value thuộc attribute đã cho."""
    AttrVal = env["product.attribute.value"]
    val = AttrVal.search([("name", "=", value_name), ("attribute_id", "=", attr.id)], limit=1)
    if not val:
        val = AttrVal.create({"name": value_name, "attribute_id": attr.id})
    return val


def ensure_categories(env, gift_website):
    """Bảo đảm đủ danh mục Anime Goods & Merch và 5 danh mục con."""
    Cat = env["product.public.category"]
    parent_cat = Cat.search([("name", "=", "Anime Goods & Merch")], limit=1)
    if not parent_cat:
        vals = {"name": "Anime Goods & Merch", "sequence": 1}
        if gift_website:
            vals["website_id"] = gift_website.id
        parent_cat = Cat.create(vals)
    elif gift_website and not parent_cat.website_id:
        parent_cat.website_id = gift_website.id

    cat_records = {}
    for idx, (key, cat_name) in enumerate(SUB_CAT_NAMES.items(), start=1):
        rec = Cat.search([("name", "=", cat_name), ("parent_id", "=", parent_cat.id)], limit=1)
        if not rec:
            vals = {
                "name": cat_name,
                "parent_id": parent_cat.id,
                "sequence": idx * 10,
            }
            if gift_website:
                vals["website_id"] = gift_website.id
            rec = Cat.create(vals)
        elif gift_website and not rec.website_id:
            rec.website_id = gift_website.id
        cat_records[key] = rec
    return parent_cat, cat_records


def ensure_stock_for_product(env, prod_tmpl, default_qty=20.0):
    """Nạp tồn kho mặc định vào kho chính cho các biến thể chưa có tồn kho."""
    Quant = env["stock.quant"]
    warehouse = env["stock.warehouse"].search([], limit=1)
    if not warehouse or not warehouse.lot_stock_id:
        return
    location = warehouse.lot_stock_id
    for variant in prod_tmpl.product_variant_ids:
        existing_quants = Quant.search([
            ("product_id", "=", variant.id),
            ("location_id", "=", location.id),
        ])
        current_qty = sum(existing_quants.mapped("quantity"))
        if current_qty <= 0:
            Quant.with_context(inventory_mode=True).create({
                "product_id": variant.id,
                "location_id": location.id,
                "inventory_quantity": default_qty,
            }).action_apply_inventory()


def sync_gallery_images(env, prod_tmpl, item):
    """Đồng bộ ảnh phụ gallery (bỏ ảnh chính) vào product.image với prefix [FB]."""
    ProductImage = env["product.image"]
    old_fb_images = ProductImage.search([
        ("product_tmpl_id", "=", prod_tmpl.id),
        ("name", "=like", "[FB]%"),
    ])
    if old_fb_images:
        old_fb_images.unlink()

    main_img = item.get("main_image")
    gallery = [g for g in item.get("gallery_images", []) if g != main_img]
    added = 0
    for seq, img_file in enumerate(gallery, start=1):
        b64 = read_img_base64(img_file)
        if b64:
            ProductImage.create({
                "name": f"[FB] {item['sku']} - Ảnh {seq}",
                "sequence": seq * 10,
                "image_1920": b64,
                "product_tmpl_id": prod_tmpl.id,
            })
            added += 1
    return added


def generate_csv_from_json(payload):
    """Sinh bổ sung file CSV UTF-8-SIG từ JSON nếu cần đồng bộ."""
    products = payload.get("products", [])
    if not products:
        return
    fieldnames = [
        "default_code",
        "name",
        "list_price",
        "wbh_store_scope",
        "public_categ_names",
        "anime_series",
        "characters",
        "variants_summary",
        "wbh_short_highlight",
        "description_sale",
        "wbh_care_note",
        "main_image",
        "source_post_date",
        "source_permalink",
    ]
    with open(DATA_CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in products:
            categ_names = [SUB_CAT_NAMES.get(k, k) for k in item.get("category_keys", [])]
            variants_str = " | ".join(
                f"{v['name']} ({int(item['list_price'] + v['price_extra']):,}đ)"
                for v in item.get("variants", [])
            )
            writer.writerow({
                "default_code": item["sku"],
                "name": item["name"],
                "list_price": int(item["list_price"]),
                "wbh_store_scope": item.get("wbh_store_scope", "gift"),
                "public_categ_names": ", ".join(categ_names),
                "anime_series": item.get("anime_series", ""),
                "characters": ", ".join(item.get("characters", [])),
                "variants_summary": variants_str,
                "wbh_short_highlight": item.get("wbh_short_highlight", ""),
                "description_sale": item.get("description_sale", ""),
                "wbh_care_note": item.get("wbh_care_note", ""),
                "main_image": item.get("main_image", ""),
                "source_post_date": item.get("source_post_date", ""),
                "source_permalink": item.get("source_permalink", ""),
            })


def run_import(env):
    """Thực thi nạp toàn bộ sản phẩm từ fb_manhdaodao_products.json vào Odoo."""
    if not os.path.exists(DATA_JSON_PATH):
        raise FileNotFoundError(f"Không tìm thấy file dữ liệu: {DATA_JSON_PATH}")

    with open(DATA_JSON_PATH, "r", encoding="utf-8") as f:
        payload = json.load(f)

    gift_website = env.ref("wbh_core.website_gift_store", raise_if_not_found=False)
    parent_cat, cat_records = ensure_categories(env, gift_website)

    attr_series = get_or_create_attr(env, "Bộ Phim (Anime)", "radio", "no_variant")
    attr_char = get_or_create_attr(env, "Nhân Vật (Bias)", "radio", "no_variant")
    attr_option = get_or_create_attr(env, "Gói Phân Loại", "select", "always")
    attr_card_type = get_or_create_attr(env, "Mẫu Thẻ Sưu Tầm", "select", "always")

    attr_map = {
        "Gói Phân Loại": attr_option,
        "Mẫu Thẻ Sưu Tầm": attr_card_type,
    }

    Prod = env["product.template"]
    products_data = payload.get("products", [])
    print(f"=== BAT DAU IMPORT {len(products_data)} SAN PHAM TU MANH DAO DAO FB ===")

    for item in products_data:
        sku = item["sku"]
        series_val = get_or_create_attr_value(env, attr_series, item["anime_series"])
        char_vals = [get_or_create_attr_value(env, attr_char, c) for c in item.get("characters", [])]

        variant_attr_name = item.get("variant_attribute", "Gói Phân Loại")
        variant_attr = attr_map.get(variant_attr_name) or get_or_create_attr(env, variant_attr_name, "select", "always")
        variant_val_records = []
        price_extra_by_val_id = {}
        for v in item.get("variants", []):
            v_rec = get_or_create_attr_value(env, variant_attr, v["name"])
            variant_val_records.append(v_rec)
            price_extra_by_val_id[v_rec.id] = float(v.get("price_extra", 0.0))

        categ_ids = [parent_cat.id]
        for key in item.get("category_keys", []):
            if key in cat_records:
                categ_ids.append(cat_records[key].id)

        attr_lines = [
            Command.create({
                "attribute_id": attr_series.id,
                "value_ids": [Command.set([series_val.id])],
            }),
        ]
        if char_vals:
            attr_lines.append(Command.create({
                "attribute_id": attr_char.id,
                "value_ids": [Command.set([c.id for c in char_vals])],
            }))
        if variant_val_records:
            attr_lines.append(Command.create({
                "attribute_id": variant_attr.id,
                "value_ids": [Command.set([v.id for v in variant_val_records])],
            }))

        main_img_b64 = read_img_base64(item.get("main_image"))
        common_vals = {
            "name": item["name"],
            "default_code": sku,
            "list_price": float(item["list_price"]),
            "wbh_store_scope": item.get("wbh_store_scope", "gift"),
            "wbh_short_highlight": item.get("wbh_short_highlight", ""),
            "wbh_care_note": item.get("wbh_care_note", ""),
            "description_sale": item.get("description_sale", ""),
            "public_categ_ids": [Command.set(categ_ids)],
            "is_published": True,
            "sale_ok": True,
            "type": "consu",
            "is_storable": False,
        }
        if main_img_b64:
            common_vals["image_1920"] = main_img_b64

        matches = Prod.with_context(active_test=False).search([
            "|",
            "|",
            ("default_code", "=", sku),
            ("product_variant_ids.default_code", "=like", f"{sku}%"),
            ("name", "=", item["name"]),
        ]).sorted("id")
        existing = matches[:1]
        if len(matches) > 1:
            duplicates = matches[1:].filtered("active")
            for dup in duplicates:
                unlinked = False
                try:
                    with env.cr.savepoint():
                        dup.unlink()
                        unlinked = True
                except Exception:
                    unlinked = False
                if not unlinked:
                    dup.product_variant_ids.write({"default_code": False})
                    dup.write({
                        "active": False,
                        "is_published": False,
                        "is_storable": False,
                    })
        if not existing:
            create_vals = dict(common_vals, attribute_line_ids=attr_lines)
            prod = Prod.create(create_vals)
            action_label = "CREATED"
        else:
            update_vals = dict(common_vals, active=True)
            # Chỉ tái tạo attribute_line_ids khi số lượng giá trị variant chưa khớp để tránh mất ID variant đang dùng
            existing_variant_line = existing.attribute_line_ids.filtered(lambda l: l.attribute_id == variant_attr)
            expected_v_ids = {v.id for v in variant_val_records}
            current_v_ids = set(existing_variant_line.value_ids.ids) if existing_variant_line else set()
            if expected_v_ids != current_v_ids or not existing.attribute_line_ids:
                update_vals["attribute_line_ids"] = [Command.clear()] + attr_lines
            existing.write(update_vals)
            prod = existing
            action_label = "UPDATED"

        # Gán price_extra cho từng biến thể
        target_line = prod.attribute_line_ids.filtered(lambda l: l.attribute_id == variant_attr)
        for ptav in target_line.product_template_value_ids:
            val_id = ptav.product_attribute_value_id.id
            if val_id in price_extra_by_val_id:
                ptav.price_extra = price_extra_by_val_id[val_id]

        # Gán default_code cho các variant để dễ quản lý kho & nhận diện idempotent
        for idx, variant in enumerate(prod.product_variant_ids.sorted("id"), start=1):
            expected_code = f"{sku}-V{idx:02d}"
            if variant.default_code != expected_code:
                variant.default_code = expected_code

        gallery_count = sync_gallery_images(env, prod, item)
        if prod.is_storable:
            ensure_stock_for_product(env, prod, default_qty=20.0)

        print(
            f"[{action_label}] {sku} | ID={prod.id} | Variants={len(prod.product_variant_ids)} "
            f"| Gallery={gallery_count} | URL={prod.website_url}"
        )


if "env" in globals():
    run_import(env)
    env.cr.commit()
    print("=== HOAN TAT IMPORT (ODOO SHELL MODE) ===")
elif __name__ == "__main__":
    import odoo
    db_name = os.environ.get("ODOO_DB", "web_ban_hang_dev")
    odoo.tools.config.parse_config(["-c", "/etc/odoo/odoo.conf", "-d", db_name])
    registry = Registry(db_name)
    with registry.cursor() as cr:
        local_env = api.Environment(cr, SUPERUSER_ID, {})
        run_import(local_env)
        cr.commit()
    print(f"=== HOAN TAT IMPORT VAO DB {db_name} ===")
