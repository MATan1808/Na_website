# DESIGN.md — Hệ Thống Quy Chuẩn Thiết Kế Giao Diện (Design System Specification)

> **Dự án**: Hệ Sinh Thái 2 Website Bán Hàng (`web_ban_hang`) — **Odoo 19.0 Community (LGPL-3)**  
> **Áp dụng**: Bắt buộc tuân thủ cho mọi AI Agent, lập trình viên và tác vụ can thiệp vào UI, QWeb Templates, SCSS, và CSS Snippets.

---

## 1. Nguyên Tắc Cốt Lõi (Core Design Principles)

1. **Tuân thủ Bản sắc Độc lập của 2 Thương hiệu (Multi-Website Coexistence)**:
   - **Web 1 — Cửa Hàng Quà Tặng (`theme_gift_store`)**: Cảm xúc, ấm áp, kẹo ngọt, năng động (Warm & Playful). Dành cho Gấu bông, Móc khóa, Blind Box.
   - **Web 2 — Cửa Hàng Thời Trang (`theme_fashion_store`)**: Tối giản, thanh lịch, sang trọng, thời thượng (Editorial & Minimalist). Dành cho Quần áo, Lookbook, Phụ kiện streetwear.
2. **Upgrade-Safe 100% trong Odoo 19.0**:
   - Không can thiệp sửa trực tiếp file lõi của Odoo.
   - Khai báo biến qua `$o-color-palettes` và `$o-theme-font-configs` trong `primary_variables.scss` với cờ `!default`.
   - Sử dụng CSS Custom Properties (`--wbh-*`) và utility classes có prefix (`.wbh-gift-*`, `.wbh-fashion-*`) để triệt tiêu hoàn toàn nguy cơ xung đột (CSS scoping).
3. **Tương thích Bootstrap 5.3.3 & Không dùng Tailwind trực tiếp**:
   - Odoo 19 Website Builder chạy trên nền Bootstrap 5.3.3. Tránh cài đặt Tailwind CSS trực tiếp vào Odoo bundle vì gây xung đột class (`container`, `row`, `btn`, `d-flex`). Thay vào đó, toàn bộ design tokens được đồng bộ qua file `css/system.css` và biến SCSS của theme.

---

## 2. Hệ Thống Màu Sắc (Color Tokens)

### 2.1. Cửa Hàng Quà Tặng (Store 1 — Gift & Blind Box)
- `--wbh-gift-primary`: `#FF6B8B` (Hồng san hô ngọt ngào — CTA chính, nút mua ngay, badge hot).
- `--wbh-gift-secondary`: `#FFB347` (Vàng mật ong ấm áp — huy hiệu giảm giá, dịp lễ, ngôi sao đánh giá).
- `--wbh-gift-bg`: `#FFF6F0` (Kem đào ấm — nền section dịu mắt, thân thiện).
- `--wbh-gift-surface`: `#FFFFFF` (Trắng tinh khiết — nền thẻ sản phẩm, dropdown, modal).
- `--wbh-gift-text`: `#3D2C2E` (Nâu cacao đậm — chữ chính đạt chuẩn tương phản WCAG AA).
- `--wbh-gift-text-muted`: `#8C7A7C` (Nâu xám nhạt — mô tả phụ, giá gạch).

### 2.2. Cửa Hàng Thời Trang (Store 2 — Fashion & Lookbook)
- `--wbh-fashion-primary`: `#111111` (Đen than tuyền — CTA dứt khoát, typography đậm nét).
- `--wbh-fashion-accent`: `#C8B6A6` (Be cát sa mạc — đường viền sang trọng, điểm nhấn lookbook).
- `--wbh-fashion-bg`: `#F5F5F3` (Xám đá sáng — nền background trung tính tôn màu vải).
- `--wbh-fashion-surface`: `#FFFFFF` (Trắng tuyệt đối — thẻ sản phẩm, khung ảnh lookbook).
- `--wbh-fashion-text`: `#222222` (Đen than chữ chính — độ nét cao).
- `--wbh-fashion-text-muted`: `#777777` (Xám trung tính — thông số size, chất liệu vải).

---

## 3. Kiểu Chữ & Typography

### 3.1. Quà Tặng (Gift Store)
- **Heading**: `'Quicksand', 'Nunito', sans-serif` — Bo tròn, thân thiện, dễ mến.
- **Body & UI**: `'Be Vietnam Pro', sans-serif` — Chuẩn font tiếng Việt sắc nét trên mọi màn hình.

### 3.2. Thời Trang (Fashion Store)
- **Heading & Lookbook**: `'Plus Jakarta Sans', 'Playfair Display', sans-serif` — Tinh tế, thời thượng.
- **Body & Product Specs**: `'Inter', -apple-system, sans-serif` — Tối giản, hiện đại, khoảng cách ký tự (tracking) thoáng.

---

## 4. Hình Khối, Tỷ Lệ & Khoảng Cách (Shapes & Spacing)

| Thành phần | Cửa Hàng Quà Tặng (Web 1) | Cửa Hàng Thời Trang (Web 2) |
|---|---|---|
| **Border Radius** | Bo góc lớn (`16px` – `24px`, nút dạng `rounded-pill`) | Bo góc tối giản (`0px` – `4px`, vuông vức sắc sảo) |
| **Tỷ lệ ảnh sản phẩm** | `1:1` (Vuông vắn tôn hình gấu bông, móc khóa) | `3:4` (Ảnh dọc chuẩn Lookbook thời trang quốc tế) |
| **Bóng đổ (Shadow)** | Mềm mại, ấm cúng (`0 8px 24px rgba(255,107,139,0.12)`) | Nhẹ và sắc nét (`0 2px 8px rgba(0,0,0,0.06)`) |
| **Hiệu ứng Hover** | Nhún nhẹ (`translateY(-4px)` kèm xoay nhẹ icon) | Phóng to ảnh tinh tế (`transform: scale(1.04)`) |

---

## 5. Quy Trình Kiểm Tra & Tích Hợp (Checklist Before Changing UI)

Trước khi thực hiện bất kỳ thay đổi nào liên quan đến giao diện người dùng:
1. [ ] Đọc kỹ `DESIGN.md` để nắm đúng bảng màu và phong cách của từng website.
2. [ ] Tham chiếu file `css/system.css` và mở `html/preview.html` trên trình duyệt để kiểm tra trực quan các components.
3. [ ] Tái sử dụng các class có sẵn (`.wbh-gift-btn-primary`, `.wbh-fashion-btn`, `.wbh-product-card...`), KHÔNG tự tạo style inline tùy tiện.
4. [ ] Nếu có xung đột về layout, giải thích rõ nguyên nhân với Sếp trước khi can thiệp diện rộng.
