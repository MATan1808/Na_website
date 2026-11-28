# -*- coding: utf-8 -*-
def migrate(cr, version):
    """Tắt 2 phương thức vận chuyển cũ, bật ĐVVC VIETTEL POST và cập nhật vùng miền tỉnh mẫu."""
    if not version:
        return
    cr.execute("""
        UPDATE delivery_carrier
           SET is_published = FALSE
         WHERE id IN (
             SELECT res_id FROM ir_model_data
              WHERE module = 'wbh_delivery_vn'
                AND model = 'delivery.carrier'
                AND name IN ('carrier_wbh_standard', 'carrier_wbh_hold_order', 'carrier_wbh_ghn')
         )
    """)
    cr.execute("""
        UPDATE delivery_carrier
           SET is_published = TRUE,
               allow_cash_on_delivery = FALSE
         WHERE id IN (
             SELECT res_id FROM ir_model_data
              WHERE module = 'wbh_delivery_vn'
                AND model = 'delivery.carrier'
                AND name = 'carrier_wbh_viettel_post'
         )
    """)
    region_map = {
        'HCM': 'south',
        'CT': 'south',
        'DN': 'central',
        'HN': 'north',
        'HP': 'north',
    }
    for code, region in region_map.items():
        cr.execute(
            "UPDATE wbh_vn_province SET wbh_region = %s WHERE code = %s",
            (region, code),
        )
