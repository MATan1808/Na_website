(function () {
    'use strict';

    /**
     * Theme Web 2 — Fashion & Lookbook Motion, Livechat & Dynamic Filter Helpers (Odoo 19.0 Community)
     * Nguyên tắc Unslop: KHÔNG bao giờ ẩn nội dung (opacity: 0) khi tải hoặc cuộn nhanh.
     */
    var HEX_COLOR_RE = /^#[0-9a-fA-F]{3,8}$/;
    var toastTimer = null;

    function isWebsiteBuilderEditMode() {
        var body = document.body;
        var docEl = document.documentElement;
        return Boolean(
            (body && (body.classList.contains('editor_enable') || body.classList.contains('o_editable'))) ||
            (docEl && docEl.classList.contains('o_website_preview'))
        );
    }

    function isReducedMotion() {
        return Boolean(
            window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches
        );
    }

    function renderLucideIcons(root) {
        if (!window.lucide || typeof window.lucide.createIcons !== 'function') {
            return;
        }
        try {
            window.lucide.createIcons({
                root: root || document,
                attrs: {
                    'stroke-width': '1.5',
                    'aria-hidden': 'true',
                },
            });
        } catch (_err) {
            // Bỏ qua an toàn nếu gặp node lỗi
        }
    }

    function applyTagDotColors(scopeEl) {
        var dots = scopeEl.querySelectorAll('[data-wbh-dot-color]');
        dots.forEach(function (dot) {
            var color = (dot.getAttribute('data-wbh-dot-color') || '').trim();
            if (HEX_COLOR_RE.test(color)) {
                dot.style.backgroundColor = color;
            }
        });
    }

    function showToast(scopeEl, message) {
        var toastEl = scopeEl.querySelector('#wbhFashionToast');
        if (!toastEl || !message) {
            return;
        }
        toastEl.textContent = message;
        toastEl.hidden = false;
        toastEl.classList.add('is-visible');
        if (toastTimer) {
            window.clearTimeout(toastTimer);
        }
        toastTimer = window.setTimeout(function () {
            toastEl.classList.remove('is-visible');
            toastEl.hidden = true;
        }, 3200);
    }

    function fallbackCopy(text) {
        try {
            var area = document.createElement('textarea');
            area.value = text;
            area.setAttribute('readonly', 'readonly');
            area.style.position = 'fixed';
            area.style.opacity = '0';
            area.style.left = '-9999px';
            document.body.appendChild(area);
            area.select();
            var ok = document.execCommand('copy');
            document.body.removeChild(area);
            return Boolean(ok);
        } catch (_err) {
            return false;
        }
    }

    function copyTextToClipboard(text) {
        if (navigator.clipboard && typeof navigator.clipboard.writeText === 'function') {
            return navigator.clipboard.writeText(text).then(
                function () { return true; },
                function () { return fallbackCopy(text); }
            );
        }
        return Promise.resolve(fallbackCopy(text));
    }

    function findLivechatTriggerElement() {
        var roots = document.querySelectorAll('.o-livechat-root');
        for (var i = 0; i < roots.length; i += 1) {
            var root = roots[i];
            var searchRoot = root.shadowRoot || root;
            var btn = searchRoot.querySelector(
                'button.o-livechat-LivechatButton, [part="openChatButton"], .o-mail-ChatHub-bubbleBtn, .o-mail-ChatWindow-header'
            );
            if (btn) {
                return btn;
            }
        }
        return document.querySelector('button.o-livechat-LivechatButton, .o_livechat_button');
    }

    function openFloatingContactMenu(scopeEl, openState) {
        var root = scopeEl.querySelector('[data-wbh-floating-root="true"]');
        if (!root) {
            return;
        }
        var toggleBtn = root.querySelector('[data-wbh-floating-toggle="true"]');
        var menuEl = root.querySelector('.wbh-fashion-floating-menu');
        if (!toggleBtn || !menuEl) {
            return;
        }
        var shouldOpen = typeof openState === 'boolean' ? openState : menuEl.hidden;
        if (shouldOpen) {
            menuEl.hidden = false;
            root.classList.add('is-open');
            toggleBtn.setAttribute('aria-expanded', 'true');
            if (window.gsap && !isWebsiteBuilderEditMode() && !isReducedMotion()) {
                window.gsap.fromTo(
                    menuEl,
                    { y: 8, opacity: 0 },
                    {
                        y: 0,
                        opacity: 1,
                        duration: 0.22,
                        ease: 'power3.out',
                        clearProps: 'transform,opacity',
                    }
                );
            }
        } else {
            root.classList.remove('is-open');
            toggleBtn.setAttribute('aria-expanded', 'false');
            menuEl.hidden = true;
        }
    }

    function triggerOdooLivechat(scopeEl, productTitle) {
        var shareText = productTitle
            ? (productTitle + ' — ' + window.location.href)
            : window.location.href;
        copyTextToClipboard(shareText).then(function () {
            var triggerEl = findLivechatTriggerElement();
            if (triggerEl) {
                triggerEl.click();
                showToast(scopeEl, 'Đã chép tên & link SP — Đang mở chat tư vấn');
                return;
            }
            window.setTimeout(function () {
                var retryEl = findLivechatTriggerElement();
                if (retryEl) {
                    retryEl.click();
                    showToast(scopeEl, 'Đã chép tên & link SP — Đang mở chat tư vấn');
                } else {
                    openFloatingContactMenu(scopeEl, true);
                    showToast(scopeEl, 'Đã chép tên & link SP — Chọn Facebook/Zalo để nhắn ngay');
                }
            }, 350);
        });
    }

    function bindContactAndCopyActions(scopeEl) {
        scopeEl.querySelectorAll('[data-wbh-action="copy-product"]').forEach(function (btn) {
            if (btn.dataset.wbhBound === '1') {
                return;
            }
            btn.dataset.wbhBound = '1';
            btn.addEventListener('click', function () {
                var title = btn.getAttribute('data-wbh-product-name') || document.title;
                var text = title + '\n' + window.location.href;
                copyTextToClipboard(text).then(function (ok) {
                    showToast(
                        scopeEl,
                        ok ? 'Đã chép tên & link sản phẩm' : 'Không thể truy cập clipboard'
                    );
                });
            });
        });

        scopeEl.querySelectorAll('[data-wbh-action="livechat"]').forEach(function (btn) {
            if (btn.dataset.wbhBound === '1') {
                return;
            }
            btn.dataset.wbhBound = '1';
            btn.addEventListener('click', function () {
                var title = btn.getAttribute('data-wbh-product-name') || '';
                triggerOdooLivechat(scopeEl, title);
            });
        });

        var floatRoot = scopeEl.querySelector('[data-wbh-floating-root="true"]');
        var toggleBtn = floatRoot && floatRoot.querySelector('[data-wbh-floating-toggle="true"]');
        if (toggleBtn && toggleBtn.dataset.wbhBound !== '1') {
            toggleBtn.dataset.wbhBound = '1';
            toggleBtn.addEventListener('click', function () {
                openFloatingContactMenu(scopeEl);
            });
            document.addEventListener('click', function (ev) {
                if (floatRoot.classList.contains('is-open') && !floatRoot.contains(ev.target)) {
                    openFloatingContactMenu(scopeEl, false);
                }
            });
            document.addEventListener('keydown', function (ev) {
                if (ev.key === 'Escape' && floatRoot.classList.contains('is-open')) {
                    openFloatingContactMenu(scopeEl, false);
                    toggleBtn.focus();
                }
            });
        }
    }

    function bindStickyCartBar(scopeEl) {
        var stickyBar = scopeEl.querySelector('.wbh-fashion-mobile-sticky-bar');
        var triggerBtns = scopeEl.querySelectorAll('[data-wbh-trigger-cart="true"]');
        triggerBtns.forEach(function (btn) {
            if (btn.dataset.wbhBound === '1') {
                return;
            }
            btn.dataset.wbhBound = '1';
            btn.addEventListener('click', function (ev) {
                ev.preventDefault();
                var mainAddBtn = document.getElementById('add_to_cart');
                if (mainAddBtn) {
                    mainAddBtn.click();
                }
            });
        });

        if (!stickyBar) {
            return;
        }
        var mainCta = document.getElementById('add_to_cart');
        if (!mainCta || typeof window.IntersectionObserver !== 'function') {
            return;
        }
        stickyBar.classList.add('wbh-sticky-hidden');
        var observer = new window.IntersectionObserver(
            function (entries) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) {
                        stickyBar.classList.add('wbh-sticky-hidden');
                    } else {
                        stickyBar.classList.remove('wbh-sticky-hidden');
                    }
                });
            },
            { threshold: 0.1 }
        );
        observer.observe(mainCta);
    }

    function initSubtleEditorialMotion(scopeEl) {
        if (!window.gsap) {
            return;
        }
        // Chỉ trượt nhẹ trục Y (12px -> 0) trên media hero, không đưa opacity về 0
        var heroMedia = scopeEl.querySelectorAll('.s_fashion_lookbook_hero .wbh-fashion-hero-media');
        if (heroMedia.length) {
            window.gsap.fromTo(
                heroMedia,
                { y: 12 },
                {
                    y: 0,
                    duration: 0.45,
                    ease: 'power3.out',
                    clearProps: 'transform',
                }
            );
        }
    }

    function bootstrapFashionStore() {
        var scopeEl = document.querySelector('#wrapwrap.wbh-store-fashion');
        if (!scopeEl) {
            return;
        }
        renderLucideIcons(scopeEl);
        applyTagDotColors(scopeEl);
        bindContactAndCopyActions(scopeEl);
        bindStickyCartBar(scopeEl);

        if (isWebsiteBuilderEditMode() || isReducedMotion()) {
            return;
        }
        initSubtleEditorialMotion(scopeEl);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', bootstrapFashionStore);
    } else {
        bootstrapFashionStore();
    }
})();
