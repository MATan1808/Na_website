# LỘ TRÌNH PHÁT TRIỂN & THEO DÕI TIẾN ĐỘ — 4 GIAI ĐOẠN (`web_ban_hang`)

> **Thương hiệu triển khai**: **Manh Dao Dao — Anime Goods & Quà Tặng** *(hệ sinh thái Multi-Website Odoo 19.0 Community LGPL-3)*  
> **Phiên bản tài liệu**: `v0.3.7` · **Cập nhật lần cuối**: `2026-11-27`  
> **Môi trường đang chạy live**: Local Server `http://100.64.56.52:1901` (LAN: `http://192.168.1.37:1901`)  
> **Repository GitHub**: `https://github.com/MATan1808/Na_website.git` (nhánh `main`)

---

## 1. Bảng Tổng Quan Tiến Độ 4 Giai Đoạn

| Giai đoạn | Trọng tâm & Mục tiêu cốt lõi | Trạng thái hiện tại | Tiến độ | Module phụ trách |
|---|---|---|:---:|---|
| **Giai đoạn 1** | **Website & Quản trị Sản phẩm CRUD đầy đủ** *(Thêm · Xem · Sửa · Xóa/Lưu trữ)* | Đang hoàn thiện tối ưu đăng nhanh | **~85%** | `wbh_core`, `theme_gift_store`, `theme_fashion_store` |
| **Giai đoạn 2** | **Bộ lọc Sản phẩm Linh động 100% — Cấm Hardcode** *(Giá · Nhân vật · Phân loại · Nhãn ưu đãi/giảm giá động)* | Đã có khung cơ bản, sắp build tính năng động | **~25%** | `wbh_core`, `theme_gift_store` |
| **Giai đoạn 3** | **Tương tác & Tư vấn Chốt đơn 3 Kênh** *(Web Chat · Facebook · Zalo)* | Đã cài `im_livechat` & nút Zalo footer, sắp build cụm 3 kênh | **~20%** | `wbh_core`, `website_livechat`, `theme_gift_store` |
| **Giai đoạn 4** | **Thanh toán & Vận chuyển VN** *(VietQR · COD · Gom đơn · GHN/GHTK)* | Chưa triển khai *(làm sau Giai đoạn 3)* | **0%** | `wbh_payment_vietqr`, `wbh_delivery_vn` |

---

## 2. Chi Tiết Từng Giai Đoạn & Checklist Kiểm Soát

---

### GIAI ĐOẠN 1 — Xây dựng Website & Quản trị Sản phẩm CRUD (`~85%`)

**Mục tiêu**: Website hoạt động ổn định trên cả điện thoại và máy tính; chủ shop đăng nhập Backend có thể **Thêm – Xem – Sửa – Xóa / Lưu trữ** sản phẩm trơn tru, quản lý được giá, tồn kho, biến thể và ảnh chụp thực tế.

#### 1.1. Nghiệp vụ CRUD chi tiết
- **Thêm sản phẩm (`Create`)**:
  - Nhập Tên sản phẩm, Mã SKU nội bộ, Giá bán (`list_price`), Giá gốc gạch ngang (`compare_list_price` — hiển thị khuyến mãi).
  - Nhập Tồn kho ban đầu (`qty_available`), Ngưỡng cảnh báo sắp hết hàng (`wbh_low_stock_threshold`).
  - Tải Ảnh đại diện vuông `1:1` + **Album nhiều ảnh phụ** (chụp cận khuôn mặt doll, tem tag off, vết xước/cond card, phụ kiện kèm theo).
  - Khai báo **Biến thể bán hàng** (VD: *Fullset 380k / Body trần 280k / Outfit rời 120k* hoặc *Card thường / Hologram*).
  - Nhập **Điểm nổi bật ngắn** (`wbh_short_highlight`) hiện ngay dưới tên SP và **Lưu ý tình trạng / bảo quản** (`wbh_care_note`) hiện trong mục thu gọn.
- **Xem & Hiển thị (`Read`)**:
  - Trang chủ có Hero Banner, thanh dịp mua/nhân vật, lưới sản phẩm nổi bật; trang `/shop` chia cột responsive rõ đẹp trên Mobile & Desktop.
  - Tìm kiếm theo từ khóa tên sản phẩm/mã SKU; nhãn trạng thái tồn kho tự động (*Sẵn hàng giao ngay* / *Sắp hết hàng* / *Tạm hết hàng*).
  - Trang chi tiết sản phẩm có phóng to ảnh, chọn biến thể dạng nút chạm to dễ bấm trên mobile và thanh Sticky Bottom Bar luôn hiển thị nút Mua.
- **Sửa nhanh (`Update`)**:
  - Cập nhật giá bán, giá gạch ngang, số lượng tồn kho, thêm/bớt ảnh chi tiết, chỉnh mô tả bất cứ lúc nào.
  - Công tắc **Xuất bản (`is_published`)** bật/tắt 1 chạm ngay trên web hoặc trong Backend để ẩn/hiện sản phẩm tức thì.
  - Hỗ trợ sửa hàng loạt trên màn hình danh sách (`List View` editable) khi cần chỉnh giá hoặc trạng thái nhiều món cùng lúc.
- **Xóa & Lưu trữ (`Delete / Archive`)**:
  - **Xóa hẳn (`Delete`)**: Cho phép xóa vĩnh viễn các sản phẩm tạo nháp hoặc tạo nhầm chưa từng phát sinh đơn hàng.
  - **Lưu trữ (`Archive`)**: Các sản phẩm đã bán hết và từng có đơn hàng cũ có thể bấm *Lưu trữ* để biến mất 100% khỏi cửa hàng mà vẫn giữ toàn vẹn lịch sử doanh thu và đơn hàng.

#### 1.2. Checklist tiến độ Giai đoạn 1
- [x] Hạ tầng Docker di động (`odoo:19.0` Community + `postgres:15-bookworm`) chạy live trên Local Server `100.64.56.52:1901`.
- [x] Giao diện `theme_gift_store` + Bộ nhận diện **Manh Dao Dao** (Logo ngang `1020x280`, Favicon cận mặt, sửa triệt để lặp 2 footer & scrolltop mobile).
- [x] Fix tận gốc quyền đọc tồn kho trang `/shop` cho khách vãng lai (`compute_sudo=True` trên `wbh_is_low_stock` & `product.sudo().qty_available`).
- [x] Nạp bộ sản phẩm mẫu Anime Goods (Cotton Doll 20cm Bakugo, Card/Can Badge/Mochi Todoroki, Shikishi) đầy đủ biến thể.
- [ ] **Tối ưu Form đăng nhanh sản phẩm Anime Goods (`< 60 giây/món`)**: Gom toàn bộ ô cần thiết (*Tên, Giá bán, Giá gốc, Website, Ảnh/Album, Tồn kho, Nhãn lọc*) vào 1 màn hình gọn, ẩn tab kỹ thuật rườm rà.
- [ ] **Hiển thị Giá gốc gạch ngang & Badge `% giảm`** tự động trên thẻ sản phẩm `/shop` và trang chi tiết khi `compare_list_price > list_price`.
- [ ] **Kiểm thử trọn vẹn thao tác CRUD** (Tạo mới ➜ Sửa giá/ảnh ➜ Ẩn/Hiện ➜ Lưu trữ & Xóa nháp) trên Local Server.

---

### GIAI ĐOẠN 2 — Bộ lọc Sản phẩm Linh động 100%, Không Hardcode (`~25%`)

> **NGUYÊN TẮC CỨNG CỦA GIAI ĐOẠN 2 (TUYỆT ĐỐI KHÔNG HARDCODE)**  
> **Cấm tuyệt đối** viết cứng tên nhân vật (*Bakugo, Todoroki...*), tên bộ Anime (*MHA...*), loại sản phẩm (*Doll, Off...*) hay trạng thái (*Giảm giá...*) trong code XML/Python/JS.  
> Mọi tiêu chí lọc ngoài trang `/shop` **BẮT BUỘC tự động sinh ra** từ dữ liệu chủ shop tạo và tích chọn lúc thêm/sửa sản phẩm. Nhãn/nhân vật nào chưa có sản phẩm đang đăng bán thì tự ẩn, ngay khi chủ shop gắn cho sản phẩm đầu tiên thì tự động hiện lên bộ lọc!

#### 2.1. Bốn trục bộ lọc động hoàn toàn
1. **Lọc theo Khoảng giá (Dynamic Price Filter)**:
   - Thanh trượt kéo `Từ giá – Đến giá` tự động co giãn theo mức giá `Min – Max` thực tế của các sản phẩm đang bán trên website.
   - Hỗ trợ thêm các nút bấm nhanh khoảng giá (VD: *Dưới 50k · 50k–150k · 150k–300k · Trên 300k*) cấu hình động trong Backend, không viết cứng trong template.
2. **Lọc theo Nhãn Trạng thái / Ưu đãi động (`Dynamic Filter Tags` — đúng ví dụ của Sếp)**:
   - Xây dựng từ `product.tag` (gắn cờ `wbh_show_in_filter = True` và màu sắc huy hiệu `wbh_tag_color`).
   - **Cách vận hành cho chủ shop**: Khi thêm hoặc sửa sản phẩm (VD: *Búp bê Bakugo 20cm*), chủ shop chỉ cần tích chọn nhãn **`Đang giảm giá`** (hoặc tự tạo thêm bất kỳ nhãn mới nào ngay tại ô nhập như `Hàng hiếm / Secret`, `Pre-order`, `Hàng sẵn`, `Mới về`, `Pass lỗ`) ➜ Ngoài trang `/shop` tự động xuất hiện mục lọc tương ứng (kèm số lượng món khớp) và tự gắn huy hiệu màu lên thẻ sản phẩm.
   - Hỗ trợ thêm quy tắc tiện lợi: nếu sản phẩm có *Giá gốc > Giá bán*, có thể gợi ý/tự động gắn vào nhóm *Đang giảm giá*.
3. **Lọc theo Nhân vật & Bộ Anime (`No-Variant Attributes`)**:
   - Dùng `product.attribute` với chế độ **`create_variant = 'no_variant'`** (thuộc tính chỉ dùng để mô tả & lọc, **không** đẻ ra biến thể SKU phức tạp).
   - Khi đăng sản phẩm mới của nhân vật/bộ phim nào (VD gõ thêm `Gojo Satoru` hoặc `Jujutsu Kaisen`), hệ thống tự ghi nhận vào bộ lọc **Nhân vật** và **Bộ Anime** ngoài `/shop` ngay lập tức.
4. **Lọc theo Phân loại hàng (`Doll` / `Goods Off` / `Fanmade` / `Card` / `Badge` / `Outfit`)**:
   - Kết hợp **Danh mục Website đa cấp** (`product.public.category` — do chủ shop tự thêm/sửa/xóa/sắp xếp thứ tự) và thuộc tính phân loại động `no_variant` (VD phân loại *Hàng Chính Hãng / Official Goods* vs *Cotton Doll* vs *Fanmade*).

#### 2.2. Trải nghiệm lọc mượt cho người mua
- Cho phép **lọc kết hợp nhiều điều kiện cùng lúc** (VD: `Nhân vật: Bakugo` + `Loại: Cotton Doll` + `Ưu đãi: Đang giảm giá` + `Giá: 200k–400k`).
- Hiển thị thanh **Chip bộ lọc đang chọn** ngay đầu danh sách sản phẩm kèm dấu `×` để bỏ từng điều kiện hoặc bấm *Xóa tất cả* trong 1 chạm.
- Giao diện ngăn kéo trượt (**Offcanvas Drawer Filter**) tối ưu ngón tay trên điện thoại, kèm sắp xếp động (*Mới nhất · Giá thấp ➜ cao · Giá cao ➜ thấp*).

#### 2.3. Checklist tiến độ Giai đoạn 2
- [x] Khởi tạo khung Danh mục Website (`product.public.category`) và 7 Thuộc tính mẫu trong `wbh_core`.
- [x] Bật sẵn sidebar danh mục & thuộc tính trong `theme_gift_store/data/presets.xml`.
- [ ] Mở rộng `product.tag` trong `wbh_core`: thêm cờ `wbh_show_in_filter`, `wbh_tag_color`, `wbh_filter_group` và hiển thị ngay ô chọn nổi bật khi thêm/sửa sản phẩm.
- [ ] Tạo 2 thuộc tính `no_variant` chuẩn cho Anime Goods (*Nhân vật*, *Bộ Anime*, *Phân loại Doll/Off*) giúp gõ mới nhân vật trực tiếp ngay lúc up SP mà không sinh SKU thừa.
- [ ] Controller & Template `/shop` đọc động **nhãn `product.tag` + thuộc tính `no_variant` + khoảng giá Min/Max** (tự ẩn nhóm rỗng, đếm số SP thực tế, hỗ trợ lọc nhiều tiêu chí đồng thời).
- [ ] Thiết kế UI ngăn kéo lọc Mobile (Offcanvas) + dải Chip bộ lọc đang áp dụng + Huy hiệu badge trên thẻ sản phẩm.
- [ ] Kiểm thử: Thêm mới 1 sản phẩm và tích nhãn tự tạo bất kỳ ➜ kiểm tra bộ lọc trên `/shop` tự xuất hiện ngay, bỏ tích/ẩn SP ➜ bộ lọc tự ẩn.

---

### GIAI ĐOẠN 3 — Tương tác & Tư vấn Chốt đơn 3 Kênh: Web · Facebook · Zalo (`~20%`)

**Mục tiêu**: Khách hàng đang xem bất kỳ món đồ nào muốn hỏi tình trạng (cond card, quay video doll, mặc thử outfit, chốt đơn nhanh) đều có thể liên hệ ngay với shop qua **đúng 3 kênh quen thuộc** và chủ shop trả lời được thuận tiện:

#### 3.1. Chi tiết 3 kênh tương tác
1. **Kênh 1 — Chat trực tiếp ngay trên Website (`Odoo Livechat`)**:
   - Khách bấm là chat được ngay trên trình duyệt điện thoại/máy tính mà **không cần đăng nhập tài khoản**.
   - Tin nhắn báo trực tiếp về màn hình quản trị Odoo (`Discuss / Livechat`) để chủ shop hoặc nhân viên trả lời tức thì.
   - Tự động đính kèm **tên + link sản phẩm khách đang xem** vào tin nhắn đầu tiên để shop biết ngay khách hỏi món nào.
   - Khi shop offline ngoài giờ, khung chat tự hiển thị lời nhắn hẹn phản hồi kèm gợi ý chuyển sang Facebook/Zalo.
2. **Kênh 2 — Facebook Messenger (`m.me/...`)**:
   - Nút bấm mở thẳng khung chat Fanpage / Facebook cá nhân của shop (mở app Messenger trên điện thoại hoặc tab mới trên máy tính).
   - Hỗ trợ nút phụ *"Chép tên & link sản phẩm"* (hoặc pre-fill tin nhắn) để khách dán gửi qua Messenger hỏi hàng trong 1 giây.
3. **Kênh 3 — Zalo (`zalo.me/...`)**:
   - Nút bấm mở thẳng cửa sổ chat Zalo / Zalo OA của shop trên cả Mobile & Desktop.

#### 3.2. Bố cục hiển thị & Cấu hình động
- **Trên trang Chi tiết sản phẩm (Product Detail)** và **Giỏ hàng**: Hiển thị cụm **3 nút hành động rõ ràng** (*Chat tại Web · Nhắn Facebook · Nhắn Zalo*) ngay dưới nút Mua hàng.
- **Nút nổi đa kênh (Floating 3-in-1 Contact Widget)**: Gọn gàng ở góc màn hình, bấm vào xòe ra 3 biểu tượng (Web Chat / Messenger / Zalo), tính toán vị trí chuẩn để không đè lên nút cuộn `#o_footer_scrolltop` hay Sticky Bottom Bar trên điện thoại.
- **Cấu hình không hardcode**: Bổ sung các trường cấu hình ngay trong *Website ➜ Cấu hình ➜ Thông tin liên hệ 3 kênh* (Link Facebook Messenger, Link/SĐT Zalo, Bật/Tắt từng kênh, Câu chào gợi ý).

#### 3.3. Checklist tiến độ Giai đoạn 3
- [x] Cài đặt sẵn module chuẩn `im_livechat` & `website_livechat` trong Odoo 19.0 Community.
- [x] Gắn nút Zalo cơ bản ở Topbar và Footer của `theme_gift_store`.
- [ ] Bổ sung trường cấu hình 3 kênh động trên model `website` (`wbh_fb_messenger_url`, `wbh_zalo_url`, `wbh_livechat_enabled`, `wbh_contact_prompt`).
- [ ] Tạo Extension Widget cụm 3 kênh (*Chat Web · Facebook · Zalo*) gắn vào trang Chi tiết sản phẩm (qua slot `wbh_gift_options_slot` / khối hỗ trợ) và Giỏ hàng.
- [ ] Thiết kế Nút nổi 3-in-1 responsive mobile (tương thích nút scrolltop và sticky bar) + tự truyền tên sản phẩm đang xem vào cửa sổ Web Livechat.
- [ ] Kiểm thử luồng khách bấm cả 3 kênh trên Mobile & Desktop.

---

### GIAI ĐOẠN 4 — Thanh toán & Vận chuyển (`0%`)

**Mục tiêu**: Hoàn thiện luồng thanh toán tiện lợi, miễn phí lâu dài cho shop cá nhân/D2C và tự động hóa tính phí – tạo đơn vận chuyển nội địa Việt Nam.

#### 4.1. Thanh toán (`wbh_payment_vietqr`)
- **VietQR động chuẩn EMVCo / Napas 247**: Tự sinh mã QR chuyển khoản ngay trong Python/Odoo (miễn phí 100%, hỗ trợ mọi ngân hàng Việt Nam), tự điền sẵn số tài khoản chủ shop, **đúng số tiền đơn hàng** và **nội dung chuyển khoản chứa mã đơn** để không chuyển nhầm.
- **Đối soát tự động (Webhook)**: Tích hợp sẵn Adapter **SePay Free** (mở sẵn interface cho PayOS / Casso) nhận biến động số dư và tự động xác nhận đơn hàng đã thanh toán (*Idempotent — chống xác nhận trùng*).
- **Thanh toán khi nhận hàng (`COD`) & Quy tắc đặt cọc**:
  - Hỗ trợ bật/tắt COD linh hoạt theo từng sản phẩm hoặc giá trị đơn (VD: cho COD với hàng có sẵn, bắt buộc chuyển khoản cọc trước với đơn Pre-order hoặc đơn giá trị lớn).

#### 4.2. Vận chuyển & Gom đơn (`wbh_delivery_vn`)
- **Địa giới hành chính Việt Nam 3 cấp**: Tỉnh/Thành phố ➜ Quận/Huyện ➜ Phường/Xã rõ ràng khi khách nhập địa chỉ giao hàng.
- **Chính sách Ship nội bộ / Đồng giá & Gom đơn**:
  - Cấu hình phí ship đồng giá (VD nội thành 20k, tỉnh 30k), tự động **Freeship** khi đạt giá trị đơn tối thiểu.
  - Tùy chọn **"Gom đơn / Giữ hàng tại shop" (`0đ ship`)**: Phục vụ khách mua card/badge nhỏ lẻ muốn giữ đơn chờ gộp chung chuyến ship sau *(đặc thù cực kỳ cần thiết của Anime Goods Shop)*.
- **Kết nối hãng vận chuyển (`GHN` ➜ `GHTK` & `Viettel Post`)**:
  - Ưu tiên tích hợp **GHN** trước (API miễn phí 100%, có Sandbox test), tự động tính cước phí theo khối lượng/kích thước gói hàng, đẩy tạo mã vận đơn từ Backend và đồng bộ trạng thái hành trình giao hàng.

#### 4.3. Checklist tiến độ Giai đoạn 4
- [ ] Thiết kế & xây dựng module `wbh_payment_vietqr` (EMVCo QR offline + SePay Free webhook + quy tắc COD/cọc).
- [ ] Thiết kế & xây dựng module `wbh_delivery_vn` (Địa giới VN 3 cấp + Đồng giá/Freeship/Gom đơn + API GHN).
- [ ] Mở rộng GHTK / Viettel Post & tra cứu mã vận đơn ngay trên trang tài khoản khách hàng (Portal).
- [ ] Kiểm thử thanh toán Sandbox & luồng tạo vận đơn khép kín.

---

## 3. Ghi Chú Vận Hành & Đồng Bộ

- Mọi phát triển ở cả 4 giai đoạn bắt buộc tuân thủ **100% Odoo 19.0 Community (`LGPL-3`)** (không phụ thuộc Enterprise) và quy trình `Dev Local ➜ Git Commit & Push (Na_website.git) ➜ Pull & Upgrade trên Local Server (100.64.56.52)`.
- Sau mỗi hạng mục hoàn thành trong checklist ở trên, cập nhật lại `% tiến độ` và dấu `[x]` trực tiếp trong file này kèm [CHANGELOGS.md](file:///F:/BACKUP_LINUX/web_ban_hang/docs/CHANGELOGS.md).
