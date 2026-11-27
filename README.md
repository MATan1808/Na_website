# Hệ Sinh Thái 2 Website Bán Hàng (E-Commerce Multi-Store — Thuần Odoo 19.0 Community)

> **Trạng thái dự án**: `v0.3.6` — Tích hợp bộ công cụ UI/UX & Animation chuẩn MochiStudio (`GSAP 3.15.1`, `Lucide 1.82.0`, audit `Impeccable` + `Front-End Checklist` + `UI UX Pro Max`) vào 2 Storefronts thuần Odoo 19.0 Community (`wbh_core` `v19.0.1.1.0`, `theme_gift_store` `v19.0.1.1.0`, `theme_fashion_store` `v19.0.1.1.0`).  
> **Thư mục gốc dự án**: `F:\BACKUP_LINUX\web_ban_hang`  
> **Repository**: `https://github.com/MATan1808/Na_website.git` (nhánh `main`)  
> **Quy trình phát triển**: `/idea` ➜ `/req` ➜ `/spec` ➜ `/plan` ➜ `/build` ➜ `/code-review` ➜ `/test` ➜ `/review` ➜ `/ship`

---

## 1. Tổng Quan Dự Án

Dự án xây dựng song song **2 website thương mại điện tử D2C độc lập về thương hiệu và tài khoản khách hàng** trên cùng **1 hệ thống lõi quản trị tập trung thuần Odoo 19.0 Community (LGPL-3)**:

### 1.1. Web 1 — Cửa Hàng Quà Tặng: Móc Khóa, Gấu Bông & Blind Box
- **Mục tiêu**: Bán sản phẩm quà tặng, phụ kiện, móc khóa, gấu bông, blind box cho nhóm khách trẻ (16–30 tuổi).
- **Tính năng đặc thù (`wbh_gift_store` + `theme_gift_store`)**:
  - Dịch vụ đóng gói hộp quà cao cấp + thiệp viết tay theo yêu cầu (tự động tính phụ phí hoặc miễn phí theo ngưỡng giá trị đơn).
  - Cá nhân hóa sản phẩm (nhập nội dung khắc tên móc khóa, thêu tên gấu bông, chọn font/vị trí chuẩn hóa cho xưởng).
  - So sánh kích thước gấu bông trực quan với vật mẫu thực tế (chai nước, iPhone, chiều cao người mẫu 1m60...).
  - Combo quà tặng theo dịp lễ (Sinh nhật, Valentine, 8/3, 20/10, Tốt nghiệp, Kỷ niệm, Giáng sinh) và theo mức ngân sách.

### 1.2. Web 2 — Cửa Hàng Thời Trang Quần Áo
- **Mục tiêu**: Bán quần áo, trang phục thời trang xu hướng, tối ưu trải nghiệm mua nhanh trên thiết bị di động (18–35 tuổi).
- **Tính năng đặc thù (`wbh_fashion_store` + `theme_fashion_store`)**:
  - Bảng quy đổi Size & công cụ gợi ý Size thông minh theo Chiều cao, Cân nặng và Sở thích mặc (ôm / vừa / rộng).
  - Bộ lọc thời trang chuyên sâu (Bảng màu trực quan Color Swatch, Form dáng, Chất liệu vải, Dịp mặc).
  - Mua trọn bộ phối đồ (**Shop The Look / Mix & Match**): chọn size từng món và thêm cả set vào giỏ hàng trong 1 bước.
  - Video người mẫu mặc chuyển động thực tế (định dạng ngắn dạng Reels/TikTok dọc lưu trên Media CDN).
  - Chính sách & luồng tự tạo yêu cầu đổi size nhanh chóng ngay trên Cổng khách hàng (Odoo Portal).

### 1.3. Hệ Thống Cốt Lõi (Core E-Commerce Engine)
- Quản lý tập trung 2 website trên 1 lõi **Odoo 19.0 Community**: sản phẩm, biến thể (SKU), tồn kho thời gian thực, giỏ hàng và đơn hàng.
- **Tách riêng hoàn toàn tài khoản khách hàng & tích điểm Loyalty theo từng thương hiệu** (`specific_user_account=True` trên từng `website`, tách chương trình Loyalty theo `website_id`).
- Thanh toán nội địa Việt Nam ưu tiên miễn phí, lâu dài: **COD** & **VietQR động chuẩn EMVCo / Napas 247** (tự sinh mã QR offline miễn phí 100% trong Odoo cho mọi ngân hàng VN + Adapter Webhook đối soát tự động mặc định **SePay Free**, mở rộng PayOS/Casso).
- Tích hợp vận chuyển nội địa: hỗ trợ sẵn **Ship nội bộ / Đồng giá** + ưu tiên tích hợp **GHN** trước (API miễn phí 100%, có Sandbox), mở rộng **GHTK & Viettel Post**.
- Chương trình khuyến mãi, mã giảm giá (Voucher) và **Flash Sale** đếm ngược theo từng website.

---

## 2. Năm Quyết Định Công Nghệ & Kiến Trúc Đã Chốt

| STT | Hạng mục | Quyết định đã chốt | Chi tiết kỹ thuật |
|---:|---|---|---|
| 1 | **Phiên bản & Giấy phép** | **100% Odoo `19.0` Community (`LGPL-3`, miễn phí vĩnh viễn)** | Backend Python `3.12` + ORM 19.0; Frontend Website Builder + QWeb + **OWL `2.8.4`** + **Bootstrap `5.3.3`** / SCSS. **TUYỆT ĐỐI không khai báo `depends` vào bất kỳ module Enterprise (`*_enterprise`, `account_accountant`...) nào**, tương thích 100% cả Community lẫn Enterprise. |
| 2 | **Tài khoản & Tích điểm Loyalty** | **Tách riêng hoàn toàn theo từng thương hiệu** | Bật `specific_user_account=True` trên cả `website_gift_store` và `website_fashion_store`; chương trình Loyalty, Voucher, hạng thành viên tách biệt theo `website_id`. |
| 3 | **Thanh toán & Vận chuyển VN** | **Ưu tiên miễn phí, bền vững, ai cũng dùng được** | - **VietQR (`wbh_payment_vietqr`)**: Tự sinh QR chuẩn **EMVCo / Napas 247** offline ngay trong Odoo (miễn phí 100%, mọi ngân hàng VN) + Adapter Webhook mặc định **SePay** (gói Free rộng rãi) và mở interface cho PayOS/Casso.<br>- **Vận chuyển (`wbh_delivery_vn`)**: Hỗ trợ sẵn Ship nội bộ/Đồng giá + ưu tiên **GHN** trước (API miễn phí 100%, có Sandbox), sau đó mở rộng GHTK & Viettel Post. |
| 4 | **Cơ sở dữ liệu & Hạ tầng Docker Di Động** | **PostgreSQL `15` + Docker di động 100% trong repo Git** | Mặc định `odoo:19.0` + `postgres:15-bookworm` (hỗ trợ tùy chọn `360ai/postgres:15-ai` kèm `pgvector` trên Local Server). Chạy tạm trên **máy Windows hiện tại** (data trên ổ `F:\` còn `227.22 GB`, port `1901`/`8089`, DB `web_ban_hang_dev`), khi **Local Server ở nhà** khởi động lại chỉ cần `git pull` + `docker compose up -d` + restore backup. Tách biệt hoàn toàn khỏi `demo-19` và `F:\BACKUP_LINUX\save\dev_env\19.0\`. |
| 5 | **Lộ trình ưu tiên** | **3 Milestone theo hướng Catalog-First** | Ưu tiên dựng xong Docker + Backend lõi + Frontend 2 cửa hàng ở **Milestone 1** để Sếp đăng nhập và upload sản phẩm ngay trước khi làm các tính năng chuyên sâu ở Milestone 2 & 3. |

---

## 3. Lộ Trình Triển Khai 3 Milestone & 7 Custom Modules (`addons/`)

Tất cả 7 custom modules đặt trong `F:\BACKUP_LINUX\web_ban_hang\addons\`, **100% thuần Community (0% phụ thuộc Enterprise)**:

| Milestone | Mục tiêu & Giá trị bàn giao | Modules phụ trách | Nhóm phụ thuộc Odoo 19.0 Community |
|---|---|---|---|
| **Milestone 1 — Catalog-First *(LÀM NGAY)*** | Dựng hạ tầng Docker di động (`docker-compose.yml`, `config/odoo.conf`, `.env.example`) + Backend cốt lõi + Giao diện cơ bản 2 Storefronts để Sếp **đăng nhập và up sản phẩm ngay** (danh mục, biến thể màu/size/chất liệu/form/blind box, hiển thị đẹp trên 2 web, giỏ hàng & đặt hàng COD/chuyển khoản cơ bản sẵn có của Odoo). | `wbh_core`<br>`theme_gift_store`<br>`theme_fashion_store` | `base`, `website`, `website_sale`, `website_sale_wishlist`, `website_sale_comparison`, `website_sale_stock`, `sale_management`, `stock`, `product`, `contacts`, `portal` |
| **Milestone 2 — Storefront Features** | Hoàn thiện bộ tính năng đặc thù nâng cao chuyển đổi cho từng ngành hàng:<br>- Web 1: gói quà + thiệp viết tay, cá nhân hóa khắc/thêu tên, so sánh kích thước trực quan, combo theo dịp.<br>- Web 2: gợi ý size thông minh, bộ lọc thời trang nâng cao, Shop The Look thêm trọn bộ 1 click, video mẫu mặc (Cloudflare R2/Stream CDN), luồng yêu cầu đổi size trên Portal. | `wbh_gift_store`<br>`wbh_fashion_store` | `wbh_core`, `website_sale`, `sale_management`, `portal`, `stock` |
| **Milestone 3 — VN Integrations & Growth** | Tự động hóa thanh toán, giao nhận nội địa và giữ chân khách hàng:<br>- VietQR động chuẩn EMVCo + Webhook SePay Free (mở rộng PayOS/Casso).<br>- Vận chuyển Ship nội bộ/Đồng giá + GHN (mở rộng GHTK & Viettel Post).<br>- Tích điểm Loyalty tách riêng từng thương hiệu & Flash Sale đếm ngược. | `wbh_payment_vietqr`<br>`wbh_delivery_vn`<br>*(mở rộng `wbh_core`)* | `payment`, `payment_custom`, `delivery`, `stock_delivery`, `loyalty`, `website_sale_loyalty`, `website_sale` |

---

## 4. Cấu Trúc Thư Mục Chuẩn AIaC 3.0 & Odoo 19.0

```text
F:\BACKUP_LINUX\web_ban_hang\
├── README.md                        # Tổng quan dự án, 5 quyết định chốt, lộ trình 3 Milestone & cây thư mục
├── AGENTS.md                        # Quy chuẩn điều phối Multi-Agent, luật 100% Community & vòng đời 9 bước
├── .gitignore                       # Chuẩn Odoo 19.0 / Python / Docker (KHÔNG ignore .claude/ & .env.example)
├── docker-compose.yml               # [Đã có — M1] Cấu hình Docker di động (odoo:19.0 + postgres:15-bookworm)
├── .env.example                     # [Đã có — M1] Mẫu 11 biến môi trường sạch (copy sang .env khi chạy)
├── config\
│   └── odoo.conf                    # [Đã có — M1] Cấu hình Odoo 19.0 (13 tùy chọn: addons_path, dbfilter, proxy_mode...)
├── .claude\                         # Cấu hình cục bộ Cấp 1 (AIaC — commit kèm repo private, sạch secret)
│   ├── CLAUDE.md                    # Chỉ dẫn cục bộ dự án thuần Odoo 19.0 Community Multi-Store
│   └── settings.local.json          # Cấu hình workspace & metadata AIaC (JSON hợp lệ, không secret)
├── docs\                            # Toàn bộ tài liệu dự án chuẩn AIaC 3.0
│   ├── IDEA.md                      # [v1.2] Bối cảnh, bài toán, 5 quyết định chốt & lộ trình 3 Milestone
│   ├── REQUIREMENTS.md              # [v1.1] Yêu cầu chức năng (FR) & phi chức năng (NFR) theo 3 Milestone
│   ├── ARCH.md                      # [v1.1] Kiến trúc kỹ thuật 100% Community, DB PG 15 & Docker di động
│   ├── CONTEXT.md                   # [v1.0] Bảng thuật ngữ nghiệp vụ (Domain Glossary) chuẩn 360-odoo
│   ├── SPEC.md                      # [v1.0] Đặc tả kỹ thuật chi tiết Milestone 1 sẵn sàng để /build ngay
│   ├── DEPLOY_GUIDE.md              # [v1.0] Hướng dẫn chạy Docker Windows, up sản phẩm & chuyển sang Local Server
│   ├── CHANGELOGS.md                # [v0.3.0] Nhật ký thay đổi các phiên bản dự án
│   └── AUDIT_ROADMAP.md             # [Tạo ở /review-/ship] Checklist kiểm duyệt & bàn giao
├── addons\                          # 7 Custom Modules Odoo 19.0 Community (M1 đã build & qua /code-review)
│   ├── wbh_core\                    # [Đã có — M1] Lõi Multi-Website tách tài khoản, danh mục/thuộc tính & form up SP
│   ├── theme_gift_store\            # [Đã có — M1] Custom Theme Upgrade-Safe Web 1 (Quà tặng)
│   ├── theme_fashion_store\         # [Đã có — M1] Custom Theme Upgrade-Safe Web 2 (Thời trang)
│   ├── wbh_gift_store\              # [M2] Nghiệp vụ đặc thù Web 1 (Gói quà, Cá nhân hóa, So sánh size, Combo)
│   ├── wbh_fashion_store\           # [M2] Nghiệp vụ đặc thù Web 2 (Gợi ý Size, Shop The Look, Video, Đổi size)
│   ├── wbh_payment_vietqr\          # [M3] Thanh toán VietQR EMVCo offline + Webhook SePay Free + COD
│   └── wbh_delivery_vn\             # [M3] Vận chuyển Ship nội bộ/Đồng giá + GHN ➜ GHTK / Viettel Post
└── data\                            # [Ignored trong Git] Dữ liệu runtime cục bộ (filestore/, sessions/)
```

---

## 5. Danh Mục Tài Liệu Dự Án

- **Thông Tin Website & Định Hướng Anime Goods**: [docs/THONG_TIN_WEBSITE.md](docs/THONG_TIN_WEBSITE.md)
- **Hệ Thống Thiết Kế Giao Diện (Design System)**: [DESIGN.md](DESIGN.md)
- **Ý tưởng & 5 Quyết định Chốt**: [docs/IDEA.md](docs/IDEA.md)
- **Yêu cầu Chức năng & Phi chức năng (3 Milestone)**: [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md)
- **Kiến trúc Kỹ thuật Thuần Odoo 19.0 Community**: [docs/ARCH.md](docs/ARCH.md)
- **Bảng Thuật Ngữ Nghiệp Vụ (Domain Glossary)**: [docs/CONTEXT.md](docs/CONTEXT.md)
- **Đặc tả Kỹ thuật Chi tiết Milestone 1 (`/spec`)**: [docs/SPEC.md](docs/SPEC.md)
- **Hướng dẫn Cài đặt, Up Sản Phẩm & Chuyển Server**: [docs/DEPLOY_GUIDE.md](docs/DEPLOY_GUIDE.md)
- **Nhật ký Phiên bản**: [docs/CHANGELOGS.md](docs/CHANGELOGS.md)
- **Quy chuẩn Điều phối Multi-Agent**: [AGENTS.md](AGENTS.md)
- **Chỉ dẫn Cục bộ AIaC**: [.claude/CLAUDE.md](.claude/CLAUDE.md)

---

## 6. Quy Chuẩn Vận Hành & Git (AIaC 3.0)

- **Chính sách tài liệu**: Trước mọi thao tác `git commit` / `git push`, bắt buộc rà soát và cập nhật đồng bộ tài liệu trong `docs/` cùng `description` changelog trong `__manifest__.py` của từng module thay đổi.
- **Git Commit Attribution**: Mọi commit bắt buộc gắn trailer:
  ```text
  Authored-By: 360org <support@360.org.vn>
  ```
- **Commit `.claude/`**: Luôn kiểm tra sạch secret và commit kèm thư mục `.claude/` trong repository private để đồng bộ cấu hình AIaC giữa các máy phát triển.
- **Zero-Bypass Promotion Pipeline**: Mọi thay đổi mã nguồn chỉ đi qua luồng Git (`Dev -> Push -> Local Server Pull/Test -> Production Pull/Deploy/Test live`), tuyệt đối không `rsync`/`scp` vượt cấp và không sửa nóng trực tiếp trên máy chủ.
