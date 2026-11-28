#!/usr/bin/env bash
set -euo pipefail

DB_NAME="${1:-web_ban_hang_dev}"

echo "=== [1/4] Keo code moi nhat tu GitHub (origin/main) ==="
git pull origin main

echo "=== [2/4] Nang cap 4 module Odoo 19 Community ($DB_NAME) ==="
docker compose exec -T odoo odoo -c /etc/odoo/odoo.conf -d "$DB_NAME" \
  -u wbh_core,theme_gift_store,wbh_delivery_vn,wbh_payment_vietqr \
  --stop-after-init

echo "=== [3/4] Dong bo du lieu DB, logo/favicon moi & xoa cache assets ==="
docker compose exec -T odoo odoo shell -c /etc/odoo/odoo.conf -d "$DB_NAME" --no-http \
  < addons/wbh_core/scripts/apply_cr_manhdaodao.py

echo "=== [4/4] Khoi dong lai Odoo va kiem tra live ==="
docker compose restart odoo
sleep 5
curl -fsSI "http://localhost:${ODOO_PORT:-1901}/theme_gift_store/static/src/img/brand_logo_dark.jpg" | head -n 1
curl -fsS "http://localhost:${ODOO_PORT:-1901}/" | grep -q "Tiền trao tay" && echo "LIVE_VERIFY=OK (Giao dien moi da len live!)"
