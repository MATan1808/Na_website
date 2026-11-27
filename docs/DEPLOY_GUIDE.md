# Hướng Dẫn Triển Khai & Vận Hành (DEPLOY_GUIDE) — `web_ban_hang`

> **Phiên bản**: `v1.0`  
> **Ngày tạo**: `2026-11-25`  
> **Nền tảng**: **100% Odoo 19.0 Community (LGPL-3)** + **PostgreSQL 15** + **Docker Compose Di Động**  
> **Thư mục gốc dự án**: `F:\BACKUP_LINUX\web_ban_hang`  
> **Lộ trình ưu tiên**: **Milestone 1 (Catalog-First)** — Dựng hạ tầng Docker + `wbh_core` + `theme_gift_store` + `theme_fashion_store` để Sếp đăng nhập quản trị và upload sản phẩm ngay.

---

## 1. Tổng Quan Kiến Trúc Triển Khai Di Động

Dự án được đóng gói **Docker di động 100% ngay trong kho Git** (`docker-compose.yml`, `config/odoo.conf`, `.env.example`) để có thể:
1. **Chạy tạm ngay trên máy Windows hiện tại** (lưu toàn bộ Docker data trên ổ `F:\` còn trống `227.22 GB` để bảo vệ ổ `C:\`).
2. **Chuyển mượt sang Local Server ở nhà** ngay khi máy server khởi động lại chỉ bằng quy trình chuẩn Git (`git pull` ➜ chỉnh `.env` ➜ `docker compose up -d` ➜ khôi phục bản sao lưu DB & Filestore).

### Thông số cô lập môi trường (bắt buộc không trùng dự án cũ)

| Thành phần | Giá trị chuẩn của `web_ban_hang` | Ghi chú cách ly |
|---|---|---|
| **Odoo Image** | `odoo:19.0` (**100% Community — LGPL-3**) | Không cài hoặc phụ thuộc bất kỳ module `*_enterprise` nào. |
| **PostgreSQL Image** | `postgres:15-bookworm` *(mặc định di động)* | Tùy chọn chuyển sang `360ai/postgres:15-ai` (kèm `pgvector`) trên Local Server khi cần tính năng AI/vector. |
| **Tên cụm Container** | `CLIENT_NAME=web-ban-hang` | Tách biệt hoàn toàn với `demo-19`. |
| **Cổng Web HTTP** | `1901` *(hoặc `8089` qua `.env`)* | Thuộc dải port `1900`–`1999` chuẩn `360-local-builder-env`, không đụng `demo-19` (`8079`/`1900`). |
| **Cổng Longpolling / Gevent** | `7089` | Không đụng `demo-19` (`7079`). |
| **Cổng PostgreSQL Host** | `51901` | Chỉ bind `127.0.0.1:51901:5432` để an toàn nội bộ. |
| **Database & Bộ lọc** | `web_ban_hang_dev` (local) / `web_ban_hang_prod` (prod)<br>`DB_FILTER=^web_ban_hang.*$` | Cấm dùng chung DB `demo-19` hay dump `vuahethong_v19_prod_test.dump`. |
| **Docker Volume & Filestore** | Volume `web_ban_hang_pgdata`<br>Bind `data/filestore/`, `data/sessions/` | Tách biệt 100% với `odoo19-db` và `dev_env\19.0\data\filestore\demo-19`. |
| **Custom Addons** | `F:\BACKUP_LINUX\web_ban_hang\addons\` | Mount vào `/mnt/extra-addons`; tuyệt đối không trộn vào `F:\BACKUP_LINUX\save\dev_env\19.0\modules\default\`. |

> **Lưu ý khi tham chiếu mẫu `F:\BACKUP_LINUX\save\dev_env\19.0\`**: Mẫu `services\odoo-base.yml` cũ có chứa dòng bind mount cứng từ Linux (`/media/tanma/DATA/save/mobile_versions:...`) — đã loại bỏ hoàn toàn trong `docker-compose.yml` di động của `web_ban_hang`.

---

## 2. Cài Đặt & Chạy Tạm Trên Máy Windows Hiện Tại

Theo kết quả khảo sát thực tế, máy Windows hiện chưa cài Docker Desktop / PostgreSQL / Odoo native, ổ `C:\` còn `24.77 GB`, ổ `F:\` còn `227.22 GB` và tồn tại một distro WSL2 hỏng tên `VCloudOdoo19`. Thực hiện tuần tự 5 bước sau:

### Bước 2.1 — Dọn entry WSL2 hỏng `VCloudOdoo19`
Mở **PowerShell (Run as Administrator)** và kiểm tra danh sách distro WSL2:

```powershell
wsl --list --verbose
```

Xóa bỏ entry `VCloudOdoo19` đang trỏ vào thư mục không còn tồn tại (`F:\BACKUP_LINUX\local_odoo19\wsl_distro`):

```powershell
wsl --unregister VCloudOdoo19
wsl --update
```

### Bước 2.2 — Cài Docker Desktop (WSL2) & chuyển dữ liệu sang ổ `F:\`
1. Tải và cài đặt **Docker Desktop for Windows** (chọn chế độ **Use WSL 2 instead of Hyper-V**).
2. Khởi động lại máy nếu Windows yêu cầu.
3. Mở **Docker Desktop ➜ Settings ➜ Resources ➜ Advanced**:
   - Đổi **Disk image location** từ ổ `C:\` sang **`F:\DockerData\wsl`** (tạo sẵn thư mục `F:\DockerData\wsl` trước).
   - Nhấn **Apply & Restart** để Docker chuyển toàn bộ image/volume sang ổ `F:\`, bảo vệ dung lượng trống của ổ `C:\`.
4. Kiểm tra lại bằng PowerShell:

```powershell
docker --version
docker compose version
```

### Bước 2.3 — Cấu hình tệp `.env` từ mẫu `.env.example`
Tại thư mục gốc dự án `F:\BACKUP_LINUX\web_ban_hang`:

```powershell
cd F:\BACKUP_LINUX\web_ban_hang
Copy-Item .env.example .env
```

Mở tệp `F:\BACKUP_LINUX\web_ban_hang\.env` và điền mật khẩu mạnh (tệp `.env` đã được khai báo trong `.gitignore`, **tuyệt đối không commit lên Git**):

```env
CLIENT_NAME=web-ban-hang
ODOO_IMAGE=odoo:19.0
POSTGRES_IMAGE=postgres:15-bookworm

ODOO_PORT=1901
LONGPOLLING_PORT=7089
DB_PORT=51901

POSTGRES_USER=odoo
POSTGRES_PASSWORD=<nhap_mat_khau_db_manh>
ODOO_MASTER_PASSWORD=<nhap_master_password_manh>

DB_NAME=web_ban_hang_dev
DB_FILTER=^web_ban_hang.*$
```

*(Nếu muốn chạy cổng `8089` thay vì `1901`, chỉ cần đổi `ODOO_PORT=8089` trong `.env`.)*

### Bước 2.4 — Khởi chạy Docker & Cài 3 Module Milestone 1
Tạo sẵn thư mục dữ liệu runtime cục bộ (đã được `.gitignore` bỏ qua) và khởi chạy hệ thống:

```powershell
mkdir -Force data\filestore, data\sessions, logs
docker compose up -d
docker compose logs -f odoo
```

Đợi đến khi log hiển thị `HTTP service (werkzeug) running on 0.0.0.0:8069`, sau đó khởi tạo database `web_ban_hang_dev` và cài sẵn 3 module **Milestone 1** (`wbh_core`, `theme_gift_store`, `theme_fashion_store`):

```powershell
docker compose exec odoo odoo -c /etc/odoo/odoo.conf `
  -d web_ban_hang_dev `
  -i wbh_core,theme_gift_store,theme_fashion_store `
  --without-demo=all `
  --stop-after-init

docker compose restart odoo
```

*(Hoặc truy cập trình duyệt `http://localhost:1901/web/database/manager`, tạo database tên `web_ban_hang_dev`, đăng nhập và cài 3 module trên từ menu **Ứng dụng**.)*

### Bước 2.5 — Cấu hình xem thử song song 2 Website trên máy cục bộ
- **Cách 1 (Nhanh nhất, không sửa hosts)**: Đăng nhập Backend, vào thanh trên cùng của giao diện Website và dùng **Website Switcher** để chuyển qua lại giữa **Web 1 — Quà Tặng** và **Web 2 — Thời Trang** ngay trên `http://localhost:1901`.
- **Cách 2 (Test đúng 2 tên miền độc lập)**: Mở `C:\Windows\System32\drivers\etc\hosts` bằng quyền Administrator và thêm:

```text
127.0.0.1 quatang.local
127.0.0.1 thoitrang.local
```

Sau đó vào **Website ➜ Cấu hình ➜ Website** trong Backend Odoo, gán domain `http://quatang.local:1901` cho Web 1 và `http://thoitrang.local:1901` cho Web 2.

### Các lệnh vận hành thường dùng
```powershell
# Xem trạng thái container
docker compose ps

# Nâng cấp module sau khi kéo code mới
docker compose exec odoo odoo -c /etc/odoo/odoo.conf -d web_ban_hang_dev -u wbh_core,theme_gift_store,theme_fashion_store --stop-after-init
docker compose restart odoo

# Tắt hệ thống (giữ nguyên dữ liệu DB & Filestore)
docker compose down
```

---

## 3. Hướng Dẫn Nhanh Cho Sếp — Đăng Nhập & Up Sản Phẩm Ngay (Milestone 1)

Ngay khi Milestone 1 hoàn tất và container chạy ổn định, Sếp có thể bắt đầu nhập kho sản phẩm cho cả 2 cửa hàng:

### Bước 3.1 — Đăng nhập Backend quản trị Odoo 19.0
1. Mở trình duyệt truy cập **`http://localhost:1901/web/login`** (hoặc `http://localhost:8089/web/login` nếu chọn cổng `8089`).
2. Nhập tài khoản quản trị đã khởi tạo khi tạo DB `web_ban_hang_dev`.
3. Kiểm tra 2 website đã được `wbh_core` khởi tạo sẵn tại **Website ➜ Cấu hình ➜ Website**:
   - **Web 1 — Quà Tặng** (đã bật `Tài khoản khách hàng riêng theo Website` — `specific_user_account=True`).
   - **Web 2 — Thời Trang** (đã bật `Tài khoản khách hàng riêng theo Website` — `specific_user_account=True`).

### Bước 3.2 — Quy trình 5 bước up sản phẩm lên Web 1 (Quà Tặng) & Web 2 (Thời Trang)
1. Vào menu **Website ➜ Thương mại điện tử ➜ Sản phẩm** ➜ nhấn **Mới**.
2. **Tab Thông tin chung**:
   - Nhập **Tên sản phẩm**, **Giá bán** (VNĐ), mã nội bộ (SKU gốc) và tải **Ảnh đại diện** (ưu tiên ảnh rõ nét, tỷ lệ đồng nhất).
   - Điền mô tả ngắn nổi bật (`wbh_short_highlight`) và ghi chú bảo quản/lưu ý giao hàng (`wbh_care_note`) ngay trên form sản phẩm đã tối ưu của `wbh_core`.
3. **Tab Bán hàng ➜ Mục Thương mại điện tử (CỰC KỲ QUAN TRỌNG)**:
   - **Website**: Bắt buộc chọn đúng **Web 1 (Quà Tặng)** hoặc **Web 2 (Thời Trang)** để sản phẩm hiển thị đúng cửa hàng (tránh để trống gây lẫn sản phẩm giữa 2 thương hiệu).
   - **Phạm vi cửa hàng (`wbh_store_scope`)**: Chọn đồng bộ với Website (`gift` cho Web 1, `fashion` cho Web 2).
   - **Danh mục Website**: Chọn danh mục phù hợp đã khởi tạo sẵn (VD Web 1: *Gấu Bông*, *Móc Khóa*, *Blind Box*, *Combo Quà Tặng*; Web 2: *Áo*, *Quần*, *Váy/Đầm*, *Set Phối Đồ*).
   - **Media bổ sung**: Tải thêm nhiều ảnh góc chụp sản phẩm để hiển thị thư viện ảnh trượt trên mobile.
4. **Tab Thuộc tính & Biến thể**:
   - **Với Web 1 (Quà Tặng)**: Chọn các thuộc tính mẫu như *Màu sắc (Color Swatch)*, *Kích thước gấu bông (cm)*, *Dịp tặng quà*, *Phiên bản Blind Box*.
   - **Với Web 2 (Thời Trang)**: Chọn *Màu sắc (Color Swatch)*, *Size quần áo (S/M/L/XL/XXL)*, *Form dáng*, *Chất liệu*.
   - Nhấn **Cấu hình** nếu cần chỉnh phụ thu giá riêng cho từng kích thước (VD: gấu bông 80cm đắt hơn 40cm).
5. **Nhập tồn kho & Xuất bản lên Web**:
   - Nhấn nút thông minh **Số lượng hiện có (On Hand)** ở đầu trang để nhập tồn kho ban đầu cho từng biến thể SKU.
   - Nhấn nút **Đi đến Website (Go to Website)** ➜ gạt công tắc **Chưa xuất bản ➜ Đã xuất bản (Published)** ở góc trên cùng để sản phẩm hiện ngay cho khách xem và đặt mua.

> **Mẹo kiểm tra nhanh trên di động**: Mở DevTools trình duyệt (`F12` ➜ biểu tượng Mobile `375x812`) để kiểm tra bộ lọc màu/size, hình ảnh sản phẩm và nút *Thêm vào giỏ hàng* trên cả 2 storefront.

---

## 4. Quy Trình Chuyển Môi Trường Sang Local Server Ở Nhà

Khi **Local Server ở nhà** (VD: `192.168.1.100`) hoạt động trở lại, thực hiện di chuyển tuân thủ **tuyệt đối Zero-Bypass Promotion Pipeline**:
- **Mã nguồn**: CHỈ đồng bộ qua **Git** (`git push` từ Windows ➜ `git pull` trên Local Server). **Cấm tuyệt đối** copy/rsync mã nguồn vượt cấp hoặc sửa code trực tiếp trên server.
- **Dữ liệu sản phẩm đã up (Database + Filestore)**: Chuyển qua bản backup có kiểm chứng tính toàn vẹn.

### Bước 4.1 — Trên máy Windows: Push code & Tạo bản sao lưu DB + Filestore
1. Kiểm tra sạch mã nguồn, đồng bộ `docs/*.md`, commit kèm `.claude/` (đã quét sạch secret) với trailer chuẩn và push lên Git:

```powershell
cd F:\BACKUP_LINUX\web_ban_hang
git status
git push origin main
```

2. Sao lưu Database `web_ban_hang_dev` và thư mục Filestore ra một thư mục tạm ngoài Git (VD: `F:\BACKUP_LINUX\backups\web_ban_hang\`):

```powershell
mkdir -Force F:\BACKUP_LINUX\backups\web_ban_hang

# 1. Dump PostgreSQL định dạng nén custom (-Fc)
docker compose exec -T db pg_dump -U odoo -Fc web_ban_hang_dev > F:\BACKUP_LINUX\backups\web_ban_hang\web_ban_hang_dev_20261125.dump

# 2. Nén thư mục Filestore (chứa toàn bộ ảnh sản phẩm Sếp đã up)
Compress-Archive -Path F:\BACKUP_LINUX\web_ban_hang\data\filestore\web_ban_hang_dev -DestinationPath F:\BACKUP_LINUX\backups\web_ban_hang\filestore_20261125.zip -Force
```

3. Chuyển **riêng 2 tệp backup dữ liệu** (`*.dump` và `filestore_*.zip`) sang Local Server (tuyệt đối không copy mã nguồn).

### Bước 4.2 — Trên Local Server ở nhà: Kéo code từ Git & Dựng Container
Đăng nhập SSH vào Local Server, clone hoặc kéo code mới nhất đúng nhánh `main`:

```bash
# Nếu lần đầu dựng trên server:
git clone https://github.com/MATan1808/web_ban_hang.git /srv/projects/web_ban_hang
cd /srv/projects/web_ban_hang

# Nếu đã có repo:
cd /srv/projects/web_ban_hang && git fetch origin && git pull origin main
```

Tạo tệp `.env` riêng cho môi trường Local Server (đặt mật khẩu mạnh, chọn port trong dải `1900`–`1999` theo `360-local-builder-env`, có thể dùng `POSTGRES_IMAGE=360ai/postgres:15-ai` nếu server đã sẵn image này):

```bash
cp .env.example .env
nano .env
mkdir -p data/filestore data/sessions logs
docker compose up -d
```

### Bước 4.3 — Khôi phục Database & Filestore lên Local Server
1. Tạo database đích (VD `web_ban_hang_dev` hoặc `web_ban_hang_staging`) và khôi phục tệp `.dump`:

```bash
docker compose exec -T db createdb -U odoo -T template0 web_ban_hang_dev
docker compose exec -T db pg_restore -U odoo -d web_ban_hang_dev --no-owner --no-acl < /path/to/backup/web_ban_hang_dev_20261125.dump
```

2. Giải nén tệp `filestore_*.zip` vào đúng đường dẫn `data/filestore/web_ban_hang_dev` và cấp quyền sở hữu cho UID `101` (user `odoo` trong container chính thức `odoo:19.0`):

```bash
unzip /path/to/backup/filestore_20261125.zip -d ./data/filestore/
sudo chown -R 101:101 ./data/filestore ./data/sessions
```

3. Khởi động lại Odoo, cập nhật module và kiểm tra vận hành thực tế:

```bash
docker compose restart odoo
docker compose logs --tail=100 odoo
```

4. **Kiểm tra nghiệm thu sau chuyển môi trường**:
   - Truy cập cả 2 storefront (HTTP `200 OK`), không lỗi asset CSS/JS, log container sạch không có `ERROR`/`Traceback`.
   - Kiểm tra đầy đủ sản phẩm, biến thể màu/size và ảnh đại diện Sếp đã up từ máy Windows đều hiển thị trọn vẹn.
   - Đảm bảo `web.base.url` trong *Cài đặt ➜ Kỹ thuật ➜ Tham số hệ thống* và domain của 2 Website đã trỏ đúng địa chỉ Local Server mới.

---

## 5. Xử Lý Sự Cố Thường Gặp (Troubleshooting)

| Hiện tượng | Nguyên nhân phổ biến | Cách khắc phục |
|---|---|---|
| Container `odoo` báo trùng port `1901` | Dịch vụ khác đang dùng cổng `1901` | Đổi `ODOO_PORT=8089` trong `.env` và chạy lại `docker compose up -d`. |
| Vào web thấy màn hình chọn DB trống hoặc lỗi 404 | Tên DB mới không khớp `DB_FILTER=^web_ban_hang.*$` | Đảm bảo tên DB bắt đầu bằng `web_ban_hang` (VD: `web_ban_hang_dev`). |
| Sản phẩm đã tạo nhưng không hiện ngoài cửa hàng | Quên bật công tắc **Published** hoặc gán sai **Website** | Vào trang sản phẩm chọn đúng *Website* + gạt công tắc *Đã xuất bản (Published)*. |
| Ảnh sản phẩm bị vỡ sau khi restore sang Linux Server | Sai đường dẫn hoặc sai quyền sở hữu thư mục `data/filestore/<db_name>` | Kiểm tra tên thư mục trùng khớp tên DB và chạy `sudo chown -R 101:101 ./data/filestore`. |
| Ổ `C:\` Windows nhanh đầy khi chạy Docker | Chưa chuyển *Disk image location* của Docker Desktop sang ổ `F:\` | Làm lại **Bước 2.2** chuyển về `F:\DockerData\wsl` và chạy `docker system prune`. |
