"""
Unit tests for sample_app/cart.py
"""
import pytest
from sample_app.cart import ShoppingCart, CartItem


def test_cart_add_and_accumulate():
    cart = ShoppingCart()
    cart.add_item("item-1", "Mechanical Keyboard", 100.0, 1, weight_kg=1.2)
    cart.add_item("item-2", "Wireless Mouse", 50.0, 2, weight_kg=0.3)
    
    assert len(cart.items) == 2
    assert cart.calculate_subtotal() == 200.0
    
    # Adding more of item-1
    cart.add_item("item-1", "Mechanical Keyboard", 100.0, 1)
    assert cart.items["item-1"].quantity == 2
    assert cart.calculate_subtotal() == 300.0


def test_cart_remove_and_update():
    cart = ShoppingCart()
    cart.add_item("item-A", "USB-C Cable", 15.0, 3)
    assert cart.remove_item("item-A") is True
    assert cart.remove_item("item-nonexistent") is False
    assert len(cart.items) == 0

    cart.add_item("item-B", "Monitor Arm", 80.0, 1)
    cart.update_quantity("item-B", 3)
    assert cart.items["item-B"].quantity == 3
    assert cart.calculate_subtotal() == 240.0
    
    # Update to 0 removes item
    cart.update_quantity("item-B", 0)
    assert len(cart.items) == 0


def test_cart_weight_aggregation():
    cart = ShoppingCart()
    cart.add_item("item-heavy", "Steel Dumbbell", 40.0, 2, weight_kg=10.0)
    cart.add_item("item-light", "Foam Roller", 20.0, 1, weight_kg=0.5)
    assert cart.get_total_weight() == 20.5


def test_cart_capacity_overflow():
    cart = ShoppingCart(max_items=2)
    cart.add_item("i1", "Item 1", 10.0, 1)
    cart.add_item("i2", "Item 2", 10.0, 1)
    with pytest.raises(OverflowError):
        cart.add_item("i3", "Item 3", 10.0, 1)


def test_cart_discounted_subtotal():
    cart = ShoppingCart()
    cart.add_item("laptop", "Developer Laptop", 1000.0, 1)
    
    # Gold tier gives 20% discount -> 800.0
    subtotal_gold = cart.get_discounted_subtotal(membership_tier="GOLD")
    assert subtotal_gold == 800.0
    
    # Gold tier + SAVE10 coupon -> 790.0
    subtotal_both = cart.get_discounted_subtotal(membership_tier="GOLD", coupon_code="SAVE10")
    assert subtotal_both == 790.0
