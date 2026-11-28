#!/usr/bin/env bash
set -eo pipefail

DB_NAME="${1:-web_ban_hang_dev}"
PORT="${ODOO_PORT:-1901}"

# Tu dong nhan dien docker compose hoac docker-compose
if docker compose version >/dev/null 2>&1; then
  DC="docker compose"
elif docker-compose version >/dev/null 2>&1; then
  DC="docker-compose"
else
  DC=""
fi

echo "=== [1/4] Keo code moi nhat tu GitHub (origin/main) ==="
git pull origin main

echo "=== [2/4] Nang cap 4 module Odoo 19 Community ($DB_NAME) ==="
if [ -n "$DC" ]; then
  $DC exec -T odoo odoo -c /etc/odoo/odoo.conf -d "$DB_NAME" \
    -u wbh_core,theme_gift_store,wbh_delivery_vn,wbh_payment_vietqr \
    --stop-after-init
else
  docker exec web-ban-hang-app odoo -c /etc/odoo/odoo.conf -d "$DB_NAME" \
    -u wbh_core,theme_gift_store,wbh_delivery_vn,wbh_payment_vietqr \
    --stop-after-init
fi

echo "=== [3/4] Dong bo du lieu DB, logo/favicon moi & xoa cache assets ==="
if [ -n "$DC" ]; then
  $DC exec -T odoo python3 /mnt/extra-addons/wbh_core/scripts/apply_cr_manhdaodao.py || \
  $DC exec -T odoo odoo shell -c /etc/odoo/odoo.conf -d "$DB_NAME" --no-http \
    < addons/wbh_core/scripts/apply_cr_manhdaodao.py
else
  docker exec web-ban-hang-app python3 /mnt/extra-addons/wbh_core/scripts/apply_cr_manhdaodao.py
fi

echo "=== [4/4] Khoi dong lai Odoo va kiem tra live ==="
if [ -n "$DC" ]; then
  $DC restart odoo
else
  docker restart web-ban-hang-app
fi

echo "Dang doi Odoo san sang (toi da 30 giay)..."
for i in {1..30}; do
  if curl -fsS "http://localhost:${PORT}/" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

if curl -fsS "http://localhost:${PORT}/" 2>/dev/null | grep -q "Tiền trao tay"; then
  echo ">>> LIVE_VERIFY=OK: Giao dien moi Manh Dao Dao da cap nhat thanh cong tren server!"
else
  echo ">>> Odoo da khoi dong xong. Vui long mo trinh duyet va tai lai trang web."
fi

