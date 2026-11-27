(function () {
    'use strict';

    /**
     * Theme Web 2 — Fashion & Lookbook Motion + Lucide Icons (Odoo 19.0 Community)
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
                    'stroke-width': '1.5',
                    'aria-hidden': 'true',
                },
            });
        } catch (_err) {
            // Bỏ qua an toàn nếu gặp node lỗi
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
        bindStickyCartBar(scopeEl);

        if (isWebsiteBuilderEditMode()) {
            return;
        }
        var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (reduceMotion) {
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
