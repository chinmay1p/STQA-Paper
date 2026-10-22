"""
Unit tests for sample_app/tax.py
"""
import pytest
from sample_app.tax import (
    calculate_sales_tax,
    calculate_vat,
    is_tax_exempt,
    calculate_duty_fee,
    calculate_composite_tax,
)


def test_sales_tax_jurisdictions():
    assert calculate_sales_tax(100.0, "CA") == 8.25
    assert calculate_sales_tax(100.0, "NY") == 8.50
    assert calculate_sales_tax(100.0, "TX") == 6.25
    assert calculate_sales_tax(100.0, "DE") == 0.00
    assert calculate_sales_tax(100.0, "UNKNOWN") == 5.00
    with pytest.raises(ValueError):
        calculate_sales_tax(-10.0, "CA")


def test_vat_calculations():
    assert calculate_vat(100.0, "GB") == 20.00
    assert calculate_vat(100.0, "DE") == 19.00
    assert calculate_vat(100.0, "JP") == 10.00
    assert calculate_vat(100.0, "IN") == 18.00
    assert calculate_vat(100.0, "UNKNOWN") == 15.00
    with pytest.raises(ValueError):
        calculate_vat(-50.0, "GB")


def test_tax_exemption_rules():
    assert is_tax_exempt("GOVERNMENT", "GOV-98765") is True
    assert is_tax_exempt("NON_PROFIT", "NP-12345") is True
    assert is_tax_exempt("EDUCATIONAL", "EDU-4421") is True
    assert is_tax_exempt("RESALE", "RES-99881") is True
    assert is_tax_exempt("INDIVIDUAL", "IND-12345") is False
    assert is_tax_exempt("GOVERNMENT", "") is False
    assert is_tax_exempt("GOVERNMENT", "123") is False  # too short


def test_duty_fee_categories():
    assert calculate_duty_fee(1000.0, "LUXURY") == 120.0
    assert calculate_duty_fee(1000.0, "ELECTRONICS") == 60.0
    assert calculate_duty_fee(1000.0, "APPAREL") == 40.0
    assert calculate_duty_fee(1000.0, "GENERAL") == 20.0
    with pytest.raises(ValueError):
        calculate_duty_fee(-100.0, "LUXURY")


def test_composite_tax_exempt_toggle():
    assert calculate_composite_tax(100.0, "CA", is_exempt=False) == 8.25
    assert calculate_composite_tax(100.0, "CA", is_exempt=True) == 0.0
    assert calculate_composite_tax(200.0, "NY", is_exempt=True) == 0.0
