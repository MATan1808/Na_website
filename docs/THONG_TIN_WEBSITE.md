# THÔNG TIN WEBSITE & ĐỊNH HƯỚNG BÁN HÀNG ANIME GOODS
## Dự Án: Hệ Sinh Thái 2 Website Bán Hàng — Odoo 19.0 Community (`web_ban_hang`)

> **Ngày cập nhật**: 2026-11-27  
> **Nền tảng kỹ thuật**: 100% Odoo 19.0 Community (LGPL-3) + PostgreSQL 15 (Docker)  
> **Cổng truy cập Local Server**: [http://100.64.56.52:1901](http://100.64.56.52:1901) *(LAN: `http://192.168.1.37:1901` · Local Docker: `http://localhost:1901` · Tiền tệ hiển thị chuẩn: **`VNĐ (₫)`**)*  
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

#### Bộ 10 Lô Sản Phẩm & 49 Ảnh Thật Từ Facebook `Manh Dao Dao` (`MDD-FB-001` ➜ `MDD-FB-010`)
- **Nguồn dữ liệu JSON**: [fb_manhdaodao_products.json](file:///F:/BACKUP_LINUX/web_ban_hang/addons/wbh_core/data/fb_manhdaodao_products.json) (37 biến thể)
- **Nguồn bảng CSV (mở Excel)**: [fb_manhdaodao_products.csv](file:///F:/BACKUP_LINUX/web_ban_hang/addons/wbh_core/data/fb_manhdaodao_products.csv)
- **Kho ảnh thật (`49` ảnh)**: `addons/wbh_core/static/src/img/fb_manhdaodao/`
- **Script nạp chuẩn Idempotent**: `addons/wbh_core/scripts/import_fb_products.py`

| Mã SKU | Tên sản phẩm trên Web | Giá từ | Biến thể / Ảnh |
|---|---|---:|---:|
| `MDD-FB-001` | Combo Goods Mới Về My Hero Academia (Card, Huy Hiệu, Sticker & Plushie) | 20.000 đ | 6 biến thể · 4 ảnh |
| `MDD-FB-002` | Deal Full Bakugo Katsuki — Standee Acrylic, Card, Photocard, Móc Khóa & Nui Bông | 15.000 đ | 5 biến thể · 5 ảnh |
| `MDD-FB-003` | Sale Card Bo Góc & Clear Card My Hero Academia Đồng Giá 15K | 15.000 đ | 3 biến thể · 5 ảnh |
| `MDD-FB-004` | Goods Anime Pass Sẵn Giao Ngay — Huy Hiệu Can Badge, Card & Phụ Kiện | 25.000 đ | 3 biến thể · 5 ảnh |
| `MDD-FB-005` | Bộ Deal Mới Share Goods Anime — Vé Ticket, Memo & Card Sưu Tầm | 25.000 đ | 3 biến thể · 5 ảnh |
| `MDD-FB-006` | Card Polaroid Instax, Sticker & Huy Hiệu MHA Có Sẵn (Deku / Bakugo / Toga) | 15.000 đ | 4 biến thể · 5 ảnh |
| `MDD-FB-007` | Deal Share Tổng Hợp Goods & Card Anime Đợt Tháng 11 (Hỗ Trợ Keep Hàng) | 30.000 đ | 3 biến thể · 5 ảnh |
| `MDD-FB-008` | Bộ Sưu Tập Tổng Hợp MHA Đa Nhân Vật — Snapmide, Clear Card, Badge & Standee | 15.000 đ | 4 biến thể · 5 ảnh |
| `MDD-FB-009` | Kho Clear Card & Goods MHA Hàng Có Sẵn (Bakugo / Kaminari / Kyoka Jiro) | 20.000 đ | 3 biến thể · 5 ảnh |
| `MDD-FB-010` | Set Pass All Char Anime Goods & Card Sưu Tầm (Ưu Đãi Lấy Trọn Nhân Vật) | 25.000 đ | 3 biến thể · 5 ảnh |

> **Lệnh đồng bộ lại dữ liệu từ file JSON khi sửa giá/mô tả**:  
> `docker exec -i web-ban-hang-app odoo shell -c /etc/odoo/odoo.conf -d web_ban_hang_dev --no-http < /mnt/extra-addons/wbh_core/scripts/import_fb_products.py`

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

---

## 5. HƯỚNG DẪN PUBLIC WEBSITE RA INTERNET & GẮN DOMAIN MIỄN PHÍ (MÁY Ở NHÀ)

Địa chỉ hiện tại `http://100.64.56.52:1901` là IP nội bộ **Tailscale / CGNAT** (chưa có HTTPS và chưa có tên miền). Để bạn bè dùng 4G/Wifi bên ngoài truy cập mượt qua tên miền `https://manhdaodao...` (bỏ cổng `:1901`, không cần mở port modem/router ở nhà), anh có thể dùng **Cách 1 (Cloudflare Tunnel — chuẩn lâu dài)** hoặc **Cách 2 (Tailscale Funnel — chạy thử nhanh trong 1 phút)**.

### Cách 1 — Gắn Domain miễn phí `manhdaodao.*` + Cloudflare Tunnel (Khuyên dùng)

#### Gợi ý chọn đuôi tên miền miễn phí (tương thích Cloudflare DNS)
| Tên miền gợi ý | Chi phí | Ghi chú |
|---|---|---|
| **`manhdaodao.id.vn`** | **Miễn phí 2 năm đầu** | Chương trình VNNIC cho công dân VN 18–23 tuổi (đăng ký tại `tenten.vn`, `nhanhoa.com`, `pavietnam.vn`). Đẹp và uy tín nhất để gửi bạn bè. |
| **`manhdaodao.dpdns.org`** | **Miễn phí** | Đăng ký tại `https://dash.domain.digitalplat.org`, hỗ trợ trỏ Nameserver về Cloudflare Free. |
| **`manhdaodao.pp.ua`** | **Miễn phí** | Đăng ký cộng đồng, cho trỏ Nameserver về Cloudflare Free. |
| **`manhdaodao.shop` / `.store`** | ~25.000đ – 50.000đ/năm đầu | Tùy chọn mua rẻ (Porkbun/Namecheap/Cloudflare) nếu muốn đuôi quốc tế chuyên nghiệp không cần chờ duyệt. |

> **Lưu ý:** Không dùng `duckdns.org` cho Cloudflare Tunnel vì DuckDNS không cho đổi Nameserver sang Cloudflare.

#### 5 bước triển khai chi tiết
1. **Bước 1 — Đăng ký tên miền & đưa lên Cloudflare Free (`\$0`)**:
   - Đăng ký 1 tên miền `manhdaodao.<đuôi>` ở bảng trên.
   - Đăng nhập `https://dash.cloudflare.com` ➜ **Add a domain** ➜ nhập `manhdaodao.<đuôi>` ➜ chọn gói **Free (`\$0`)**.
   - Lấy 2 dòng **Nameserver** do Cloudflare cấp (`*.ns.cloudflare.com`), dán thay thế vào trang quản lý tên miền vừa đăng ký và đợi Cloudflare báo **Active**.
2. **Bước 2 — Tạo Cloudflare Tunnel & lấy Token**:
   - Trong Cloudflare, mở **Zero Trust** (gói Free) ➜ **Networks** ➜ **Tunnels** ➜ **Create a tunnel**.
   - Chọn **Cloudflared** ➜ đặt tên `manhdaodao-home` ➜ copy chuỗi **`CLOUDFLARE_TUNNEL_TOKEN`** (`eyJhIjo...`) và **tuyệt đối không commit lên Git**.
3. **Bước 3 — Khai báo Public Hostname trong Tunnel**:
   - **Web 1 (Manh Dao Dao)**: Domain `manhdaodao.<đuôi>` (để trống Subdomain) ➜ Type: `HTTP` ➜ URL: `odoo:8069`.
   - **Web 2 (Thời trang — tùy chọn)**: Subdomain `fashion`, Domain `manhdaodao.<đuôi>` ➜ Type: `HTTP` ➜ URL: `odoo:8069`.
   - *(Lưu ý khi lên Giai đoạn 3 Livechat)*: thêm rule cho đường dẫn `/websocket` trỏ về `odoo:8072`.
4. **Bước 4 — Bật `cloudflared` trong Docker trên máy ở nhà**:
   ```bash
   git pull origin main
   ```
   Mở tệp `.env` trên máy server ở nhà (tệp này đã có trong `.gitignore`), bỏ dấu `#` ở dòng `COMPOSE_PROFILES=tunnel` và dán token vào:
   ```env
   COMPOSE_PROFILES=tunnel
   CLOUDFLARED_IMAGE=cloudflare/cloudflared:latest
   CLOUDFLARE_TUNNEL_TOKEN=<dan_token_cloudflare_vao_day>
   ```
   Khởi chạy container Tunnel và kiểm tra log kết nối:
   ```bash
   docker compose --profile tunnel up -d
   docker compose logs -f cloudflared
   ```
5. **Bước 5 — Cấu hình Domain chuẩn trong Odoo Backend**:
   - Đăng nhập Backend Odoo ➜ **Website ➜ Cấu hình ➜ Website**, chọn từng website và điền **Tên miền (Domain)** là `https://manhdaodao.<đuôi>` (không kèm `:1901`).
   - Vào **Cài đặt ➜ Kỹ thuật ➜ Tham số hệ thống**: đặt `web.base.url` = `https://manhdaodao.<đuôi>` và thêm/đặt `web.base.url.freeze` = `True` (tránh bị Odoo tự ghi đè lại IP `100.64.56.52:1901` mỗi khi admin đăng nhập bằng IP nội bộ).
   - *(Ghi chú: Tệp `config/odoo.conf` đã bật sẵn `proxy_mode = True` nên Odoo tự nhận diện HTTPS chuẩn từ Cloudflare Tunnel.)*

### Cách 2 — Bật nhanh trong 1 phút chưa cần đăng ký Domain (Tailscale Funnel)

Nếu muốn gửi ngay đường dẫn có HTTPS cho bạn bè test trước khi kịp đăng ký domain:
1. Vào `https://login.tailscale.com/admin/machines`, đổi tên máy server thành `manhdaodao`.
2. Vào tab **DNS** (`https://login.tailscale.com/admin/dns`), bật **MagicDNS** và **HTTPS Certificates**.
3. Chạy 1 lệnh trên máy server ở nhà:
   ```bash
   tailscale funnel --bg 1901
   ```
4. Chia sẻ đường dẫn trả về dạng `https://manhdaodao.<tailnet>.ts.net` cho bạn bè truy cập bình thường bằng 4G/Wifi mà không cần cài Tailscale.
