# DESIGN.md — Hệ Thống Quy Chuẩn Thiết Kế Giao Diện (Design System Specification)

> **Dự án**: Hệ Sinh Thái 2 Website Bán Hàng (`web_ban_hang`) — **Odoo 19.0 Community (LGPL-3)**  
> **Áp dụng**: Bắt buộc tuân thủ cho mọi AI Agent, lập trình viên và tác vụ can thiệp vào UI, QWeb Templates, SCSS, và CSS Snippets.

---

## 1. Nguyên Tắc Cốt Lõi (Core Design Principles)

1. **Tuân thủ Bản sắc Độc lập của 2 Thương hiệu (Multi-Website Coexistence)**:
   - **Web 1 — Manh Dao Dao - Boku no Hero Academia Anime Goods Shop (`theme_gift_store`)**: Sạch sẽ, sắc nét, đậm chất sưu tầm Anime Goods (Blue & Black — đồng bộ logo mèo đen mắt xanh dương & lựu đạn xanh dương). Tập trung Doll và các loại goods *Boku no Hero Academia* (card, postcard, clear file, bookmark, standee, key, badge...). Slogan: *Tiền trao tay, quýt về ngay*.
   - **Web 2 — Cửa Hàng Thời Trang (`theme_fashion_store`)**: Tối giản, thanh lịch, sang trọng, thời thượng (Editorial & Minimalist). Dành cho Quần áo, Lookbook, Phụ kiện streetwear.
2. **Upgrade-Safe 100% trong Odoo 19.0**:
   - Không can thiệp sửa trực tiếp file lõi của Odoo.
   - Khai báo biến qua `$o-color-palettes` và `$o-theme-font-configs` trong `primary_variables.scss` với cờ `!default`.
   - Sử dụng CSS Custom Properties (`--wbh-*`) và utility classes có prefix (`.wbh-store-gift`, `.wbh-gift-*`, `.wbh-store-fashion`, `.wbh-fashion-*`) để triệt tiêu hoàn toàn nguy cơ xung đột (CSS scoping).
3. **Tương thích Bootstrap 5.3.3 & Không dùng Tailwind trực tiếp**:
   - Odoo 19 Website Builder chạy trên nền Bootstrap 5.3.3. Tránh cài đặt Tailwind CSS trực tiếp vào Odoo bundle vì gây xung đột class (`container`, `row`, `btn`, `d-flex`). Toàn bộ design tokens được đồng bộ qua `css/variables.css`, `css/system.css` và biến SCSS của theme.

---

## 2. Hệ Thống Màu Sắc (Color Tokens)

### 2.1. Web 1 — Manh Dao Dao Anime Goods Shop (Xanh Dương – Đen, WCAG AA)
- `--wbh-gift-primary`: `#1D4ED8` (Xanh dương chủ đạo — CTA chính, nút mua ngay, điểm nhấn thương hiệu; contrast `>= 6.7:1` với chữ trắng).
- `--wbh-gift-primary-hover`: `#1E40AF` (Xanh dương đậm — trạng thái hover/active CTA; contrast `>= 8.6:1`).
- `--wbh-gift-topbar-bg`: `#0B1220` / `#0F172A` (Đen xanh navy đậm — topbar, footer tối, badge giảm giá).
- `--wbh-gift-bg`: `#F4F7FB` (Nền sáng ánh xanh dịu — nền trang sạch sẽ, tôn ảnh sản phẩm thật).
- `--wbh-gift-surface`: `#FFFFFF` (Trắng tinh khiết — nền thẻ sản phẩm, header, hộp tư vấn).
- `--wbh-gift-border`: `#DCE4F0` (Viền hairline xanh xám mảnh).
- `--wbh-gift-text`: `#0B1220` (Đen mực đậm — chữ chính đạt chuẩn WCAG AA).
- `--wbh-gift-text-muted`: `#52627A` (Xám xanh trung tính — mô tả phụ, giá gạch, đạt `>= 5.2:1` trên nền trắng).

### 2.2. Web 2 — Cửa Hàng Thời Trang (Fashion & Lookbook)
- `--wbh-fashion-primary`: `#111111` (Đen than tuyền — CTA dứt khoát, typography đậm nét).
- `--wbh-fashion-accent`: `#C8B6A6` (Be cát sa mạc — đường viền sang trọng, điểm nhấn lookbook).
- `--wbh-fashion-bg`: `#F5F5F3` (Xám đá sáng — nền background trung tính tôn màu vải).
- `--wbh-fashion-surface`: `#FFFFFF` (Trắng tuyệt đối — thẻ sản phẩm, khung ảnh lookbook).
- `--wbh-fashion-text`: `#222222` (Đen than chữ chính — độ nét cao).
- `--wbh-fashion-text-muted`: `#777777` (Xám trung tính — thông số size, chất liệu vải).

---

## 3. Kiểu Chữ & Typography

### 3.1. Web 1 — Manh Dao Dao
- **Heading**: `'Quicksand', 'Be Vietnam Pro', sans-serif` — Bo tròn gọn gàng, thân thiện nhưng sắc nét.
- **Body & UI**: `'Be Vietnam Pro', sans-serif` — Chuẩn font tiếng Việt sắc nét trên mọi màn hình, hỗ trợ `tabular-nums` cho bảng giá.

### 3.2. Web 2 — Thời Trang (Fashion Store)
- **Heading & Lookbook**: `'Plus Jakarta Sans', 'Playfair Display', sans-serif` — Tinh tế, thời thượng.
- **Body & Product Specs**: `'Inter', -apple-system, sans-serif` — Tối giản, hiện đại, khoảng cách ký tự (tracking) thoáng.

---

## 4. Hình Khối, Tỷ Lệ & Khoảng Cách (Shapes & Spacing)

| Thành phần | Web 1 — Manh Dao Dao (`theme_gift_store`) | Web 2 — Thời Trang (`theme_fashion_store`) |
|---|---|---|
| **Border Radius** | Phân cấp theo lưới 4px (`6px` badge, `10px` button, `12px` card, `16px` panel) | Bo góc tối giản (`0px` – `4px`, vuông vức sắc sảo) |
| **Tỷ lệ ảnh sản phẩm** | `1:1` (Vuông vắn tôn hình Doll, Card, Postcard, Standee, Badge) | `3:4` (Ảnh dọc chuẩn Lookbook thời trang quốc tế) |
| **Bóng đổ (Shadow)** | Trung tính, không glow màu (`0 1px 2px rgba(11,18,32,0.05)` / hover `0 8px 20px rgba(11,18,32,0.08)`) | Nhẹ và sắc nét (`0 2px 8px rgba(0,0,0,0.06)`) |
| **Hiệu ứng Hover** | Đổi màu viền/nền mượt & zoom ảnh `1.03` | Phóng to ảnh tinh tế (`transform: scale(1.04)`) |

---

## 5. Bộ Nhận Diện, Icon, Chuyển Động & Kiểm Định Chất Lượng (UI Polish Standards)

- **Logo Web 1 (`addons/theme_gift_store/static/src/img/`)**:
  - `brand_logo_dark.jpg` & `brand_logo_light.jpg`: Ảnh gốc nhận diện mèo đen mắt xanh dương + lựu đạn xanh dương.
  - `logo_emblem_transparent.png`: Biểu tượng tách nền trong suốt (`RGBA PNG`).
  - `favicon.ico`: Đa kích thước `32x32` & `64x64`.
  - `logo.png`: Logo ngang navbar kết hợp biểu tượng mèo đen + lựu đạn xanh bên trái và chữ `MANH DAO DAO · ANIME GOODS SHOP` màu xanh dương đậm bên phải.
- **Hệ thống Icon (`Lucide v1.82.0`, self-hosted)**: Đóng gói tại `addons/wbh_core/static/lib/lucide/lucide.min.js` (`web.assets_frontend`), dùng `citrus` cho icon cam/quýt trên topbar thay cho emoji thô.
  - Web 1: `stroke-width: 1.65`.
  - Web 2: `stroke-width: 1.5`.
- **Hệ thống Chuyển động (`GSAP v3.15.1 + ScrollTrigger`, self-hosted)**: Đóng gói tại `addons/wbh_core/static/lib/gsap/`, thực thi qua `theme_gift_motion.js` và `theme_fashion_motion.js` với 3 chốt bảo vệ bắt buộc:
  1. Cô lập tuyệt đối trong `#wrapwrap.wbh-store-gift` và `#wrapwrap.wbh-store-fashion`.
  2. Tắt hiệu ứng khi Odoo Website Builder đang bật chế độ chỉnh sửa (`editor_enable`, `o_editable`, `o_website_preview`).
  3. Tôn trọng `@media (prefers-reduced-motion: reduce)` và tự giải phóng `clearProps` sau khi chạy; tuyệt đối không đặt `opacity: 0` bẫy cuộn.
- **Chuẩn Audit Giao Diện (`360-frontend-polish`: `heydamir/unslop` CC-BY-4.0 + Impeccable + Front-End Checklist + UI UX Pro Max)**:
  - Áp dụng 9 passes của `unslop`: nền tĩnh lặng `#F4F7FB` cho Web 1, tương phản WCAG AA `>= 4.5:1`, không `low-contrast`, không `dark-glow`, không `side-tab`, không `nested-cards`, không `bounce-easing`, không `skipped-heading`, không inline `onclick=` hay `style=`.
  - `select.form-select` một mũi tên chuẩn, thẻ `/shop` ẩn `.oe_subdescription` dài, thanh khoảng giá bỏ `,00` thập phân cuối, luôn có `:focus-visible`, `preconnect` Google Fonts, `<meta name="theme-color" content="#0B1220">` và vùng chạm mobile `>= 44px`.

---

## 6. Quy Trình Kiểm Tra & Tích Hợp (Checklist Before Changing UI)

Trước khi thực hiện bất kỳ thay đổi nào liên quan đến giao diện người dùng:
1. [ ] Đọc kỹ `DESIGN.md` để nắm đúng bảng màu và phong cách của từng website.
2. [ ] Tham chiếu file `css/system.css` và mở `html/preview.html` trên trình duyệt để kiểm tra trực quan các components.
3. [ ] Tái sử dụng các class có sẵn (`.wbh-gift-btn-primary`, `.wbh-fashion-btn-primary`, `.wbh-gift-card`, `.wbh-fashion-card`...), KHÔNG tự tạo style inline tùy tiện.
4. [ ] Chạy `run-impeccable-audit.ps1` và kiểm tra syntax JS/XML trước khi bàn giao.
