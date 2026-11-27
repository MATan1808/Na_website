# -*- coding: utf-8 -*-

VN_BANK_BINS = {
    '970422': 'MBBank (MB)',
    '970436': 'Vietcombank (VCB)',
    '970407': 'Techcombank (TCB)',
    '970416': 'ACB',
    '970418': 'BIDV',
    '970415': 'VietinBank (CTG)',
    '970432': 'VPBank',
    '970423': 'TPBank',
    '970403': 'Sacombank (STB)',
    '970405': 'Agribank',
    '970441': 'VIB',
    '970437': 'HDBank',
    '970443': 'SHB',
    '970426': 'MSB',
    '970448': 'OCB',
}

VN_BANK_SELECTION = [(bin_code, f"{name} — {bin_code}") for bin_code, name in VN_BANK_BINS.items()]

DEFAULT_PAYMENT_METHOD_CODES = {
    'vietqr',
}

COD_PAYMENT_METHOD_CODES = {
    'wbh_cod',
}

NAPAS_GUID = 'A000000727'
NAPAS_SERVICE_ACCOUNT = 'QRIBFTTA'
VND_NUMERIC_CODE = '704'
VN_COUNTRY_CODE = 'VN'
