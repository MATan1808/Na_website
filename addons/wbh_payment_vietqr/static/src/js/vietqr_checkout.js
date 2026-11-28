import { PaymentPostProcessing } from '@payment/interactions/post_processing';
import { registry } from '@web/core/registry';
import { patch } from '@web/core/utils/patch';
import { Interaction } from '@web/public/interaction';

const MAX_PROOF_SIZE_BYTES = 5 * 1024 * 1024;
const ALLOWED_PROOF_TYPES = new Set(['image/png', 'image/jpeg', 'image/webp']);

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

async function copyTextToClipboard(btn, text) {
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
            window.setTimeout(() => {
                label.textContent = original;
                btn.classList.remove('is-copied');
            }, 2000);
        }
    }
}

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
        await copyTextToClipboard(btn, btn.dataset.wbhCopy || '');
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

export class VietQRInlineCard extends Interaction {
    static selector = '.wbh-vietqr-inline-card';
    dynamicContent = {
        '[data-wbh-copy]': { 't-on-click': this.onClickCopy },
    };

    start() {
        if (window.lucide && typeof window.lucide.createIcons === 'function') {
            window.lucide.createIcons();
        }
    }

    async onClickCopy(ev) {
        ev.preventDefault();
        const btn = ev.currentTarget;
        await copyTextToClipboard(btn, btn.dataset.wbhCopy || '');
    }
}

export class VietQRProofUpload extends Interaction {
    static selector = '.wbh-vietqr-proof-box';
    dynamicContent = {
        '[data-wbh-proof-input]': { 't-on-change': this.onChangeFile },
        '[data-wbh-proof-upload-btn]': { 't-on-click': this.onClickUpload },
    };

    setup() {
        this.uploadUrl = this.el.dataset.wbhUploadUrl || '/payment/vietqr/upload_proof';
        this.orderId = this.el.dataset.wbhOrderId || '';
        this.accessToken = this.el.dataset.wbhAccessToken || '';
        this._previewObjectUrl = null;
    }

    destroy() {
        if (this._previewObjectUrl) {
            URL.revokeObjectURL(this._previewObjectUrl);
            this._previewObjectUrl = null;
        }
        super.destroy();
    }

    _setStatus(message, isError = false) {
        const statusEl = this.el.querySelector('[data-wbh-proof-status]');
        if (!statusEl) {
            return;
        }
        statusEl.replaceChildren();
        const span = document.createElement('span');
        span.className = isError ? 'text-danger fw-semibold' : 'text-success fw-semibold';
        span.textContent = message;
        statusEl.appendChild(span);
    }

    onChangeFile(ev) {
        const input = ev.currentTarget;
        const file = input.files && input.files[0];
        const previewWrap = this.el.querySelector('[data-wbh-proof-preview-wrap]');
        const previewImg = this.el.querySelector('[data-wbh-proof-preview]');

        if (this._previewObjectUrl) {
            URL.revokeObjectURL(this._previewObjectUrl);
            this._previewObjectUrl = null;
        }
        if (!file) {
            if (previewWrap) {
                previewWrap.classList.add('d-none');
            }
            return;
        }
        if (file.size > MAX_PROOF_SIZE_BYTES) {
            this._setStatus('Dung lượng ảnh vượt quá 5MB, vui lòng chọn ảnh nhỏ hơn.', true);
            input.value = '';
            return;
        }
        if (file.type && !ALLOWED_PROOF_TYPES.has(file.type)) {
            this._setStatus('Chỉ hỗ trợ ảnh định dạng PNG, JPG/JPEG hoặc WEBP.', true);
            input.value = '';
            return;
        }
        if (previewWrap && previewImg) {
            this._previewObjectUrl = URL.createObjectURL(file);
            previewImg.src = this._previewObjectUrl;
            previewWrap.classList.remove('d-none');
        }
        this._setStatus(`Đã chọn: ${file.name}. Bấm "Gửi ảnh bill CK" để đính kèm vào đơn hàng.`);
    }

    async onClickUpload(ev) {
        ev.preventDefault();
        const input = this.el.querySelector('[data-wbh-proof-input]');
        const btn = ev.currentTarget;
        const file = input && input.files && input.files[0];
        if (!file) {
            this._setStatus('Vui lòng chọn ảnh chụp màn hình chuyển khoản trước khi gửi.', true);
            return;
        }
        if (file.size > MAX_PROOF_SIZE_BYTES) {
            this._setStatus('Dung lượng ảnh vượt quá 5MB.', true);
            return;
        }

        const csrfEl = this.el.querySelector('[data-wbh-csrf]');
        const csrfToken = (csrfEl && csrfEl.value) || (window.odoo && window.odoo.csrf_token) || '';

        const formData = new FormData();
        formData.append('order_id', this.orderId);
        if (this.accessToken) {
            formData.append('access_token', this.accessToken);
        }
        if (csrfToken) {
            formData.append('csrf_token', csrfToken);
        }
        formData.append('proof_file', file);

        btn.disabled = true;
        this._setStatus('Đang tải ảnh bill chuyển khoản lên...');
        try {
            const resp = await this.waitFor(fetch(this.uploadUrl, {
                method: 'POST',
                credentials: 'same-origin',
                body: formData,
            }));
            const data = await resp.json();
            if (!resp.ok || !data.success) {
                this._setStatus((data && data.error) || 'Không thể tải ảnh bill CK, vui lòng thử lại.', true);
            } else {
                this._setStatus(data.message || `Đã đính kèm bill CK: ${data.filename}`);
            }
        } catch {
            this._setStatus('Lỗi kết nối khi tải ảnh bill CK, vui lòng thử lại.', true);
        } finally {
            btn.disabled = false;
        }
    }
}

registry
    .category('public.interactions')
    .add('wbh_payment_vietqr.vietqr_payment_card', VietQRPaymentCard);
registry
    .category('public.interactions')
    .add('wbh_payment_vietqr.vietqr_inline_card', VietQRInlineCard);
registry
    .category('public.interactions')
    .add('wbh_payment_vietqr.vietqr_proof_upload', VietQRProofUpload);
