(function () {
    'use strict';

    /**
     * Theme Web 1 — Gift & Anime Goods Motion + Lucide Icons (Odoo 19.0 Community)
     * 3 chốt bảo vệ: Multi-website scope (.wbh-store-gift), Website Builder Edit Mode, prefers-reduced-motion.
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
                    'stroke-width': '1.9',
                    'aria-hidden': 'true',
                },
            });
        } catch (_err) {
            // Không làm gián đoạn render nếu một node thiếu attribute
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

    function initGiftMotion(scopeEl) {
        if (!window.gsap) {
            return;
        }
        var gsap = window.gsap;
        var ScrollTrigger = window.ScrollTrigger;
        if (ScrollTrigger && typeof gsap.registerPlugin === 'function') {
            gsap.registerPlugin(ScrollTrigger);
        }

        // 1. Hero entrance (nhẹ nhàng, ấm áp)
        var heroSection = scopeEl.querySelector('.s_gift_hero');
        if (heroSection) {
            var heroTargets = heroSection.querySelectorAll(
                '.wbh-gift-eyebrow, .wbh-gift-hero__title, .wbh-gift-hero__lead, .wbh-gift-hero__trust, .wbh-gift-hero__tile'
            );
            if (heroTargets.length) {
                gsap.from(heroTargets, {
                    y: 22,
                    opacity: 0,
                    duration: 0.65,
                    stagger: 0.08,
                    ease: 'power2.out',
                    clearProps: 'transform,opacity',
                });
            }
        }

        // 2. ScrollTrigger batch reveal cho danh mục, card nổi bật & lưới /shop
        if (!ScrollTrigger) {
            return;
        }
        var revealGroups = [
            '.wbh-gift-occasion-card',
            '.wbh-gift-featured-card',
            '.oe_product_cart',
        ];
        revealGroups.forEach(function (selector) {
            var nodes = scopeEl.querySelectorAll(selector);
            if (!nodes.length) {
                return;
            }
            gsap.set(nodes, { opacity: 0, y: 20 });
            ScrollTrigger.batch(nodes, {
                start: 'top 90%',
                once: true,
                onEnter: function (batch) {
                    gsap.to(batch, {
                        opacity: 1,
                        y: 0,
                        duration: 0.55,
                        stagger: 0.06,
                        ease: 'power2.out',
                        clearProps: 'transform,opacity',
                    });
                },
            });
        });
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
        initGiftMotion(scopeEl);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', bootstrapGiftStore);
    } else {
        bootstrapGiftStore();
    }
})();
