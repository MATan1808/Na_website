# Nhật Ký Thay Đổi (CHANGELOGS) — Hệ Sinh Thái 2 Website Bán Hàng (`web_ban_hang`)

Tài liệu ghi nhận đầy đủ lịch sử thay đổi các phiên bản của dự án theo chuẩn **AIaC 3.0 (`360-odoo`)**.

> **Quy ước phiên bản**:
> - Phiên bản tổng thể dự án/tài liệu: `v<major>.<minor>.<patch>` (hiện tại `v0.4.0` — Hoàn thành Giai đoạn 1–4: Sửa nhanh & Giá gạch `-XX%`, Bộ lọc động 100%, Tư vấn 3 kênh, Thanh toán VietQR EMVCo + COD & Vận chuyển VN 3 cấp + GHN).
> - Phiên bản từng custom Odoo module trong `addons/`: `v19.0.<major>.<minor>.<patch>` (đồng bộ cả trong `docs/CHANGELOGS.md` và trường `description` của từng `__manifest__.py`).
>
> **Quy ước Tag**: `[NEW]` Tính năng/tài liệu mới · `[FIX]` Sửa lỗi · `[IMPROVE]` Cải tiến · `[SECURITY]` Bảo mật · `[REFACTOR]` Tái cấu trúc · `[MIGRATE]` Nâng cấp/chuyển đổi.

---

## v0.4.0 (2026-11-28)

### Hoàn Thiện Trọn Bộ 4 Giai Đoạn — Bộ Lọc Động 100%, Tư Vấn 3 Kênh, Thanh Toán VietQR & Vận Chuyển VN
- `[NEW]` **Giai đoạn 1–3 Backend (`wbh_core` `v19.0.1.2.0`)**:
  - Bổ sung `wbh_discount_percent` + `wbh_has_discount` trên `product.template`, gộp album ảnh `product_template_image_ids`, `product_tag_ids` và `compare_list_price` vào tab Thông tin chung, thêm view sửa nhanh `<list editable="bottom">` và bộ lọc `Đang giảm giá`.
  - Mở rộng `product.tag` (`wbh_show_in_filter`, `wbh_filter_group`, `wbh_badge_hex`), thêm model `wbh.price.range` (`data/wbh_filter_data.xml` `noupdate="1"`) và controller `WbhWebsiteSale` (`controllers/shop.py`) lọc động kết hợp 100% (`tags`, `attrib`/`attribute_values`, `min_price`/`max_price`, `category`, `search`, `wbh_on_sale=1`), tự ẩn hoàn toàn mọi tiêu chí có `count == 0`.
  - Mở rộng model `website` (`wbh_fb_messenger_url`, `wbh_livechat_enabled`, `wbh_contact_prompt`) phục vụ cấu hình động 3 kênh tư vấn.
- `[NEW]` **Giai đoạn 1–3 Storefront (`theme_gift_store` & `theme_fashion_store` `v19.0.1.3.0`)**:
  - Hiển thị giá gốc gạch ngang `compare_list_price` (chống trùng core) + huy hiệu `-XX%` trên thẻ `/shop` và PDP.
  - Hiển thị bảng bộ lọc động từ `wbh_filter_ctx` trên Sidebar & Offcanvas Mobile (`>= 44px` + badge đếm), dải Active Filter Chips (`×` & `Xóa tất cả`) và tối đa 2 nhãn động trên thẻ sản phẩm.
  - Thêm Hộp tư vấn 3 kênh trên PDP & `/shop/cart` (`Chat tại Web`, `Nhắn Facebook`, `Nhắn Zalo`, `Chép tên & link SP`) cùng Widget Liên hệ nổi 3 trong 1 (`bottom: 88px` không đè `#o_footer_scrolltop_wrapper` và sticky mobile bar).
- `[NEW]` **Giai đoạn 4 Thanh toán (`wbh_payment_vietqr` `v19.0.1.0.0`, `LGPL-3`)**:
  - Sinh mã QR VietQR chuẩn EMVCo / Napas 247 (`CRC16-CCITT 0x1021`) offline qua `ir.actions.report.barcode`, tích hợp Webhook SePay Free (`POST /payment/vietqr/webhook/sepay`, xác thực `hmac.compare_digest`, idempotent) & adapter PayOS/Casso, API polling trạng thái giao dịch `/payment/vietqr/status/<reference>`, thẻ QR chuẩn `DESIGN.md` và quy tắc bật/tắt COD & gợi ý đặt cọc.
- `[NEW]` **Giai đoạn 4 Vận chuyển (`wbh_delivery_vn` `v19.0.1.0.0`, `LGPL-3`)**:
  - Xây dựng địa giới hành chính Việt Nam 3 cấp (`wbh.vn.province`, `wbh.vn.district`, `wbh.vn.ward`) kèm API cascade trên checkout `/shop/address`, 3 phương thức vận chuyển (`Đồng giá 30.000đ — Freeship từ 300.000đ`, `Gom đơn / Giữ hàng tại shop — 0đ ship`, `Giao Hàng Nhanh (GHN)` Sandbox/Prod kèm fallback và hook GHTK/VTP) cùng theo dõi mã vận đơn & nhãn Gom đơn trên Portal `/my/orders/<id>`.

---

## v0.3.14 (2026-11-28)

### Vá Selector `footer.o_footer` Nút Cuộn Đầu Trang & Chống Tràn Ngang PDP Mobile
- `[FIX]` **Hiển thị trọn vẹn nút cuộn đầu trang `#o_footer_scrolltop_wrapper`** (`theme_gift_store` & `theme_fashion_store` `v19.0.1.2.2`): Đổi selector từ `#footer.o_footer` sang `footer.o_footer, #bottom.o_footer` khớp ID thật của Odoo 19 để `height: auto !important; min-height: 3.5rem` có hiệu lực.
- `[FIX]` **Chống tràn ngang PDP mobile**: Bổ sung `overflow-x: clip` trên `.wbh-store-gift` / `.wbh-store-fashion` và `table-layout: fixed` trên `#product_full_spec table`.

---

## v0.3.13 (2026-11-28)

### Hoàn Thiện Sau Kiểm Định Live — Sửa `select.form-select`, Toolbar Mobile `/shop`, Bỏ `+1 555` & Việt Hóa 100% PDP
- `[FIX]` **Việt hóa triệt để các nhãn core trên Trang chi tiết & Breadcrumb** (`wbh_core` `v19.0.1.1.3`): Thêm `views/website_sale_vi_templates.xml` chuyển `All products` ➜ `Tất cả sản phẩm`, `Add to cart` ➜ `Thêm vào giỏ hàng`, `Add to compare` ➜ `So sánh sản phẩm`.
- `[FIX]` **Gỡ bỏ `+1 555-555-5556` và nút `Contact Us` thừa** (`theme_gift_store` `v19.0.1.2.1`, `theme_fashion_store` `v19.0.1.2.1`): Tắt `website.header_text_element` và `website.header_call_to_action` trong `presets.xml` và `theme.utils`.
- `[FIX]` **Sửa tận gốc `select.form-select.css_attribute_select` double-caret & tràn `416px` mobile**: Ghi đè selector đặc hiệu cao của Odoo `product_configurator.scss` bằng SVG chevron chuẩn duy nhất + `max-width: 100% !important`.
- `[FIX]` **Tối ưu Mobile `390x844`**: Bọc toolbar `/shop` thành 2 hàng (thanh tìm kiếm đủ rộng, không cắt nút `Bộ lọc`), bật hiển thị nút Wishlist trên mobile, ẩn chắc `.wbh-gift-topbar__tagline` ở `< 576px` và mở chiều cao `#o_footer_scrolltop_wrapper` hết bị che nửa dưới.

---

## v0.3.12 (2026-11-28)

### Unslop 9 Passes — Khử "Mùi AI" & Sửa Triệt Để Lỗi UI/UX Trên Storefront Live (`theme_gift_store` & `theme_fashion_store` `v19.0.1.2.0`)
- `[NEW]` **Tích hợp chính thức skill `heydamir/unslop` (`CC-BY-4.0`)** vào plugin AIaC `360-frontend-polish` (`v1.1.0`) tại `F:\BACKUP_LINUX\aiac\360org\plugins\360-frontend-polish\prompts\references\unslop\`.
- `[FIX]` **Gỡ bỏ bẫy GSAP `opacity: 0` trên toàn trang chủ và `/shop`**: Thay thế cơ chế ẩn thẻ trước khi cuộn (`ScrollTrigger.batch`) bằng hiển thị tức thì `opacity: 1` (chỉ trượt nhẹ `y: 10px -> 0` trên gallery hero), tránh mất/mờ sản phẩm khi tải hoặc cuộn nhanh.
- `[IMPROVE]` **Thay 100% khung pastel icon "AI slop" bằng ảnh sản phẩm thật**: Hero & Lưới nổi bật của Web 1 dùng trực tiếp ảnh chụp thật (`bakugo_doll_fullset.jpg`, `todoroki_goods_collection.jpg`, `bakugo_doll_body.jpg`, `bakugo_poster.jpg`), sửa lỗi chính tả `"bông bông"` và căn chỉnh câu chữ đúng ngành Anime Goods trên nền Warm Paper (`#F7F4EE`).
- `[FIX]` **Khắc phục triệt để layout `/shop` & PDP**:
  - Ẩn đoạn `.oe_subdescription` dài 8–12 dòng trên thẻ `/shop` giúp card đều tăm tắp trên cả desktop và mobile 2 cột.
  - Vá lỗi `<select class="form-select">` bị lặp 2 mũi tên (`double-caret`) và cắt dọc chữ ở bộ lọc sidebar + trang chi tiết.
  - Chuẩn hóa căn giữa dọc (`inline-flex`) cho mọi nút bấm, bọc nền trắng mờ cho nút Wishlist & mũi tên slider PDP, cố định topbar 1 hàng trên mobile `390px` và nới rộng ô tìm kiếm `/shop`.

---

## v0.3.11 (2026-11-27)

### Chuẩn Hóa Tiền Tệ `VNĐ (₫)` & Đưa 15 Sản Phẩm Thật Anime Goods Lên Đầu Trang 1 `/shop`
- `[FIX]` **Chuyển đơn vị tiền tệ hiển thị trên `/shop` từ `$ USD` sang `₫ VNĐ`** (`wbh_core` `v19.0.1.1.2`): Kích hoạt `base.VND` (`active=True`, `position='after'`, `rounding=1.0`), cập nhật `res.company` và `product.pricelist` dùng chung cho cả 2 website sang `VNĐ (₫)`.
- `[IMPROVE]` **Dọn sạch rác & tối ưu thứ tự hiển thị `/shop`** trong `addons/wbh_core/scripts/import_fb_products.py`:
  - Xóa/lưu trữ toàn bộ sản phẩm test rác (`T1`), ẩn sản phẩm dịch vụ (`Standard delivery`, `Gift Card`, `Top-up eWallet`) và sản phẩm mẫu chưa có ảnh khỏi `/shop`.
  - Cô lập đúng sản phẩm Thời trang sang Web 2 (`website_fashion_store`), tránh rò sang Web 1.
  - Sắp xếp `website_sequence` (`10..150`) đưa toàn bộ **10 lô sản phẩm Facebook Manh Dao Dao (`MDD-FB-001`..`MDD-FB-010`)** và **5 sản phẩm MHA chủ lực** lên ngay đầu Trang 1 `/shop`.

---

## v0.3.10 (2026-11-27)

### Hỗ Trợ Public Website Máy Ở Nhà Qua Cloudflare Tunnel & Domain Miễn Phí
- `[NEW]` **Bổ sung dịch vụ `cloudflared` (Docker Compose `profiles: ["tunnel"]`)** vào `docker-compose.yml` và các biến mẫu (`COMPOSE_PROFILES`, `CLOUDFLARED_IMAGE`, `CLOUDFLARE_TUNNEL_TOKEN`) vào `.env.example` để public website ra Internet có HTTPS xanh miễn phí mà không cần mở port modem/router.
- `[NEW]` **Bổ sung Mục 5 trong `docs/THONG_TIN_WEBSITE.md`**: Hướng dẫn đăng ký domain miễn phí `manhdaodao.*`, cấu hình Cloudflare Tunnel (kèm `web.base.url.freeze`) và phương án bật nhanh Tailscale Funnel.

---

## v0.3.9 (2026-11-27)

### Đồng Bộ Bộ 10 Sản Phẩm & 49 Ảnh Thật Facebook `Manh Dao Dao` (`MDD-FB-001` ➜ `MDD-FB-010`)
- `[NEW]` **Bộ dữ liệu & hình ảnh sản phẩm thật** trong `wbh_core` (`v19.0.1.1.1`):
  - `addons/wbh_core/data/fb_manhdaodao_products.json` & `fb_manhdaodao_products.csv`: 10 lô sản phẩm Anime Goods (*My Hero Academia*), tổng **37 biến thể**, kèm giá tham khảo, điểm nổi bật, lưu ý unbox và thuộc tính `no_variant` (*Bộ Phim (Anime)*, *Nhân Vật (Bias)*).
  - `addons/wbh_core/static/src/img/fb_manhdaodao/*.jpg`: **49 ảnh thật** (`3,28 MB`) cho ảnh đại diện và gallery chi tiết từng sản phẩm.
  - `addons/wbh_core/scripts/import_fb_products.py`: Script nạp idempotent chuẩn Odoo 19.0 Community (hỗ trợ cả `odoo shell` và chạy trực tiếp `python3`).
- `[IMPROVE]` Cập nhật bảng sản phẩm và tiến độ thực tế trong `docs/THONG_TIN_WEBSITE.md`, `docs/ROADMAP_TIEN_DO.md` và `README.md`, đồng thời nạp live toàn bộ 10 sản phẩm lên Local Server `http://100.64.56.52:1901`.

---

## v0.3.8 (2026-11-27)

### Đồng Bộ Skill `360-frontend-polish`, Bộ Repo MochiStudio & Nâng Cấp Live (`100.64.56.52:1901`)
- `[IMPROVE]` **Đăng ký và ràng buộc skill `360-frontend-polish`** (`GSAP 3.15.1`, `Lucide 1.82.0`, `Impeccable`, `Front-End Checklist`, `UI UX Pro Max`) vào `F:\BACKUP_LINUX\aiac\CLAUDE.md`, `.claude/settings.local.json`, `.claude/CLAUDE.md`, `AGENTS.md` và lộ trình 4 giai đoạn trong `docs/ROADMAP_TIEN_DO.md` (nâng Giai đoạn 1 lên **~90%**).
- `[IMPROVE]` Nâng cấp live 3 module (`wbh_core`, `theme_gift_store`, `theme_fashion_store` `v19.0.1.1.0`) trên Local Server `100.64.56.52:1901` và kiểm định `Impeccable` trực tiếp trên HTML live.

---

## v0.3.7 (2026-11-27)

### Chuẩn Hóa Lộ Trình 4 Giai Đoạn & Bảng Theo Dõi Tiến Độ (`docs/ROADMAP_TIEN_DO.md`)
- `[NEW]` **Khởi tạo `docs/ROADMAP_TIEN_DO.md`**: Đặc tả chi tiết kèm checklist `[x]` / `[ ]` và `%` tiến độ cho 4 giai đoạn:
  1. **Giai đoạn 1 (`~85%`)**: Website & Quản trị Sản phẩm CRUD đầy đủ (*Thêm · Xem · Sửa · Xóa/Lưu trữ*).
  2. **Giai đoạn 2 (`~25%`)**: Bộ lọc động 100% (**Cấm Hardcode**) theo *Khoảng giá*, *Nhân vật & Bộ Anime* (`no_variant`), *Phân loại Doll/Goods Off* và *Nhãn ưu đãi/giảm giá động* (`product.tag`).
  3. **Giai đoạn 3 (`~20%`)**: Tương tác & tư vấn chốt đơn **3 kênh** (*Chat Web trực tiếp · Facebook Messenger · Zalo*) cấu hình động.
  4. **Giai đoạn 4 (`0%`)**: Thanh toán (`wbh_payment_vietqr`) & Vận chuyển (`wbh_delivery_vn` — đồng giá/Freeship/gom đơn + GHN/GHTK).
- `[IMPROVE]` Đồng bộ lộ trình 4 giai đoạn và liên kết repo `https://github.com/MATan1808/Na_website.git` vào `README.md`, `AGENTS.md`, `.claude/CLAUDE.md` và `docs/THONG_TIN_WEBSITE.md`.

---

## v0.3.6 (2026-11-27)

### Nâng Cấp UI/UX, Motion & Hệ Thống Icon Chuẩn MochiStudio (`GSAP` + `Lucide` + `Impeccable` + `Front-End Checklist`)
- `[NEW]` **Đóng gói plugin AIaC `360-frontend-polish`** tại `F:\BACKUP_LINUX\aiac\360org\plugins\360-frontend-polish\` (kèm junction `~/.claude/skills/360-frontend-polish`), hợp nhất quy chuẩn của `impeccable`, `Front-End-Checklist`, `ui-ux-pro-max-skill`, `GSAP` và `Lucide`.
- `[NEW]` **Self-hosted `GSAP v3.15.1` (kèm `ScrollTrigger`) & `Lucide v1.82.0`** trong `addons/wbh_core/static/lib/` (`wbh_core` `v19.0.1.1.0`), nạp qua `web.assets_frontend` không phụ thuộc CDN bên ngoài.
- `[IMPROVE]` **Nâng cấp `theme_gift_store` (`v19.0.1.1.0`) & `theme_fashion_store` (`v19.0.1.1.0`)**:
  - Bổ sung `theme_gift_motion.js` và `theme_fashion_motion.js` với 3 chốt bảo vệ: cô lập Multi-Website, an toàn khi chỉnh sửa trong Website Builder, và tuân thủ `prefers-reduced-motion`.
  - Nâng cấp toàn bộ icon storefront sang **Lucide SVG** đồng bộ theo cá tính thương hiệu (`stroke-width: 1.9` cho Web 1, `1.5` cho Web 2).
  - Khắc phục các lỗi do `npx impeccable detect` phát hiện: nâng tương phản topbar/CTA đạt WCAG AA (`>= 4.5:1`), gỡ bỏ `side-tab`, thay inline `onclick=` / `style=` bằng `data-wbh-trigger-cart` + `IntersectionObserver`, bổ sung `:focus-visible`, `preconnect` Google Fonts, `<meta name="theme-color">` và hover scale `1.04` chuẩn `DESIGN.md`.
- `[IMPROVE]` **Cập nhật `html/preview.html`, `css/system.css` và `DESIGN.md`**: Nhúng trực tiếp Lucide + GSAP chạy offline ngay khi mở file xem trước.

---

## v0.3.5 (2026-11-27)

### Khắc Phục Lặp 2 Footer, Nút Cuộn Đầu Trang Bị Che & Chuẩn Hóa Bản Quyền
- `[FIX]` **Triệt tiêu lỗi lặp 2 footer** (`theme_gift_store` `v19.0.1.0.2`, `theme_fashion_store` `v19.0.1.0.1`): Tắt `website.footer_custom` (`active=False` trong `presets.xml` và `disable_view` trong `theme.utils`) để không hiển thị khối footer tiếng Anh mẫu của Odoo phía trên footer thương hiệu.
- `[FIX]` **Sửa nút cuộn tròn `#o_footer_scrolltop_wrapper` bị che khuất nửa dưới trên mobile**: Đưa `.wbh-gift-footer-band` và `.wbh-fashion-footer-band` lên trước `//div[@id='footer']` và nâng `z-index: 10` kèm khoảng đệm `padding-top: 1.75rem` cho `.o_footer_copyright > .container`.
- `[IMPROVE]` Thay thế chuỗi bản quyền mẫu `Copyright © Company name` bằng `Bản quyền © <website.name>` tự động theo từng website.

---

## v0.3.4 (2026-11-27)

### Nhận Diện Thương Hiệu Manh Dao Dao, Chuẩn Hóa Docker Named Volumes & Vá Quyền Tồn Kho `/shop`
- `[NEW]` **Bộ nhận diện thương hiệu Manh Dao Dao Anime Goods Shop** trong `addons/theme_gift_store/static/src/img/`:
  - `logo.png` (`1020x280` px RGBA): Logo ngang chuẩn eCommerce tách sạch nền caro, kết hợp mascot Anime & lựu đạn/tia nổ cùng typography `MANH DAO DAO — ANIME GOODS SHOP`.
  - `logo_emblem_transparent.png` (`931x945` px RGBA): Bản tròn nguyên bản tách nền trong suốt 100% dùng cho OpenGraph/chia sẻ MXH.
  - `favicon.ico` (`32x32` & `64x64` px): Icon cận cảnh nhân vật sắc nét trên tab trình duyệt.
- `[IMPROVE]` **Tối ưu CSS Logo Navbar** trong `addons/theme_gift_store/static/src/scss/theme_gift.scss`: Nâng chiều cao logo lên `60px` trên desktop (`48px` khi cuộn, `46px` trên mobile) bọc chặt trong `.wbh-store-gift`.
- `[FIX]` **Sửa tận gốc lỗi `403 Forbidden` khi khách vãng lai xem `/shop`**: Bổ sung `compute_sudo=True` cho trường `wbh_is_low_stock` trong `wbh_core` (`v19.0.1.0.1`) và đọc `product.sudo().qty_available` trong `theme_gift_store` (`v19.0.1.0.1`), không cần mở quyền đọc trực tiếp `stock.move`/`stock.warehouse`.
- `[IMPROVE]` **Chuẩn hóa Docker Named Volumes** trong `docker-compose.yml`: Chuyển `filestore` và `sessions` sang `web_ban_hang_filestore` và `web_ban_hang_sessions` để tương thích mọi filesystem trên Linux Local Server (kể cả ổ đĩa mount NTFS/FUSE) và Windows.

---

## v0.3.3 (2026-11-27)

### Design System & Nạp Bộ Sản Phẩm Anime Goods & Búp Bê Cotton Doll 20cm
- `[NEW]` **Hệ Thống Thiết Kế Chuẩn**: Tạo `DESIGN.md`, `css/variables.css`, `css/system.css` và trang xem trước trực quan `html/preview.html`.
- `[NEW]` **Nạp Dòng Sản Phẩm Anime Goods & Cotton Doll 20cm Thực Tế**:
  - `Doll Bông Cotton Doll 20cm Bakugo Katsuki (Tóc Xù Kèm Outfit Sporty)`: Biến thể Fullset 380k, Body trần thêu sầu riêng 280k, Outfit rời 120k.
  - `Bộ Sưu Tập Card Bo Góc & Photocards Todoroki Shoto`: Card thường 20k - 40k, Hologram bạc hiếm 85k, Set 2 card kèm khung 120k.
  - `Huy Hiệu Kim Loại Can Badge Todoroki Shoto 58mm`: Phủ kim tuyến / dạ quang (20k - 40k).
  - `Mochi Kororin Bông Tròn Todoroki Shoto 10cm`: Nuigurumi ú mini treo balo (130k).
  - `Tranh Ký Shikishi Viền Vàng Bakugo Katsuki`: Awakening Explosion Special (65k).
- `[IMPROVE]` Cập nhật thanh danh mục và Hero Banner trang chủ Web 1 dẫn trực tiếp vào bộ sưu tập Anime Doll & Goods.

---

## v0.3.2 (2026-11-27)

### Mở Rộng Ứng Dụng E-Commerce & Chăm Sóc Khách Hàng Odoo 19.0
- `[NEW]` **Cài đặt mở rộng 5 cụm module nghiệp vụ đắc lực**:
  - `loyalty` & `website_sale_loyalty`: Quản lý chương trình khuyến mãi, tạo mã giảm giá voucher (`VOUCHER50K`, `FREESHIP`), thẻ quà tặng, tích điểm thành viên và áp dụng trực tiếp trong giỏ hàng web.
  - `im_livechat` & `website_livechat`: Khung chat trực tuyến nổi góc màn hình hỗ trợ tư vấn tức thời khách chọn quà tặng và chọn size quần áo.
  - `purchase`: Quản lý đơn mua hàng, theo dõi đơn nhập hàng và công nợ với xưởng sản xuất gấu bông, móc khóa và thời trang.
  - `website_blog`: Chuyên mục Blog tin tức, cẩm nang phối đồ và gợi ý quà tặng chuẩn SEO.
  - `mass_mailing`: Tiếp thị Email tự động, gửi email chăm sóc khách hàng và nhắc giỏ hàng bỏ quên.
  - `crm`: Quản lý khách hàng tiềm năng và chuyển đổi cơ hội kinh doanh.
- `[IMPROVE]` Khởi tạo sẵn 11 sản phẩm mẫu đa dạng có đầy đủ thuộc tính biến thể Màu sắc (Color Swatch) và Size trên cả 2 website.

---

## v0.3.0 (2026-11-26)

### Hoàn Tất `/build` & Cổng `/code-review` Vòng 2 — Milestone 1 (Catalog-First)
Toàn bộ **49 file mới** của Milestone 1 đã vượt qua **100% cổng `/code-review`** (`py_compile` 15/15 PASS, `ET.parse` 23/23 PASS, 100% **Odoo 19.0 Community `LGPL-3`**, 0% phụ thuộc Enterprise, 0% anti-pattern, cô lập tuyệt đối Multi-Website, đủ 7/7 extension slots cho Milestone 2 & 3, sạch secret):

- `[NEW]` **Hạ tầng Docker di động (3 file)**:
  - `F:\BACKUP_LINUX\web_ban_hang\docker-compose.yml`: 2 dịch vụ `db` (`postgres:15-bookworm`) + `odoo` (`odoo:19.0`), tên container `${CLIENT_NAME:-web-ban-hang}-db`/`-app`, healthcheck đầy đủ, bind `127.0.0.1:51901:5432`, mount tương đối `./addons`, `./config/odoo.conf:ro`, `./data/filestore`, `./data/sessions`, volume `web_ban_hang_pgdata` và network cô lập `web_ban_hang_net`.
  - `F:\BACKUP_LINUX\web_ban_hang\.env.example`: đủ 11/11 biến môi trường (`CLIENT_NAME`, `ODOO_IMAGE`, `POSTGRES_IMAGE`, `ODOO_PORT=1901`, `LONGPOLLING_PORT=7089`, `DB_PORT=51901`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `ODOO_MASTER_PASSWORD`, `DB_NAME`, `DB_FILTER`), 100% placeholder sạch secret.
  - `F:\BACKUP_LINUX\web_ban_hang\config\odoo.conf`: đủ 13/13 tùy chọn `[options]` chuẩn Odoo 19.0, định dạng LF-only tương thích cả Windows Docker Desktop (WSL2) và Linux Local Server.
- `[NEW]` **Module `addons/wbh_core/` (`v19.0.1.0.0`, 15 file, `LGPL-3`)**:
  - Khởi tạo 2 Website độc lập (`website_gift_store`, `website_fashion_store`) với `specific_user_account=True` tách riêng tài khoản khách hàng.
  - Mở rộng `website` và `product.template` chuẩn Odoo 19.0 (`models.Constraint`, `models.Index`, `@api.model_create_multi`, `odoo.fields.Command`), tự động đồng bộ `website_id` theo `wbh_store_scope` và lọc sản phẩm sắp hết hàng.
  - Phân quyền chuẩn Odoo 19.0 dùng `res.groups.privilege` (`res_groups_privilege_wbh`), `security/ir.model.access.csv`, `ir.rule` cô lập Public/Portal theo website & công ty (kèm `uninstall_hook` khôi phục rule gốc an toàn).
  - Dữ liệu mẫu `noupdate="1"` gồm cây danh mục cho 2 cửa hàng và bộ 7 thuộc tính biến thể chuẩn; bộ views backend tối ưu upload sản phẩm nhanh, menu *2 Cửa Hàng (WBH)* và bộ unit test `tests/test_wbh_core.py`.
- `[NEW]` **Module `addons/theme_gift_store/` (`v19.0.1.0.0`, 16 file, `LGPL-3`, Upgrade-Safe Odoo 19.0)**:
  - Cô lập tuyệt đối Multi-Website bằng class `.wbh-store-gift` và điều kiện `website.wbh_store_type == 'gift'` (không ghi đè sang Web 2).
  - Bảng màu ấm `$o-color-1..5`, font tiếng Việt `Be Vietnam Pro` / `Quicksand`, khai báo asset bundles chuẩn Odoo 19.0 (`web._assets_primary_variables`, `web.assets_frontend`, `website.assets_wysiwyg`).
  - `data/presets.xml` (`noupdate="1"`) tự động gán `theme_id` & tỷ lệ ảnh `1_1`, kích hoạt tự động `_theme_load` / `theme.utils._theme_gift_store_post_copy` cho Web 1; trang chủ & 3 Building Blocks kéo-thả (`s_gift_hero`, `s_gift_occasion_bar`, `s_gift_featured_grid`), trang Shop/Product tối ưu mobile và đủ 3 extension slots (`wbh_gift_options_slot`, `wbh_gift_size_compare_slot`, `wbh_flash_sale_banner_slot`).
- `[NEW]` **Module `addons/theme_fashion_store/` (`v19.0.1.0.0`, 15 file, `LGPL-3`, Upgrade-Safe Odoo 19.0)**:
  - Cô lập tuyệt đối Multi-Website bằng class `.wbh-store-fashion` và điều kiện `website.wbh_store_type == 'fashion'` (không ghi đè sang Web 1).
  - Bảng màu tối giản Editorial `$o-color-1..5`, font tiếng Việt `Plus Jakarta Sans` / `Inter`, khai báo asset bundles chuẩn Odoo 19.0 (`web._assets_primary_variables`, `web.assets_frontend`, `website.assets_wysiwyg`).
  - `data/presets.xml` (`noupdate="1"`) tự động gán `theme_id` & `_theme_load` cho Web 2; trang chủ & 3 Building Blocks kéo-thả (`s_fashion_lookbook_hero`, `s_fashion_category_strip`, `s_fashion_editorial_grid`), trang Shop/Product khung ảnh dọc `3:4`, Color Swatch, Size pills dễ chạm mobile và đủ 4 extension slots (`wbh_fashion_size_advisor_slot`, `wbh_fashion_video_gallery_slot`, `wbh_fashion_shop_the_look_slot`, `wbh_flash_sale_banner_slot`).
- `[IMPROVE]` Đồng bộ Pre-Ship tài liệu khung AIaC (`README.md`, `AGENTS.md`, `.claude/CLAUDE.md`, `docs/CHANGELOGS.md`) và chuẩn hóa tên asset bundle editor từ `web_editor.assets_wysiwyg` sang `website.assets_wysiwyg` đúng thực tế mã nguồn Odoo 19.0.

---

## v0.2.0 (2026-11-25)

### Chốt 5 Quyết Định Kiến Trúc, Lộ Trình Catalog-First & Hoàn Tất Bộ Tài Liệu `/spec` Milestone 1
- `[IMPROVE]` Chốt toàn bộ 5 quyết định kiến trúc & vận hành cùng Sếp:
  1. **100% Odoo 19.0 Community (`LGPL-3`, miễn phí vĩnh viễn)** — cấm tuyệt đối phụ thuộc bất kỳ module Enterprise (`*_enterprise`, `account_accountant`...) nào.
  2. **Tách riêng hoàn toàn Tài khoản khách hàng & Tích điểm Loyalty theo từng thương hiệu** (`specific_user_account=True`, tách chương trình Loyalty theo `website_id`).
  3. **Thanh toán & Vận chuyển VN ưu tiên miễn phí, lâu dài**: VietQR tự sinh chuẩn **EMVCo / Napas 247** offline ngay trong Odoo + Adapter Webhook **SePay Free** (mở rộng PayOS/Casso); Vận chuyển Ship nội bộ/Đồng giá + ưu tiên **GHN** trước (API miễn phí 100%, có Sandbox), mở rộng GHTK & Viettel Post.
  4. **Hạ tầng Docker di động 100% trong repo Git**: chạy tạm trên máy Windows hiện tại (data trên ổ `F:\`), sẵn sàng chuyển sang Local Server ở nhà qua `git pull` + `docker compose up -d` + restore DB/filestore.
  5. **Lộ trình 3 Milestone theo hướng Catalog-First**: **Milestone 1** (Docker di động + `wbh_core` + `theme_gift_store` + `theme_fashion_store` để Sếp đăng nhập và up sản phẩm trước) ➜ **Milestone 2** (`wbh_gift_store` + `wbh_fashion_store`) ➜ **Milestone 3** (`wbh_payment_vietqr` + `wbh_delivery_vn` + Loyalty tách riêng & Flash Sale).
- `[NEW]` Tạo mới `F:\BACKUP_LINUX\web_ban_hang\docs\CONTEXT.md` (v1.0): bảng thuật ngữ nghiệp vụ (Domain Glossary) chuẩn `360-odoo`.
- `[NEW]` Tạo mới `F:\BACKUP_LINUX\web_ban_hang\docs\SPEC.md` (v1.0): đặc tả kỹ thuật chi tiết Milestone 1 sẵn sàng để `/build` ngay (cấu trúc Docker di động, `wbh_core` 100% Community, `theme_gift_store` & `theme_fashion_store` chuẩn Upgrade-Safe Odoo 19.0, cùng extension points cho Milestone 2 & 3).
- `[NEW]` Tạo mới `F:\BACKUP_LINUX\web_ban_hang\docs\DEPLOY_GUIDE.md` (v1.0): hướng dẫn cài đặt & chạy Docker tạm trên Windows (dọn WSL `VCloudOdoo19`, chuyển disk image sang ổ `F:\`), hướng dẫn nhanh Sếp đăng nhập và up sản phẩm lên Web 1 & Web 2, cùng quy trình chuyển môi trường sang Local Server tuân thủ Zero-Bypass Promotion Pipeline.
- `[IMPROVE]` Cập nhật đồng bộ `F:\BACKUP_LINUX\web_ban_hang\docs\IDEA.md` (v1.2), `F:\BACKUP_LINUX\web_ban_hang\docs\ARCH.md` (v1.1) và `F:\BACKUP_LINUX\web_ban_hang\docs\REQUIREMENTS.md` (v1.1) theo 5 quyết định chốt và lộ trình 3 Milestone.
- `[REFACTOR]` Cập nhật `F:\BACKUP_LINUX\web_ban_hang\.gitignore` từ mẫu Node/Next.js sang chuẩn **Odoo 19.0 / Python / Docker** (ignore `.env`, `data/`, `logs/`, `*.dump`, `*.sql`, `__pycache__/`, `.venv/`...; **KHÔNG ignore** `.claude/` và `.env.example`).
- `[IMPROVE]` Cập nhật đồng bộ khung AIaC: `F:\BACKUP_LINUX\web_ban_hang\README.md`, `F:\BACKUP_LINUX\web_ban_hang\AGENTS.md`, `F:\BACKUP_LINUX\web_ban_hang\.claude\CLAUDE.md` và `F:\BACKUP_LINUX\web_ban_hang\.claude\settings.local.json`.

---

## v0.1.0 (2026-11-25)

### Khởi tạo khung chuẩn AIaC 3.0 & Chốt kiến trúc thuần Odoo 19.0 Multi-Website
- `[NEW]` Hoàn tất khảo sát thực tế hạ tầng máy chủ cục bộ Windows và kho Docker Odoo sẵn có tại `F:\BACKUP_LINUX\save\dev_env\19.0\` (Odoo `19.0`, Python `3.12`, OWL `2.8.4`, Bootstrap `5.3.3`, **1.474 modules** Community + Enterprise, PostgreSQL `15` với image `360ai/postgres:15-ai` kèm `pgvector`).
- `[IMPROVE]` Cập nhật tài liệu ý tưởng `F:\BACKUP_LINUX\web_ban_hang\docs\IDEA.md` (v1.1): bổ sung Quyết định Công nghệ thuần **Odoo 19.0 + PostgreSQL 15** và đánh giá tái sử dụng hạ tầng trên máy Sếp.
- `[NEW]` Khởi tạo tài liệu kiến trúc kỹ thuật `F:\BACKUP_LINUX\web_ban_hang\docs\ARCH.md` (v1.0) và tài liệu yêu cầu `F:\BACKUP_LINUX\web_ban_hang\docs\REQUIREMENTS.md` (v1.0).
- `[IMPROVE]` Cập nhật `F:\BACKUP_LINUX\web_ban_hang\README.md` và tạo mới `F:\BACKUP_LINUX\web_ban_hang\AGENTS.md`, `F:\BACKUP_LINUX\web_ban_hang\docs\CHANGELOGS.md`, `F:\BACKUP_LINUX\web_ban_hang\.claude\CLAUDE.md`, `F:\BACKUP_LINUX\web_ban_hang\.claude\settings.local.json`.

---

## Cột Mốc Dự Kiến Tiếp Theo (Roadmap)

- **`v0.3.1` (Bước `/test` ➜ `/review` ➜ `/ship` Milestone 1 trên Docker thực tế)**:
  - Chạy `docker compose up -d`, cài đặt `wbh_core`, `theme_gift_store`, `theme_fashion_store` trên DB `web_ban_hang_dev` và chạy kiểm thử `test_wbh_core.py` + kiểm tra trực tiếp 2 Storefronts (desktop & mobile) để Sếp đăng nhập up sản phẩm ngay.
- **`v0.4.0` (Milestone 2 — Storefront Features)**:
  - Xây dựng `wbh_gift_store` (gói quà + thiệp, cá nhân hóa khắc/thêu tên, so sánh kích thước, combo dịp lễ) và `wbh_fashion_store` (gợi ý size thông minh, Shop The Look, video mẫu mặc CDN, luồng đổi size Portal).
- **`v0.5.0` (Milestone 3 — VN Integrations & Growth)**:
  - Xây dựng `wbh_payment_vietqr` (EMVCo offline + SePay Free webhook), `wbh_delivery_vn` (Ship nội bộ/Đồng giá + GHN ➜ GHTK/VTP), Loyalty tách riêng từng thương hiệu, Flash Sale & `docs/AUDIT_ROADMAP.md`.
