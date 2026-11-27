# Chỉ Dẫn Cục Bộ Dự Án — `web_ban_hang` (AIaC Cấp 1 — Thuần Odoo 19.0 Community)

> File cấu hình **Cấp 1 (Project Local)** do AIaC 3.0 quản lý cho dự án `F:\BACKUP_LINUX\web_ban_hang`.  
> Kế thừa đầy đủ Global `CLAUDE.md` và kỹ năng chuyên sâu **`360-odoo`** tại `F:\BACKUP_LINUX\aiac\360org\plugins\360-odoo\prompts\SKILL.md` (qua symlink `C:\Users\ADMIN\.claude\360org -> F:\BACKUP_LINUX\aiac\360org`). Không lặp lại hay ghi đè các luật global; chỉ ghi nhận ràng buộc đặc thù của dự án này.

---

## 1. Năm Quyết Định Cứng Đã Chốt Với Sếp

1. **100% Odoo `19.0` Community (`LGPL-3`, miễn phí vĩnh viễn)**:
   - **CẤM TUYỆT ĐỐI** khai báo `depends`, kế thừa model/view hoặc import bất kỳ module Enterprise nào (`*_enterprise`, `web_enterprise`, `account_accountant`, `crm_enterprise`, `mail_enterprise`...).
   - Mọi custom module bắt buộc khai báo `'license': 'LGPL-3'` và tương thích 100% cả Odoo 19.0 Community thuần lẫn Enterprise.
2. **Tách riêng hoàn toàn Tài khoản khách hàng & Tích điểm Loyalty theo từng thương hiệu**:
   - Bắt buộc bật `specific_user_account=True` trên cả 2 website (`website_gift_store` cho Web 1 Quà tặng và `website_fashion_store` cho Web 2 Thời trang); mọi chương trình Loyalty/Voucher tách riêng theo `website_id`.
3. **Thanh toán & Vận chuyển VN ưu tiên miễn phí, lâu dài**:
   - **VietQR (`wbh_payment_vietqr`)**: Tự sinh QR chuẩn **EMVCo / Napas 247** offline ngay trong Odoo (miễn phí 100%, mọi ngân hàng VN) + Adapter Webhook đối soát tự động mặc định **SePay Free** (mở interface cho PayOS/Casso).
   - **Vận chuyển (`wbh_delivery_vn`)**: Hỗ trợ sẵn Ship nội bộ/Đồng giá + ưu tiên tích hợp **GHN** trước (API miễn phí 100%, có Sandbox), mở rộng GHTK & Viettel Post.
4. **Hạ tầng Docker di động 100% trong repo Git (`Windows ➜ Local Server`)**:
   - Đóng gói `docker-compose.yml`, `config/odoo.conf`, `.env.example` ngay tại root `F:\BACKUP_LINUX\web_ban_hang\`.
   - Image mặc định di động: `odoo:19.0` Community + `postgres:15-bookworm` (hỗ trợ tùy chọn `360ai/postgres:15-ai` kèm `pgvector` trên Local Server).
   - Chạy tạm trên máy Windows hiện tại (data đặt trên ổ `F:\` còn `227.22 GB`), khi Local Server ở nhà hoạt động lại chỉ cần `git pull` + `docker compose up -d` + restore DB/filestore.
5. **Lộ trình ưu tiên 4 Giai đoạn (`docs/ROADMAP_TIEN_DO.md`)**:
   - **Giai đoạn 1 — Website & CRUD Sản phẩm**: Hoàn thiện nền tảng Docker + `wbh_core` + `theme_gift_store` + `theme_fashion_store` để Thêm/Xem/Sửa/Xóa & Lưu trữ sản phẩm nhanh gọn.
   - **Giai đoạn 2 — Bộ lọc Động 100% (CẤM HARDCODE)**: Lọc theo Khoảng giá, Nhân vật, Bộ Anime, Phân loại (`Doll`/`Off`) và Nhãn trạng thái/giảm giá (`product.tag`) phải tự động sinh từ dữ liệu người quản trị gắn lúc thêm/sửa sản phẩm.
   - **Giai đoạn 3 — Tương tác 3 Kênh**: Tư vấn & chốt đơn trực tiếp qua 3 kênh đồng bộ: **Web Livechat** + **Facebook Messenger** + **Zalo** (cấu hình động trong Backend).
   - **Giai đoạn 4 — Thanh toán & Vận chuyển**: **`wbh_payment_vietqr`** (VietQR EMVCo + SePay Free + COD/đặt cọc) + **`wbh_delivery_vn`** (Ship đồng giá/Freeship/Gom đơn + GHN ➜ GHTK & Viettel Post).

---

## 2. Quy Tắc Kỹ Thuật Bắt Buộc (Odoo 19.0 Community)

1. **XML Views**:
   - **Cấm tuyệt đối** `attrs=` và `states=`; dùng trực tiếp `invisible`, `readonly`, `required`.
   - Bắt buộc dùng `<list>` thay cho `<tree>`.
2. **Python ORM & Bảo mật (`Python 3.12`)**:
   - Dùng `@api.model_create_multi`, `odoo.fields.Command` (không dùng tuple x2many), `models.Constraint()` và `models.Index()`.
   - Tôn trọng `allowed_company_ids`, `website_id` và `specific_user_account=True` trên mọi luồng dữ liệu đa cửa hàng; ưu tiên toán tử `any!` / `not any!`.
   - Mọi HTML đưa vào `message_post()` bắt buộc bọc bằng `markupsafe.Markup(...)`.
   - Mọi model mới bắt buộc có đầy đủ `security/ir.model.access.csv` và `ir.rule` (đặc biệt tách dữ liệu giữa Web 1 và Web 2). Webhook thanh toán/vận chuyển bắt buộc xác thực chữ ký/token ở trust boundary.
3. **Website Theme Upgrade-Safe, Design System & `360-frontend-polish` (`OWL 2.8.4` + `Bootstrap 5.3.3` / `SCSS` + `GSAP` + `Lucide`)**:
   - **BẮT BUỘC đọc `DESIGN.md` tại thư mục gốc và kích hoạt skill `360-frontend-polish` trước khi thực hiện bất kỳ thay đổi nào liên quan đến UI, QWeb, CSS/SCSS hay Theme**.
   - Tham chiếu Design Tokens (`css/variables.css`, `css/system.css`) và bản xem trước `html/preview.html` để tái sử dụng đúng bảng màu, kiểu chữ và components của từng cửa hàng (Web 1 Quà Tặng vs Web 2 Thời Trang).
   - Dùng thống nhất **Lucide SVG** (`data-lucide`) và **GSAP + ScrollTrigger** self-hosted trong `addons/wbh_core/static/lib/` (đủ 3 chốt bảo vệ: cô lập `.wbh-store-*`, tắt khi bật Website Builder edit mode, tôn trọng `prefers-reduced-motion`); cấm inline `onclick=`, vùng chạm mobile `>= 44px`, tương phản WCAG AA `>= 4.5:1`, và chạy `F:\BACKUP_LINUX\aiac\360org\plugins\360-frontend-polish\scripts\run-impeccable-audit.ps1` kiểm định trước khi ship.
   - Mọi `website.page` bắt buộc bọc bởi `<div id="wrap" class="oe_structure oe_empty">`.
   - Mọi snippet kéo-thả bắt buộc có `o_colored_level` và `data-snippet`.
   - Tắt view core qua `data/presets.xml` (`active=False`); quản lý màu động qua `$o-color-1..5` trong `primary_variables.scss`; khai báo đúng bundles `web._assets_primary_variables`, `web.assets_frontend`, `website.assets_wysiwyg`, `web.assets_backend`.

---

## 3. Cách Ly Hạ Tầng & Quản Lý Git / `.gitignore`

- **Cô lập tuyệt đối**:
  - `CLIENT_NAME=web-ban-hang`, DB `web_ban_hang_dev` / `web_ban_hang_prod` (`DB_FILTER=^web_ban_hang.*$`), Docker volume `web_ban_hang_pgdata`, filestore/sessions riêng (`data/filestore`, `data/sessions`), port dải `1900`–`1999` (Web `1901`/`8089`, Longpolling `7089`, DB Host `51901`).
  - Tuyệt đối không dùng chung `demo-19` / `odoo19-db`, không ghi vào `F:\BACKUP_LINUX\save\dev_env\19.0\modules\default\`, không dùng dump `vuahethong_v19_prod_test.dump` và không hardcode đường dẫn Linux cũ.
- **Quy trình Tài liệu & Git**:
  - Vòng đời bắt buộc: `/idea ➜ /req ➜ /spec ➜ /plan ➜ /build ➜ /code-review ➜ /test ➜ /review ➜ /ship` (chi tiết tại `F:\BACKUP_LINUX\web_ban_hang\AGENTS.md`).
  - **Pre-Push Docs Sync**: Đồng bộ `docs/*.md`, `README.md` và changelog `__manifest__.py` trước mọi `git push`.
  - **`.gitignore` chuẩn Odoo/Docker**: Luôn ignore `.env`, `data/`, `logs/`, `*.dump`, `*.sql`, `__pycache__/`, `.venv/`; **KHÔNG ignore** `.claude/` và `.env.example`. Quét sạch secret trong `.claude/` trước khi commit.
  - **Git Attribution**: Mọi commit gắn trailer `Authored-By: 360org <support@360.org.vn>`.
  - **Zero-Bypass Promotion Pipeline**: Chỉ triển khai mã nguồn qua Git; cấm `rsync`/`scp` code vượt cấp và cấm sửa nóng trên máy chủ.
