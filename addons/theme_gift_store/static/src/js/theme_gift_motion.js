(function () {
    'use strict';

    /**
     * Theme Web 1 — Gift & Anime Goods Motion + Lucide Icons (Odoo 19.0 Community)
     * Nguyên tắc Unslop: KHÔNG bao giờ ẩn nội dung (opacity: 0) khi tải hoặc cuộn nhanh.
     */
    function isWebsiteBuilderEditMode() {
        var body = document.body;
        var docEl = document.documentElement;
        return Boolean(
            (body && (body.classList.contains('editor_enable') || body.classList.contains('o_editable'))) ||
            (docEl && docEl.classList.contains('o_website_preview'))
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
                    'stroke-width': '1.65',
                    'aria-hidden': 'true',
                },
            });
        } catch (_err) {
            // Bỏ qua an toàn nếu một node không hợp lệ
        }
    }

    function bindStickyCartBar(scopeEl) {
        var stickyBar = scopeEl.querySelector('.wbh-gift-sticky-bar');
        var triggerBtns = scopeEl.querySelectorAll('[data-wbh-trigger-cart="true"]');
        triggerBtns.forEach(function (btn) {
            if (btn.dataset.wbhBound === '1') {
                return;
            }
            btn.dataset.wbhBound = '1';
            btn.addEventListener('click', function () {
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

    function initSubtleHeroMotion(scopeEl) {
        if (!window.gsap) {
            return;
        }
        // Chỉ trượt nhẹ trục Y (10px -> 0), KHÔNG đưa opacity về 0 để không bao giờ làm mờ nội dung
        var galleryItems = scopeEl.querySelectorAll('.s_gift_hero .wbh-gift-hero__gallery-item');
        if (galleryItems.length) {
            window.gsap.fromTo(
                galleryItems,
                { y: 10 },
                {
                    y: 0,
                    duration: 0.42,
                    stagger: 0.06,
                    ease: 'power2.out',
                    clearProps: 'transform',
                }
            );
        }
    }

    function bootstrapGiftStore() {
        var scopeEl = document.querySelector('#wrapwrap.wbh-store-gift');
        if (!scopeEl) {
            return;
        }
        renderLucideIcons(scopeEl);
        bindStickyCartBar(scopeEl);

        if (isWebsiteBuilderEditMode()) {
            return;
        }
        var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (reduceMotion) {
            return;
        }
        initSubtleHeroMotion(scopeEl);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', bootstrapGiftStore);
    } else {
        bootstrapGiftStore();
    }
})();
