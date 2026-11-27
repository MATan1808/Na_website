# -*- coding: utf-8 -*-
from . import models
from . import controllers


def uninstall_hook(env):
    """Khôi phục record rule mặc định của website_sale khi gỡ cài đặt wbh_core."""
    default_public_rule = env.ref(
        'website_sale.product_template_public',
        raise_if_not_found=False,
    )
    if default_public_rule:
        default_public_rule.write({'active': True})
