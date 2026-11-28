(function () {
    'use strict';

    var GIFT_SHIP_PLACEHOLDER = 'VD: Nguyễn Văn A, 0901234567, 12 Lê Lợi, Phường Bến Nghé...';

    /**
     * Cascading Vietnam 3-level address selector on /shop/address:
     * Tỉnh/TP -> Quận/Huyện -> Phường/Xã
     * Also protects simplified Web 1 fields from CustomerAddress auto-country side effects.
     */
    function resetSelect(selectEl, placeholderText, disable) {
        if (!selectEl) {
            return;
        }
        while (selectEl.options.length > 0) {
            selectEl.remove(0);
        }
        var defaultOpt = document.createElement('option');
        defaultOpt.value = '';
        defaultOpt.textContent = placeholderText;
        selectEl.appendChild(defaultOpt);
        selectEl.disabled = Boolean(disable);
    }

    function populateSelect(selectEl, items, placeholderText) {
        if (!selectEl) {
            return;
        }
        resetSelect(selectEl, placeholderText, false);
        if (!Array.isArray(items)) {
            return;
        }
        items.forEach(function (item) {
            if (!item || typeof item.id === 'undefined') {
                return;
            }
            var opt = document.createElement('option');
            opt.value = String(item.id);
            opt.textContent = String(item.name || '');
            selectEl.appendChild(opt);
        });
        selectEl.disabled = items.length === 0;
    }

    function fetchJson(url) {
        return window.fetch(url, {
            method: 'GET',
            credentials: 'same-origin',
            headers: {
                Accept: 'application/json',
            },
        }).then(function (response) {
            if (!response.ok) {
                throw new Error('HTTP ' + response.status);
            }
            return response.json();
        });
    }

    function isGiftSimplified(form) {
        var flag = form.querySelector('input[name="wbh_gift_simplified"]');
        return Boolean(flag && flag.value === '1');
    }

    function enforceGiftSimplifiedFields(form) {
        if (!isGiftSimplified(form)) {
            return;
        }
        ['street', 'street2', 'city', 'zip', 'country_id', 'state_id', 'company_name', 'vat'].forEach(
            function (fname) {
                var fieldEl = form.querySelector('[name="' + fname + '"]');
                if (fieldEl) {
                    fieldEl.required = false;
                    fieldEl.removeAttribute('required');
                }
            }
        );
        var phoneInput = form.querySelector('#o_phone');
        if (phoneInput && phoneInput.placeholder !== GIFT_SHIP_PLACEHOLDER) {
            phoneInput.placeholder = GIFT_SHIP_PLACEHOLDER;
        }
        var vnBlocks = form.querySelectorAll('.wbh-vn-address-field');
        vnBlocks.forEach(function (el) {
            el.classList.remove('d-none');
        });
    }

    function toggleVnFieldsByCountry(form) {
        var vnBlocks = form.querySelectorAll('.wbh-vn-address-field');
        if (!vnBlocks.length) {
            return;
        }
        if (isGiftSimplified(form)) {
            vnBlocks.forEach(function (el) {
                el.classList.remove('d-none');
            });
            return;
        }
        var countrySelect = form.querySelector('select[name="country_id"]');
        if (!countrySelect) {
            return;
        }
        var selectedOption = countrySelect.selectedOptions && countrySelect.selectedOptions[0];
        var countryCode = selectedOption ? (selectedOption.getAttribute('code') || '') : '';
        var showVn = !countrySelect.value || countryCode.toUpperCase() === 'VN';
        vnBlocks.forEach(function (el) {
            el.classList.toggle('d-none', !showVn);
        });
    }

    function initVnAddressCascade() {
        var form = document.querySelector('form.address_autoformat');
        if (!form) {
            return;
        }
        var provinceSelect = form.querySelector('select[name="wbh_vn_province_id"]');
        var districtSelect = form.querySelector('select[name="wbh_vn_district_id"]');
        var wardSelect = form.querySelector('select[name="wbh_vn_ward_id"]');
        if (!provinceSelect || !districtSelect || !wardSelect) {
            return;
        }

        if (form.dataset.wbhVnBound === '1') {
            return;
        }
        form.dataset.wbhVnBound = '1';

        enforceGiftSimplifiedFields(form);
        if (isGiftSimplified(form) && typeof window.MutationObserver === 'function') {
            var observer = new window.MutationObserver(function () {
                enforceGiftSimplifiedFields(form);
            });
            observer.observe(form, {
                attributes: true,
                subtree: true,
                attributeFilter: ['required', 'placeholder'],
            });
        }

        var countrySelect = form.querySelector('select[name="country_id"]');
        if (countrySelect) {
            toggleVnFieldsByCountry(form);
            countrySelect.addEventListener('change', function () {
                toggleVnFieldsByCountry(form);
                enforceGiftSimplifiedFields(form);
            });
        }

        provinceSelect.addEventListener('change', function () {
            var provinceId = provinceSelect.value;
            resetSelect(districtSelect, 'Chọn Quận/Huyện...', true);
            resetSelect(wardSelect, 'Chọn Phường/Xã...', true);

            var cityInput = form.querySelector('input[name="city"]');
            var selectedProvOpt = provinceSelect.selectedOptions && provinceSelect.selectedOptions[0];
            if (cityInput && provinceId && selectedProvOpt && (!cityInput.value.trim() || isGiftSimplified(form))) {
                cityInput.value = selectedProvOpt.textContent.trim();
            }

            if (!provinceId) {
                return;
            }
            fetchJson('/wbh/vn/districts/' + encodeURIComponent(provinceId))
                .then(function (items) {
                    if (provinceSelect.value === provinceId) {
                        populateSelect(districtSelect, items, 'Chọn Quận/Huyện...');
                    }
                })
                .catch(function () {
                    resetSelect(districtSelect, 'Không tải được Quận/Huyện', true);
                });
        });

        districtSelect.addEventListener('change', function () {
            var districtId = districtSelect.value;
            resetSelect(wardSelect, 'Chọn Phường/Xã...', true);

            if (!districtId) {
                return;
            }
            fetchJson('/wbh/vn/wards/' + encodeURIComponent(districtId))
                .then(function (items) {
                    if (districtSelect.value === districtId) {
                        populateSelect(wardSelect, items, 'Chọn Phường/Xã...');
                    }
                })
                .catch(function () {
                    resetSelect(wardSelect, 'Không tải được Phường/Xã', true);
                });
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initVnAddressCascade);
    } else {
        initVnAddressCascade();
    }
})();
