# AGENTS.md — Quy Chuẩn Điều Phối Multi-Agent (AIaC 3.0 & `360-odoo`)

> **Dự án**: Hệ Sinh Thái 2 Website Bán Hàng (`web_ban_hang`) — Thuần **Odoo 19.0 Community (LGPL-3) Multi-Website** + **PostgreSQL 15**  
> **Thư mục gốc dự án**: `F:\BACKUP_LINUX\web_ban_hang`  
> **Chuẩn kế thừa**: AIaC Root `F:\BACKUP_LINUX\aiac` (qua symlink `C:\Users\ADMIN\.claude\360org -> F:\BACKUP_LINUX\aiac\360org`), plugin `360-odoo` và `360-local-builder-env`.  
> **Trạng thái hiện tại (`v0.3.4`, 2026-11-27)**: Hoàn thiện bộ logo thương hiệu Manh Dao Dao, chuẩn hóa Docker Named Volumes (`web_ban_hang_filestore`, `web_ban_hang_sessions`) và vá `compute_sudo` cho `/shop` (`wbh_core` `v19.0.1.0.1`, `theme_gift_store` `v19.0.1.0.1`, `theme_fashion_store` `v19.0.1.0.0`), sẵn sàng chạy chuẩn Zero-Bypass trên Local Server.

---

## 1. Mục Tiêu, Ràng Buộc Cứng & Thứ Tự Ưu Tiên Triển Khai

Tài liệu này quy định cơ cấu vai trò, phân bổ mô hình AI, vòng đời phát triển 9 bước và các cổng kiểm soát chất lượng bắt buộc cho mọi AI Agent tham gia phát triển dự án **Hệ Sinh Thái 2 Website Bán Hàng**:

### 1.1. Luật Cứng Kiến Trúc Đã Chốt Với Sếp (KHÔNG ĐƯỢC VI PHẠM)
1. **100% Odoo 19.0 Community (`LGPL-3`, miễn phí vĩnh viễn)**:
   - **CẤM TUYỆT ĐỐI** khai báo `depends`, kế thừa view/model hay import bất kỳ module Enterprise nào (`*_enterprise`, `web_enterprise`, `account_accountant`, `crm_enterprise`, `mail_enterprise`, `sale_renting`, ...).
   - Kể cả khi máy phát triển có tham chiếu kho `F:\BACKUP_LINUX\save\dev_env\19.0\origin\addons\`, mọi custom module bắt buộc chỉ phụ thuộc module Community sạch để chạy mượt trên cả **Odoo 19.0 Community thuần** lẫn Enterprise.
2. **Tách riêng hoàn toàn Tài khoản & Tích điểm Loyalty theo từng thương hiệu**:
   - Bắt buộc cấu hình `specific_user_account=True` trên cả 2 website (`website_gift_store`, `website_fashion_store`) và tách riêng chương trình Loyalty/Voucher theo `website_id`.
3. **Thanh toán & Vận chuyển VN ưu tiên miễn phí, lâu dài**:
   - `wbh_payment_vietqr`: Tự sinh mã QR chuẩn **EMVCo / Napas 247** offline ngay trong Odoo (miễn phí 100%, mọi ngân hàng VN) + Adapter Webhook đối soát tự động mặc định **SePay Free** (mở rộng PayOS/Casso).
   - `wbh_delivery_vn`: Hỗ trợ sẵn Ship nội bộ/Đồng giá + ưu tiên **GHN** trước (API miễn phí 100%, có Sandbox), mở rộng GHTK & Viettel Post.
4. **Hạ tầng Docker di động 100% trong repo Git**:
   - Đóng gói `docker-compose.yml`, `config/odoo.conf`, `.env.example` ngay tại root repo dùng `odoo:19.0` Community + `postgres:15-bookworm` (hỗ trợ tùy chọn `360ai/postgres:15-ai`), chạy tạm trên máy Windows hiện tại (data trên ổ `F:\`) và chuyển sang Local Server ở nhà bằng `git pull` + `docker compose up -d` + restore DB/filestore.

### 1.2. Thứ Tự Ưu Tiên 3 Milestone (Catalog-First) Cho 7 Custom Modules (`addons/`)
1. **Milestone 1 — Catalog-First *(LÀM NGAY)***:
   - Hạ tầng Docker di động (`docker-compose.yml`, `config/odoo.conf`, `.env.example`)
   - `wbh_core` (Core Multi-Website tách tài khoản, danh mục/thuộc tính mẫu, form backend tối ưu up sản phẩm nhanh)
   - `theme_gift_store` (Custom Theme Upgrade-Safe Web 1 — Quà tặng)
   - `theme_fashion_store` (Custom Theme Upgrade-Safe Web 2 — Thời trang)
2. **Milestone 2 — Storefront Features *(Làm sau Milestone 1)***:
   - `wbh_gift_store` (gói quà + thiệp, cá nhân hóa khắc/thêu tên, so sánh kích thước trực quan, combo theo dịp)
   - `wbh_fashion_store` (gợi ý size thông minh, bộ lọc chuyên sâu, Shop The Look, video mẫu mặc qua R2/Stream CDN, luồng đổi size trên Portal)
3. **Milestone 3 — VN Integrations & Growth *(Làm sau Milestone 2)***:
   - `wbh_payment_vietqr` (VietQR EMVCo offline + SePay Free webhook + COD)
   - `wbh_delivery_vn` (Ship nội bộ/Đồng giá + GHN ➜ GHTK & Viettel Post)
   - Mở rộng Loyalty tách riêng theo thương hiệu & Flash Sale đếm ngược.

### 1.3. Thứ Tự Ưu Tiên Chỉ Dẫn (3 Cấp)
1. **Cấp 1 (Cao nhất)**: `F:\BACKUP_LINUX\web_ban_hang\.claude\` (`CLAUDE.md`, `settings.local.json`) và `AGENTS.md` này.
2. **Cấp 2**: AIaC Root `F:\BACKUP_LINUX\aiac\360org\plugins\360-odoo\` và Global `CLAUDE.md`.
3. **Cấp 3 (Fallback)**: Môi trường IDE/CLI cục bộ.

---

## 2. Cơ Cấu Đội Ngũ Agent & Phân Bổ Mô Hình AI

**Nguyên tắc vàng theo chuẩn `360-odoo`**: Dùng **Claude / Codex** cho các tác vụ tư duy kiến trúc, phân tích nghiệp vụ và kiểm duyệt sâu (`PLAN & ANALYSIS`). Dùng **Gemini** cho các tác vụ sinh mã theo mẫu, viết test và đóng gói phát hành (`CODE & EXECUTION`).

| Vai trò Agent | Mô hình AI khuyến nghị | Phạm vi & Nhiệm vụ chính | Bước phụ trách |
|---|---|---|---|
| **Architect (Neo)** | Claude Opus 4.7+ hoặc Codex / GPT-5 | Điều phối tổng thể, cập nhật `REQUIREMENTS.md`, `CONTEXT.md`, `SPEC.md`, `ARCH.md`, chia atomic tasks ở `/plan` đúng thứ tự 3 Milestone. | `/req`, `/spec`, `/plan` |
| **Coder** | Gemini 2.x Pro / 3.x Flash | Sinh cấu hình Docker di động và mã Python (Models, Controllers, Services), XML Views, QWeb Templates, OWL `2.8.4` JS, SCSS cho 7 custom modules thuần Community dựa trên `SPEC.md`. | `/build` |
| **Code Reviewer** | Claude Opus 4.7+ hoặc Codex / GPT-5 *(bắt buộc khác model đã `/build`)* | Cổng chặn bắt buộc giữa `/build` và `/test`. Chỉ đọc `git diff` vừa sinh và kiểm tra 4 trục chất lượng Odoo + kiểm tra **0% phụ thuộc Enterprise**. Không chạy test, không viết test. | `/code-review` |
| **Tester** | Gemini 3.x Flash | Viết và chạy Unit tests Python (`TransactionCase`/`HttpCase`), Odoo Tours và E2E Playwright cho cả 2 website (mobile & desktop) trong Docker cô lập. | `/test` |
| **Reviewer** | Claude Opus 4.7+ hoặc Codex / GPT-5 | Kiểm duyệt 2 trục song song (**Standards** + **Spec**): chạy `odoo_linter.py`, xác minh 100% Community, kiểm tra ACL/Record Rules, phát hiện N+1 query, đối chiếu đầy đủ tiêu chí nghiệm thu từng Milestone. | `/review` |
| **Shipper** | Gemini 3.x Flash | Rà soát đồng bộ tài liệu `docs/*.md`, cập nhật `docs/CHANGELOGS.md` và changelog trong `__manifest__.py`, quét secret trong `.claude/`, chạy git clean và push theo quy trình Zero-Bypass. | `/ship` |

---

## 3. Vòng Đời Phát Triển 9 Bước (Mandatory 9-Step Lifecycle)

Mọi tính năng và module của `web_ban_hang` bắt buộc đi qua tuần tự 9 bước:

```text
/idea ➜ /req ➜ /spec ➜ /plan ➜ /build ➜ /code-review ➜ /test ➜ /review ➜ /ship
  PO    Arch.   Arch.   Arch.   Coder   Code Reviewer  Tester  Reviewer  Shipper
                                  ▲           │
                                  └───────────┘
                           Vòng lặp fix → re-review (tối đa 3 vòng)
```

### Quy tắc từng cổng chuyển giao (Stage Gates)
1. **`/idea` ➜ `/req` ➜ `/spec` *(Đã hoàn tất cho Milestone 1)***: Toàn bộ 5 câu hỏi mở đã chốt với Sếp; `docs/IDEA.md`, `docs/REQUIREMENTS.md`, `docs/ARCH.md`, `docs/CONTEXT.md`, `docs/SPEC.md` và `docs/DEPLOY_GUIDE.md` đã đồng bộ 100%.
2. **`/plan` ➜ `/build`**: Chia nhỏ thành các atomic tasks độc lập theo đúng thứ tự ưu tiên:
   - **Đợt 1 (Milestone 1 — Catalog-First)**: Docker di động ➜ `wbh_core` ➜ `theme_gift_store` + `theme_fashion_store`.
   - **Đợt 2 (Milestone 2)**: `wbh_gift_store` + `wbh_fashion_store`.
   - **Đợt 3 (Milestone 3)**: `wbh_payment_vietqr` + `wbh_delivery_vn` + mở rộng Loyalty tách riêng & Flash Sale.
3. **Subagent-Driven Development tại `/build`**:
   - Mỗi atomic task giao cho 1 sub-agent Coder độc lập (fresh context), không để 2 agent sửa cùng 1 file đồng thời.
   - Ưu tiên tra cứu quan hệ model/module qua `odoo-graph-mcp` (nếu đã index) trước khi sửa mã, tránh đọc mò toàn codebase.
4. **Cổng chặn bắt buộc `/code-review`**:
   - Model review **bắt buộc khác** model đã `/build`.
   - Soi đúng `git diff` trên **4 trục**:
     1. **Correctness**: sai `self`/recordset, thiếu `ensure_one()`, `create()`/`write()` trong vòng lặp, thiếu `@api.depends`, mất dữ liệu khi `unlink()`, sai tách biệt `website_id` / tài khoản giữa Web 1 và Web 2.
     2. **Reuse & Community Purity**: viết lại logic/mixin đã có sẵn trong Odoo 19.0 Community core (`website_sale`, `stock`, `sale_management`, `payment`, `delivery`) hoặc trong `wbh_core`; **chặn ngay (Critical)** nếu phát hiện bất kỳ `depends`/import nào dính module `*_enterprise` hay `account_accountant`.
     3. **Over-engineering**: tạo abstraction thừa chỉ có 1 implementation, cấu hình hóa giá trị cố định, làm vượt phạm vi Milestone hiện tại (VD: kéo tính năng M2/M3 làm phình M1).
     4. **Security & Validation tại Trust Boundary**: thiếu `ir.model.access.csv` / `ir.rule`, lạm dụng `sudo()`, truy vấn SQL không tham số hóa, xác thực chữ ký webhook VietQR/vận chuyển lỏng lẻo, truyền raw HTML vào `message_post()` không bọc `markupsafe.Markup()`.
   - Còn lỗi **Critical/High** thì **CẤM** chuyển sang `/test`. Trần tối đa **3 vòng** fix ➜ re-review; nếu vượt quá 3 vòng phải escalate ngược về Architect để rà lại `docs/SPEC.md`.
5. **Kiểm thử tại `/test`**: Chạy toàn bộ test suite trên database riêng `web_ban_hang_test` trong Docker cô lập trên image `odoo:19.0` Community thuần; kiểm tra cả 2 website (Web 1 và Web 2), quy trình up sản phẩm, hiển thị biến thể và đặt hàng trên viewport mobile.
6. **Kiểm duyệt 2 trục tại `/review`**:
   - **Trục Standards**: chuẩn Odoo 19.0 Community thuần (0% Enterprise), hiệu năng truy vấn (không N+1), bảo mật, chuẩn Theme Upgrade-Safe.
   - **Trục Spec**: đối chiếu 100% tiêu chí nghiệm thu của Milestone hiện tại trong `docs/REQUIREMENTS.md` và `docs/SPEC.md`.
7. **Đóng gói & phát hành tại `/ship`**: Đồng bộ tài liệu `docs/*.md`, cập nhật `docs/CHANGELOGS.md` và `__manifest__.py`, kiểm tra sạch secret trong `.claude/`, push Git đúng quy trình Zero-Bypass.

---

## 4. Ràng Buộc Kỹ Thuật Bắt Buộc Cho Odoo 19.0 Community (`360-odoo`)

Mọi Agent sinh mã hoặc kiểm duyệt cho dự án này **bắt buộc** tuân thủ tuyệt đối các tiêu chuẩn Odoo 19.0 sau:

### 4.1. XML Views & Actions
- **Cấm tuyệt đối** thuộc tính cũ `attrs="..."` và `states="..."`. Sử dụng trực tiếp biểu thức Python trên `invisible="..."`, `readonly="..."`, `required="..."`.
- Dùng thẻ `<list>` thay cho `<tree>` theo chuẩn Odoo 19.0.
- Tuân thủ đặt tên XML ID có prefix rõ ràng theo tên module (`wbh_core.*`, `theme_gift_store.*`, `theme_fashion_store.*`, ...).

### 4.2. Python ORM & Backend (Python 3.12 / Odoo 19.0 Community)
- Bắt buộc dùng `@api.model_create_multi` khi override hàm `create()`.
- Dùng `odoo.fields.Command` (`Command.create`, `Command.update`, `Command.link`, `Command.set`, `Command.clear`, ...) thay cho tuple `(0, 0, ...)`, `(4, id, 0)`.
- Khai báo ràng buộc và chỉ mục bằng `models.Constraint()` và `models.Index()` thay cho `_sql_constraints` / `index=True` kiểu cũ.
- Tôn trọng ngữ cảnh đa công ty / đa website (`allowed_company_ids`, `website_id`) và tách riêng tài khoản (`specific_user_account=True`) khi lọc sản phẩm, khách hàng, đơn hàng, tồn kho và điểm thành viên.
- Ưu tiên toán tử miền hiện đại `any!` / `not any!` khi lọc quan hệ phức tạp.
- Mọi nội dung HTML truyền vào `message_post()` hoặc `mail.message` bắt buộc bọc qua `markupsafe.Markup(...)`, cấm truyền raw string.

### 4.3. Frontend & Website Theme Upgrade-Safe (`OWL 2.8.4` + `Bootstrap 5.3.3` / `SCSS`)
- **BẮT BUỘC ĐỌC `DESIGN.md` TRƯỚC KHI SỬA UI**: Mọi Agent trước khi can thiệp vào bất kỳ thành phần giao diện nào (Views, QWeb, SCSS, JS Snippets) bắt buộc đọc file `DESIGN.md` tại thư mục gốc và tham chiếu `css/system.css` + `html/preview.html` để tái sử dụng đúng bảng màu, kiểu chữ, khoảng cách và components của từng website.
- Áp dụng nghiêm ngặt cho `theme_gift_store` và `theme_fashion_store`:
  - Mọi trang `website.page` bắt buộc có khung `<div id="wrap" class="oe_structure oe_empty">`.
  - Mọi Building Block / Snippet kéo-thả bắt buộc có class `o_colored_level` và thuộc tính `data-snippet`.
  - Khi tắt view/header/footer mặc định của core phải khai báo qua `data/presets.xml` (`active=False`), không xóa cưỡng bức record gốc.
  - Bảng màu động của từng cửa hàng quản lý qua biến SCSS `$o-color-1..5` trong `primary_variables.scss`.
  - Khai báo đúng asset bundles chuẩn Odoo 19.0: `web._assets_primary_variables`, `web.assets_frontend`, `website.assets_wysiwyg`, `web.assets_backend`.
  - Tài nguyên media dung lượng lớn (video người mẫu Web 2 ở Milestone 2, ảnh chất lượng cao) phục vụ qua **Cloudflare R2 / Stream CDN**, không làm phình database PostgreSQL.

### 4.4. Chuẩn Changelog trong `__manifest__.py`
Mỗi custom module trong `addons/` bắt buộc khai báo `'license': 'LGPL-3'` và tóm tắt lịch sử phiên bản trong trường `description` của `__manifest__.py`:
```python
'license': 'LGPL-3',
'description': """
Tên Module — Changelog
======================

v19.0.1.0.0 (YYYY-MM-DD)
------------------------
- [NEW] Mô tả tính năng mới thêm.
- [FIX] Mô tả lỗi đã khắc phục.
""",
```
Các tag hợp lệ: `[NEW]`, `[FIX]`, `[IMPROVE]`, `[SECURITY]`, `[REFACTOR]`, `[MIGRATE]`.

---

## 5. An Toàn Hạ Tầng, Bảo Mật & Quy Trình Git

### 5.1. Cách Ly Hạ Tầng & Docker Di Động (Windows ➜ Local Server)
- **Đóng gói di động**: Sử dụng `docker-compose.yml`, `config/odoo.conf`, `.env.example` ngay trong repo `F:\BACKUP_LINUX\web_ban_hang\`, chạy image chuẩn `odoo:19.0` Community + `postgres:15-bookworm` (hỗ trợ tùy chọn `360ai/postgres:15-ai`).
- **Cấm tuyệt đối**:
  - Không dùng chung database `demo-19` hoặc Docker volume `odoo19-db`.
  - Không đặt code `web_ban_hang` vào `F:\BACKUP_LINUX\save\dev_env\19.0\modules\default\`.
  - Không dùng dump database của dự án khác (`vuahethong_v19_prod_test.dump`).
  - Không hardcode đường dẫn Linux cũ (`/media/tanma/DATA/...`) trong `docker-compose.yml`.
  - Bắt buộc dùng container riêng (`CLIENT_NAME=web-ban-hang`), database riêng (`web_ban_hang_dev` / `web_ban_hang_prod`, `DB_FILTER=^web_ban_hang.*$`), volume riêng (`web_ban_hang_pgdata`), filestore/sessions riêng (`data/filestore`, `data/sessions`) và dải port riêng (`1900`–`1999`, VD: Web `1901`/`8089`, Longpolling `7089`, DB Host `51901`).

### 5.2. Quy Tắc Ngôn Ngữ, Bảo Mật & Git
- **Ngôn ngữ**: 100% tiếng Việt cho tài liệu, báo cáo, giải thích, commit message và trao đổi với Sếp.
- **Pre-Push Docs Sync Trigger**: Bắt buộc cập nhật đồng bộ `docs/*.md` (`CHANGELOGS.md`, `ARCH.md`, `SPEC.md`, `REQUIREMENTS.md`, `CONTEXT.md`, `DEPLOY_GUIDE.md`, `README.md`) trước mọi lệnh `git push`.
- **Commit `.claude/` & Quét Secret**: Luôn commit kèm thư mục `.claude/` (đảm bảo `.gitignore` KHÔNG ignore `.claude/` và `.env.example`, nhưng LUÔN ignore `.env`), **bắt buộc quét sạch secret/token/API key/password** trước khi stage. Nếu phát hiện secret thì DỪNG NGAY và báo Sếp.
- **Git Commit Trailer (Bắt buộc)**:
  ```text
  Authored-By: 360org <support@360.org.vn>
  ```
  *(Tuyệt đối không dùng `Co-Authored-By: Claude...`).*
- **Zero-Bypass Promotion Pipeline**:
  `Fetch code mới nhất ➜ Dev ➜ Push ➜ Local Server Pull/Test ➜ (Lỗi quay lại Dev & Push) ➜ Production Pull/Deploy/Test live ➜ Done/Report`.  
  ⛔ Cấm `rsync`/`scp` mã nguồn vượt cấp, cấm sửa code trực tiếp trên máy chủ, cấm thao tác trên thư mục không có `.git`.
