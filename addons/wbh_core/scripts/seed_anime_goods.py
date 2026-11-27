import base64
import os
import odoo
from odoo.modules.registry import Registry
from odoo import api, SUPERUSER_ID, Command

IMG_DIR = "/mnt/extra-addons/wbh_core/static/src/img/anime_goods"

def read_img_base64(filename):
    path = os.path.join(IMG_DIR, filename)
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read())
    return False

registry = Registry("web_ban_hang_dev")
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})

    print("=== SEEDING ANIME MERCHANDISE CATEGORIES ===")
    Cat = env["product.public.category"]
    
    parent_cat = Cat.search([("name", "=", "Anime Goods & Merch")], limit=1)
    if not parent_cat:
        parent_cat = Cat.create({
            "name": "Anime Goods & Merch",
            "sequence": 1,
        })
    print(f"Parent Category: {parent_cat.name} (ID: {parent_cat.id})")

    sub_cats = {
        "doll": "Búp Bê Bông Doll 20cm & Outfit",
        "card": "Card Bo Góc & Photocards",
        "badge": "Huy Hiệu (Can Badges) & Pin Balo",
        "mochi": "Mochi Bông Tròn & Túi Mù",
        "poster": "Tranh Ký & Standee Nhân Vật",
    }
    cat_records = {}
    for key, name in sub_cats.items():
        rec = Cat.search([("name", "=", name), ("parent_id", "=", parent_cat.id)], limit=1)
        if not rec:
            rec = Cat.create({
                "name": name,
                "parent_id": parent_cat.id,
                "sequence": 10,
            })
        cat_records[key] = rec
        print(f"  - Sub-category: {rec.name} (ID: {rec.id})")

    print("\n=== SEEDING ATTRIBUTES ===")
    Attr = env["product.attribute"]
    AttrVal = env["product.attribute.value"]

    # 1. Attribute: Anime Series
    attr_series = Attr.search([("name", "=", "Bộ Phim (Anime)")], limit=1)
    if not attr_series:
        attr_series = Attr.create({
            "name": "Bộ Phim (Anime)",
            "display_type": "radio",
            "create_variant": "no_variant",
        })
    val_mha = AttrVal.search([("name", "=", "My Hero Academia"), ("attribute_id", "=", attr_series.id)], limit=1)
    if not val_mha:
        val_mha = AttrVal.create({"name": "My Hero Academia", "attribute_id": attr_series.id})

    # 2. Attribute: Character
    attr_char = Attr.search([("name", "=", "Nhân Vật (Bias)")], limit=1)
    if not attr_char:
        attr_char = Attr.create({
            "name": "Nhân Vật (Bias)",
            "display_type": "radio",
            "create_variant": "no_variant",
        })
    val_baku = AttrVal.search([("name", "=", "Bakugo Katsuki (Kacchan)"), ("attribute_id", "=", attr_char.id)], limit=1)
    if not val_baku:
        val_baku = AttrVal.create({"name": "Bakugo Katsuki (Kacchan)", "attribute_id": attr_char.id})
    val_todo = AttrVal.search([("name", "=", "Todoroki Shoto"), ("attribute_id", "=", attr_char.id)], limit=1)
    if not val_todo:
        val_todo = AttrVal.create({"name": "Todoroki Shoto", "attribute_id": attr_char.id})

    # 3. Attribute: Doll Option
    attr_option = Attr.search([("name", "=", "Gói Phân Loại")], limit=1)
    if not attr_option:
        attr_option = Attr.create({
            "name": "Gói Phân Loại",
            "display_type": "select",
            "create_variant": "always",
        })
    val_fullset = AttrVal.search([("name", "=", "Full Set (Body Búp Bê + Set Đồ Áo Khoác)"), ("attribute_id", "=", attr_option.id)], limit=1)
    if not val_fullset:
        val_fullset = AttrVal.create({"name": "Full Set (Body Búp Bê + Set Đồ Áo Khoác)", "attribute_id": attr_option.id})
    val_bodyonly = AttrVal.search([("name", "=", "Chỉ Body Bông (Thêu Sầu Riêng Ở Bụng)"), ("attribute_id", "=", attr_option.id)], limit=1)
    if not val_bodyonly:
        val_bodyonly = AttrVal.create({"name": "Chỉ Body Bông (Thêu Sầu Riêng Ở Bụng)", "attribute_id": attr_option.id})
    val_outfitonly = AttrVal.search([("name", "=", "Chỉ Set Đồ Rời (Áo Khoác Zip + Quần + Thun)"), ("attribute_id", "=", attr_option.id)], limit=1)
    if not val_outfitonly:
        val_outfitonly = AttrVal.create({"name": "Chỉ Set Đồ Rời (Áo Khoác Zip + Quần + Thun)", "attribute_id": attr_option.id})

    # 4. Attribute: Card Goods Type
    attr_card_type = Attr.search([("name", "=", "Mẫu Thẻ Sưu Tầm")], limit=1)
    if not attr_card_type:
        attr_card_type = Attr.create({
            "name": "Mẫu Thẻ Sưu Tầm",
            "display_type": "select",
            "create_variant": "always",
        })
    val_card_regular = AttrVal.search([("name", "=", "Card Bo Góc Thường (Đồng Phục UA)"), ("attribute_id", "=", attr_card_type.id)], limit=1)
    if not val_card_regular:
        val_card_regular = AttrVal.create({"name": "Card Bo Góc Thường (Đồng Phục UA)", "attribute_id": attr_card_type.id})
    val_card_holo = AttrVal.search([("name", "=", "Card Laser Hologram Phủ Nhũ Bạc Hiếm (85k)"), ("attribute_id", "=", attr_card_type.id)], limit=1)
    if not val_card_holo:
        val_card_holo = AttrVal.create({"name": "Card Laser Hologram Phủ Nhũ Bạc Hiếm (85k)", "attribute_id": attr_card_type.id})
    val_card_special = AttrVal.search([("name", "=", "Set 2 Card Todoroki Đặc Biệt Kèm Khung (120k)"), ("attribute_id", "=", attr_card_type.id)], limit=1)
    if not val_card_special:
        val_card_special = AttrVal.create({"name": "Set 2 Card Todoroki Đặc Biệt Kèm Khung (120k)", "attribute_id": attr_card_type.id})

    print("\n=== SEEDING PRODUCTS ===")
    Prod = env["product.template"]

    img_doll_full = read_img_base64("bakugo_doll_fullset.jpg")
    img_doll_body = read_img_base64("bakugo_doll_body.jpg")
    img_poster = read_img_base64("bakugo_poster.jpg")
    img_goods = read_img_base64("todoroki_goods_collection.jpg")

    # PRODUCT 1: Bakugo Cotton Doll 20cm
    prod_doll = Prod.search([("name", "ilike", "Doll Bông Bakugo")], limit=1)
    doll_vals = {
        "name": "Búp Bê Bông Cotton Doll 20cm Bakugo Katsuki (Tóc Xù Kèm Outfit Sporty)",
        "list_price": 380000.0,
        "public_categ_ids": [Command.set([cat_records["doll"].id, parent_cat.id])],
        "is_published": True,
        "sale_ok": True,
        "image_1920": img_doll_full,
        "description_sale": "Búp bê bông Cotton Doll 20cm nhân vật Bakugo Katsuki (My Hero Academia). Tóc bông xù vàng bồng bềnh, mắt đỏ thêu xếch cá tính, bụng thêu icon sầu riêng tức giận. Có tùy chọn mua Fullset hoặc mua lẻ Body / Outfit đồ thay thế.",
        "attribute_line_ids": [
            Command.create({
                "attribute_id": attr_series.id,
                "value_ids": [Command.set([val_mha.id])],
            }),
            Command.create({
                "attribute_id": attr_char.id,
                "value_ids": [Command.set([val_baku.id])],
            }),
            Command.create({
                "attribute_id": attr_option.id,
                "value_ids": [Command.set([val_fullset.id, val_bodyonly.id, val_outfitonly.id])],
            }),
        ],
    }
    if not prod_doll:
        prod_doll = Prod.create(doll_vals)
        print(f"Created Product 1: {prod_doll.name} (ID: {prod_doll.id})")
    else:
        prod_doll.write({
            "image_1920": img_doll_full,
            "list_price": 380000.0,
            "is_published": True,
        })
        print(f"Updated Product 1: {prod_doll.name}")

    # Set price extra on variants for Product 1
    for ptav in prod_doll.attribute_line_ids.filtered(lambda l: l.attribute_id == attr_option).product_template_value_ids:
        if ptav.product_attribute_value_id == val_bodyonly:
            ptav.price_extra = -100000.0  # 280k
        elif ptav.product_attribute_value_id == val_outfitonly:
            ptav.price_extra = -260000.0  # 120k
        elif ptav.product_attribute_value_id == val_fullset:
            ptav.price_extra = 0.0  # 380k

    # PRODUCT 2: Todoroki Photocard Collection
    prod_cards = Prod.search([("name", "ilike", "Card Bo Góc Todoroki")], limit=1)
    card_vals = {
        "name": "Bộ Sưu Tập Card Bo Góc & Photocards Todoroki Shoto (My Hero Academia)",
        "list_price": 20000.0,
        "public_categ_ids": [Command.set([cat_records["card"].id, parent_cat.id])],
        "is_published": True,
        "sale_ok": True,
        "image_1920": img_goods,
        "description_sale": "Card bo góc sưu tầm chính hãng & fanmerch chất lượng cao nhân vật Todoroki Shoto. Cán màng bảo vệ bóng gương chống trầy xước, tùy chọn phiên bản Hologram ánh bạc lấp lánh.",
        "attribute_line_ids": [
            Command.create({
                "attribute_id": attr_series.id,
                "value_ids": [Command.set([val_mha.id])],
            }),
            Command.create({
                "attribute_id": attr_char.id,
                "value_ids": [Command.set([val_todo.id])],
            }),
            Command.create({
                "attribute_id": attr_card_type.id,
                "value_ids": [Command.set([val_card_regular.id, val_card_holo.id, val_card_special.id])],
            }),
        ],
    }
    if not prod_cards:
        prod_cards = Prod.create(card_vals)
        print(f"Created Product 2: {prod_cards.name} (ID: {prod_cards.id})")
    else:
        prod_cards.write({"image_1920": img_goods, "is_published": True})
        print(f"Updated Product 2: {prod_cards.name}")

    # Set price extra for cards
    for ptav in prod_cards.attribute_line_ids.filtered(lambda l: l.attribute_id == attr_card_type).product_template_value_ids:
        if ptav.product_attribute_value_id == val_card_holo:
            ptav.price_extra = 65000.0  # 20k + 65k = 85k
        elif ptav.product_attribute_value_id == val_card_special:
            ptav.price_extra = 100000.0  # 20k + 100k = 120k

    # PRODUCT 3: Huy Hiệu Can Badge Todoroki Shoto
    prod_badge = Prod.search([("name", "ilike", "Huy Hiệu Kim Loại Can Badge Todoroki")], limit=1)
    badge_vals = {
        "name": "Huy Hiệu Kim Loại Can Badge Todoroki Shoto 58mm (Phủ Kim Tuyến / Dạ Quang)",
        "list_price": 25000.0,
        "public_categ_ids": [Command.set([cat_records["badge"].id, parent_cat.id])],
        "is_published": True,
        "sale_ok": True,
        "image_1920": img_goods,
        "description_sale": "Huy hiệu tròn 58mm mặt kim loại cao cấp ghim cài balo, phủ kim tuyến lấp lánh ánh kim sa, hình in sắc nét chuẩn animation.",
        "attribute_line_ids": [
            Command.create({
                "attribute_id": attr_series.id,
                "value_ids": [Command.set([val_mha.id])],
            }),
            Command.create({
                "attribute_id": attr_char.id,
                "value_ids": [Command.set([val_todo.id])],
            }),
        ],
    }
    if not prod_badge:
        prod_badge = Prod.create(badge_vals)
        print(f"Created Product 3: {prod_badge.name} (ID: {prod_badge.id})")
    else:
        prod_badge.write({"image_1920": img_goods, "is_published": True})

    # PRODUCT 4: Mochi Bông Tròn Todoroki 10cm
    prod_mochi = Prod.search([("name", "ilike", "Mochi Kororin Bông Tròn Todoroki")], limit=1)
    mochi_vals = {
        "name": "Mochi Kororin Bông Tròn Todoroki Shoto Mini 10cm (Cục Bông Ú Treo Balo)",
        "list_price": 130000.0,
        "public_categ_ids": [Command.set([cat_records["mochi"].id, parent_cat.id])],
        "is_published": True,
        "sale_ok": True,
        "image_1920": img_goods,
        "description_sale": "Nuigurumi cục bông tròn ú Mochi Kororin 10cm Todoroki Shoto. Chất liệu vải nhung nỉ mềm mịn bóp cực đã tay, kèm dây treo tiện lợi mang đi học, đi chơi.",
        "attribute_line_ids": [
            Command.create({
                "attribute_id": attr_series.id,
                "value_ids": [Command.set([val_mha.id])],
            }),
            Command.create({
                "attribute_id": attr_char.id,
                "value_ids": [Command.set([val_todo.id])],
            }),
        ],
    }
    if not prod_mochi:
        prod_mochi = Prod.create(mochi_vals)
        print(f"Created Product 4: {prod_mochi.name} (ID: {prod_mochi.id})")
    else:
        prod_mochi.write({"image_1920": img_goods, "is_published": True})

    # PRODUCT 5: Tranh Ký Shikishi / Poster Bakugo Katsuki
    prod_poster = Prod.search([("name", "ilike", "Tranh Ký Shikishi Bakugo")], limit=1)
    poster_vals = {
        "name": "Tranh Ký Shikishi Viền Vàng Bakugo Katsuki (Awakening Explosion Edition)",
        "list_price": 65000.0,
        "public_categ_ids": [Command.set([cat_records["poster"].id, parent_cat.id])],
        "is_published": True,
        "sale_ok": True,
        "image_1920": img_poster,
        "description_sale": "Tranh Shikishi bìa cứng ép viền nhũ vàng sang trọng, in art gốc cảnh chiến đấu bùng nổ của Bakugo Katsuki. Thích hợp trưng bày bàn học, kệ sách hoặc góc sưu tầm anime.",
        "attribute_line_ids": [
            Command.create({
                "attribute_id": attr_series.id,
                "value_ids": [Command.set([val_mha.id])],
            }),
            Command.create({
                "attribute_id": attr_char.id,
                "value_ids": [Command.set([val_baku.id])],
            }),
        ],
    }
    if not prod_poster:
        prod_poster = Prod.create(poster_vals)
        print(f"Created Product 5: {prod_poster.name} (ID: {prod_poster.id})")
    else:
        prod_poster.write({"image_1920": img_poster, "is_published": True})

    cr.commit()
    print("\n=== ALL ANIME GOODS PRODUCTS SEEDED SUCCESSFULLY! ===")
