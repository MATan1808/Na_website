(function () {
    'use strict';

    /**
     * Theme Web 2 — Fashion & Lookbook Motion + Lucide Icons (Odoo 19.0 Community)
     * 3 chốt bảo vệ: Multi-website scope (.wbh-store-fashion), Website Builder Edit Mode, prefers-reduced-motion.
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

    function initFashionMotion(scopeEl) {
        if (!window.gsap) {
            return;
        }
        var gsap = window.gsap;
        var ScrollTrigger = window.ScrollTrigger;
        if (ScrollTrigger && typeof gsap.registerPlugin === 'function') {
            gsap.registerPlugin(ScrollTrigger);
        }

        // 1. Editorial Hero entrance (power3.out mượt mà, không nảy)
        var heroSection = scopeEl.querySelector('.s_fashion_lookbook_hero');
        if (heroSection) {
            var heroTargets = heroSection.querySelectorAll(
                '.wbh-fashion-eyebrow, .wbh-fashion-hero-title, .wbh-fashion-hero-lead, .wbh-fashion-hero-cta, .wbh-fashion-hero-cta-secondary, .wbh-fashion-hero-media'
            );
            if (heroTargets.length) {
                gsap.from(heroTargets, {
                    y: 24,
                    opacity: 0,
                    duration: 0.75,
                    stagger: 0.08,
                    ease: 'power3.out',
                    clearProps: 'transform,opacity',
                });
            }
        }

        // 2. ScrollTrigger batch reveal cho Category Strip, Editorial Lookbook & /shop
        if (!ScrollTrigger) {
            return;
        }
        var revealGroups = [
            '.wbh-fashion-cat-card',
            '.wbh-fashion-editorial-card',
            '.wbh-fashion-product-card',
        ];
        revealGroups.forEach(function (selector) {
            var nodes = scopeEl.querySelectorAll(selector);
            if (!nodes.length) {
                return;
            }
            gsap.set(nodes, { opacity: 0, y: 22 });
            ScrollTrigger.batch(nodes, {
                start: 'top 90%',
                once: true,
                onEnter: function (batch) {
                    gsap.to(batch, {
                        opacity: 1,
                        y: 0,
                        duration: 0.65,
                        stagger: 0.07,
                        ease: 'power3.out',
                        clearProps: 'transform,opacity',
                    });
                },
            });
        });
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
        initFashionMotion(scopeEl);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', bootstrapFashionStore);
    } else {
        bootstrapFashionStore();
    }
})();
