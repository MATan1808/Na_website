# CONTEXT — Từ Điển Miền Nghiệp Vụ & Quy Ước Hệ Thống (Domain Glossary)

> **Phiên bản tài liệu**: v1.0  
> **Ngày tạo**: 2026-11-25  
> **Dự án**: Hệ Sinh Thái 2 Website Bán Hàng (`web_ban_hang`) — Thuần **Odoo 19.0 Community (LGPL-3)** + **PostgreSQL 15**  
> **Mục đích**: Chuẩn hóa 100% thuật ngữ nghiệp vụ, khái niệm kiến trúc và quy ước đặt tên kỹ thuật giữa Sếp (PO) và đội ngũ Multi-Agent (Architect, Coder, Code Reviewer, Tester, Reviewer, Shipper) theo chuẩn `360-odoo`.  
> **Tài liệu liên quan**: [IDEA.md](file:///F:/BACKUP_LINUX/web_ban_hang/docs/IDEA.md) | [ARCH.md](file:///F:/BACKUP_LINUX/web_ban_hang/docs/ARCH.md) | [REQUIREMENTS.md](file:///F:/BACKUP_LINUX/web_ban_hang/docs/REQUIREMENTS.md) | [SPEC.md](file:///F:/BACKUP_LINUX/web_ban_hang/docs/SPEC.md)

---

## 1. Thuật Ngữ Kiến Trúc & Chiến Lược Triển Khai

| Thuật ngữ | Định nghĩa & Ngữ cảnh áp dụng trong `web_ban_hang` |
|---|---|
| **Single-Core Multi-Website** | Kiến trúc dùng **1 lõi Odoo 19.0 Community** và **1 cơ sở dữ liệu PostgreSQL 15** để vận hành song song 2 website bán hàng độc lập (2 tên miền, 2 giao diện theme, 2 bộ danh mục hiển thị) nhưng dùng chung 1 Back-office quản trị kho và đơn hàng. |
| **Odoo 19.0 Community (LGPL-3)** | Phiên bản mã nguồn mở miễn phí vĩnh viễn của Odoo 19.0. **Luật cứng của dự án**: 100% custom modules chỉ phụ thuộc vào các module Community chuẩn, tuyệt đối không phụ thuộc bất kỳ module Enterprise (`*_enterprise`, `account_accountant`...) nào. |
| **Catalog-First Strategy** | Chiến lược ưu tiên phát triển theo 3 Milestone do Sếp chốt: hoàn thiện **Milestone 1** (Docker di động + `wbh_core` + 2 themes cơ bản) trước để Sếp có thể nhập liệu, đăng tải sản phẩm và xem live ngay; sau đó mới bồi đắp nghiệp vụ chuyên sâu ở **Milestone 2** và tích hợp Thanh toán/Vận chuyển/Loyalty ở **Milestone 3**. |
| **Portable Docker Stack** | Bộ cấu hình Docker (`docker-compose.yml`, `config/odoo.conf`, `.env.example`) đóng gói 100% bên trong Git repo, không hardcode đường dẫn máy cá nhân, cho phép chạy tạm trên máy Windows (ổ `F:\`) và chuyển nguyên trạng sang Local Server ở nhà chỉ bằng `git pull` + `docker compose up -d` + restore dữ liệu. |
| **Upgrade-Safe Theme (Odoo 19.0)** | Chuẩn thiết kế giao diện Website theo `360-odoo` đảm bảo nâng cấp Odoo không gãy vỡ: dùng wrapper `<div id="wrap" class="oe_structure oe_empty">`, snippet có `o_colored_level` + `data-snippet`, tắt view gốc bằng `data/presets.xml` (`active="False"`), quản lý màu động qua `$o-color-1..5`. |
| **Zero-Bypass Promotion Pipeline** | Luật thép triển khai mã nguồn của AIaC 3.0: chỉ đẩy code theo luồng Git (`Dev Local ➜ Push ➜ Local Server Staging Pull/Test ➜ Production Pull/Deploy`), cấm tuyệt đối `rsync`/`scp` code vượt cấp hoặc sửa code trực tiếp trên máy chủ. |

---

## 2. Thuật Ngữ Đa Website & Tách Thương Hiệu (Multi-Store Isolation)

| Thuật ngữ | Định nghĩa & Ánh xạ Kỹ thuật |
|---|---|
| **Web 1 — Cửa Hàng Quà Tặng** | Thương hiệu bán Móc khóa, Gấu bông & Blind Box. XML ID: `wbh_core.website_gift_store`, loại cửa hàng `wbh_store_type = 'gift'`, chạy giao diện `theme_gift_store` và nghiệp vụ `wbh_gift_store`. |
| **Web 2 — Cửa Hàng Thời Trang** | Thương hiệu bán Quần áo & phụ kiện thời trang. XML ID: `wbh_core.website_fashion_store`, loại cửa hàng `wbh_store_type = 'fashion'`, chạy giao diện `theme_fashion_store` và nghiệp vụ `wbh_fashion_store`. |
| **Tách Tài Khoản Khách Hàng (`specific_user_account`)** | Cờ chuẩn của Odoo Website được đặt cố định `True` trên cả 2 website. Một khách hàng đăng ký tại Web 1 sẽ có tài khoản độc lập hoàn toàn, không tự động đăng nhập sang Web 2 nhằm bảo toàn bản sắc từng thương hiệu. |
| **Tách Loyalty Theo Thương Hiệu** | Mọi chương trình tích điểm, hạng thành viên và voucher (`loyalty.program`) đều gắn chặt `website_id` của Web 1 hoặc Web 2. Điểm tích từ mua quà tặng không dùng chéo sang mua quần áo và ngược lại. |
| **Phạm vi Cửa hàng (`wbh_store_scope`)** | Trường chọn nhanh trên form sản phẩm (`product.template`) gồm 3 giá trị: `gift` (chỉ Web 1), `fashion` (chỉ Web 2), `both` (hiển thị cả 2 website). Tự động đồng bộ trường `website_id` chuẩn của Odoo giúp Sếp nhập liệu không bị nhầm lẫn. |

---

## 3. Thuật Ngữ Miền Ngành Quà Tặng (Web 1 — `wbh_gift_store`)

| Thuật ngữ | Định nghĩa Nghiệp vụ |
|---|---|
| **Blind Box (Hộp mù)** | Sản phẩm sưu tầm đóng hộp kín không biết trước mẫu bên trong. Gồm biến thể **Hộp lẻ (Single Box)** và **Nguyên bộ (Full Set / Case)**; có thể đi kèm tỷ lệ mẫu hiếm (**Secret / Hidden**). |
| **Gói quà & Thiệp viết tay (Gift Wrapping)** | Dịch vụ cộng thêm khi mua quà: khách chọn mẫu hộp quà, màu ruy-băng và nhập nội dung lời chúc in/viết tay lên thiệp. Có cấu hình phụ phí tự động và ngưỡng giá trị đơn để miễn phí gói quà. |
| **Cá nhân hóa sản phẩm (Personalization)** | Cho phép khách nhập tên/ký tự cần khắc lên móc khóa hoặc thêu lên gấu bông, kèm chọn font chữ và vị trí. Dữ liệu gắn trực tiếp vào dòng đơn hàng (`sale.order.line`) và in ra phiếu cho xưởng gia công. |
| **So sánh kích thước trực quan (Visual Size Comparison)** | Thành phần minh họa đặt kích thước thực (cm) của gấu bông/móc khóa bên cạnh vật mẫu quen thuộc (iPhone, chai nước 500ml, người mẫu 1m60) giúp giảm tỷ lệ khách hoàn hàng do hiểu nhầm kích cỡ. |
| **Combo theo dịp & ngân sách** | Nhóm sản phẩm hoặc gói ưu đãi phân loại theo dịp tặng (Sinh nhật, Valentine, 8/3, 20/10, Tốt nghiệp, Giáng sinh) và khung giá (`<200k`, `200k–500k`, `>500k`). |

---

## 4. Thuật Ngữ Miền Ngành Thời Trang (Web 2 — `wbh_fashion_store`)

| Thuật ngữ | Định nghĩa Nghiệp vụ |
|---|---|
| **Color Swatch (Bảng màu trực quan)** | Hiển thị màu sắc thật (mã hex hoặc ảnh họa tiết vải) thay vì chỉ chữ tên màu, giúp khách chọn màu trực quan ngay trên thẻ sản phẩm và bộ lọc. |
| **Form dáng (Fit)** | Kiểu cắt may của trang phục (VD: `Oversize`, `Regular`, `Slim Fit`, `Relaxed`), dùng làm bộ lọc quan trọng và tham số đầu vào cho công cụ gợi ý size. |
| **Gợi ý Size thông minh (Smart Size Advisor)** | Widget OWL cho phép khách nhập **Chiều cao (cm)**, **Cân nặng (kg)** và **Sở thích mặc** (Ôm / Vừa / Rộng) để hệ thống đối chiếu bảng quy đổi và đề xuất size phù hợp nhất ngay trên trang sản phẩm. |
| **Shop The Look (Mix & Match)** | Bộ phối đồ hoàn chỉnh gồm nhiều sản phẩm rời (áo + quần/váy + phụ kiện). Khách có thể chọn màu/size từng món và thêm trọn bộ vào giỏ hàng chỉ bằng 1 thao tác, có thể đi kèm chiết khấu mua theo set. |
| **Video người mẫu dọc 9:16** | Video ngắn phong cách Reels/TikTok quay người mẫu mặc sản phẩm di chuyển thực tế, phát từ CDN (Cloudflare Stream/R2) để khách quan sát độ rủ và co giãn vải. |
| **Yêu cầu đổi size (Size Exchange Request)** | Phiếu khách tự tạo trên lịch sử đơn hàng (Portal) khi muốn đổi size sản phẩm đã nhận; hệ thống kiểm tra tồn kho size mới tức thì và theo dõi minh bạch tiến độ thu hồi/đổi hàng. |

---

## 5. Thuật Ngữ Thanh Toán & Vận Chuyển Việt Nam (Milestone 3)

| Thuật ngữ | Định nghĩa Nghiệp vụ & Kỹ thuật |
|---|---|
| **VietQR EMVCo / Napas 247 Offline** | Chuẩn mã hóa chuỗi QR chuyển khoản nhanh liên ngân hàng tại Việt Nam. Module `wbh_payment_vietqr` tự sinh mã QR trực tiếp trong Python/Odoo (miễn phí 100%, không lệ thuộc bên thứ ba để tạo mã), điền sẵn số tài khoản, đúng số tiền và nội dung chuyển khoản chứa mã đơn duy nhất. |
| **SePay Free Webhook** | Dịch vụ trung gian nhận thông báo biến động số dư ngân hàng qua Webhook với gói miễn phí rộng rãi, được chọn làm adapter đối soát tự động mặc định (mở sẵn interface để cắm thêm PayOS hoặc Casso khi cần). |
| **Idempotency (Tính bất biến giao dịch)** | Nguyên tắc bắt buộc khi xử lý Webhook thanh toán: dù cổng Webhook gửi lặp lại cùng một mã giao dịch ngân hàng nhiều lần, hệ thống chỉ ghi nhận thanh toán và xác nhận đơn hàng **đúng 1 lần duy nhất**. |
| **Quy tắc cọc COD (COD Deposit Rule)** | Cơ chế hạn chế bom hàng đối với các đơn có giá trị lớn hoặc sản phẩm cá nhân hóa khắc/thêu tên (không thể bán lại cho người khác): khóa COD toàn phần hoặc yêu cầu thanh toán VietQR trước. |
| **Địa giới hành chính VN 3 cấp** | Hệ thống phân cấp địa chỉ giao hàng Việt Nam gồm **Tỉnh/Thành phố ➜ Quận/Huyện ➜ Phường/Xã**, được ánh xạ (mapping) mã định danh sang API của GHN, GHTK và Viettel Post. |
| **GHN Free API & Sandbox** | Giao Hàng Nhanh — hãng vận chuyển nội địa được ưu tiên tích hợp đầu tiên ở Milestone 3 do cung cấp API miễn phí 100% cùng môi trường Sandbox đầy đủ để kiểm thử tự động trước khi lên thật. |

---

## 6. Quy Ước Đặt Tên Kỹ Thuật (Naming Conventions)

Mọi mã nguồn sinh ra ở bước `/build` bắt buộc tuân thủ quy ước nhất quán sau:

| Đối tượng | Quy ước Đặt tên | Ví dụ Chuẩn |
|---|---|---|
| **Tên Custom Modules** | Prefix `wbh_` cho module nghiệp vụ; `theme_` cho module giao diện | `wbh_core`, `wbh_gift_store`, `wbh_fashion_store`, `wbh_payment_vietqr`, `wbh_delivery_vn`, `theme_gift_store`, `theme_fashion_store` |
| **Tên Model Odoo mới** | Prefix `wbh.` dùng chữ thường ngăn cách bằng dấu chấm | `wbh.size.chart`, `wbh.size.exchange.request`, `wbh.lookbook`, `wbh.gift.box` |
| **Tên Trường mở rộng** | Prefix `wbh_` trên các model core kế thừa (`product.template`, `website`, `sale.order.line`...) | `wbh_store_scope`, `wbh_short_highlight`, `wbh_care_note`, `wbh_store_type` |
| **XML ID** | `<tên_module>.<mô_tả_ngắn_rõ_nghĩa>` | `wbh_core.website_gift_store`, `wbh_core.attr_color_swatch`, `theme_gift_store.s_gift_hero` |
| **CSS / SCSS Class & Slot** | Prefix `wbh-` hoặc `s_gift_` / `s_fashion_` cho snippet; `#wbh_*_slot` cho extension slot | `.wbh-product-highlight`, `.s_gift_occasion_bar`, `#wbh_fashion_size_advisor_slot` |
| **Phiên bản Module** | `19.0.<major>.<minor>.<patch>` | `19.0.1.0.0` |
| **Docker & Database** | `CLIENT_NAME=web-ban-hang`, DB `web_ban_hang_<env>`, Volume `web_ban_hang_pgdata` | `web_ban_hang_dev`, `web_ban_hang_staging`, `web_ban_hang_prod` |
