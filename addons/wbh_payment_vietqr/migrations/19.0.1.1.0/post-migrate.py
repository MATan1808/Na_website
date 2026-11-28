# -*- coding: utf-8 -*-
def migrate(cr, version):
    """Đảm bảo VietQR luôn enabled/published và tắt COD trên nâng cấp lên 19.0.1.1.0."""
    if not version:
        return
    cr.execute("""
        UPDATE payment_method
           SET active = TRUE
         WHERE id IN (
             SELECT res_id FROM ir_model_data
              WHERE module = 'wbh_payment_vietqr'
                AND model = 'payment.method'
                AND name = 'payment_method_vietqr'
         )
    """)
    cr.execute("""
        UPDATE payment_provider
           SET state = 'enabled',
               is_published = TRUE
         WHERE id IN (
             SELECT res_id FROM ir_model_data
              WHERE module = 'wbh_payment_vietqr'
                AND model = 'payment.provider'
                AND name = 'payment_provider_vietqr'
         )
    """)
    cr.execute("""
        INSERT INTO payment_provider_payment_method_rel (payment_provider_id, payment_method_id)
        SELECT pp.res_id, pm.res_id
          FROM ir_model_data pp, ir_model_data pm
         WHERE pp.module = 'wbh_payment_vietqr' AND pp.model = 'payment.provider' AND pp.name = 'payment_provider_vietqr'
           AND pm.module = 'wbh_payment_vietqr' AND pm.model = 'payment.method' AND pm.name = 'payment_method_vietqr'
        ON CONFLICT DO NOTHING
    """)
    cr.execute("""
        UPDATE payment_provider
           SET state = 'disabled',
               is_published = FALSE
         WHERE id IN (
             SELECT res_id FROM ir_model_data
              WHERE module = 'wbh_payment_vietqr'
                AND model = 'payment.provider'
                AND name = 'payment_provider_cod'
         )
    """)
    cr.execute("""
        UPDATE payment_method
           SET active = FALSE
         WHERE id IN (
             SELECT res_id FROM ir_model_data
              WHERE module = 'wbh_payment_vietqr'
                AND model = 'payment.method'
                AND name = 'payment_method_cod'
         )
    """)
