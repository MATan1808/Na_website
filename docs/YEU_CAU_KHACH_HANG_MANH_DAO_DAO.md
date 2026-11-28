# Yêu Cầu Chỉnh Sửa Từ Khách Hàng — Manh Dao Dao Shop (`CR-M1.5`)

> **Ngày tiếp nhận**: `2026-11-28`  
> **Nguồn dữ liệu**: Tổng hợp trực tiếp từ **11 ảnh chụp phản hồi & logo mới** của khách hàng (`Manh Dao Dao`)  
> **Phạm vi áp dụng**: **Web 1 — Manh Dao Dao** (`wbh_core` `v19.0.1.3.0`, `theme_gift_store` `v19.0.1.4.0`, `wbh_payment_vietqr` `v19.0.1.1.0`, `wbh_delivery_vn` `v19.0.1.1.0`)  
> **Trạng thái**: **Đã triển khai mã nguồn & kiểm định tĩnh (`v0.4.1`) — sẵn sàng nâng cấp lên Local Server** *(chạy `addons/wbh_core/scripts/apply_cr_manhdaodao.py` sau khi upgrade 4 module)*

---

## 1. Nguyên Tắc Chung Áp Dụng Toàn Website

1. **Định vị thương hiệu mới**: Đổi sang **`Manh Dao Dao - Boku no Hero Academia Anime Goods Shop`** (tập trung goods *Boku no Hero Academia*, bỏ chữ *"Quà Tặng"* chung chung).
2. **Slogan xuyên suốt**: **`🍊 Tiền trao tay, quýt về ngay`** (biểu tượng quả cam/quýt thay cho biểu tượng hộp quà).
3. **Kênh liên hệ duy nhất (Luật cứng toàn site)**: **Bỏ hoàn toàn Zalo và Số điện thoại (`0900 000 001`)** ở mọi nơi (Topbar, Menu nổi Tư vấn, Trang sản phẩm, Giỏ hàng, Footer) — **chỉ giữ Facebook (gắn link FB chủ shop) và Chat trực tiếp trên Web**.
4. **Nhận diện & Bảng màu mới**:
   - Đổi biểu tượng logo sang **mèo đen mắt xanh dương + lựu đạn xanh dương** (từ 2 file logo mới khách gửi), giữ nguyên phần chữ `MANH DAO DAO · ANIME GOODS SHOP`.
   - Đổi tone màu nền & màu nhấn toàn site từ kem–đỏ rượu sang **tone xanh dương hoặc đen** đồng bộ với logo mới.

---

## 2. Bảng Chi Tiết Yêu Cầu Theo Từng Màn Hình (`CR-01` ➜ `CR-10`)

| Mã YC | Màn hình / Khu vực | Hiện trạng trên Web | Yêu cầu chỉnh sửa của khách hàng | Ảnh nguồn |
|---|---|---|---|---|
| **`CR-01`** | **Topbar & Header** | - Slogan: *Gửi trọn cảm xúc trong từng món quà nhỏ*<br>- Có SĐT `0900 000 001`<br>- Nút `Zalo CSKH`<br>- Logo nhân vật anime nữ tóc xanh<br>- Nền kem + tone đỏ rượu | - Đổi slogan thành **`🍊 Tiền trao tay, quýt về ngay`** (icon quả cam/quýt).<br>- **Xóa** số điện thoại `0900 000 001`.<br>- Đổi nút `Zalo CSKH` ➜ **`Facebook CSKH`** (gắn link FB chủ shop).<br>- **Chỉ đổi biểu tượng logo** sang logo mèo đen + lựu đạn xanh dương; **giữ nguyên chữ** `MANH DAO DAO · ANIME GOODS SHOP`.<br>- Đổi màu nền / bảng màu chủ đạo sang **tone xanh dương hoặc đen**. | Ảnh 1, 2, 3 |
| **`CR-02`** | **Trang chủ (Hero Banner) & Nút Tư vấn nổi** | - Nhãn nhỏ: `Manh Dao Dao · Anime Goods & Cotton Doll 20cm`<br>- H1: `Cotton Doll 20cm và phụ kiện Anime tuyển chọn, sẵn hàng giao ngay`<br>- Mô tả về doll, card, can badge...<br>- Có 2 nút: `Xem bộ sưu tập →` và `Cotton Doll 20cm`<br>- Trust badge: `Đóng hộp chống sốc kỹ`<br>- Widget `Tư vấn`: Chat Web, Facebook, Zalo, SĐT | - Nhãn nhỏ: **`Manh Dao Dao . Boku no Hero Academia Anime Goods Shop`**.<br>- H1: **`Doll và các loại goods Boku no Hero, hàng sẵn giao ngay`** *(lưu ý xác nhận lại chữ cuối `ngay` do mép ảnh cắt sát)*.<br>- Mô tả: **`Gồm doll, card các loại, postcard (pc), clear file, bookmark, standee, key, badge...`**.<br>- **Xóa** nút phụ `Cotton Doll 20cm` (chỉ giữ nút `Xem bộ sưu tập →`).<br>- Trust badge: giữ `Ảnh chụp sản phẩm thật`, đổi dòng 2 thành **`Gói an toàn, chống sốc kỹ`**.<br>- Menu nổi `Tư vấn`: giữ `Chat tại Web`, giữ `Nhắn Facebook` (**gắn link FB của chủ shop**), **xóa** `Nhắn Zalo` và **xóa** `0900 000 001`. | Ảnh 4 |
| **`CR-03`** | **Chân trang (Footer)** | - Tiêu đề & Bản quyền: `Manh Dao Dao — Anime Goods & Quà Tặng`<br>- Slogan: *Gửi trọn cảm xúc trong từng món quà nhỏ*<br>- Có nút `0900 000 001` và `Zalo tư vấn quà` | - Đổi tên thương hiệu & dòng bản quyền thành **`Manh Dao Dao - Boku no Hero Academia Anime Goods Shop`**.<br>- Đổi slogan thành **`Tiền trao tay, quýt về ngay`**.<br>- **Xóa hết** nút `0900 000 001` và `Zalo tư vấn quà` — **chỉ để kênh Facebook**. | Ảnh 5 |
| **`CR-04`** | **Trang Cửa hàng `/shop` (Sidebar Bộ lọc)** | - Nhóm lọc `Gói Phân Loại`<br>- Nhóm lọc `Mẫu Thẻ Sưu Tầm`<br>- Khoảng giá: `15.000,00 ₫` – `380.000,00 ₫` | - Đổi tên nhóm lọc `Gói Phân Loại` ➜ **`Loại goods`**.<br>- **Xóa / ẩn hoàn toàn** nhóm lọc `Mẫu Thẻ Sưu Tầm`.<br>- Thanh `Khoảng giá`: **bỏ 2 số 0 thập phân cuối (`,00`)** ➜ hiển thị `15.000 ₫` – `380.000 ₫`. | Ảnh 7 |
| **`CR-05`** | **Phân loại sản phẩm (`Loại goods`)** | Đang dùng tên thuộc tính `Gói Phân Loại` với giá trị hỗn hợp | - Chủ shop hỏi **có tự cài được phân loại không** ➜ **Có** (chủ shop tự thêm/sửa/xóa ngay trong Odoo).<br>- Cài sẵn bộ 8 phân loại chuẩn theo yêu cầu khách:<br>`CARD`, `POSTCARD (PC)`, `STANDEE`, `KEY`, `FIGURE`, `BADGE`, `CLEAR FILE`, `KHÁC` *(có thể bổ sung `DOLL` nếu cần)*. | Ảnh 6, 7 |
| **`CR-06`** | **Trang Chi tiết sản phẩm (PDP)** | - Chính sách mặc định (*Điều khoản và điều kiện / Đảm bảo hoàn tiền 30 ngày / Giao hàng 2-3 ngày*)<br>- Có hộp gập *Hướng dẫn bảo quản & Lưu ý quà tặng*<br>- Khối tư vấn: *Cần xem ảnh thật hoặc tư vấn chọn hàng?*, có SĐT & Zalo | - Thay 3 dòng chính sách mặc định bằng **4 dòng quy định của shop**:<br>  1. `Hàng mddf, df nặng sẽ note`<br>  2. `Đi đơn vào chủ nhật hàng tuần`<br>  3. `Quay video khi unbox, chỉ giải quyết khi có video`<br>  4. `Đvvc: Viettel Post`<br>- **Xóa hoàn toàn** khối gập *Hướng dẫn bảo quản & Lưu ý quà tặng*.<br>- Khối tư vấn: đổi tiêu đề thành **`Cần vid check hoặc tư vấn chọn hàng?`**; **xóa** `0900 000 001` và **xóa** `Nhắn Zalo` (chỉ giữ `Chat tại Web`, `Nhắn Facebook`, `Chép tên & link SP`). | Ảnh 6 |
| **`CR-07`** | **Trang Giỏ hàng (`/shop/cart`)** | - Hiển thị dòng `Thuế` (`3.000 ₫`)<br>- Khối tư vấn giống PDP | - Đổi dòng `Thuế` thành **`Phí gói`**, cài mặc định **`5.000đ`** *(hiện thị 5.000 ₫ thay cho thuế %)*.<br>- Đồng bộ bỏ SĐT `0900 000 001`, bỏ `Nhắn Zalo` và đổi tiêu đề sang **`Cần vid check hoặc tư vấn chọn hàng?`**. | Ảnh 8 |
| **`CR-08`** | **Trang Điền thông tin đặt hàng (`/shop/address`)** | Form mặc định Odoo gồm: *Tên của bạn, Email, Điện thoại, Tên công ty, Mã số thuế, Đường và số, Căn hộ, Thành phố, Mã Zip, Quốc gia...* | - Đổi `Tên của bạn *` ➜ **`Tên fb`** (bắt buộc).<br>- Đổi `Email *` ➜ **`Link fb`** (bắt buộc).<br>- Đổi `Điện thoại *` ➜ **`Thông tin ship (Tên, sđt, địa chỉ cũ không ghi tắt)`**.<br>- **Xóa / ẩn** các trường thừa: `Tên công ty`, `Mã số thuế`, `Đường và số *`, `Căn hộ, phòng suite,...`, `Thành phố *` (ô text cũ), `Mã Zip *`, `Quốc gia`.<br>- **Giữ lại 3 ô chọn địa giới hành chính Việt Nam**: **`Tỉnh/TP`**, **`Quận/Huyện`**, **`Phường/Xã`**. | Ảnh 9 |
| **`CR-09`** | **Trang Giao hàng & Phương thức thanh toán (`/shop/checkout`)** | - Có *Giao hàng tiêu chuẩn (Đồng giá 30.000đ - Freeship từ 300.000đ)* và *Gom đơn / Giữ hàng tại shop (0đ ship)*<br>- Hỗ trợ COD + chuyển khoản | - **Xóa** 2 phương thức vận chuyển cũ (*Đồng giá 30k / Gom đơn 0đ*).<br>- Chỉ giữ **1 phương thức vận chuyển**: **`ĐVVC VIETTEL POST`** — phí ship **`Từ 12.000đ – 20.000đ tùy tỉnh thành`**.<br>- **Chỉ bật duy nhất 1 phương thức thanh toán**: **Chuyển khoản trước rồi ship (`CK trước`)** — **tắt hoàn toàn thanh toán khi nhận hàng (COD)**. | Ảnh 10 |
| **`CR-10`** | **Trang Thanh toán cuối (`/shop/payment`)** | Đang hiển thị cảnh báo *"Không có phương thức thanh toán nào khả dụng"* | - Hiển thị **ảnh mã QR chuyển khoản của chủ shop** ngay tại bước thanh toán.<br>- Thêm **mục tải ảnh chụp màn hình chuyển khoản (`Upload bill CK`)** để khách gửi ảnh xác nhận ngay trên đơn hàng. | Ảnh 11 |

---

## 3. Lưu Ý Kỹ Thuật Khi Triển Khai Trên Odoo 19.0 Community

1. **Ô `Link fb` thay cho `Email *` ở `/shop/address` (`CR-08`)**:
   - Trong Odoo core, controller `/shop/address` kiểm tra định dạng email (`@`). Nếu khách nhập URL Facebook (`https://facebook.com/...`), cần điều chỉnh validation ở controller/form của `wbh_core` để nhận URL hợp lệ vào trường `wbh_facebook_url` (hoặc lưu thay thế/sinh email kỹ thuật nội bộ sạch sẽ, không chặn đơn).
   - Ẩn `Quốc gia` nhưng tự gán ngầm `country_id = base.vn` để bộ chọn **3 cấp địa giới Việt Nam (`Tỉnh/TP` ➜ `Quận/Huyện` ➜ `Phường/Xã`)** của `wbh_delivery_vn` hoạt động chuẩn xác.
2. **Dòng `Phí gói: 5.000đ` thay cho `Thuế` (`CR-07`)**:
   - Không dùng thuế `%` vì dễ sai số theo giá đơn hàng; triển khai dưới dạng phụ phí/dòng phí đóng gói cố định `5.000đ` hoặc nhãn hiển thị tách bạch trong tổng đơn ở `wbh_core` / `theme_gift_store`.
3. **Upload ảnh bill chuyển khoản (`CR-10`)**:
   - Bổ sung khối hiển thị QR tĩnh/động + input upload ảnh (`jpg`/`png`/`webp`, giới hạn dung lượng an toàn) trên `/shop/payment`, đính kèm trực tiếp vào `sale.order` (`ir.attachment` + ghi chú chatter dùng `markupsafe.Markup`) để chủ shop mở đơn là thấy ngay ảnh bill của khách.
4. **Xử lý 2 ảnh Logo mới (`CR-01`)**:
   - File khách gửi hiện có nền đen đặc và nền trắng đặc; khi triển khai cần tách nền trong suốt (`RGBA PNG`) để gắn sắc nét lên Header + tạo lại `favicon.ico`.

---

## 4. 7 Câu Hỏi Cần Sếp Chốt Lại Với Khách Trước Khi Code

1. **Link Facebook chính thức của shop** là gì? *(Để gắn vào nút `Facebook CSKH` trên Topbar, `Nhắn Facebook` ở nút Tư vấn, PDP, Giỏ hàng và Footer.)*
2. **Ảnh mã QR ngân hàng của chủ shop** (và thông tin STK / Chủ TK / Ngân hàng nếu muốn hiển thị kèm dưới ảnh QR cho khách dễ copy).
3. **Chốt tone màu chủ đạo**: Khách muốn web theo hướng **Nền sáng sạch sẽ** (trắng/xanh nhạt, nhấn **Xanh dương đậm + Topbar đen** khớp bản logo nền trắng) hay **Nền tối hoàn toàn** (đen + xanh dương neon khớp bản logo nền đen)?
4. **Xác nhận cách tính `Phí gói 5.000đ`**: Thu cố định **`5.000đ / mỗi đơn hàng`** hay `5.000đ / mỗi món`?
5. **Xác nhận biểu phí Viettel Post (`12.000đ – 20.000đ`)**: Kho của shop đặt ở tỉnh/thành nào (ví dụ TP.HCM hay Hà Nội) và quy tắc chia giá ship theo khu vực cụ thể ra sao (ví dụ: nội tỉnh `12.000đ`, cùng miền `15.000đ`, liên miền `20.000đ`)?
6. **Xác nhận câu tiêu đề Hero ở Ảnh 4**: Cụm bị mép ảnh cắt là **`Doll và các loại goods Boku no Hero, hàng sẵn giao ngay`** đúng không?
7. **Xác nhận link `Khám phá nhanh` ở Footer (Ảnh 5)**: Có cần sửa các mục *Tất cả quà tặng / Gấu bông / Móc khóa / Blind Box* sang các mục goods *Boku no Hero* (`Card / Postcard / Standee / Doll / Badge...`) cho đồng bộ luôn không?

---

## 5. Tài Nguyên Logo Khách Đã Gửi (Lưu Tạm Phiên Làm Việc)

- Bản nền đen: `C:/Users/ADMIN/.gemini/antigravity/brain/e741ecf4-dfc9-43f1-96c7-0bb60ed71d4c/.user_uploaded/media_1795855992263_1b54b68e.jpg`
- Bản nền trắng: `C:/Users/ADMIN/.gemini/antigravity/brain/e741ecf4-dfc9-43f1-96c7-0bb60ed71d4c/.user_uploaded/media_1795855992269_cf813861.jpg`
