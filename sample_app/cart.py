"""
cart.py: Shopping cart management, item tracking, subtotal aggregation, and promotional pricing.
Depends on: sample_app.discount
"""
from typing import Dict, List, Optional
from sample_app.discount import calculate_tier_discount, apply_coupon_code, bulk_quantity_discount


class CartItem:
    def __init__(self, item_id: str, name: str, unit_price: float, quantity: int = 1, weight_kg: float = 0.5):
        if unit_price < 0:
            raise ValueError("Unit price cannot be negative")
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if weight_kg < 0:
            raise ValueError("Weight cannot be negative")
        self.item_id = item_id
        self.name = name
        self.unit_price = float(unit_price)
        self.quantity = int(quantity)
        self.weight_kg = float(weight_kg)

    @property
    def line_total(self) -> float:
        return bulk_quantity_discount(self.unit_price, self.quantity)

    @property
    def total_weight(self) -> float:
        return self.weight_kg * self.quantity


class ShoppingCart:
    def __init__(self, max_items: int = 50):
        self.items: Dict[str, CartItem] = {}
        self.max_items = max_items

    def add_item(self, item_id: str, name: str, unit_price: float, quantity: int = 1, weight_kg: float = 0.5) -> None:
        if len(self.items) >= self.max_items and item_id not in self.items:
            raise OverflowError("Shopping cart reached maximum item capacity")
        
        if item_id in self.items:
            new_qty = self.items[item_id].quantity + quantity
            if new_qty <= 0:
                del self.items[item_id]
            else:
                self.items[item_id].quantity = new_qty
        else:
            self.items[item_id] = CartItem(item_id, name, unit_price, quantity, weight_kg)

    def remove_item(self, item_id: str) -> bool:
        if item_id in self.items:
            del self.items[item_id]
            return True
        return False

    def update_quantity(self, item_id: str, quantity: int) -> None:
        if item_id not in self.items:
            raise KeyError(f"Item {item_id} not in cart")
        if quantity <= 0:
            self.remove_item(item_id)
        else:
            self.items[item_id].quantity = quantity

    def calculate_subtotal(self) -> float:
        return round(sum(item.line_total for item in self.items.values()), 2)

    def get_total_weight(self) -> float:
        return round(sum(item.total_weight for item in self.items.values()), 2)

    def get_discounted_subtotal(self, membership_tier: Optional[str] = None, coupon_code: Optional[str] = None) -> float:
        subtotal = self.calculate_subtotal()
        if membership_tier:
            subtotal = calculate_tier_discount(subtotal, membership_tier)
        if coupon_code:
            subtotal = apply_coupon_code(subtotal, coupon_code)
        return round(subtotal, 2)

    def clear(self) -> None:
        self.items.clear()
