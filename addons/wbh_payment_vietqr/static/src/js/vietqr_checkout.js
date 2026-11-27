import { PaymentPostProcessing } from '@payment/interactions/post_processing';
import { registry } from '@web/core/registry';
import { patch } from '@web/core/utils/patch';
import { Interaction } from '@web/public/interaction';

patch(PaymentPostProcessing, {
    /**
     * Cho phép đơn COD ('wbh_cod') chuyển thẳng sang trang xác nhận đơn hàng ngay ở trạng thái pending.
     */
    getFinalStates(providerCode) {
        const finalStates = super.getFinalStates(...arguments);
        if (providerCode === 'wbh_cod') {
            finalStates.add('pending');
        }
        return finalStates;
    },
});

export class VietQRPaymentCard extends Interaction {
    static selector = '.wbh-vietqr-card';
    dynamicContent = {
        '[data-wbh-copy]': { 't-on-click': this.onClickCopy },
        '[data-wbh-check-status]': { 't-on-click': this.onClickCheckStatus },
    };

    setup() {
        this.reference = this.el.dataset.wbhReference || '';
        this.autoPoll = this.el.dataset.wbhAutoPoll === '1';
        this.landingRoute = this.el.dataset.wbhLandingRoute || '/shop/confirmation';
        this._isRedirecting = false;
    }

    start() {
        if (window.lucide && typeof window.lucide.createIcons === 'function') {
            window.lucide.createIcons();
        }
        if (this.autoPoll && this.reference) {
            this._schedulePoll();
        }
    }

    _schedulePoll() {
        this.waitForTimeout(async () => {
            if (this._isRedirecting) {
                return;
            }
            const done = await this._checkStatus();
            if (!done && !this._isRedirecting) {
                this._schedulePoll();
            }
        }, 4000);
    }

    async onClickCopy(ev) {
        ev.preventDefault();
        const btn = ev.currentTarget;
        const text = btn.dataset.wbhCopy || '';
        if (!text) {
            return;
        }
        let copied = false;
        try {
            if (navigator.clipboard && window.isSecureContext) {
                await navigator.clipboard.writeText(text);
                copied = true;
            }
        } catch {
            copied = false;
        }
        if (!copied) {
            const textarea = document.createElement('textarea');
            textarea.value = text;
            textarea.setAttribute('readonly', 'readonly');
            textarea.className = 'visually-hidden';
            document.body.appendChild(textarea);
            textarea.select();
            try {
                copied = document.execCommand('copy');
            } finally {
                textarea.remove();
            }
        }
        if (copied) {
            const label = btn.querySelector('[data-wbh-copy-label]');
            if (label) {
                const original = label.textContent;
                label.textContent = 'Đã sao chép';
                btn.classList.add('is-copied');
                this.waitForTimeout(() => {
                    label.textContent = original;
                    btn.classList.remove('is-copied');
                }, 2000);
            }
        }
    }

    async onClickCheckStatus(ev) {
        ev.preventDefault();
        await this._checkStatus(true);
    }

    async _checkStatus(manual = false) {
        if (!this.reference) {
            return false;
        }
        const statusTextEl = this.el.querySelector('[data-wbh-status-text]');
        const badgeEl = this.el.querySelector('[data-wbh-status-badge]');
        if (manual && statusTextEl) {
            statusTextEl.textContent = 'Đang kiểm tra...';
        }
        try {
            const url = `/payment/vietqr/status/${encodeURIComponent(this.reference)}`;
            const resp = await this.waitFor(fetch(url, {
                method: 'GET',
                credentials: 'same-origin',
                headers: { Accept: 'application/json' },
            }));
            if (!resp.ok) {
                if (manual && statusTextEl) {
                    statusTextEl.textContent = 'Chưa thể kiểm tra, vui lòng thử lại';
                }
                return false;
            }
            const data = await resp.json();
            if (data.is_done) {
                this._isRedirecting = true;
                if (badgeEl) {
                    badgeEl.classList.add('is-done');
                }
                if (statusTextEl) {
                    statusTextEl.textContent = 'Đã thanh toán! Đang chuyển hướng...';
                }
                window.location = data.landing_route || this.landingRoute;
                return true;
            }
            if (manual && statusTextEl) {
                statusTextEl.textContent = 'Chưa nhận được giao dịch mới — Vui lòng thử lại sau ít giây';
            }
        } catch {
            if (manual && statusTextEl) {
                statusTextEl.textContent = 'Lỗi kết nối, vui lòng thử lại';
            }
        }
        return false;
    }
}

registry
    .category('public.interactions')
    .add('wbh_payment_vietqr.vietqr_payment_card', VietQRPaymentCard);
