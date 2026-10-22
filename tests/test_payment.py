"""
Unit tests for sample_app/payment.py
"""
import pytest
from sample_app.payment import (
    validate_luhn_checksum,
    calculate_gateway_fee,
    convert_currency,
    process_payment_settlement,
)


def test_luhn_algorithm_validation():
    # Standard valid test card numbers (Luhn compliant, >= 13 digits)
    assert validate_luhn_checksum("4000001234567899") is True
    assert validate_luhn_checksum("453201511283034") is True
    # Invalid card number (tampered last digit)
    assert validate_luhn_checksum("4000001234567898") is False
    # Too short (< 13 digits)
    assert validate_luhn_checksum("12345") is False
    # None or empty
    assert validate_luhn_checksum("") is False


def test_gateway_fee_models():
    # Credit Card: 2.9% + $0.30 -> on $100: 2.90 + 0.30 = $3.20
    assert calculate_gateway_fee(100.0, "CREDIT_CARD") == 3.20
    # Debit Card: 1.5% + $0.20 -> on $100: 1.50 + 0.20 = $1.70
    assert calculate_gateway_fee(100.0, "DEBIT_CARD") == 1.70
    # PayPal: 3.4% + $0.49 -> on $100: 3.40 + 0.49 = $3.89
    assert calculate_gateway_fee(100.0, "PAYPAL") == 3.89
    # Crypto: 1.0% + $0.00 -> on $100: $1.00
    assert calculate_gateway_fee(100.0, "CRYPTO") == 1.00
    with pytest.raises(ValueError):
        calculate_gateway_fee(-50.0, "CREDIT_CARD")


def test_fx_currency_conversion():
    # 100 USD to USD = 100
    assert convert_currency(100.0, "USD", "USD") == 100.0
    # 100 EUR = 108 USD. 108 USD / 1.0 = 108.0
    assert convert_currency(100.0, "EUR", "USD") == 108.0
    with pytest.raises(ValueError):
        convert_currency(100.0, "XYZ", "USD")


def test_payment_settlement_success():
    # Valid Luhn card (16 digits)
    valid_card = "4000001234567899"
    res = process_payment_settlement(100.0, "USD", "CREDIT_CARD", valid_card)
    assert res["success"] is True
    assert res["gross_amount"] == 100.0
    assert res["fee"] == 3.20
    assert res["net_settled"] == 96.80
    assert res["currency"] == "USD"


def test_payment_settlement_failure():
    invalid_card = "4000001234567898"
    res = process_payment_settlement(100.0, "USD", "CREDIT_CARD", invalid_card)
    assert res["success"] is False
    assert "Invalid card" in res["error"]
    
    with pytest.raises(ValueError):
        process_payment_settlement(-50.0, "USD", "CREDIT_CARD", "4000001234567899")

