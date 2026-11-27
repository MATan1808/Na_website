# SPEC — Đặc Tả Kỹ Thuật Chi Tiết Milestone 1 (Catalog-First)

> **Phiên bản tài liệu**: v1.0 — Sẵn sàng cho `/plan` và `/build` Milestone 1  
> **Ngày tạo**: 2026-11-25  
> **Nền tảng**: **100% Odoo 19.0 Community (LGPL-3)** + **PostgreSQL 15** (0% Enterprise dependency)  
> **Phạm vi Milestone 1**: Hạ tầng Docker di động + `wbh_core` + `theme_gift_store` (GĐ 1) + `theme_fashion_store` (GĐ 1)  
> **Tài liệu liên quan**: [IDEA.md](file:///F:/BACKUP_LINUX/web_ban_hang/docs/IDEA.md) | [ARCH.md](file:///F:/BACKUP_LINUX/web_ban_hang/docs/ARCH.md) | [REQUIREMENTS.md](file:///F:/BACKUP_LINUX/web_ban_hang/docs/REQUIREMENTS.md) | [CONTEXT.md](file:///F:/BACKUP_LINUX/web_ban_hang/docs/CONTEXT.md) | [DEPLOY_GUIDE.md](file:///F:/BACKUP_LINUX/web_ban_hang/docs/DEPLOY_GUIDE.md)

---

## 1. Mục Tiêu Milestone 1 & Ma Trận Truy Nguồn Yêu Cầu

**Mục tiêu bàn giao Milestone 1**: Đưa lên môi trường Docker di động chạy mượt trên máy Windows (đặt data ổ `F:\`, sẵn sàng chuyển Local Server bằng `git pull` + `docker compose up -d`) gồm Backend quản trị sản phẩm tối ưu và 2 Storefronts độc lập để Sếp đăng nhập và **upload sản phẩm lên ngay** cho cả Web 1 (Quà tặng) và Web 2 (Thời trang).

| Mã Yêu cầu (`REQUIREMENTS.md`) | Thành phần Kỹ thuật trong SPEC này |
|---|---|
| `FR-M1-01`, `NFR-01`, `NFR-05` | Mục 2: Cấu trúc Docker di động (`docker-compose.yml`, `config/odoo.conf`, `.env.example`) dùng `odoo:19.0` Community + `postgres:15-bookworm`. |
| `FR-M1-02`, `FR-M1-03`, `FR-M1-04`, `FR-M1-07`, `NFR-04` | Mục 3: Module `wbh_core` (2 Website `specific_user_account=True`, danh mục mẫu, 7 thuộc tính biến thể, mở rộng `product.template` & Backend Views tối ưu upload). |
| `FR-M1-05`, `NFR-02`, `NFR-03`, `NFR-06` | Mục 4: Module `theme_gift_store` (GĐ 1 — Upgrade-Safe Odoo 19.0 cho Web 1 Quà tặng). |
| `FR-M1-06`, `NFR-02`, `NFR-03`, `NFR-06` | Mục 5: Module `theme_fashion_store` (GĐ 1 — Upgrade-Safe Odoo 19.0 cho Web 2 Thời trang). |
| Chuẩn bị cho Milestone 2 & 3 | Mục 6: Danh sách Extension Points (QWeb slots, model hooks, adapter interfaces). |

**Ràng buộc cứng toàn bộ SPEC**:
- **0% Enterprise Dependency**: Cấm khai báo `depends` vào bất kỳ module nào không thuộc bản Odoo 19.0 Community (`LGPL-3`).
- **100% chuẩn Odoo 19.0 (`360-odoo`)**: Dùng `<list>` (cấm `<tree>`), `invisible="..."` trực tiếp (cấm `attrs=`/`states=`), `@api.model_create_multi`, `odoo.fields.Command`, `models.Constraint()`, `models.Index()`, `markupsafe.Markup(...)`, và Theme Upgrade-Safe.

---

## 2. Đặc Tả Hạ Tầng Docker Di Động (Portable Docker Stack)

Toàn bộ cấu hình Docker nằm trực tiếp trong Git repo `F:\BACKUP_LINUX\web_ban_hang\` để đảm bảo di động tuyệt đối giữa máy Windows hiện tại và Local Server ở nhà (không dùng đường dẫn tuyệt đối của Linux như `/media/tanma/...`).

### 2.1. Biến Môi Trường Mẫu (`F:\BACKUP_LINUX\web_ban_hang\.env.example`)
File `.env.example` được commit vào Git (tuyệt đối chỉ chứa placeholder, không chứa mật khẩu thật); file `.env` thực tế nằm trong `.gitignore`:

```dotenv
# Nhận diện dự án & cô lập container
CLIENT_NAME=web-ban-hang

# Docker Images (Mặc định 100% Odoo 19.0 Community + PostgreSQL 15 di động)
# Khi cần pgvector ở M3+, có thể đổi POSTGRES_IMAGE=360ai/postgres:15-ai
ODOO_IMAGE=odoo:19.0
POSTGRES_IMAGE=postgres:15-bookworm

# Dải Port cô lập (chuẩn 360-local-builder-env dải 19xx, không đụng demo-19 8079/1900)
ODOO_PORT=1901
LONGPOLLING_PORT=7089
DB_PORT=51901

# Cơ sở dữ liệu riêng biệt (TUYỆT ĐỐI không dùng chung demo-19 / odoo19-db)
POSTGRES_USER=odoo
POSTGRES_PASSWORD=change_me_postgres_password
ODOO_MASTER_PASSWORD=change_me_odoo_master_password

DB_NAME=web_ban_hang_dev
DB_FILTER=^web_ban_hang.*$
```

### 2.2. Đặc tả `F:\BACKUP_LINUX\web_ban_hang\docker-compose.yml`
Thiết kế 2 service gọn sạch, chạy được ngay bằng `docker compose up -d`:

- **Service `db`**:
  - `image: ${POSTGRES_IMAGE:-postgres:15-bookworm}`
  - `container_name: ${CLIENT_NAME:-web-ban-hang}-db`
  - `restart: unless-stopped`
  - `environment`: `POSTGRES_USER=${POSTGRES_USER:-odoo}`, `POSTGRES_PASSWORD=${POSTGRES_PASSWORD}`, `POSTGRES_DB=postgres`, `PGDATA=/var/lib/postgresql/data/pgdata`.
  - `volumes`: `web_ban_hang_pgdata:/var/lib/postgresql/data/pgdata` (named volume riêng, tự cô lập khỏi `odoo19-db`).
  - `ports`: `"127.0.0.1:${DB_PORT:-51901}:5432"` (chỉ bind loopback để an toàn).
  - `healthcheck`: `pg_isready -U ${POSTGRES_USER:-odoo} -d postgres` (interval `10s`, timeout `5s`, retries `5`).
- **Service `odoo`**:
  - `image: ${ODOO_IMAGE:-odoo:19.0}` *(Odoo 19.0 Community chính chủ, có sẵn toàn bộ core Community addons tại `/usr/lib/python3/dist-packages/odoo/addons`)*.
  - `container_name: ${CLIENT_NAME:-web-ban-hang}-app`
  - `depends_on`: `db` với `condition: service_healthy`.
  - `restart: unless-stopped`
  - `ports`: `"${ODOO_PORT:-1901}:8069"` và `"${LONGPOLLING_PORT:-7089}:8072"`.
  - `environment`: `HOST=db`, `PORT=5432`, `USER=${POSTGRES_USER:-odoo}`, `PASSWORD=${POSTGRES_PASSWORD}`.
  - `volumes`:
    - `./addons:/mnt/extra-addons` *(7 custom modules của dự án)*
    - `./config/odoo.conf:/etc/odoo/odoo.conf:ro`
    - `./data/filestore:/var/lib/odoo/filestore` *(Filestore riêng, gitignored)*
    - `./data/sessions:/var/lib/odoo/sessions` *(Sessions riêng, gitignored)*
  - `healthcheck`: kiểm tra HTTP `http://localhost:8069/web/health` (interval `30s`, timeout `10s`, retries `5`, `start_period: 40s`).
- **Named Volume**: khai báo tường minh `volumes: { web_ban_hang_pgdata: { name: "${CLIENT_NAME:-web-ban-hang}_pgdata" } }`.

### 2.3. Đặc tả `F:\BACKUP_LINUX\web_ban_hang\config\odoo.conf`
```ini
[options]
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons
data_dir = /var/lib/odoo
admin_passwd = change_me_odoo_master_password
db_host = db
db_port = 5432
db_user = odoo
dbfilter = ^web_ban_hang.*$
list_db = True
proxy_mode = True
without_demo = all
log_level = info
limit_time_cpu = 120
limit_time_real = 240
```
*(Ghi chú: Trên Staging/Production, bắt buộc đặt `list_db = False`, cấu hình `workers` theo CPU và đổi `admin_passwd` bằng bản hash PBKDF2).*

---

## 3. Đặc Tả Chi Tiết Module `wbh_core` (`F:\BACKUP_LINUX\web_ban_hang\addons\wbh_core\`)

### 3.1. Manifest & Cấu Trúc Thư Mục
- **Đường dẫn**: `F:\BACKUP_LINUX\web_ban_hang\addons\wbh_core\`
- **Cấu trúc tệp**:
  ```text
  wbh_core/
  ├── __init__.py
  ├── __manifest__.py
  ├── data/
  │   ├── website_data.xml
  │   ├── product_public_category_data.xml
  │   └── product_attribute_data.xml
  ├── models/
  │   ├── __init__.py
  │   ├── website.py
  │   └── product_template.py
  ├── security/
  │   ├── wbh_security.xml
  │   └── ir.model.access.csv
  ├── views/
  │   ├── product_template_views.xml
  │   ├── website_views.xml
  │   └── wbh_menus.xml
  └── tests/
      ├── __init__.py
      └── test_wbh_core.py
  ```
- **Thông số `__manifest__.py`**:
  - `name`: `'WBH Core — Hạ Tầng Đa Cửa Hàng Quà Tặng & Thời Trang'`
  - `version`: `'19.0.1.0.0'`
  - `category`: `'Website/Website'`
  - `license`: `'LGPL-3'`
  - `author`: `'360org'`
  - **`depends` (100% Community — đã kiểm tra 0% Enterprise)**:
    `['base', 'website', 'website_sale', 'website_sale_wishlist', 'website_sale_comparison', 'website_sale_stock', 'sale_management', 'stock', 'product', 'contacts', 'portal']`
  - `description`: Ghi đầy đủ changelog theo chuẩn `360-odoo` (`v19.0.1.0.0 (2026-11-25)` kèm `[NEW]`).

### 3.2. Thiết Kế Data Models (Chuẩn Odoo 19.0 ORM)

#### A. Mở rộng `website` (`models/website.py`)
Mục tiêu: Đánh dấu nghiệp vụ từng cửa hàng và đảm bảo tách tài khoản khách hàng.

| Field | Kiểu & Thuộc tính | Mô tả |
|---|---|---|
| `wbh_store_type` | `fields.Selection([('gift', 'Web 1 — Quà tặng'), ('fashion', 'Web 2 — Thời trang')], string='Loại Cửa hàng WBH', index=False)` | Định danh cửa hàng để các theme và module M2/M3 phân nhánh sạch không hardcode ID. |
| `wbh_brand_tagline` | `fields.Char(string='Khẩu hiệu Thương hiệu', translate=True)` | Hiển thị trên header/footer và tiêu đề SEO mặc định của từng website. |
| `wbh_support_hotline` | `fields.Char(string='Hotline CSKH')` | Số hotline hiển thị riêng cho từng thương hiệu trên footer/trang sản phẩm. |
| `wbh_support_zalo_url` | `fields.Char(string='Link Zalo CSKH')` | Nút liên hệ nhanh Zalo hiển thị riêng từng cửa hàng. |

- **Index chuẩn Odoo 19.0**: `_wbh_store_type_idx = models.Index('(wbh_store_type)')`.

#### B. Mở rộng `product.template` (`models/product_template.py`)
Mục tiêu: Tối ưu hóa việc Sếp đăng sản phẩm nhanh lên đúng Web 1 hoặc Web 2, đồng bộ tự động `website_id` và chuẩn bị thông tin hiển thị đẹp trên storefront.

| Field | Kiểu & Thuộc tính | Mô tả & Logic |
|---|---|---|
| `wbh_store_scope` | `fields.Selection([('gift', 'Web 1 — Quà tặng'), ('fashion', 'Web 2 — Thời trang'), ('both', 'Hiển thị Cả 2 Website')], string='Cửa hàng đăng bán', default='gift', required=True)` | Tự động đồng bộ trường `website_id`: `'gift'` ➜ `website_gift_store`; `'fashion'` ➜ `website_fashion_store`; `'both'` ➜ `False` (hiển thị cả 2 web). |
| `wbh_short_highlight` | `fields.Char(string='Điểm nổi bật ngắn', translate=True)` | Tóm tắt 1 dòng (VD: *"Bông PP siêu mềm, tặng kèm túi rút"* hoặc *"Cotton 250gsm thoáng mát, đứng form"*), hiển thị ngay dưới tên sản phẩm trên trang chi tiết. |
| `wbh_care_note` | `fields.Text(string='Hướng dẫn bảo quản / Lưu ý', translate=True)` | Hiển thị trong mục accordion gọn trên trang chi tiết (hướng dẫn giặt gấu bông / giặt ủi quần áo). |
| `wbh_low_stock_threshold` | `fields.Float(string='Ngưỡng cảnh báo sắp hết hàng', default=5.0)` | Ngưỡng tồn kho tối thiểu để cảnh báo nhập hàng (nền tảng cho cảnh báo tự động ở M3). |
| `wbh_is_low_stock` | `fields.Boolean(string='Sắp hết hàng', compute='_compute_wbh_is_low_stock', store=False)` | `True` khi `type == 'consu'` (hàng lưu kho `is_storable=True` trong Odoo 19) và `qty_available <= wbh_low_stock_threshold`. |

- **Ràng buộc & Chỉ mục chuẩn Odoo 19.0**:
  - `_check_wbh_low_stock_threshold = models.Constraint('CHECK(wbh_low_stock_threshold >= 0)', 'Ngưỡng cảnh báo tồn kho phải lớn hơn hoặc bằng 0.')`
  - `_wbh_store_scope_published_idx = models.Index('(wbh_store_scope, is_published)')`
- **ORM Hooks chuẩn Odoo 19.0**:
  - Hàm helper `_wbh_resolve_website_id(scope)` tra cứu an toàn bằng `self.env.ref('wbh_core.website_gift_store', raise_if_not_found=False)` và `website_fashion_store`.
  - `@api.onchange('wbh_store_scope')`: Cập nhật tức thì `self.website_id` ngay khi Sếp chọn phạm vi cửa hàng trên giao diện.
  - `@api.model_create_multi def create(self, vals_list)`: Nếu có `wbh_store_scope` mà chưa truyền tường minh `website_id`, tự động gán `website_id` tương ứng; tôn trọng `allowed_company_ids`.
  - `def write(self, vals)`: Khi `wbh_store_scope` thay đổi mà không truyền tường minh `website_id`, tự động đồng bộ lại `website_id`.

### 3.3. Dữ Liệu Khởi Tạo Mẫu (`data/` — `noupdate="1"`)

#### A. `data/website_data.xml` (2 Website Độc Lập)
1. **`wbh_core.website_gift_store`**:
   - `name`: `'Cửa Hàng Quà Tặng — Móc Khóa, Gấu Bông & Blind Box'`
   - `wbh_store_type`: `'gift'`
   - **`specific_user_account`**: `True` *(tách tài khoản khách hàng riêng Web 1)*
   - `wbh_brand_tagline`: `'Gửi trọn cảm xúc trong từng món quà nhỏ'`
   - `shop_default_sort`: `'website_sequence asc'`
   - `cart_add_on_click` / cấu hình hiển thị lọc thuộc tính mặc định bật sẵn.
2. **`wbh_core.website_fashion_store`**:
   - `name`: `'Cửa Hàng Thời Trang — Quần Áo & Lookbook'`
   - `wbh_store_type`: `'fashion'`
   - **`specific_user_account`**: `True` *(tách tài khoản khách hàng riêng Web 2)*
   - `wbh_brand_tagline`: `'Tối giản hiện đại — Chuẩn form từng khoảnh khắc'`
   - `shop_default_sort`: `'website_sequence asc'`

#### B. `data/product_public_category_data.xml` (Cây Danh Mục Mẫu)
- **Nhánh Web 1 (`website_id = ref('wbh_core.website_gift_store')`)**:
  - `wbh_core.pub_cat_gift_plush`: `Gấu bông`
  - `wbh_core.pub_cat_gift_keychain`: `Móc khóa`
  - `wbh_core.pub_cat_gift_blindbox`: `Blind Box`
  - `wbh_core.pub_cat_gift_occasion`: `Quà theo dịp` (con: `Sinh nhật`, `Valentine`, `Tốt nghiệp`, `8/3 & 20/10`)
  - `wbh_core.pub_cat_gift_combo`: `Combo quà tặng`
- **Nhánh Web 2 (`website_id = ref('wbh_core.website_fashion_store')`)**:
  - `wbh_core.pub_cat_fashion_tops`: `Áo` (con: `Áo thun`, `Áo sơ mi`, `Áo khoác`)
  - `wbh_core.pub_cat_fashion_bottoms`: `Quần` (con: `Quần jeans`, `Quần ống rộng / Tây`, `Quần short`)
  - `wbh_core.pub_cat_fashion_dresses`: `Váy & Đầm`
  - `wbh_core.pub_cat_fashion_sets`: `Set đồ / Lookbook`
  - `wbh_core.pub_cat_fashion_accessories`: `Phụ kiện thời trang`

#### C. `data/product_attribute_data.xml` (Bộ 7 Thuộc Tính Biến Thể Chuẩn)

| XML ID | Tên thuộc tính | `display_type` | `create_variant` | Giá trị khởi tạo mẫu |
|---|---|---|---|---|
| `wbh_core.attr_color_swatch` | `Màu sắc` | `color` | `always` | Đen (`#1A1A1A`), Trắng (`#FFFFFF`), Kem Be (`#F3E5D8`), Hồng Pastel (`#F8BBD0`), Xanh Navy (`#1F3A5F`), Xám (`#8E949E`), Nâu Cacao (`#6D4C41`), Đỏ Đô (`#8B1E3F`) |
| `wbh_core.attr_fashion_size` | `Size Quần Áo` | `pills` | `always` | `XS`, `S`, `M`, `L`, `XL`, `XXL`, `Freesize` |
| `wbh_core.attr_gift_plush_size` | `Kích thước Gấu Bông (cm)` | `pills` | `always` | `15cm`, `25cm`, `40cm`, `60cm`, `80cm`, `1m`, `1m2` |
| `wbh_core.attr_material` | `Chất liệu` | `pills` | `no_variant` | `Cotton 100%`, `Linen`, `Denim`, `Bông PP siêu mềm`, `Nhựa PVC/ABS`, `Acrylic`, `Hợp kim` |
| `wbh_core.attr_fashion_fit` | `Form dáng` | `pills` | `no_variant` | `Oversize`, `Regular`, `Slim Fit`, `Relaxed` |
| `wbh_core.attr_gift_occasion` | `Dịp tặng quà` | `pills` | `no_variant` | `Sinh nhật`, `Valentine`, `8/3 & 20/10`, `Tốt nghiệp`, `Kỷ niệm`, `Giáng sinh` |
| `wbh_core.attr_blindbox_edition` | `Phiên bản Blind Box` | `radio` | `always` | `Hộp lẻ (1 Box)`, `Nguyên Set (Full Case)` |

*(Lưu ý: Dùng `odoo.fields.Command` trong Python hoặc record `product.attribute.value` tách rõ trong XML để dễ bảo trì & nâng cấp).*

### 3.4. Backend Views & Menu Tối Ưu Upload Sản Phẩm (`views/`)
- **`views/wbh_menus.xml`**: Tạo menu cấp cao **"2 Cửa Hàng (WBH)"** gồm các action lọc sẵn:
  1. **Sản phẩm Web 1 — Quà tặng** (`domain="[('wbh_store_scope', 'in', ('gift', 'both'))]"`, `context="{'default_wbh_store_scope': 'gift', 'default_is_storable': True}"`).
  2. **Sản phẩm Web 2 — Thời trang** (`domain="[('wbh_store_scope', 'in', ('fashion', 'both'))]"`, `context="{'default_wbh_store_scope': 'fashion', 'default_is_storable': True}"`).
  3. **Danh mục Website** (`product.public.category` dạng `<list>` nhóm theo `website_id`).
  4. **Thuộc tính & Biến thể** (`product.attribute`).
  5. **Đơn hàng 2 Website** (`sale.order` nhóm theo `website_id`).
  6. **Cấu hình 2 Website** (`website` mở form sửa `wbh_store_type`, tagline, hotline, link Zalo).
- **`views/product_template_views.xml`**:
  - Kế thừa `product.product_template_only_form_view`: Chèn nhóm **"Thông tin Đăng bán WBH"** ngay trong tab chính (General Information) gồm `wbh_store_scope`, `website_id` (tự khóa `readonly="wbh_store_scope != 'both'"`), `public_categ_ids`, `is_published`, `wbh_short_highlight`, `wbh_care_note`, `wbh_low_stock_threshold`.
  - Kế thừa Search View: Thêm bộ lọc nhanh `Web 1 — Quà tặng`, `Web 2 — Thời trang`, `Đã đăng bán`, `Chưa đăng bán`, `Sắp hết hàng` và Group By `wbh_store_scope` / `website_id`.
  - Kế thừa List View (`<list>` — cấm `<tree>`): Thêm cột `wbh_store_scope` (widget `badge`), `is_published` (widget `boolean_toggle` cho phép Sếp bật/tắt đăng bán nhanh ngay ngoài danh sách!).

### 3.5. Phân Quyền & Bảo Mật (`security/`)
- **`security/wbh_security.xml`**:
  - Tạo danh mục quyền `WBH Multi-Store` với 2 nhóm kế thừa chuẩn:
    - `wbh_core.group_wbh_catalog_user` (Nhân viên đăng sản phẩm & vận hành — kế thừa `sales_team.group_sale_salesman`, `stock.group_stock_user`).
    - `wbh_core.group_wbh_manager` (Quản trị 2 cửa hàng — kế thừa `wbh_core.group_wbh_catalog_user`, `website.group_website_designer`, `sales_team.group_sale_manager`).
  - Record rules (`ir.rule`) đảm bảo người dùng Public/Portal chỉ truy cập sản phẩm `is_published = True` thuộc `website_id` tương ứng hoặc dùng chung, tôn trọng `allowed_company_ids`.
- **`security/ir.model.access.csv`**: Khai báo đầy đủ quyền truy cập cho mọi model mở rộng (nếu có model mới ở M2/M3) và đảm bảo nhóm `group_wbh_catalog_user` có đủ quyền CRUD trên `product.public.category` và `product.attribute.value`.

---

## 4. Đặc Tả Chi Tiết Module `theme_gift_store` (Giai Đoạn 1 — Upgrade-Safe Odoo 19.0)

- **Đường dẫn**: `F:\BACKUP_LINUX\web_ban_hang\addons\theme_gift_store\`
- **`__manifest__.py`**:
  - `name`: `'Theme Web 1 — Cửa Hàng Quà Tặng (Móc Khóa, Gấu Bông & Blind Box)'`
  - `version`: `'19.0.1.0.0'`
  - `category`: `'Theme/eCommerce'`
  - `license`: `'LGPL-3'`
  - `depends`: `['wbh_core', 'theme_default']` *(100% Community)*
  - `assets`:
    - `'web._assets_primary_variables'`: `['theme_gift_store/static/src/scss/primary_variables.scss']`
    - `'web.assets_frontend'`: `['theme_gift_store/static/src/scss/theme_gift.scss']`
    - `'web_editor.assets_wysiwyg'`: `['theme_gift_store/static/src/scss/theme_gift_editor.scss']`
- **Cấu trúc tệp**:
  ```text
  theme_gift_store/
  ├── __init__.py
  ├── __manifest__.py
  ├── data/
  │   └── presets.xml
  ├── views/
  │   ├── layout.xml
  │   ├── pages/
  │   │   └── home.xml
  │   ├── snippets/
  │   │   ├── s_gift_hero.xml
  │   │   ├── s_gift_occasion_bar.xml
  │   │   ├── s_gift_featured_grid.xml
  │   │   └── snippets.xml
  │   └── shop_templates.xml
  └── static/
      └── src/
          ├── img/
          └── scss/
              ├── primary_variables.scss
              ├── theme_gift.scss
              └── theme_gift_editor.scss
  ```
- **Bảng màu SCSS (`primary_variables.scss`)**:
  - `$o-color-1: #FF6B8B;` (Hồng san hô chủ đạo — CTA & điểm nhấn)
  - `$o-color-2: #FFB347;` (Vàng mật ong — nhãn ưu đãi / dịp lễ)
  - `$o-color-3: #FFF6F0;` (Kem ấm — nền section dịu mắt)
  - `$o-color-4: #FFFFFF;` (Trắng tinh khiết — nền thẻ sản phẩm)
  - `$o-color-5: #3D2C2E;` (Nâu cacao đậm — chữ chính dễ đọc, độ tương phản cao đạt WCAG AA)
  - Typography thân thiện tiếng Việt: `Be Vietnam Pro` / `Quicksand`.
- **Chuẩn Upgrade-Safe (`data/presets.xml` & `views/`)**:
  - `data/presets.xml`: Bật bộ lọc thuộc tính Shop (`website_sale.products_attributes` `active="True"`), bật danh mục Shop (`website_sale.products_categories` `active="True"`), bật Wishlist (`website_sale_wishlist`), tắt các khối header/footer không dùng bằng `active="False"`.
  - Trang chủ (`views/pages/home.xml`): Bắt buộc wrapper `<div id="wrap" class="oe_structure oe_empty">`.
  - 3 Building Blocks kéo-thả chuẩn (`o_colored_level` + `data-snippet`):
    1. `s_gift_hero`: Banner lớn chủ đề quà tặng kèm nút "Chọn quà theo dịp" và "Khám phá Blind Box".
    2. `s_gift_occasion_bar`: Thanh biểu tượng chọn nhanh theo danh mục (Gấu bông, Móc khóa, Blind Box, Sinh nhật, Valentine, Combo).
    3. `s_gift_featured_grid`: Khối hiển thị lưới sản phẩm nổi bật dẫn tới `/shop`.
  - **Header & Footer riêng Web 1**: Kế thừa template layout chỉ kích hoạt trong scope của `theme_gift_store` (tuyệt đối không ghi đè sang `theme_fashion_store`), hiển thị `website.wbh_brand_tagline`, hotline và link Zalo của Web 1.
  - **Trang Shop & Trang Chi Tiết (`views/shop_templates.xml`)**:
    - Thẻ sản phẩm bo góc mềm (`border-radius: 16px`), tỷ lệ ảnh `1:1` vuông vắn phù hợp gấu bông/móc khóa/blind box, hiển thị chấm màu Color Swatch & nhãn tình trạng còn hàng.
    - Trang chi tiết: Hiển thị `product.wbh_short_highlight` dạng badge nổi bật dưới tiêu đề, bộ chọn biến thể `pills` / `color`, accordion hiển thị `product.wbh_care_note`, thanh sticky bottom bar trên mobile (giá + nút "Thêm vào giỏ").

---

## 5. Đặc Tả Chi Tiết Module `theme_fashion_store` (Giai Đoạn 1 — Upgrade-Safe Odoo 19.0)

- **Đường dẫn**: `F:\BACKUP_LINUX\web_ban_hang\addons\theme_fashion_store\`
- **`__manifest__.py`**:
  - `name`: `'Theme Web 2 — Cửa Hàng Thời Trang (Quần Áo & Lookbook)'`
  - `version`: `'19.0.1.0.0'`
  - `category`: `'Theme/eCommerce'`
  - `license`: `'LGPL-3'`
  - `depends`: `['wbh_core', 'theme_default']` *(100% Community)*
  - `assets`:
    - `'web._assets_primary_variables'`: `['theme_fashion_store/static/src/scss/primary_variables.scss']`
    - `'web.assets_frontend'`: `['theme_fashion_store/static/src/scss/theme_fashion.scss']`
    - `'web_editor.assets_wysiwyg'`: `['theme_fashion_store/static/src/scss/theme_fashion_editor.scss']`
- **Cấu trúc tệp**:
  ```text
  theme_fashion_store/
  ├── __init__.py
  ├── __manifest__.py
  ├── data/
  │   └── presets.xml
  ├── views/
  │   ├── layout.xml
  │   ├── pages/
  │   │   └── home.xml
  │   ├── snippets/
  │   │   ├── s_fashion_lookbook_hero.xml
  │   │   ├── s_fashion_category_strip.xml
  │   │   ├── s_fashion_editorial_grid.xml
  │   │   └── snippets.xml
  │   └── shop_templates.xml
  └── static/
      └── src/
          ├── img/
          └── scss/
              ├── primary_variables.scss
              ├── theme_fashion.scss
              └── theme_fashion_editor.scss
  ```
- **Bảng màu SCSS (`primary_variables.scss`)**:
  - `$o-color-1: #111111;` (Đen than tối giản — nút CTA & viền sắc nét)
  - `$o-color-2: #C8B6A6;` (Be cát editorial — điểm nhấn thời trang)
  - `$o-color-3: #F5F5F3;` (Xám đá nhạt — nền section sạch)
  - `$o-color-4: #FFFFFF;` (Trắng tuyệt đối — làm nổi bật màu vải)
  - `$o-color-5: #222222;` (Chữ chính đậm sắc nét)
  - Typography hỗ trợ tiếng Việt hiện đại: `Plus Jakarta Sans` / `Inter`.
- **Chuẩn Upgrade-Safe (`data/presets.xml` & `views/`)**:
  - `data/presets.xml`: Bật bộ lọc thuộc tính Shop (`website_sale.products_attributes` `active="True"`), danh mục (`website_sale.products_categories` `active="True"`), tắt các phần tử mặc định thừa bằng `active="False"`.
  - Trang chủ (`views/pages/home.xml`): Bắt buộc wrapper `<div id="wrap" class="oe_structure oe_empty">`.
  - 3 Building Blocks kéo-thả chuẩn (`o_colored_level` + `data-snippet`):
    1. `s_fashion_lookbook_hero`: Banner Lookbook full-bleed kèm nút "Xem Bộ Sưu Tập Mới".
    2. `s_fashion_category_strip`: Lưới 4 ô danh mục chủ lực (Áo, Quần, Váy & Đầm, Set đồ).
    3. `s_fashion_editorial_grid`: Lưới sản phẩm phong cách tạp chí thời trang tỷ lệ ảnh dọc `3:4`.
  - **Header & Footer riêng Web 2**: Bố cục tối giản thanh thoát, hiển thị tagline/hotline/Zalo riêng của Web 2, tuyệt đối tách biệt với Web 1.
  - **Trang Shop & Trang Chi Tiết (`views/shop_templates.xml`)**:
    - Thẻ sản phẩm tỷ lệ ảnh dọc **`3:4`** (`aspect-ratio: 3/4; object-fit: cover;`) chuyên cho ảnh người mẫu mặc quần áo, hiển thị chấm màu **Color Swatch** ngay dưới ảnh.
    - Bộ lọc thuộc tính rõ ràng (Màu sắc, Size Quần Áo, Form dáng, Chất liệu, Khoảng giá), mở dạng drawer gọn trên mobile.
    - Trang chi tiết: Hiển thị `product.wbh_short_highlight`, nút chọn Size dạng pills lớn dễ chạm 1 tay trên điện thoại, accordion `product.wbh_care_note` (Chất liệu & Hướng dẫn giặt ủi), thanh sticky bottom Add-to-Cart trên mobile.

---

## 6. Extension Points Mở Sẵn Cho Milestone 2 & Milestone 3

Để Milestone 2 và Milestone 3 có thể cắm vào mượt mà mà **không phải đập đi xây lại** code Milestone 1, toàn bộ các điểm mở rộng sau bắt buộc được đặt sẵn ngay trong Milestone 1:

### 6.1. QWeb Extension Slots trên Storefronts
- **Trong `theme_gift_store/views/shop_templates.xml`**:
  - `<div id="wbh_gift_options_slot" class="wbh-ext-slot"/>` (đặt ngay trên nút Thêm vào giỏ) ➜ Milestone 2 (`wbh_gift_store`) sẽ kế thừa XPath chèn Widget Gói quà + Thiệp & Form Cá nhân hóa khắc/thêu tên.
  - `<div id="wbh_gift_size_compare_slot" class="wbh-ext-slot"/>` (đặt dưới mô tả ngắn) ➜ Milestone 2 chèn Block So sánh kích thước cạnh vật mẫu.
  - `<div id="wbh_flash_sale_banner_slot" class="wbh-ext-slot"/>` (đặt trên giá sản phẩm) ➜ Milestone 3 chèn đồng hồ đếm ngược Flash Sale.
- **Trong `theme_fashion_store/views/shop_templates.xml`**:
  - `<div id="wbh_fashion_size_advisor_slot" class="wbh-ext-slot"/>` (đặt cạnh nhóm chọn Size Quần Áo) ➜ Milestone 2 (`wbh_fashion_store`) chèn nút mở OWL Gợi ý Size thông minh.
  - `<div id="wbh_fashion_video_gallery_slot" class="wbh-ext-slot"/>` (trong khu vực media gallery) ➜ Milestone 2 chèn trình phát Video người mẫu dọc 9:16 từ CDN.
  - `<div id="wbh_fashion_shop_the_look_slot" class="wbh-ext-slot"/>` (đặt ngay dưới phần chi tiết sản phẩm) ➜ Milestone 2 chèn khối Shop The Look chọn size từng món & thêm trọn bộ 1 click.
  - `<div id="wbh_flash_sale_banner_slot" class="wbh-ext-slot"/>` ➜ Milestone 3 chèn Flash Sale.

### 6.2. Backend & Service Extension Points trong `wbh_core`
- **Nhận diện Cửa hàng chuẩn**: Trường `website.wbh_store_type` (`'gift'` / `'fashion'`) là khóa duy nhất để `wbh_gift_store`, `wbh_fashion_store` và `loyalty` (M3) áp dụng quy tắc đúng cửa hàng.
- **Chuẩn bị cho Thanh toán (`wbh_payment_vietqr` — M3)**:
  - Thiết kế kế thừa `payment.provider` (`code = 'vietqr'`) với lớp service tách biệt `VietQREmvcoGenerator` (sinh chuỗi EMVCo/Napas 247 offline thuần Python, 0% phụ thuộc bên thứ ba) và interface adapter `VietQRWebhookAdapter` (mặc định triển khai `SePayAdapter`, mở rộng dễ dàng `PayOSAdapter` / `CassoAdapter`).
- **Chuẩn bị cho Vận chuyển (`wbh_delivery_vn` — M3)**:
  - Thiết kế kế thừa `delivery.carrier` (`delivery_type` theo hãng) dùng chung bảng địa giới hành chính VN 3 cấp (`wbh.vn.province`, `wbh.vn.district`, `wbh.vn.ward`), ưu tiên triển khai `GhnCarrierAdapter` (API miễn phí + Sandbox) song song cấu hình Ship nội bộ/Đồng giá, sau đó bổ sung `GhtkCarrierAdapter` và `VtpCarrierAdapter`.

---

## 7. Kế Hoạch Kiểm Thử & Cổng Chặn Milestone 1 (`/code-review` & `/test`)

1. **Automated Unit Tests (`wbh_core/tests/test_wbh_core.py` — `TransactionCase`)**:
   - Kiểm tra 2 bản ghi `website_gift_store` & `website_fashion_store` tồn tại và đều có `specific_user_account == True`.
   - Kiểm tra tạo sản phẩm với `wbh_store_scope='gift'` tự động gán `website_id == website_gift_store`; đổi sang `'fashion'` tự động cập nhật `website_id == website_fashion_store`; đổi sang `'both'` gán `website_id == False`.
   - Kiểm tra `models.Constraint` từ chối giá trị `wbh_low_stock_threshold < 0`.
   - Kiểm tra tồn tại đủ 7 thuộc tính mẫu (`attr_color_swatch` có `display_type == 'color'`, v.v.) và cây danh mục của 2 website.
2. **Kiểm tra Tự động Cổng `/code-review` (4 trục)**:
   - Xác minh 100% `depends` không chứa bất kỳ module Enterprise nào.
   - Xác minh 0% sử dụng `<tree>`, `attrs=`, `states=`, `_sql_constraints`, tuple x2many `(0, 0, ...)`.
   - Xác minh 2 theme có đủ `<div id="wrap" class="oe_structure oe_empty">`, `o_colored_level`, `data-snippet`, `data/presets.xml`, `$o-color-1..5`.
   - Xác minh `.env.example` và `.claude/` sạch 100% secret/password thật.
3. **Kiểm thử Thực tế E2E Milestone 1**:
   - Dựng `docker compose up -d`, cài đặt 3 module M1 trên DB sạch `web_ban_hang_dev`.
   - Upload 2 sản phẩm mẫu (1 Gấu bông/Blind Box cho Web 1, 1 Áo/Quần có màu + size cho Web 2), kiểm tra hiển thị trên 2 storefront (Desktop & Mobile viewport), kiểm tra bộ lọc & tạo đơn hàng thử thành công.
