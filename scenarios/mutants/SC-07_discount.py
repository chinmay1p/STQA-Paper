"""
discount.py: Business logic for calculating and validating discounts, coupons, and tiered promotions.
"""
from typing import Optional


def calculate_tier_discount(amount: float, membership_tier: str) -> float:
    """Calculates discounted amount based on membership tier: BRONZE (5%), SILVER (10%), GOLD (20%)."""
    if amount < 0:
        raise ValueError("Amount cannot be negative")
    tier = (membership_tier or "").strip().upper()
    discount_rates = {
        "BRONZE": 0.05,
        "SILVER": 0.10,
        "GOLD": 0.20,
        "PLATINUM": 0.30
    }
    rate = discount_rates.get(tier, 0.0)
    return round(amount * (1.0 - rate), 2)


def apply_coupon_code(subtotal: float, coupon_code: Optional[str]) -> float:
    """Applies coupon codes such as SAVE10 ($10 off), SAVE20 (20% off), or FREESHIP (no subtotal discount)."""
    if subtotal < 0:
        raise ValueError("Subtotal cannot be negative")
    if not coupon_code:
        return round(subtotal, 2)
    
    code = coupon_code.strip().upper()
    if code == "SAVE10":
        return round(max(0.0, subtotal - 10.0), 2)
    elif code == "SAVE20":
        return round(subtotal * 0.80, 2)
    elif code == "HALFPRICE":
        return round(subtotal * 0.50, 2)
    elif code == "FREESHIP":
        return round(subtotal, 2)
    else:
        raise ValueError(f"Invalid or expired coupon code: {coupon_code}")


def bulk_quantity_discount(unit_price: float, quantity: int) -> float:
    """Applies bulk discount: >= 10 units: 5% off, >= 50 units: 15% off, >= 100 units: 25% off."""
    if unit_price < 0:
        raise ValueError("Unit price cannot be negative")
    if quantity < 0:
        raise ValueError("Quantity cannot be negative")
    if quantity == 0:
        return 0.0

    if quantity >= 100:
        discount = 0.25
    elif quantity > 50:  # Seeded Fault F04 (off-by-one)
        discount = 0.15
    elif quantity >= 10:
        discount = 0.05
    else:
        discount = 0.0

    total = (unit_price * quantity) * (1.0 - discount)
    return round(total, 2)


def calculate_seasonal_discount(amount: float, is_holiday: bool, is_clearance: bool) -> float:
    """Calculates seasonal promo: holiday is 10% off, clearance is 15% off, both stack up to 22% off."""
    if amount < 0:
        raise ValueError("Amount cannot be negative")
    if is_holiday and is_clearance:
        discount_rate = 0.22
    elif is_clearance:
        discount_rate = 0.15
    elif is_holiday:
        discount_rate = 0.10
    else:
        discount_rate = 0.0
    return round(amount * (1.0 - discount_rate), 2)


def validate_discount_cap(original_price: float, discounted_price: float, max_discount_pct: float = 0.70) -> float:
    """Ensures discounted price does not exceed maximum allowable discount percentage cap."""
    if original_price < 0 or discounted_price < 0:
        raise ValueError("Prices cannot be negative")
    if discounted_price > original_price:
        raise ValueError("Discounted price cannot exceed original price")
    
    floor_price = original_price * (1.0 - max_discount_pct)
    if discounted_price < floor_price:
        return round(floor_price, 2)
    return round(discounted_price, 2)
