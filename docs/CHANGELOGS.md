# Nhật Ký Thay Đổi (CHANGELOGS) — Hệ Sinh Thái 2 Website Bán Hàng (`web_ban_hang`)

Tài liệu ghi nhận đầy đủ lịch sử thay đổi các phiên bản của dự án theo chuẩn **AIaC 3.0 (`360-odoo`)**.

> **Quy ước phiên bản**:
> - Phiên bản tổng thể dự án/tài liệu: `v<major>.<minor>.<patch>` (hiện tại `v0.3.6` — tích hợp bộ công cụ UI/UX & Animation từ kho MochiStudio: `GSAP 3.15.1`, `Lucide 1.82.0`, chuẩn audit `Impeccable` + `Front-End Checklist` + `UI UX Pro Max`).
> - Phiên bản từng custom Odoo module trong `addons/`: `v19.0.<major>.<minor>.<patch>` (đồng bộ cả trong `docs/CHANGELOGS.md` và trường `description` của từng `__manifest__.py`).
>
> **Quy ước Tag**: `[NEW]` Tính năng/tài liệu mới · `[FIX]` Sửa lỗi · `[IMPROVE]` Cải tiến · `[SECURITY]` Bảo mật · `[REFACTOR]` Tái cấu trúc · `[MIGRATE]` Nâng cấp/chuyển đổi.

---

## v0.3.6 (2026-11-27)

### Nâng Cấp UI/UX, Motion & Hệ Thống Icon Chuẩn MochiStudio (`GSAP` + `Lucide` + `Impeccable` + `Front-End Checklist`)
- `[NEW]` **Đóng gói plugin AIaC `360-frontend-polish`** tại `F:\BACKUP_LINUX\aiac\360org\plugins\360-frontend-polish\` (kèm junction `~/.claude/skills/360-frontend-polish`), hợp nhất quy chuẩn của `impeccable`, `Front-End-Checklist`, `ui-ux-pro-max-skill`, `GSAP` và `Lucide`.
- `[NEW]` **Self-hosted `GSAP v3.15.1` (kèm `ScrollTrigger`) & `Lucide v1.82.0`** trong `addons/wbh_core/static/lib/` (`wbh_core` `v19.0.1.1.0`), nạp qua `web.assets_frontend` không phụ thuộc CDN bên ngoài.
- `[IMPROVE]` **Nâng cấp `theme_gift_store` (`v19.0.1.1.0`) & `theme_fashion_store` (`v19.0.1.1.0`)**:
  - Bổ sung `theme_gift_motion.js` và `theme_fashion_motion.js` với 3 chốt bảo vệ: cô lập Multi-Website, an toàn khi chỉnh sửa trong Website Builder, và tuân thủ `prefers-reduced-motion`.
  - Nâng cấp toàn bộ icon storefront sang **Lucide SVG** đồng bộ theo cá tính thương hiệu (`stroke-width: 1.9` cho Web 1, `1.5` cho Web 2).
  - Khắc phục các lỗi do `npx impeccable detect` phát hiện: nâng tương phản topbar/CTA đạt WCAG AA (`>= 4.5:1`), gỡ bỏ `side-tab`, thay inline `onclick=` / `style=` bằng `data-wbh-trigger-cart` + `IntersectionObserver`, bổ sung `:focus-visible`, `preconnect` Google Fonts, `<meta name="theme-color">` và hover scale `1.04` chuẩn `DESIGN.md`.
- `[IMPROVE]` **Cập nhật `html/preview.html`, `css/system.css` và `DESIGN.md`**: Nhúng trực tiếp Lucide + GSAP chạy offline ngay khi mở file xem trước.

---

## v0.3.5 (2026-11-27)

### Khắc Phục Lặp 2 Footer, Nút Cuộn Đầu Trang Bị Che & Chuẩn Hóa Bản Quyền
- `[FIX]` **Triệt tiêu lỗi lặp 2 footer** (`theme_gift_store` `v19.0.1.0.2`, `theme_fashion_store` `v19.0.1.0.1`): Tắt `website.footer_custom` (`active=False` trong `presets.xml` và `disable_view` trong `theme.utils`) để không hiển thị khối footer tiếng Anh mẫu của Odoo phía trên footer thương hiệu.
- `[FIX]` **Sửa nút cuộn tròn `#o_footer_scrolltop_wrapper` bị che khuất nửa dưới trên mobile**: Đưa `.wbh-gift-footer-band` và `.wbh-fashion-footer-band` lên trước `//div[@id='footer']` và nâng `z-index: 10` kèm khoảng đệm `padding-top: 1.75rem` cho `.o_footer_copyright > .container`.
- `[IMPROVE]` Thay thế chuỗi bản quyền mẫu `Copyright © Company name` bằng `Bản quyền © <website.name>` tự động theo từng website.

---

## v0.3.4 (2026-11-27)

### Nhận Diện Thương Hiệu Manh Dao Dao, Chuẩn Hóa Docker Named Volumes & Vá Quyền Tồn Kho `/shop`
- `[NEW]` **Bộ nhận diện thương hiệu Manh Dao Dao Anime Goods Shop** trong `addons/theme_gift_store/static/src/img/`:
  - `logo.png` (`1020x280` px RGBA): Logo ngang chuẩn eCommerce tách sạch nền caro, kết hợp mascot Anime & lựu đạn/tia nổ cùng typography `MANH DAO DAO — ANIME GOODS SHOP`.
  - `logo_emblem_transparent.png` (`931x945` px RGBA): Bản tròn nguyên bản tách nền trong suốt 100% dùng cho OpenGraph/chia sẻ MXH.
  - `favicon.ico` (`32x32` & `64x64` px): Icon cận cảnh nhân vật sắc nét trên tab trình duyệt.
- `[IMPROVE]` **Tối ưu CSS Logo Navbar** trong `addons/theme_gift_store/static/src/scss/theme_gift.scss`: Nâng chiều cao logo lên `60px` trên desktop (`48px` khi cuộn, `46px` trên mobile) bọc chặt trong `.wbh-store-gift`.
- `[FIX]` **Sửa tận gốc lỗi `403 Forbidden` khi khách vãng lai xem `/shop`**: Bổ sung `compute_sudo=True` cho trường `wbh_is_low_stock` trong `wbh_core` (`v19.0.1.0.1`) và đọc `product.sudo().qty_available` trong `theme_gift_store` (`v19.0.1.0.1`), không cần mở quyền đọc trực tiếp `stock.move`/`stock.warehouse`.
- `[IMPROVE]` **Chuẩn hóa Docker Named Volumes** trong `docker-compose.yml`: Chuyển `filestore` và `sessions` sang `web_ban_hang_filestore` và `web_ban_hang_sessions` để tương thích mọi filesystem trên Linux Local Server (kể cả ổ đĩa mount NTFS/FUSE) và Windows.

---

## v0.3.3 (2026-11-27)

### Design System & Nạp Bộ Sản Phẩm Anime Goods & Búp Bê Cotton Doll 20cm
- `[NEW]` **Hệ Thống Thiết Kế Chuẩn**: Tạo `DESIGN.md`, `css/variables.css`, `css/system.css` và trang xem trước trực quan `html/preview.html`.
- `[NEW]` **Nạp Dòng Sản Phẩm Anime Goods & Cotton Doll 20cm Thực Tế**:
  - `Doll Bông Cotton Doll 20cm Bakugo Katsuki (Tóc Xù Kèm Outfit Sporty)`: Biến thể Fullset 380k, Body trần thêu sầu riêng 280k, Outfit rời 120k.
  - `Bộ Sưu Tập Card Bo Góc & Photocards Todoroki Shoto`: Card thường 20k - 40k, Hologram bạc hiếm 85k, Set 2 card kèm khung 120k.
  - `Huy Hiệu Kim Loại Can Badge Todoroki Shoto 58mm`: Phủ kim tuyến / dạ quang (20k - 40k).
  - `Mochi Kororin Bông Tròn Todoroki Shoto 10cm`: Nuigurumi ú mini treo balo (130k).
  - `Tranh Ký Shikishi Viền Vàng Bakugo Katsuki`: Awakening Explosion Special (65k).
- `[IMPROVE]` Cập nhật thanh danh mục và Hero Banner trang chủ Web 1 dẫn trực tiếp vào bộ sưu tập Anime Doll & Goods.

---

## v0.3.2 (2026-11-27)

### Mở Rộng Ứng Dụng E-Commerce & Chăm Sóc Khách Hàng Odoo 19.0
- `[NEW]` **Cài đặt mở rộng 5 cụm module nghiệp vụ đắc lực**:
  - `loyalty` & `website_sale_loyalty`: Quản lý chương trình khuyến mãi, tạo mã giảm giá voucher (`VOUCHER50K`, `FREESHIP`), thẻ quà tặng, tích điểm thành viên và áp dụng trực tiếp trong giỏ hàng web.
  - `im_livechat` & `website_livechat`: Khung chat trực tuyến nổi góc màn hình hỗ trợ tư vấn tức thời khách chọn quà tặng và chọn size quần áo.
  - `purchase`: Quản lý đơn mua hàng, theo dõi đơn nhập hàng và công nợ với xưởng sản xuất gấu bông, móc khóa và thời trang.
  - `website_blog`: Chuyên mục Blog tin tức, cẩm nang phối đồ và gợi ý quà tặng chuẩn SEO.
  - `mass_mailing`: Tiếp thị Email tự động, gửi email chăm sóc khách hàng và nhắc giỏ hàng bỏ quên.
  - `crm`: Quản lý khách hàng tiềm năng và chuyển đổi cơ hội kinh doanh.
- `[IMPROVE]` Khởi tạo sẵn 11 sản phẩm mẫu đa dạng có đầy đủ thuộc tính biến thể Màu sắc (Color Swatch) và Size trên cả 2 website.

---

## v0.3.0 (2026-11-26)

### Hoàn Tất `/build` & Cổng `/code-review` Vòng 2 — Milestone 1 (Catalog-First)
Toàn bộ **49 file mới** của Milestone 1 đã vượt qua **100% cổng `/code-review`** (`py_compile` 15/15 PASS, `ET.parse` 23/23 PASS, 100% **Odoo 19.0 Community `LGPL-3`**, 0% phụ thuộc Enterprise, 0% anti-pattern, cô lập tuyệt đối Multi-Website, đủ 7/7 extension slots cho Milestone 2 & 3, sạch secret):

- `[NEW]` **Hạ tầng Docker di động (3 file)**:
  - `F:\BACKUP_LINUX\web_ban_hang\docker-compose.yml`: 2 dịch vụ `db` (`postgres:15-bookworm`) + `odoo` (`odoo:19.0`), tên container `${CLIENT_NAME:-web-ban-hang}-db`/`-app`, healthcheck đầy đủ, bind `127.0.0.1:51901:5432`, mount tương đối `./addons`, `./config/odoo.conf:ro`, `./data/filestore`, `./data/sessions`, volume `web_ban_hang_pgdata` và network cô lập `web_ban_hang_net`.
  - `F:\BACKUP_LINUX\web_ban_hang\.env.example`: đủ 11/11 biến môi trường (`CLIENT_NAME`, `ODOO_IMAGE`, `POSTGRES_IMAGE`, `ODOO_PORT=1901`, `LONGPOLLING_PORT=7089`, `DB_PORT=51901`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `ODOO_MASTER_PASSWORD`, `DB_NAME`, `DB_FILTER`), 100% placeholder sạch secret.
  - `F:\BACKUP_LINUX\web_ban_hang\config\odoo.conf`: đủ 13/13 tùy chọn `[options]` chuẩn Odoo 19.0, định dạng LF-only tương thích cả Windows Docker Desktop (WSL2) và Linux Local Server.
- `[NEW]` **Module `addons/wbh_core/` (`v19.0.1.0.0`, 15 file, `LGPL-3`)**:
  - Khởi tạo 2 Website độc lập (`website_gift_store`, `website_fashion_store`) với `specific_user_account=True` tách riêng tài khoản khách hàng.
  - Mở rộng `website` và `product.template` chuẩn Odoo 19.0 (`models.Constraint`, `models.Index`, `@api.model_create_multi`, `odoo.fields.Command`), tự động đồng bộ `website_id` theo `wbh_store_scope` và lọc sản phẩm sắp hết hàng.
  - Phân quyền chuẩn Odoo 19.0 dùng `res.groups.privilege` (`res_groups_privilege_wbh`), `security/ir.model.access.csv`, `ir.rule` cô lập Public/Portal theo website & công ty (kèm `uninstall_hook` khôi phục rule gốc an toàn).
  - Dữ liệu mẫu `noupdate="1"` gồm cây danh mục cho 2 cửa hàng và bộ 7 thuộc tính biến thể chuẩn; bộ views backend tối ưu upload sản phẩm nhanh, menu *2 Cửa Hàng (WBH)* và bộ unit test `tests/test_wbh_core.py`.
- `[NEW]` **Module `addons/theme_gift_store/` (`v19.0.1.0.0`, 16 file, `LGPL-3`, Upgrade-Safe Odoo 19.0)**:
  - Cô lập tuyệt đối Multi-Website bằng class `.wbh-store-gift` và điều kiện `website.wbh_store_type == 'gift'` (không ghi đè sang Web 2).
  - Bảng màu ấm `$o-color-1..5`, font tiếng Việt `Be Vietnam Pro` / `Quicksand`, khai báo asset bundles chuẩn Odoo 19.0 (`web._assets_primary_variables`, `web.assets_frontend`, `website.assets_wysiwyg`).
  - `data/presets.xml` (`noupdate="1"`) tự động gán `theme_id` & tỷ lệ ảnh `1_1`, kích hoạt tự động `_theme_load` / `theme.utils._theme_gift_store_post_copy` cho Web 1; trang chủ & 3 Building Blocks kéo-thả (`s_gift_hero`, `s_gift_occasion_bar`, `s_gift_featured_grid`), trang Shop/Product tối ưu mobile và đủ 3 extension slots (`wbh_gift_options_slot`, `wbh_gift_size_compare_slot`, `wbh_flash_sale_banner_slot`).
- `[NEW]` **Module `addons/theme_fashion_store/` (`v19.0.1.0.0`, 15 file, `LGPL-3`, Upgrade-Safe Odoo 19.0)**:
  - Cô lập tuyệt đối Multi-Website bằng class `.wbh-store-fashion` và điều kiện `website.wbh_store_type == 'fashion'` (không ghi đè sang Web 1).
  - Bảng màu tối giản Editorial `$o-color-1..5`, font tiếng Việt `Plus Jakarta Sans` / `Inter`, khai báo asset bundles chuẩn Odoo 19.0 (`web._assets_primary_variables`, `web.assets_frontend`, `website.assets_wysiwyg`).
  - `data/presets.xml` (`noupdate="1"`) tự động gán `theme_id` & `_theme_load` cho Web 2; trang chủ & 3 Building Blocks kéo-thả (`s_fashion_lookbook_hero`, `s_fashion_category_strip`, `s_fashion_editorial_grid`), trang Shop/Product khung ảnh dọc `3:4`, Color Swatch, Size pills dễ chạm mobile và đủ 4 extension slots (`wbh_fashion_size_advisor_slot`, `wbh_fashion_video_gallery_slot`, `wbh_fashion_shop_the_look_slot`, `wbh_flash_sale_banner_slot`).
- `[IMPROVE]` Đồng bộ Pre-Ship tài liệu khung AIaC (`README.md`, `AGENTS.md`, `.claude/CLAUDE.md`, `docs/CHANGELOGS.md`) và chuẩn hóa tên asset bundle editor từ `web_editor.assets_wysiwyg` sang `website.assets_wysiwyg` đúng thực tế mã nguồn Odoo 19.0.

---

## v0.2.0 (2026-11-25)

### Chốt 5 Quyết Định Kiến Trúc, Lộ Trình Catalog-First & Hoàn Tất Bộ Tài Liệu `/spec` Milestone 1
- `[IMPROVE]` Chốt toàn bộ 5 quyết định kiến trúc & vận hành cùng Sếp:
  1. **100% Odoo 19.0 Community (`LGPL-3`, miễn phí vĩnh viễn)** — cấm tuyệt đối phụ thuộc bất kỳ module Enterprise (`*_enterprise`, `account_accountant`...) nào.
  2. **Tách riêng hoàn toàn Tài khoản khách hàng & Tích điểm Loyalty theo từng thương hiệu** (`specific_user_account=True`, tách chương trình Loyalty theo `website_id`).
  3. **Thanh toán & Vận chuyển VN ưu tiên miễn phí, lâu dài**: VietQR tự sinh chuẩn **EMVCo / Napas 247** offline ngay trong Odoo + Adapter Webhook **SePay Free** (mở rộng PayOS/Casso); Vận chuyển Ship nội bộ/Đồng giá + ưu tiên **GHN** trước (API miễn phí 100%, có Sandbox), mở rộng GHTK & Viettel Post.
  4. **Hạ tầng Docker di động 100% trong repo Git**: chạy tạm trên máy Windows hiện tại (data trên ổ `F:\`), sẵn sàng chuyển sang Local Server ở nhà qua `git pull` + `docker compose up -d` + restore DB/filestore.
  5. **Lộ trình 3 Milestone theo hướng Catalog-First**: **Milestone 1** (Docker di động + `wbh_core` + `theme_gift_store` + `theme_fashion_store` để Sếp đăng nhập và up sản phẩm trước) ➜ **Milestone 2** (`wbh_gift_store` + `wbh_fashion_store`) ➜ **Milestone 3** (`wbh_payment_vietqr` + `wbh_delivery_vn` + Loyalty tách riêng & Flash Sale).
- `[NEW]` Tạo mới `F:\BACKUP_LINUX\web_ban_hang\docs\CONTEXT.md` (v1.0): bảng thuật ngữ nghiệp vụ (Domain Glossary) chuẩn `360-odoo`.
- `[NEW]` Tạo mới `F:\BACKUP_LINUX\web_ban_hang\docs\SPEC.md` (v1.0): đặc tả kỹ thuật chi tiết Milestone 1 sẵn sàng để `/build` ngay (cấu trúc Docker di động, `wbh_core` 100% Community, `theme_gift_store` & `theme_fashion_store` chuẩn Upgrade-Safe Odoo 19.0, cùng extension points cho Milestone 2 & 3).
- `[NEW]` Tạo mới `F:\BACKUP_LINUX\web_ban_hang\docs\DEPLOY_GUIDE.md` (v1.0): hướng dẫn cài đặt & chạy Docker tạm trên Windows (dọn WSL `VCloudOdoo19`, chuyển disk image sang ổ `F:\`), hướng dẫn nhanh Sếp đăng nhập và up sản phẩm lên Web 1 & Web 2, cùng quy trình chuyển môi trường sang Local Server tuân thủ Zero-Bypass Promotion Pipeline.
- `[IMPROVE]` Cập nhật đồng bộ `F:\BACKUP_LINUX\web_ban_hang\docs\IDEA.md` (v1.2), `F:\BACKUP_LINUX\web_ban_hang\docs\ARCH.md` (v1.1) và `F:\BACKUP_LINUX\web_ban_hang\docs\REQUIREMENTS.md` (v1.1) theo 5 quyết định chốt và lộ trình 3 Milestone.
- `[REFACTOR]` Cập nhật `F:\BACKUP_LINUX\web_ban_hang\.gitignore` từ mẫu Node/Next.js sang chuẩn **Odoo 19.0 / Python / Docker** (ignore `.env`, `data/`, `logs/`, `*.dump`, `*.sql`, `__pycache__/`, `.venv/`...; **KHÔNG ignore** `.claude/` và `.env.example`).
- `[IMPROVE]` Cập nhật đồng bộ khung AIaC: `F:\BACKUP_LINUX\web_ban_hang\README.md`, `F:\BACKUP_LINUX\web_ban_hang\AGENTS.md`, `F:\BACKUP_LINUX\web_ban_hang\.claude\CLAUDE.md` và `F:\BACKUP_LINUX\web_ban_hang\.claude\settings.local.json`.

---

## v0.1.0 (2026-11-25)

### Khởi tạo khung chuẩn AIaC 3.0 & Chốt kiến trúc thuần Odoo 19.0 Multi-Website
- `[NEW]` Hoàn tất khảo sát thực tế hạ tầng máy chủ cục bộ Windows và kho Docker Odoo sẵn có tại `F:\BACKUP_LINUX\save\dev_env\19.0\` (Odoo `19.0`, Python `3.12`, OWL `2.8.4`, Bootstrap `5.3.3`, **1.474 modules** Community + Enterprise, PostgreSQL `15` với image `360ai/postgres:15-ai` kèm `pgvector`).
- `[IMPROVE]` Cập nhật tài liệu ý tưởng `F:\BACKUP_LINUX\web_ban_hang\docs\IDEA.md` (v1.1): bổ sung Quyết định Công nghệ thuần **Odoo 19.0 + PostgreSQL 15** và đánh giá tái sử dụng hạ tầng trên máy Sếp.
- `[NEW]` Khởi tạo tài liệu kiến trúc kỹ thuật `F:\BACKUP_LINUX\web_ban_hang\docs\ARCH.md` (v1.0) và tài liệu yêu cầu `F:\BACKUP_LINUX\web_ban_hang\docs\REQUIREMENTS.md` (v1.0).
- `[IMPROVE]` Cập nhật `F:\BACKUP_LINUX\web_ban_hang\README.md` và tạo mới `F:\BACKUP_LINUX\web_ban_hang\AGENTS.md`, `F:\BACKUP_LINUX\web_ban_hang\docs\CHANGELOGS.md`, `F:\BACKUP_LINUX\web_ban_hang\.claude\CLAUDE.md`, `F:\BACKUP_LINUX\web_ban_hang\.claude\settings.local.json`.

---

## Cột Mốc Dự Kiến Tiếp Theo (Roadmap)

- **`v0.3.1` (Bước `/test` ➜ `/review` ➜ `/ship` Milestone 1 trên Docker thực tế)**:
  - Chạy `docker compose up -d`, cài đặt `wbh_core`, `theme_gift_store`, `theme_fashion_store` trên DB `web_ban_hang_dev` và chạy kiểm thử `test_wbh_core.py` + kiểm tra trực tiếp 2 Storefronts (desktop & mobile) để Sếp đăng nhập up sản phẩm ngay.
- **`v0.4.0` (Milestone 2 — Storefront Features)**:
  - Xây dựng `wbh_gift_store` (gói quà + thiệp, cá nhân hóa khắc/thêu tên, so sánh kích thước, combo dịp lễ) và `wbh_fashion_store` (gợi ý size thông minh, Shop The Look, video mẫu mặc CDN, luồng đổi size Portal).
- **`v0.5.0` (Milestone 3 — VN Integrations & Growth)**:
  - Xây dựng `wbh_payment_vietqr` (EMVCo offline + SePay Free webhook), `wbh_delivery_vn` (Ship nội bộ/Đồng giá + GHN ➜ GHTK/VTP), Loyalty tách riêng từng thương hiệu, Flash Sale & `docs/AUDIT_ROADMAP.md`.
