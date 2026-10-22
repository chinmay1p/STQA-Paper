"""
Unit tests for sample_app/orders.py
"""
import pytest
from sample_app.cart import ShoppingCart
from sample_app.authentication import generate_session_token
from sample_app.orders import (
    calculate_shipping_cost,
    calculate_order_totals,
    validate_checkout_eligibility,
    process_order_status_transition,
)


def test_shipping_cost_calculation():
    # Domestic Standard base is 5.0 (up to 5kg)
    assert calculate_shipping_cost(2.0, "DOMESTIC", express=False) == 5.0
    # Excess weight: 7kg -> 5.0 + (2kg * 2.5) = 10.0
    assert calculate_shipping_cost(7.0, "DOMESTIC", express=False) == 10.0
    # Domestic Express base is 15.0
    assert calculate_shipping_cost(3.0, "DOMESTIC", express=True) == 15.0
    # International Express base is 45.0 + excess weight
    assert calculate_shipping_cost(6.0, "INTERNATIONAL", express=True) == 47.5
    with pytest.raises(ValueError):
        calculate_shipping_cost(-1.0, "DOMESTIC")


def test_order_totals_computation():
    cart = ShoppingCart()
    cart.add_item("item-1", "Desk Lamp", 100.0, 1, weight_kg=2.0)
    
    # State NY: 8.5% tax. Domestic standard: $5 shipping.
    totals = calculate_order_totals(cart, state_code="NY", membership_tier="SILVER")
    # Silver gives 10% off -> subtotal 90.0
    # Tax on 90.0 at 8.5% -> 7.65
    # Shipping -> 5.0
    # Grand total -> 90.0 + 7.65 + 5.0 = 102.65
    assert totals["raw_subtotal"] == 100.0
    assert totals["discounted_subtotal"] == 90.0
    assert totals["tax_amount"] == 7.65
    assert totals["shipping_cost"] == 5.0
    assert totals["grand_total"] == 102.65


def test_checkout_eligibility_checks():
    salt = "secure_test_salt"
    token = generate_session_token(500, salt)
    
    cart = ShoppingCart()
    cart.add_item("prod-1", "Widget", 20.0, 1)
    
    # Valid customer
    assert validate_checkout_eligibility(500, token, salt, "CUSTOMER", cart) is True
    # Wrong token
    assert validate_checkout_eligibility(500, "bad_token", salt, "CUSTOMER", cart) is False
    # Guest role has no checkout permission
    assert validate_checkout_eligibility(500, token, salt, "GUEST", cart) is False
    # Empty cart
    empty_cart = ShoppingCart()
    assert validate_checkout_eligibility(500, token, salt, "CUSTOMER", empty_cart) is False


def test_order_status_state_machine():
    assert process_order_status_transition("PENDING", "CONFIRMED") is True
    assert process_order_status_transition("CONFIRMED", "PROCESSING") is True
    assert process_order_status_transition("PROCESSING", "SHIPPED") is True
    assert process_order_status_transition("SHIPPED", "DELIVERED") is True
    # Invalid transition: PENDING directly to DELIVERED
    assert process_order_status_transition("PENDING", "DELIVERED") is False
    # Terminal state CANCELLED cannot transition
    assert process_order_status_transition("CANCELLED", "CONFIRMED") is False


def test_order_with_tax_exemption_and_free_shipping():
    cart = ShoppingCart()
    cart.add_item("book", "Textbook", 100.0, 1, weight_kg=1.0)
    
    totals = calculate_order_totals(
        cart,
        state_code="CA",
        coupon_code="FREESHIP",
        exempt_certificate="GOV-55443"
    )
    assert totals["tax_amount"] == 0.0
    assert totals["shipping_cost"] == 0.0
    assert totals["grand_total"] == 100.0
