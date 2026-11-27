# IDEA — Hệ Sinh Thái 2 Website Bán Hàng (E-Commerce Multi-Store)

> **Trạng thái**: v1.2 — Đã chốt toàn bộ 5 quyết định kiến trúc & lộ trình 3 Milestone (Catalog-First)  
> **Ngày tạo**: 2026-11-25 | **Cập nhật lần cuối**: 2026-11-25  
> **Bước quy trình**: `/idea` (Đã duyệt) ➜ `/req` (Đã duyệt) ➜ `/spec` (Sẵn sàng) ➜ `/plan` ➜ `/build` ➜ `/code-review` ➜ `/test` ➜ `/review` ➜ `/ship`  
> **Tài liệu liên quan**: [ARCH.md](file:///F:/BACKUP_LINUX/web_ban_hang/docs/ARCH.md) | [REQUIREMENTS.md](file:///F:/BACKUP_LINUX/web_ban_hang/docs/REQUIREMENTS.md) | [CONTEXT.md](file:///F:/BACKUP_LINUX/web_ban_hang/docs/CONTEXT.md) | [SPEC.md](file:///F:/BACKUP_LINUX/web_ban_hang/docs/SPEC.md) | [DEPLOY_GUIDE.md](file:///F:/BACKUP_LINUX/web_ban_hang/docs/DEPLOY_GUIDE.md) | [README.md](file:///F:/BACKUP_LINUX/web_ban_hang/README.md)

---

## 1. Bối Cảnh (Context)

Thương mại điện tử tại Việt Nam ngày càng cạnh tranh khốc liệt trên các sàn (Shopee, TikTok Shop, Lazada) với biên lợi nhuận bị bào mòn bởi phí sàn, phụ thuộc thuật toán và khó sở hữu dữ liệu khách hàng trực tiếp (First-party Data).

Xây dựng **hệ sinh thái website bán hàng độc lập (D2C Multi-Store)** giúp doanh nghiệp:
- Chủ động thương hiệu, trải nghiệm mua sắm và chính sách chăm sóc khách hàng.
- Tối ưu hóa chuyển đổi riêng biệt cho **2 ngành hàng có hành vi mua sắm hoàn toàn khác nhau**:
  1. **Quà tặng — Móc khóa, Gấu bông & Blind Box** (mua theo cảm xúc, dịp lễ, cá nhân hóa cao).
  2. **Thời trang Quần áo** (mua theo nhu cầu mặc đẹp, nhạy cảm về size, form dáng, chất liệu và đổi trả).
- Tận dụng **1 hệ thống quản trị lõi duy nhất (Shared Core E-commerce Engine)** để quản lý tập trung kho, đơn hàng, vận chuyển, thanh toán và CRM — giảm chi phí vận hành và tránh phân mảnh dữ liệu.

---

## 2. Bài Toán Cần Giải Quyết (Problem Statement)

### 2.1. Với ngành Quà tặng (Web 1)
- Khách hàng thường bối rối không biết chọn quà gì theo dịp (sinh nhật, Valentine, tốt nghiệp, kỷ niệm) và ngân sách.
- Ảnh chụp gấu bông/phụ kiện dễ gây hiểu nhầm về kích thước thực tế khi nhận hàng.
- Nhu cầu **đóng gói quà đẹp, kèm thiệp viết tay, khắc/thêu tên** rất cao nhưng các website bán hàng thông thường không có luồng tùy chỉnh (customization) mượt mà, buộc khách phải nhắn tin thủ công qua Zalo/Messenger gây rớt đơn.

### 2.2. Với ngành Thời trang (Web 2)
- Tỷ lệ hoàn/đổi hàng cao nhất trong ngành thời trang đến từ việc **chọn sai size** và **hình ảnh không thể hiện đúng form dáng/độ rủ của vải**.
- Khách hàng có xu hướng mua theo bộ (phối sẵn) nhưng khó tìm từng món rời để ghép set.
- Thiếu công cụ lọc trực quan theo bảng màu thật, form dáng (oversize, slim, regular...) và chất liệu.

### 2.3. Với vận hành doanh nghiệp (Back-office)
- Nếu làm 2 website tách rời hoàn toàn sẽ tốn gấp đôi chi phí phát triển và bảo trì hạ tầng, khó quản trị tồn kho & xử lý đơn tập trung.
- Tuy nhiên về mặt thương hiệu, 2 cửa hàng phục vụ hai tệp cảm xúc khác nhau nên **tài khoản khách hàng và tích điểm thành viên cần tách riêng theo từng thương hiệu**, trong khi vẫn chung 1 màn hình Back-office cho đội vận hành.
- Cần tự động hóa đối soát thanh toán (VietQR động chuẩn EMVCo/Napas 247 + SePay Free) và đẩy đơn sang các hãng vận chuyển nội địa (ưu tiên GHN miễn phí API, mở rộng GHTK & Viettel Post) với chi phí nền tảng tối ưu nhất (miễn phí, bền vững lâu dài).

---

## 3. Ý Tưởng Cốt Lõi (Core Concept)

Xây dựng kiến trúc **Multi-Website + Single Core Engine thuần Odoo 19.0 Community (LGPL-3)**:
- **2 Giao diện bán hàng (Storefronts) độc lập về nhận diện thương hiệu** (domain riêng, bảng màu, font chữ, UX/UI chuyên biệt cho từng ngành hàng thông qua 2 Custom Theme Modules `theme_gift_store` và `theme_fashion_store`, tách riêng tài khoản & Loyalty theo từng website).
- **1 Hệ thống quản trị lõi (Core E-commerce Engine)** trên **Odoo 19.0 Community** quản lý chung sản phẩm, biến thể, tồn kho, đơn hàng, thanh toán và vận chuyển.

### 3.1. Web 1 — Cửa Hàng Quà Tặng: Móc Khóa, Gấu Bông & Blind Box 🧸
- **Chân dung khách hàng**: Gen Z, học sinh – sinh viên, nhân viên văn phòng trẻ (16–30 tuổi), mua làm quà tặng người yêu/bạn bè hoặc sưu tầm (blind box).
- **Trải nghiệm đặc thù**:
  - **Dịch vụ gói quà & thiệp viết tay**: Chọn mẫu hộp quà, màu ruy-băng, nhập lời chúc trực tiếp tại trang sản phẩm hoặc giỏ hàng (tính phụ phí tự động hoặc miễn phí theo ngưỡng đơn).
  - **Cá nhân hóa sản phẩm (Personalization)**: Nhập tên/ký tự muốn khắc lên móc khóa hoặc thêu lên gấu bông, chọn font chữ/vị trí, có xem trước (live preview) hoặc ghi chú chuẩn hóa cho xưởng.
  - **So sánh kích thước trực quan**: Hiển thị tỷ lệ gấu bông/phụ kiện cạnh vật mẫu quen thuộc (chai nước, iPhone, chiều cao người mẫu 1m60...) giúp khách hình dung chính xác.
  - **Combo quà tặng theo dịp**: Bộ sưu tập gợi ý sẵn theo dịp lễ (Sinh nhật, Valentine, 8/3, 20/10, Tốt nghiệp, Giáng sinh) và theo mức giá (dưới 200k, 200k–500k, trên 500k).

### 3.2. Web 2 — Cửa Hàng Thời Trang Quần Áo 👗
- **Chân dung khách hàng**: Nam/Nữ trẻ yêu thời trang (18–35 tuổi), thường xuyên mua sắm online trên mobile.
- **Trải nghiệm đặc thù**:
  - **Bảng quy đổi & Gợi ý Size thông minh**: Nhập Chiều cao + Cân nặng + Sở thích mặc (ôm / vừa / rộng) để hệ thống đề xuất size phù hợp ngay trên trang sản phẩm.
  - **Bộ lọc thời trang chuyên sâu**: Lọc theo bảng màu trực quan (color swatch), form dáng, chất liệu vải, dịp mặc và khoảng giá.
  - **Shop The Look (Mix & Match)**: Hiển thị ảnh/lookbook phối đồ hoàn chỉnh, cho phép khách chọn size từng món và thêm trọn bộ vào giỏ hàng chỉ trong 1 bước (có thể kèm ưu đãi mua theo set).
  - **Video người mẫu chuyển động thực tế**: Tích hợp video ngắn (dạng Reels/TikTok dọc) ngay trong gallery sản phẩm để khách thấy độ rủ, co giãn và form dáng thật khi di chuyển.
  - **Chính sách & Luồng đổi size nhanh**: Cho phép khách tạo yêu cầu đổi size trực tiếp trên lịch sử đơn hàng, minh bạch trạng thái đổi trả.

### 3.3. Hệ Thống Cốt Lõi (Core E-commerce Engine) ⚙️
- **Catalog & Biến thể (Variants)**: Quản lý thuộc tính linh hoạt theo từng store (Màu sắc Color Swatch, Size quần áo, Kích thước gấu bông cm, Chất liệu, Form dáng, Dịp tặng quà, Phiên bản Blind Box).
- **Quản lý Kho (Inventory)**: Tồn kho theo từng SKU/biến thể, trừ kho khi đặt hàng, cảnh báo sắp hết hàng.
- **Giỏ hàng & Thanh toán**:
  - Hỗ trợ **COD** và **VietQR động chuẩn EMVCo / Napas 247** (tự sinh QR offline miễn phí 100% cho mọi ngân hàng VN + đối soát webhook tự động mặc định qua **SePay Free**, mở rộng PayOS/Casso).
- **Tích hợp Vận chuyển**: Hỗ trợ sẵn **Ship nội bộ / Đồng giá**, ưu tiên tích hợp **GHN** (API miễn phí 100%, có Sandbox test), sau đó mở rộng **GHTK & Viettel Post**.
- **CRM, Tích điểm & Khuyến mãi**:
  - Tài khoản thành viên & chương trình Loyalty **tách riêng hoàn toàn theo từng thương hiệu** (`specific_user_account=True` trên từng website).
  - Mã giảm giá (Voucher), giảm giá theo Combo/Set, chương trình **Flash Sale** có đếm ngược.

---

## 4. Mục Tiêu Kinh Doanh & Thước Đo Thành Công (Goals & Metrics)

- **Sẵn sàng nhập hàng sớm (Catalog-First)**: Đưa hệ thống Backend + 2 Storefronts lên chạy sớm nhất ở Milestone 1 để Sếp chủ động nhập liệu danh mục, ảnh, giá và biến thể sản phẩm song song với quá trình phát triển tính năng nâng cao.
- **Tỷ lệ chuyển đổi (Conversion Rate)**: Tăng chuyển đổi trên mobile nhờ luồng mua nhanh, gợi ý size/quà rõ ràng và thanh toán VietQR 1 chạm.
- **Giá trị đơn hàng trung bình (AOV)**: Tăng AOV thông qua Combo quà tặng + phụ phí gói quà (Web 1) và Shop The Look (Web 2).
- **Giảm tỷ lệ hoàn/đổi hàng**: Giảm đơn hoàn do nhầm kích thước gấu bông (Web 1) và sai size quần áo (Web 2).
- **Tối ưu chi phí vận hành lâu dài**: 100% mã nguồn mở **Odoo 19.0 Community (LGPL-3)** miễn phí bản quyền vĩnh viễn, sử dụng VietQR EMVCo + SePay Free và GHN API miễn phí.

---

## 5. Lộ Trình Triển Khai 3 Milestone (Catalog-First Roadmap)

### Milestone 1 — Nền Tảng Catalog-First: Hạ Tầng + Backend Cốt Lõi + 2 Storefronts Cơ Bản *(ƯU TIÊN LÀM NGAY)*
- **Mục tiêu**: Sếp đăng nhập được vào Backend quản trị và **upload sản phẩm lên ngay** cho cả 2 cửa hàng, xem hiển thị live đẹp trên 2 giao diện riêng biệt và đặt hàng thử được ngay.
- **Phạm vi**:
  - Hạ tầng Docker di động 100% trong Git repo (`docker-compose.yml`, `config/odoo.conf`, `.env.example`) chạy tạm trên máy Windows (đặt data trên ổ `F:\`), sẵn sàng chuyển sang Local Server chỉ bằng `git pull` + `docker compose up -d`.
  - Module **`wbh_core`**: Khởi tạo 2 Website độc lập (`website_gift_store`, `website_fashion_store` với `specific_user_account=True`), bộ danh mục sản phẩm mẫu, bộ 7 thuộc tính biến thể (Màu sắc Color Swatch, Size quần áo, Kích thước gấu bông cm, Chất liệu, Form dáng, Dịp tặng quà, Phiên bản Blind Box), form upload sản phẩm tối ưu cho Sếp.
  - 2 Custom Theme Upgrade-Safe giai đoạn 1 (**`theme_gift_store`**, **`theme_fashion_store`**): Trang chủ, header/footer riêng từng thương hiệu, trang Shop có bộ lọc thuộc tính/màu rõ ràng, trang chi tiết sản phẩm tối ưu mobile, giỏ hàng & checkout cơ bản (COD / chuyển khoản có sẵn của Odoo 19.0 Community).

### Milestone 2 — Nghiệp Vụ Đặc Thù Từng Cửa Hàng *(LÀM SAU MILESTONE 1)*
- **Web 1 (`wbh_gift_store`)**: Dịch vụ gói quà + thiệp viết tay (phụ phí & ngưỡng miễn phí), cá nhân hóa khắc/thêu tên, so sánh kích thước trực quan cạnh vật mẫu, combo quà tặng theo dịp & ngân sách.
- **Web 2 (`wbh_fashion_store`)**: Công cụ gợi ý Size thông minh (Chiều cao/Cân nặng/Sở thích mặc), Shop The Look (chọn size từng món & thêm trọn bộ 1 click), tích hợp Video người mẫu chuyển động dọc 9:16 từ CDN, luồng yêu cầu đổi size nhanh trên Portal.

### Milestone 3 — Thanh Toán VN, Vận Chuyển VN & Tăng Trưởng *(LÀM SAU MILESTONE 2)*
- **Thanh toán (`wbh_payment_vietqr`)**: Tự sinh mã VietQR chuẩn EMVCo / Napas 247 offline (miễn phí 100%, mọi ngân hàng VN) + Webhook tự động đối soát mặc định **SePay Free** (mở interface cho PayOS/Casso) + quy tắc cọc COD đơn cá nhân hóa.
- **Vận chuyển (`wbh_delivery_vn`)**: Ship nội bộ/Đồng giá + tích hợp **GHN** (API miễn phí, có Sandbox) trước, mở rộng **GHTK & Viettel Post** + danh mục địa giới hành chính VN 3 cấp.
- **Tăng trưởng**: Loyalty & hạng thành viên tách riêng từng thương hiệu, Flash Sale có đếm ngược & giới hạn suất, offload media Cloudflare R2, báo cáo doanh thu/tồn kho chuyên sâu (và cân nhắc tích hợp CSKH Zalo OA từ `F:\BACKUP_LINUX\zalo_socal`).

---

## 6. Quyết Định Công Nghệ & Đánh Giá Hạ Tầng Sẵn Có

### 6.1. Quyết định Kiến trúc: 100% Thuần Odoo 19.0 Community (LGPL-3)

Dự án chốt triển khai **100% thuần Odoo 19.0 Community (LGPL-3, miễn phí bản quyền vĩnh viễn)**, TUYỆT ĐỐI không phụ thuộc vào bất kỳ module Enterprise nào (`*_enterprise`, `account_accountant`...).

| Thành phần | Công nghệ & Phiên bản đã chốt | Ghi chú triển khai |
|---|---|---|
| **Backend Core** | **Odoo 19.0 Community (LGPL-3)** (Python `3.12`, ORM chuẩn 19.0) | 0% phụ thuộc Enterprise; chỉ dùng module Community chuẩn (`website_sale`, `stock`, `sale_management`, `loyalty`, `crm`, `delivery`, `payment`). |
| **Frontend Storefronts** | **Odoo QWeb + OWL `2.8.4` + Bootstrap `5.3.3` + SCSS** | 2 Custom Theme độc lập (`theme_gift_store`, `theme_fashion_store`) chuẩn Website Builder upgrade-safe. |
| **Database** | **PostgreSQL 15** (`postgres:15-bookworm` mặc định di động / tùy chọn `360ai/postgres:15-ai` kèm `pgvector`) | Database & Docker volume tách biệt hoàn toàn (`web_ban_hang_dev` / `web_ban_hang_prod`, `web_ban_hang_pgdata`). |
| **Media & Video CDN** | **Cloudflare R2** (S3 API qua `boto3`) + **Cloudflare Stream/CDN** | Ảnh nặng & video người mẫu dọc 9:16 lưu ngoài Filestore để tối ưu tốc độ mobile (kích hoạt mở rộng ở M2/M3). |
| **Custom Modules** | 7 module tại `F:\BACKUP_LINUX\web_ban_hang\addons\` | M1: `wbh_core`, `theme_gift_store`, `theme_fashion_store` ➜ M2: `wbh_gift_store`, `wbh_fashion_store` ➜ M3: `wbh_payment_vietqr`, `wbh_delivery_vn`. |

### 6.2. Đánh giá Thực tế Hạ tầng Odoo trên Máy Sếp & Khả năng Tái sử dụng

Kết quả khảo sát thực tế trên máy Windows hiện tại cho thấy:
- **Runtime trên Windows Host**: Chưa cài Odoo native, chưa cài PostgreSQL native, chưa cài Docker Desktop (`docker not found`), không có tiến trình nào chạy trên các port (`5432`, `8069`, `8070`, `8072`, `8079`, `8080`, `1900`). Entry WSL2 `VCloudOdoo19` đang hỏng do thiếu `F:\BACKUP_LINUX\local_odoo19\wsl_distro`. Ổ `F:\` còn trống `227.22 GB` (phù hợp đặt source & Docker data), ổ `C:\` còn `24.77 GB`.
- **Kho hạ tầng Odoo Docker có sẵn**: Có 3 bộ môi trường `19.0`, `17.0`, `15.0` tại `F:\BACKUP_LINUX\save\dev_env\`.
- **Chiến lược Tái sử dụng kết hợp Di động (Portable Docker)**:
  - **Tái sử dụng**: Tham khảo mẫu cấu hình `odoo.conf` / Dockerfile từ `F:\BACKUP_LINUX\save\dev_env\19.0\` (loại bỏ bind mount Linux cứng `/media/tanma/DATA/save/mobile_versions:...`), và chỉ tham khảo read-only phần mã nguồn Community trong `F:\BACKUP_LINUX\save\dev_env\19.0\origin\addons\` (1.474 modules gồm cả Enterprise — **tuyệt đối lọc sạch, không khai báo phụ thuộc Enterprise**). Khi chạy container chính thức, dùng trực tiếp image chuẩn `odoo:19.0` Community để đảm bảo di động 100% giữa Windows và Local Server.
  - **Bắt buộc tách riêng**: Database (`web_ban_hang_dev` / `web_ban_hang_prod`, `DB_FILTER=^web_ban_hang.*$`), Docker volume (`web_ban_hang_pgdata`), Filestore/Sessions riêng, Custom Addons tại `F:\BACKUP_LINUX\web_ban_hang\addons\`, Container (`CLIENT_NAME=web-ban-hang`) & dải port riêng (`1901`/`8089`, Longpolling `7089`, DB Host `51901`) — không đụng `demo-19` hay `F:\DEV\v_mobile`.

---

## 7. Tổng Hợp 5 Quyết Định Đã Chốt (Closed Decisions — 2026-11-25)

Toàn bộ các câu hỏi mở đã được Sếp chốt dứt điểm, sẵn sàng chuyển thẳng sang bước `/spec` và `/build`:

| # | Hạng mục | Quyết định Đã Chốt | Trạng thái |
|---|---|---|---|
| 1 | **Edition Odoo** | **100% Odoo 19.0 Community (LGPL-3, miễn phí vĩnh viễn)**. Cấm tuyệt đối phụ thuộc module `*_enterprise` / `account_accountant`. | Đã chốt |
| 2 | **Tài khoản & Tích điểm Loyalty** | **Tách riêng hoàn toàn theo từng thương hiệu** (`specific_user_account=True` trên từng `website`, tách chương trình Loyalty theo `website_id`). | Đã chốt |
| 3 | **Thanh toán & Vận chuyển VN** | **VietQR**: Tự sinh QR chuẩn EMVCo/Napas 247 offline (miễn phí 100%) + Webhook mặc định **SePay Free** (mở interface cho PayOS/Casso). **Vận chuyển**: Ship nội bộ/Đồng giá + ưu tiên **GHN** (API miễn phí, có Sandbox) ➜ mở rộng GHTK & Viettel Post. | Đã chốt |
| 4 | **Hạ tầng Dev & Di động** | Đóng gói **Docker di động 100% trong Git repo** — chạy tạm trên máy Windows hiện tại (đặt data trên ổ `F:\`), khi Local Server ở nhà hoạt động lại chỉ cần `git pull` + `docker compose up -d`. | Đã chốt |
| 5 | **Lộ trình ưu tiên (Catalog-First)** | **Milestone 1** (Docker + `wbh_core` + `theme_gift_store` + `theme_fashion_store` để Sếp up sản phẩm ngay) ➜ **Milestone 2** (`wbh_gift_store` + `wbh_fashion_store`) ➜ **Milestone 3** (`wbh_payment_vietqr` + `wbh_delivery_vn` + Loyalty + Flash Sale). | Đã chốt |
