"""
Unit tests for sample_app/discount.py
"""
import pytest
from sample_app.discount import (
    calculate_tier_discount,
    apply_coupon_code,
    bulk_quantity_discount,
    calculate_seasonal_discount,
    validate_discount_cap,
)


def test_discount_tier_rates():
    assert calculate_tier_discount(100.0, "BRONZE") == 95.0
    assert calculate_tier_discount(100.0, "SILVER") == 90.0
    assert calculate_tier_discount(100.0, "GOLD") == 80.0
    assert calculate_tier_discount(100.0, "PLATINUM") == 70.0
    assert calculate_tier_discount(100.0, "NONE") == 100.0
    with pytest.raises(ValueError):
        calculate_tier_discount(-50.0, "GOLD")


def test_discount_coupons():
    assert apply_coupon_code(100.0, "SAVE10") == 90.0
    assert apply_coupon_code(5.0, "SAVE10") == 0.0
    assert apply_coupon_code(100.0, "SAVE20") == 80.0
    assert apply_coupon_code(200.0, "HALFPRICE") == 100.0
    assert apply_coupon_code(100.0, "FREESHIP") == 100.0
    assert apply_coupon_code(100.0, None) == 100.0
    with pytest.raises(ValueError):
        apply_coupon_code(100.0, "BOGUS_PROMO")


def test_discount_bulk_quantities():
    assert bulk_quantity_discount(10.0, 0) == 0.0
    assert bulk_quantity_discount(10.0, 5) == 50.0  # no discount
    assert bulk_quantity_discount(10.0, 10) == 95.0  # 5% discount
    assert bulk_quantity_discount(10.0, 50) == 425.0  # 15% discount
    assert bulk_quantity_discount(10.0, 100) == 750.0  # 25% discount
    with pytest.raises(ValueError):
        bulk_quantity_discount(-10.0, 5)


def test_discount_seasonal_promotions():
    assert calculate_seasonal_discount(100.0, False, False) == 100.0
    assert calculate_seasonal_discount(100.0, True, False) == 90.0
    assert calculate_seasonal_discount(100.0, False, True) == 85.0
    assert calculate_seasonal_discount(100.0, True, True) == 78.0
    with pytest.raises(ValueError):
        calculate_seasonal_discount(-10.0, True, True)


def test_discount_cap_boundary():
    # 70% max discount means minimum allowable price is 30.0 for original 100.0
    assert validate_discount_cap(100.0, 50.0, 0.70) == 50.0
    assert validate_discount_cap(100.0, 20.0, 0.70) == 30.0  # capped at floor
    assert validate_discount_cap(100.0, 30.0, 0.70) == 30.0
    with pytest.raises(ValueError):
        validate_discount_cap(100.0, 120.0)
    with pytest.raises(ValueError):
        validate_discount_cap(-10.0, 5.0)
