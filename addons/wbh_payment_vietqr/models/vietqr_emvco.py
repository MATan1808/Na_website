# -*- coding: utf-8 -*-
import base64
import logging
import re
import unicodedata

from odoo.addons.wbh_payment_vietqr.const import (
    NAPAS_GUID,
    NAPAS_SERVICE_ACCOUNT,
    VN_BANK_BINS,
    VN_COUNTRY_CODE,
    VND_NUMERIC_CODE,
)

_logger = logging.getLogger(__name__)


def crc16_ccitt(data: bytes) -> str:
    """Tính CRC16-CCITT (đa thức 0x1021, giá trị khởi tạo 0xFFFF) theo chuẩn EMVCo."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return f"{crc:04X}"


def format_tlv(tag: str, value: str) -> str:
    """Đóng gói một phần tử Tag-Length-Value theo chuẩn EMVCo (độ dài 2 chữ số)."""
    if value is None:
        return ''
    str_val = str(value)
    return f"{tag}{len(str_val):02d}{str_val}"


def sanitize_vietqr_text(text: str, max_len: int = 50) -> str:
    """Chuyển chuỗi tiếng Việt có dấu sang ASCII an toàn cho nội dung chuyển khoản ngân hàng."""
    if not text:
        return ''
    replaced = str(text).replace('đ', 'd').replace('Đ', 'D')
    normalized = unicodedata.normalize('NFKD', replaced)
    ascii_only = ''.join(ch for ch in normalized if unicodedata.category(ch) != 'Mn')
    cleaned = re.sub(r'[^A-Za-z0-9 \-._/]', ' ', ascii_only)
    collapsed = re.sub(r'\s+', ' ', cleaned).strip()
    return collapsed[:max_len]


def sanitize_account_no(account_no: str) -> str:
    """Chuẩn hóa số tài khoản ngân hàng chỉ giữ chữ và số ASCII."""
    if not account_no:
        return ''
    return re.sub(r'[^A-Za-z0-9]', '', str(account_no)).strip()


def get_bank_display_name(bank_bin: str) -> str:
    """Trả về tên ngân hàng dễ đọc từ mã BIN Napas."""
    return VN_BANK_BINS.get(bank_bin or '', bank_bin or '')


def build_vietqr_payload(bank_bin: str, account_no: str, amount: float = 0.0, transfer_note: str = '') -> str:
    """Sinh chuỗi QR chuẩn EMVCo / Napas 247 hoàn toàn offline.

    Cấu trúc TLV:
    - 00: Payload Format Indicator ('01')
    - 01: Point of Initiation Method ('12' khi có số tiền, '11' khi QR tĩnh)
    - 38: Merchant Account Info (GUID A000000727, BIN + STK, Service QRIBFTTA)
    - 53: Transaction Currency ('704' = VND)
    - 54: Transaction Amount (số nguyên VND nếu > 0)
    - 58: Country Code ('VN')
    - 62: Additional Data Field Template (subtag 08 = nội dung chuyển khoản)
    - 63: CRC16-CCITT (4 ký tự hex viết hoa)
    """
    clean_bin = sanitize_account_no(bank_bin)
    clean_account = sanitize_account_no(account_no)
    if not clean_bin or not clean_account:
        return ''

    initiation_method = '12' if amount and amount > 0 else '11'

    beneficiary_info = (
        format_tlv('00', clean_bin)
        + format_tlv('01', clean_account)
    )
    merchant_account_info = (
        format_tlv('00', NAPAS_GUID)
        + format_tlv('01', beneficiary_info)
        + format_tlv('02', NAPAS_SERVICE_ACCOUNT)
    )

    parts = [
        format_tlv('00', '01'),
        format_tlv('01', initiation_method),
        format_tlv('38', merchant_account_info),
        format_tlv('53', VND_NUMERIC_CODE),
    ]

    if amount and amount > 0:
        int_amount = int(round(float(amount)))
        if int_amount > 0:
            parts.append(format_tlv('54', str(int_amount)))

    parts.append(format_tlv('58', VN_COUNTRY_CODE))

    clean_note = sanitize_vietqr_text(transfer_note, max_len=50)
    if clean_note:
        additional_data = format_tlv('08', clean_note)
        parts.append(format_tlv('62', additional_data))

    raw_payload = ''.join(parts) + '6304'
    checksum = crc16_ccitt(raw_payload.encode('ascii'))
    return raw_payload + checksum


def generate_qr_png_base64(env, payload: str, width: int = 360, height: int = 360) -> bytes:
    """Sinh ảnh QR PNG base64 offline bằng `ir.actions.report.barcode` của Odoo core."""
    if not payload or env is None:
        return b''
    try:
        png_bytes = env['ir.actions.report'].sudo().barcode(
            'QR',
            payload,
            width=width,
            height=height,
            barLevel='M',
            quiet=True,
        )
        return base64.b64encode(png_bytes)
    except Exception as exc:
        _logger.warning("Không thể sinh mã QR VietQR offline: %s", exc)
        return b''
