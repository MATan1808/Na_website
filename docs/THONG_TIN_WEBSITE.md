# THÔNG TIN WEBSITE & ĐỊNH HƯỚNG BÁN HÀNG ANIME GOODS
## Dự Án: Hệ Sinh Thái 2 Website Bán Hàng — Odoo 19.0 Community (`web_ban_hang`)

> **Ngày cập nhật**: 2026-11-27  
> **Nền tảng kỹ thuật**: 100% Odoo 19.0 Community (LGPL-3) + PostgreSQL 15 (Docker)  
> **Cổng truy cập Local Server**: [http://100.64.56.52:1901](http://100.64.56.52:1901) *(LAN: `http://192.168.1.37:1901` · Local Docker: `http://localhost:1901`)*  
> **Lộ trình & Tiến độ 4 giai đoạn**: Xem chi tiết tại [ROADMAP_TIEN_DO.md](file:///F:/BACKUP_LINUX/web_ban_hang/docs/ROADMAP_TIEN_DO.md)  
> **Đơn vị quản lý & triển khai**: Sếp Châu (`tanma`)

---

## 1. TỔNG QUAN HỆ THỐNG 2 CỬA HÀNG ĐỘC LẬP (MULTI-WEBSITE)

Dự án vận hành trên kiến trúc **Multi-Website thuần Odoo 19.0 Community**, dùng chung một cơ sở dữ liệu và hệ thống quản lý kho/đơn hàng, nhưng **tách biệt 100% tài khoản khách hàng (`specific_user_account=True`)**, tích điểm thành viên và giao diện thương hiệu:

| Thông số | Cửa Hàng 1 (Web 1) — Quà Tặng & Anime Goods | Cửa Hàng 2 (Web 2) — Thời Trang & Lookbook |
|---|---|---|
| **Tên hiển thị** | **Manh Dao Dao — Anime Goods & Quà Tặng** | **Cửa Hàng Thời Trang — Quần Áo & Lookbook** |
| **Định vị ngành hàng** | Búp bê bông Doll 20cm, Outfit búp bê, Card bo góc, Huy hiệu Can Badge, Mochi ú, Blind Box theo phim *My Hero Academia* và các Anime hot. | Thời trang Unisex, Quần áo oversize, Streetwear, Lookbook editorial, đồ đôi & outfit búp bê. |
| **Khách hàng mục tiêu** | Fan anime/manga (Otaku), Gen Z, giới trẻ đam mê sưu tầm goods và búp bê thần tượng (Bias/Oshi). | Giới trẻ yêu thích phong cách thời trang tối giản, năng động, streetwear và ảnh mẫu lookbook. |
| **Theme nền tảng** | Custom `theme_gift_store` (kế thừa từ repo `odoo/design-themes`: `theme_kiddo` + `theme_buzzy`). | Custom `theme_fashion_store` (kế thừa `theme_loftspace` + `theme_clean`). |
| **Đường dẫn xem thử** | [http://localhost:1901/](http://localhost:1901/) | [http://localhost:1901/lookbook](http://localhost:1901/lookbook) |

---

## 2. CHI TIẾT CỬA HÀNG 1: U.A HERO STORE (THEME MY HERO ACADEMIA)

### 2.1. Repo Giao Diện Hạt Nhân Được Lựa Chọn
- **Tên Repo**: **`odoo/design-themes`**
- **Link GitHub**: [https://github.com/odoo/design-themes](https://github.com/odoo/design-themes) *(Mã nguồn mở LGPL-3, sạch 100% không dính Enterprise)*.
- **Vị trí local trong máy**: `F:\BACKUP_LINUX\save\dev_env\19.0\origin\addons\`
- **Cặp Theme hạt nhân phối hợp**:
  1. **`theme_kiddo`**: Cấu trúc thẻ sản phẩm bo tròn mềm mại, tối ưu chuyên biệt cho Búp Bê Bông (Dolls/Plushies), phụ kiện móc khóa và Blind Box.
  2. **`theme_buzzy`**: Bố cục các khối Banner cắt vát góc cạnh (Angular Clips), hiệu ứng bộc phá năng lượng Pop-Art và typography đậm chất truyện tranh Shonen Jump.

### 2.2. Nhận Diện Thương Hiệu & Bảng Màu Siêu Năng Lực (Quirk Palette)
Giao diện được thiết kế theo đúng bản sắc các nhân vật trong phim *My Hero Academia*:
- **Cam Bộc Phá & Vàng Nitro (`#FF5722` & `#FFD600`)**: Đại diện cho **Bakugo Katsuki (Kacchan)** — Dùng cho nút CTA "Mua Ngay", nhãn Bán chạy, viền card bùng nổ.
- **Đỏ Rực & Xanh Băng (`#E53935` & `#00E5FF`)**: Đại diện cho Kosei Nửa Băng Nửa Lửa của **Todoroki Shoto** — Dùng cho badge giảm giá, hiệu ứng hover card phân loại.
- **Xanh Ngọc Hero (`#00C853`)**: Đại diện cho năng lượng One For All của **Midoriya Izuku (Deku)**.
- **Slogan Chủ Đạo**: *"PLUS ULTRA! — Trao Gửi Đam Mê Qua Từng Món Quà & Búp Bê Bông Nhân Vật"*.

### 2.3. Danh Mục Mặt Hàng Thực Tế Đã Nạp
Hệ thống đã nạp sẵn 5 dòng sản phẩm chuẩn theo hình ảnh thực tế của Sếp:

1. **Búp Bê Bông Cotton Doll 20cm Bakugo Katsuki (Tóc Xù Kèm Outfit Sporty)**:
   - Link web: `/shop/bup-be-bong-cotton-doll-20cm-bakugo-katsuki-toc-xu-kem-outfit-sporty-40`
   - Biến thể 1: `Full Set (Body Búp Bê + Set Đồ Áo Khoác Zip)` — Giá: **380.000 đ**
   - Biến thể 2: `Chỉ Body Bông (Thêu Sầu Riêng Ở Bụng)` — Giá: **280.000 đ**
   - Biến thể 3: `Chỉ Set Đồ Rời (Áo Khoác Zip + Quần + Thun)` — Giá: **120.000 đ**
2. **Bộ Sưu Tập Card Bo Góc & Photocards Todoroki Shoto**:
   - Link web: `/shop/bo-suu-tap-card-bo-goc-photocards-todoroki-shoto-my-hero-academia-41`
   - Biến thể: Card Thường (**20.000 đ**), Card Hologram Bạc Hiếm (**85.000 đ**), Set 2 Card Kèm Khung (**120.000 đ**).
3. **Huy Hiệu Kim Loại Can Badge Todoroki Shoto 58mm**:
   - Link web: `/shop/huy-hieu-kim-loai-can-badge-todoroki-shoto-58mm-phu-kim-tuyen-da-quang-42`
   - Mức giá: **25.000 đ** (Phủ kim tuyến, mặt sau ghim cài chắc chắn).
4. **Mochi Kororin Bông Tròn Todoroki Shoto Mini 10cm**:
   - Link web: `/shop/mochi-kororin-bong-tron-todoroki-shoto-mini-10cm-cuc-bong-u-treo-balo-43`
   - Mức giá: **130.000 đ** (Bông nhung nỉ mềm mịn, có dây móc balo).
5. **Tranh Ký Shikishi Viền Vàng Bakugo Katsuki**:
   - Link web: `/shop/tranh-ky-shikishi-vien-vang-bakugo-katsuki-awakening-explosion-edition-44`
   - Mức giá: **65.000 đ** (Bìa cứng ép kim vàng, in cảnh bộc phá).

### 2.4. Trải Nghiệm Khách Hàng (UX Độc Quyền Anime Goods)
- **Shop By Bias / Oshi (Mua Theo Nhân Vật)**: Bộ lọc sẵn cho phép khách bấm vào **Bakugo** hoặc **Todoroki** để lọc toàn bộ sản phẩm của riêng nhân vật đó.
- **Cross-Sell Thay Đồ Búp Bê**: Mua Body Doll 20cm sẽ tự động gợi ý thêm các set Outfit áo khoác / đồ cosplay mini để thay đồ cho búp bê.
- **Bộ Lọc Theo Anime**: Sẵn sàng mở rộng thêm các bộ anime hot khác (*Jujutsu Kaisen, Haikyuu, Conan, Genshin Impact...*).

---

## 3. CHI TIẾT CỬA HÀNG 2: THỜI TRANG & LOOKBOOK

- **Định vị**: Dòng sản phẩm thời trang phong cách tối giản (Minimalist & Streetwear).
- **Bảng màu**: Đen than `#111111`, Be cát `#C8B6A6`, Xám đá `#F5F5F3`.
- **Tỷ lệ hình ảnh**: Chuẩn dọc Lookbook `3:4`.
- **Sản phẩm mẫu đã có sẵn**: Áo thun Oversize cotton 250gsm, Quần Jeans ống rộng Retro, Set đồ phối sẵn Summer Lookbook kèm bảng chọn size thông minh (S / M / L / XL).

---

## 4. HƯỚNG DẪN TRUY CẬP & QUẢN TRỊ CHO SẾP

1. **Trang Chủ Cửa Hàng Bán Hàng**:
   👉 [http://localhost:1901/](http://localhost:1901/)
2. **Khu Vực Bán Hàng Anime Goods & Doll 20cm**:
   👉 [http://localhost:1901/shop/category/anime-goods-merch-21](http://localhost:1901/shop/category/anime-goods-merch-21)
3. **Trang Xem Trước Hệ Thống Thiết Kế (Design System Preview)**:
   👉 Mở trực tiếp file: `f:\BACKUP_LINUX\web_ban_hang\html\preview.html`
4. **Trang Quản Trị Backend Odoo (Admin)**:
   👉 [http://localhost:1901/web/login](http://localhost:1901/web/login)
   - Quản lý sản phẩm, đơn hàng, khách hàng, tồn kho và bảng giá.
