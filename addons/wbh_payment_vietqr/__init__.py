# -*- coding: utf-8 -*-
from . import controllers
from . import models

from odoo.addons.payment import reset_payment_provider, setup_provider


def post_init_hook(env):
    setup_provider(env, 'vietqr')
    setup_provider(env, 'wbh_cod')


def uninstall_hook(env):
    reset_payment_provider(env, 'vietqr')
    reset_payment_provider(env, 'wbh_cod')
