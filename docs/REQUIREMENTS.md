# REQUIREMENTS — Đặc Tả Yêu Cầu Hệ Sinh Thái 2 Website Bán Hàng

> **Phiên bản tài liệu**: v1.1 (Phân nhóm theo 3 Milestone Catalog-First & 100% Odoo 19.0 Community)  
> **Ngày tạo**: 2026-11-25 | **Cập nhật lần cuối**: 2026-11-25  
> **Nền tảng đã chốt**: **100% Odoo 19.0 Community (LGPL-3)** + **PostgreSQL 15** (Multi-Website tách tài khoản & Loyalty)  
> **Bước quy trình**: `/req` (Đã chốt — Ánh xạ trực tiếp sang `docs/SPEC.md`)  
> **Tài liệu liên quan**: [IDEA.md](file:///F:/BACKUP_LINUX/web_ban_hang/docs/IDEA.md) | [ARCH.md](file:///F:/BACKUP_LINUX/web_ban_hang/docs/ARCH.md) | [CONTEXT.md](file:///F:/BACKUP_LINUX/web_ban_hang/docs/CONTEXT.md) | [SPEC.md](file:///F:/BACKUP_LINUX/web_ban_hang/docs/SPEC.md) | [DEPLOY_GUIDE.md](file:///F:/BACKUP_LINUX/web_ban_hang/docs/DEPLOY_GUIDE.md)

---

## 1. Quy Ước Milestone & Bản Đồ Ánh Xạ Module

### 1.1. Phân chia theo 3 Milestone (Chiến lược Catalog-First)
- **`M1 — Milestone 1 (Catalog-First — LÀM NGAY)`**: Hạ tầng Docker di động + Backend cốt lõi (`wbh_core`) + Frontend cơ bản 2 Storefronts (`theme_gift_store`, `theme_fashion_store`) để Sếp đăng nhập và **upload sản phẩm lên ngay**, xem live 2 giao diện và kiểm thử đặt hàng cơ bản (COD/chuyển khoản có sẵn của Odoo Community).
- **`M2 — Milestone 2 (Nghiệp vụ đặc thù 2 cửa hàng)`**: Xây dựng đầy đủ tính năng chuyển đổi đặc thù cho Web 1 (`wbh_gift_store`) và Web 2 (`wbh_fashion_store`).
- **`M3 — Milestone 3 (Thanh toán VN, Vận chuyển VN & Tăng trưởng)`**: Xây dựng `wbh_payment_vietqr` (EMVCo/Napas 247 + SePay Free), `wbh_delivery_vn` (Đồng giá + GHN miễn phí API ➜ GHTK/VTP), Loyalty tách riêng từng thương hiệu, Flash Sale đếm ngược & tối ưu CDN/báo cáo.

### 1.2. Ánh xạ sang 7 Custom Modules (`F:\BACKUP_LINUX\web_ban_hang\addons\`)
- **Milestone 1**: `wbh_core`, `theme_gift_store`, `theme_fashion_store` (+ Docker stack `docker-compose.yml`, `config/odoo.conf`, `.env.example`).
- **Milestone 2**: `wbh_gift_store`, `wbh_fashion_store`.
- **Milestone 3**: `wbh_payment_vietqr`, `wbh_delivery_vn` (và mở rộng `wbh_core`).

---

## 2. Yêu Cầu Chức Năng — Milestone 1: Catalog-First (Backend Cốt Lõi + 2 Storefronts Cơ Bản)

| Mã FR | Tên Chức Năng | Module | Mô tả Chi tiết & Tiêu chí Chấp nhận (Acceptance Criteria) |
|---|---|---|---|
| **FR-M1-01** | **Hạ tầng Docker di động 100% Community** | Docker Stack | - Khởi chạy trọn bộ Odoo 19.0 Community (`odoo:19.0`) + PostgreSQL 15 (`postgres:15-bookworm`) bằng lệnh `docker compose up -d` trên máy Windows hiện tại (data đặt ổ `F:\`), DB riêng `web_ban_hang_dev`, port `1901`/`7089`/`51901`.<br>- Di động 100%: khi Local Server ở nhà khởi động lại chỉ cần `git pull`, chỉnh `.env`, `docker compose up -d` và restore DB/filestore là chạy y hệt. |
| **FR-M1-02** | **Khởi tạo 2 Website tách biệt hoàn toàn** | `wbh_core` | - Tự động khởi tạo 2 bản ghi `website`: **`website_gift_store`** (Web 1 — Quà tặng) và **`website_fashion_store`** (Web 2 — Thời trang).<br>- Cả 2 website bật cố định **`specific_user_account = True`** để tách riêng tài khoản đăng nhập khách hàng theo từng thương hiệu ngay từ đầu. |
| **FR-M1-03** | **Danh mục & Bộ 7 Thuộc tính Biến thể mẫu** | `wbh_core` | - Khởi tạo sẵn cây danh mục `product.public.category` gắn đúng từng website (Web 1: Gấu bông, Móc khóa, Blind Box, Quà theo dịp, Combo; Web 2: Áo, Quần, Váy & Đầm, Set đồ/Lookbook, Phụ kiện).<br>- Khởi tạo sẵn 7 `product.attribute` chuẩn: **Màu sắc (Color Swatch)**, **Size Quần Áo**, **Kích thước Gấu Bông (cm)**, **Chất liệu**, **Form dáng**, **Dịp tặng quà**, **Phiên bản Blind Box (Hộp lẻ / Full Set)**. |
| **FR-M1-04** | **Trải nghiệm Backend Upload Sản Phẩm Nhanh** | `wbh_core` | - Mở rộng `product.template` với `wbh_store_scope` (Web 1 / Web 2 / Cả 2 — tự động đồng bộ `website_id`), `wbh_short_highlight`, `wbh_care_note`, `wbh_low_stock_threshold`.<br>- Menu quản trị gọn gàng lọc riêng danh sách sản phẩm Web 1 và Web 2; Sếp có thể tạo sản phẩm mới, chọn biến thể màu/size/chất liệu, up ảnh và bấm Đăng bán (Publish) trong dưới 2 phút. |
| **FR-M1-05** | **Storefront Cơ Bản Web 1 — Quà Tặng** | `theme_gift_store` | - Giao diện riêng hoàn toàn (tone ấm áp/trẻ trung Gen Z, bảng màu `$o-color-1..5`, Header/Footer riêng, `data/presets.xml` upgrade-safe).<br>- Trang chủ có banner & thanh chọn nhanh theo dịp; Trang Shop hiển thị bộ lọc thuộc tính/màu rõ ràng; Trang chi tiết hiển thị `wbh_short_highlight`, `wbh_care_note`, nút mua hàng sticky mobile và sẵn extension slots cho Milestone 2. |
| **FR-M1-06** | **Storefront Cơ Bản Web 2 — Thời Trang** | `theme_fashion_store` | - Giao diện riêng hoàn toàn (tone tối giản/editorial Lookbook, tỷ lệ ảnh sản phẩm `3:4`, Header/Footer riêng, `data/presets.xml` upgrade-safe).<br>- Trang Shop hiển thị chấm màu Color Swatch trực tiếp trên thẻ sản phẩm + bộ lọc Size/Form/Chất liệu/Màu; Trang chi tiết hiển thị chọn Size dạng pills dễ bấm 1 tay trên mobile và sẵn extension slots cho Milestone 2. |
| **FR-M1-07** | **Giỏ hàng, Tồn kho cơ bản & Đặt hàng thử** | `wbh_core` + Odoo Core | - Khách trên cả 2 website có thể thêm biến thể vào giỏ hàng, cập nhật số lượng, kiểm tra tồn kho realtime (`website_sale_stock`) và hoàn tất đặt đơn thử với phương thức cơ bản (Chuyển khoản thủ công / COD cơ bản có sẵn của Odoo 19.0 Community).<br>- Đơn hàng tạo ra trong Back-office ghi nhận chính xác `website_id` của từng cửa hàng. |

---

## 3. Yêu Cầu Chức Năng — Milestone 2: Nghiệp Vụ Đặc Thù 2 Cửa Hàng

### 3.1. Web 1 — Cửa Hàng Quà Tặng (`wbh_gift_store` + nâng cấp `theme_gift_store`)

| Mã FR | Tên Chức Năng | Milestone | Mô tả Chi tiết & Tiêu chí Chấp nhận (Acceptance Criteria) |
|---|---|---|---|
| **FR-W1-01** | **Dịch vụ Gói quà & Thiệp viết tay** | `M2` | - Tại trang sản phẩm hoặc giỏ hàng, khách bật tùy chọn **Gói quà**: chọn mẫu hộp quà, màu ruy-băng, nhập lời chúc (tối đa 250 ký tự).<br>- Tự động tính phụ phí gói quà hoặc **miễn phí** khi đơn đạt ngưỡng cấu hình.<br>- In rõ thông tin hộp quà, ruy-băng và lời chúc lên Phiếu đóng gói kho. |
| **FR-W1-02** | **Cá nhân hóa sản phẩm (Khắc/Thêu tên)** | `M2` | - Với sản phẩm cho phép cá nhân hóa, khách nhập nội dung khắc/thêu, chọn font chữ & vị trí (validate độ dài/ký tự); lưu chuẩn hóa trên `sale.order.line` hiển thị rõ ở giỏ hàng/phiếu xưởng; bổ sung xem trước (Live Preview) ở giai đoạn hoàn thiện. |
| **FR-W1-03** | **So sánh kích thước trực quan** | `M2` | - Hiển thị khối so sánh kích thước thực tế gấu bông/phụ kiện cạnh vật mẫu quen thuộc (iPhone, chai nước 500ml, bàn tay, người mẫu 1m60) kèm số đo cm cấu hình trực tiếp trong Back-office. |
| **FR-W1-04** | **Combo quà tặng theo dịp & ngân sách** | `M2` | - Trang lọc nhanh theo Dịp lễ (Sinh nhật, Valentine, 8/3, 20/10, Tốt nghiệp, Giáng sinh) và Ngân sách (`<200k`, `200k–500k`, `>500k`); hỗ trợ tạo Combo nhiều SKU giá ưu đãi và tự động trừ kho đúng từng SKU thành phần. |
| **FR-W1-05** | **Quản lý Blind Box chuyên sâu** | `M2` | - Bổ sung hiển thị thông tin series Blind Box, tỷ lệ mẫu hiếm (Secret) và quy tắc tách bán Hộp lẻ vs Nguyên Set Full Case. |

### 3.2. Web 2 — Cửa Hàng Thời Trang (`wbh_fashion_store` + nâng cấp `theme_fashion_store`)

| Mã FR | Tên Chức Năng | Milestone | Mô tả Chi tiết & Tiêu chí Chấp nhận (Acceptance Criteria) |
|---|---|---|---|
| **FR-W2-01** | **Bảng quy đổi & Gợi ý Size thông minh** | `M2` | - Widget OWL 2.8.4 trên trang sản phẩm: khách nhập **Chiều cao (cm)**, **Cân nặng (kg)** và **Sở thích mặc** (Ôm / Vừa / Rộng).<br>- Đề xuất size phù hợp tức thì theo bảng size cấu hình linh hoạt cho từng danh mục/sản phẩm kèm nút chọn nhanh size đó. |
| **FR-W2-02** | **Bộ lọc thời trang nâng cao** | `M2` | - Nâng cấp bộ lọc M1: lọc chỉ hiển thị sản phẩm **còn hàng đúng size đang chọn**, đổi màu Color Swatch tại thẻ danh sách cập nhật ngay ảnh theo màu tương ứng, lọc theo Dịp mặc. |
| **FR-W2-03** | **Shop The Look (Mix & Match)** | `M2` | - Admin tạo Lookbook gắn nhiều sản phẩm phối sẵn; khách chọn màu/size cho từng món ngay tại giao diện Shop The Look và bấm **1 nút "Thêm trọn bộ vào giỏ"** (hỗ trợ giảm giá mua theo set). |
| **FR-W2-04** | **Video người mẫu chuyển động thực tế** | `M2` | - Gallery sản phẩm hỗ trợ phát **video dọc 9:16** (Reels/TikTok) từ CDN (Cloudflare Stream/R2), có ảnh poster, tắt tiếng mặc định và tối ưu băng thông 4G. |
| **FR-W2-05** | **Luồng yêu cầu đổi size nhanh trên Portal** | `M2` | - Khách mở lịch sử đơn hàng đã giao tạo **Yêu cầu đổi size** (`wbh.size.exchange.request`): chọn sản phẩm, size mới muốn đổi; hệ thống kiểm tra tồn kho size mới tức thì và cập nhật minh bạch tiến độ xử lý. |

---

## 4. Yêu Cầu Chức Năng — Milestone 3: Thanh Toán VN, Vận Chuyển VN & Tăng Trưởng

| Mã FR | Tên Chức Năng | Module | Mô tả Chi tiết & Tiêu chí Chấp nhận (Acceptance Criteria) |
|---|---|---|---|
| **FR-PAY-01** | **Mở rộng Thanh toán COD** | `wbh_payment_vietqr` | - Cấu hình hạn mức tối đa cho phép COD và tùy chọn yêu cầu đặt cọc/chuyển khoản trước đối với đơn cá nhân hóa khắc/thêu tên (Web 1) nhằm hạn chế bom hàng. |
| **FR-PAY-02** | **VietQR Động EMVCo/Napas 247 + SePay Free** | `wbh_payment_vietqr` | - Kế thừa `payment.provider` chuẩn Odoo 19.0 Community.<br>- **Mặc định tự sinh mã QR chuẩn EMVCo / Napas 247 offline ngay trong Odoo** (miễn phí 100%, hỗ trợ mọi ngân hàng VN) kèm đúng số tiền và mã giao dịch duy nhất.<br>- **Adapter Webhook mặc định SePay (gói Free)** xác thực chữ ký bảo mật, tự động đối soát & xác nhận đơn trong 5–15 giây, đảm bảo **Idempotency** chống ghi nhận trùng; mở sẵn interface sạch cho **PayOS / Casso**. |
| **FR-SHIP-01** | **Địa giới hành chính VN 3 cấp** | `wbh_delivery_vn` | - Danh mục Tỉnh/Thành phố ➜ Quận/Huyện ➜ Phường/Xã chuẩn hóa trên checkout & Back-office, có bảng mapping mã địa giới cho các hãng vận chuyển. |
| **FR-SHIP-02** | **Ship nội bộ/Đồng giá + GHN Free API ➜ GHTK/VTP** | `wbh_delivery_vn` | - Kế thừa `delivery.carrier` chuẩn Odoo 19.0.<br>- Hỗ trợ sẵn **Ship nội bộ / Đồng giá** (và ngưỡng miễn phí ship).<br>- Ưu tiên tích hợp **GHN** đầu tiên (API miễn phí 100%, có môi trường Sandbox để test tự động), sau đó mở rộng **GHTK & Viettel Post** với so sánh phí ship & thời gian giao dự kiến. |
| **FR-SHIP-03** | **Đẩy vận đơn tự động & Tracking** | `wbh_delivery_vn` | - Đẩy đơn từ `stock.picking` sang hãng vận chuyển trong 1 click, nhận mã vận đơn + in nhãn, đồng bộ tự động trạng thái giao hàng & COD về đơn hàng và Portal khách hàng. |
| **FR-GROW-01** | **Loyalty & Hạng thành viên tách thương hiệu** | `wbh_core` + `loyalty` | - Chương trình tích/đổi điểm, voucher và hạng thành viên (Bạc/Vàng/Kim cương) cấu hình **tách riêng theo `website_id`** của Web 1 và Web 2, tuyệt đối không cộng dồn lẫn chéo điểm giữa 2 thương hiệu. |
| **FR-GROW-02** | **Flash Sale đếm ngược & Cảnh báo tồn kho** | `wbh_core` | - Tạo chiến dịch Flash Sale theo khung giờ, giới hạn tổng suất & suất/khách, đồng hồ đếm ngược realtime trên storefront; tự động gửi cảnh báo nội bộ khi SKU xuống dưới `wbh_low_stock_threshold`. |
| **FR-GROW-03** | **Offload Media Cloudflare R2 & Báo cáo** | `wbh_core` | - Tùy chọn offload ảnh dung lượng lớn lên Cloudflare R2 (`boto3`); báo cáo doanh thu, AOV, tỷ lệ hoàn/đổi và tồn kho lọc riêng từng Website và tổng hợp. *(Giai đoạn mở rộng cân nhắc ghép CSKH Zalo OA từ `F:\BACKUP_LINUX\zalo_socal` sau khi kiểm tra 0% Enterprise).* |

---

## 5. Yêu Cầu Phi Chức Năng (Non-Functional Requirements — NFR)

| Mã NFR | Danh mục | Yêu cầu Cụ thể & Chỉ tiêu Đo lường |
|---|---|---|
| **NFR-01** | **100% Odoo 19.0 Community (LGPL-3)** | - **Luật cứng**: 0% phụ thuộc module Enterprise (`*_enterprise`, `account_accountant`...) trên toàn bộ 7 custom modules. Hệ thống chạy hoàn chỉnh trên image chính chủ `odoo:19.0` Community miễn phí bản quyền vĩnh viễn. |
| **NFR-02** | **Hiệu năng & Trải nghiệm Mobile-First** | - Thiết kế ưu tiên màn hình di động (80%+ lưu lượng từ mobile).<br>- Chỉ tiêu Core Web Vitals trên mạng 4G: **LCP < 2.5s**, **CLS < 0.1**, **INP < 200ms**.<br>- Ảnh nén WebP + lazy-loading; video dọc 9:16 (M2) stream qua CDN không nghẽn worker Odoo. |
| **NFR-03** | **SEO & Chia sẻ Mạng xã hội** | - Mỗi website có `sitemap.xml`, `robots.txt`, canonical URL độc lập theo tên miền.<br>- Đầy đủ Meta Title/Description, OpenGraph (Zalo/Facebook preview) và JSON-LD Schema `Product`/`Offer`. |
| **NFR-04** | **Bảo mật & Tách biệt Dữ liệu** | - Tách riêng tài khoản khách hàng (`specific_user_account=True`) và Loyalty theo `website_id`.<br>- HTTPS/TLS trên Staging/Production, tắt `list_db = False` và khóa `DB_FILTER=^web_ban_hang.*$`.<br>- Phân quyền rõ ràng (`ir.model.access.csv` + `ir.rule`), xác thực chữ ký webhook (M3), chống XSS bằng `markupsafe.Markup`.<br>- Tuyệt đối không commit mật khẩu/token/API key vào Git hay `.claude/`. |
| **NFR-05** | **Di động Hạ tầng, Backup & Khôi phục** | - Docker stack di động 100% trong Git repo (Windows ổ `F:\` ➜ Local Server chỉ cần `git pull` + `docker compose up -d`).<br>- Cô lập hoàn toàn DB (`web_ban_hang_*`), Volume (`web_ban_hang_pgdata`), Filestore và Port khỏi `demo-19` và mọi dự án khác.<br>- Backup tự động hàng ngày 3-2-1 (`pg_dump` + Filestore), **RPO <= 24 giờ**, **RTO <= 2 giờ**. |
| **NFR-06** | **Chuẩn Odoo 19.0 & AIaC 3.0** | - Tuân thủ 100% chuẩn `360-odoo`: cấm `attrs=`, `states=`, `<tree>`; bắt buộc `@api.model_create_multi`, `Command.*`, `models.Constraint()`, `models.Index()`, theme upgrade-safe.<br>- Có unit tests `TransactionCase` cho từng milestone; tuân thủ workflow 9 bước (có cổng chặn `/code-review`), Zero-Bypass Promotion Pipeline (Git-only), Pre-Push Docs Sync Trigger và trailer `Authored-By: 360org <support@360.org.vn>`. |

---

## 6. Tiêu Chí Nghiệm Thu Milestone 1 (Catalog-First Acceptance Gate)

Milestone 1 chỉ được coi là hoàn tất và bàn giao để Sếp upload sản phẩm khi đạt **100%** các tiêu chí sau:
- [ ] `docker compose up -d` khởi chạy thành công không lỗi trên máy Windows (dùng `odoo:19.0` Community + `postgres:15-bookworm`), cài đặt thành công `wbh_core`, `theme_gift_store`, `theme_fashion_store` mà **không** cần bất kỳ module Enterprise nào.
- [ ] Trong Back-office có đủ 2 Website (`website_gift_store`, `website_fashion_store`) với `specific_user_account = True`, đủ danh mục mẫu và 7 thuộc tính biến thể (Màu sắc Color Swatch, Size Quần Áo, Kích thước Gấu Bông cm, Chất liệu, Form dáng, Dịp tặng quà, Phiên bản Blind Box).
- [ ] Sếp có thể đăng nhập Backend, tạo mới sản phẩm có biến thể cho Web 1 và Web 2, chọn `wbh_store_scope` và bật Đăng bán (Publish) mượt mà.
- [ ] Truy cập 2 Storefronts hiển thị 2 giao diện riêng biệt rõ nét (Web 1 ấm áp quà tặng, Web 2 tối giản thời trang), bộ lọc thuộc tính & Color Swatch hoạt động chính xác trên cả Desktop và Mobile.
- [ ] Kiểm thử thêm vào giỏ hàng, cập nhật số lượng và tạo đơn hàng thử thành công trên cả 2 website; đơn hàng lưu đúng `website_id` trong Back-office.
- [ ] Kiểm thử đăng ký tài khoản khách hàng ở Web 1 không tự động đăng nhập chéo sang Web 2 (`specific_user_account = True`).
- [ ] Bộ unit tests `wbh_core` pass 100% và vượt qua cổng chặn `/code-review` 4 trục.
