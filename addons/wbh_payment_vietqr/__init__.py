# -*- coding: utf-8 -*-
from . import controllers
from . import models

from odoo.fields import Command
from odoo.addons.payment import reset_payment_provider, setup_provider


def post_init_hook(env):
    setup_provider(env, 'vietqr')
    setup_provider(env, 'wbh_cod')

    vietqr_method = env.ref('wbh_payment_vietqr.payment_method_vietqr', raise_if_not_found=False)
    vietqr_provider = env.ref('wbh_payment_vietqr.payment_provider_vietqr', raise_if_not_found=False)
    if vietqr_method:
        vietqr_method.sudo().write({'active': True})
    if vietqr_provider:
        vals = {
            'state': 'enabled',
            'is_published': True,
        }
        if vietqr_method and vietqr_method not in vietqr_provider.with_context(active_test=False).payment_method_ids:
            vals['payment_method_ids'] = [Command.link(vietqr_method.id)]
        vietqr_provider.sudo().write(vals)

    cod_provider = env.ref('wbh_payment_vietqr.payment_provider_cod', raise_if_not_found=False)
    cod_method = env.ref('wbh_payment_vietqr.payment_method_cod', raise_if_not_found=False)
    if cod_provider:
        cod_provider.sudo().write({'state': 'disabled', 'is_published': False})
    if cod_method:
        cod_method.sudo().write({'active': False})


def uninstall_hook(env):
    reset_payment_provider(env, 'vietqr')
    reset_payment_provider(env, 'wbh_cod')
