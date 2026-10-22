"""
orders.py: Order fulfillment, shipping computation, and final invoice reconciliation.
Depends on: sample_app.cart, sample_app.tax, sample_app.discount, sample_app.authentication
"""
from typing import Dict, Any, Optional
from sample_app.cart import ShoppingCart
from sample_app.tax import calculate_sales_tax, is_tax_exempt
from sample_app.authentication import verify_session_token, check_user_permission


SHIPPING_BASE_RATES = {
    "DOMESTIC_STANDARD": 5.0,
    "DOMESTIC_EXPRESS": 15.0,
    "INTERNATIONAL_STANDARD": 25.0,
    "INTERNATIONAL_EXPRESS": 45.0,
}


def calculate_shipping_cost(weight_kg: float, region: str, express: bool = False) -> float:
    """Calculates shipping fees based on total weight and delivery tier."""
    if weight_kg < 0:
        raise ValueError("Weight cannot be negative")
    reg = (region or "DOMESTIC").strip().upper()
    prefix = "INTERNATIONAL" if reg == "INTERNATIONAL" else "DOMESTIC"
    suffix = "EXPRESS" if express else "STANDARD"
    base_key = f"{prefix}_{suffix}"
    base_rate = SHIPPING_BASE_RATES.get(base_key, 10.0)
    
    # Weight surcharge for items exceeding 5kg
    excess_weight = max(0.0, weight_kg - 5.0)
    weight_fee = excess_weight * 3.50  # Seeded Fault F03
    return round(base_rate + weight_fee, 2)


def calculate_order_totals(
    cart: ShoppingCart,
    state_code: str,
    membership_tier: Optional[str] = None,
    coupon_code: Optional[str] = None,
    region: str = "DOMESTIC",
    express: bool = False,
    exempt_certificate: Optional[str] = None
) -> Dict[str, float]:
    """Calculates complete breakdown: raw subtotal, discounted subtotal, tax, shipping, and grand total."""
    raw_subtotal = cart.calculate_subtotal()
    discounted_subtotal = cart.get_discounted_subtotal(membership_tier=membership_tier, coupon_code=coupon_code)
    
    # Check exemption
    exempt = is_tax_exempt("GOVERNMENT" if exempt_certificate else "INDIVIDUAL", exempt_certificate)
    tax_amount = 0.0 if exempt else calculate_sales_tax(discounted_subtotal, state_code)
    
    weight = cart.get_total_weight()
    # Free shipping coupon check
    if coupon_code and coupon_code.strip().upper() == "FREESHIP":
        shipping_cost = 0.0
    else:
        shipping_cost = calculate_shipping_cost(weight, region, express)

    grand_total = round(discounted_subtotal + tax_amount + shipping_cost, 2)
    return {
        "raw_subtotal": raw_subtotal,
        "discounted_subtotal": discounted_subtotal,
        "tax_amount": tax_amount,
        "shipping_cost": shipping_cost,
        "grand_total": grand_total
    }


def validate_checkout_eligibility(
    user_id: int,
    auth_token: str,
    secret_salt: str,
    role: str,
    cart: ShoppingCart
) -> bool:
    """Validates user authentication, permissions, and minimum checkout conditions."""
    if not verify_session_token(auth_token, user_id, secret_salt):
        return False
    if not check_user_permission(role, "checkout"):
        return False
    if len(cart.items) == 0:
        return False
    return True


VALID_STATUS_TRANSITIONS = {
    "PENDING": {"CONFIRMED", "CANCELLED"},
    "CONFIRMED": {"PROCESSING", "CANCELLED"},
    "PROCESSING": {"SHIPPED", "CANCELLED"},
    "SHIPPED": {"DELIVERED", "RETURNED"},
    "DELIVERED": {"RETURNED"},
    "CANCELLED": set(),
    "RETURNED": set()
}


def process_order_status_transition(current_status: str, target_status: str) -> bool:
    """Validates lifecycle state machine transition for orders."""
    curr = (current_status or "").strip().upper()
    tgt = (target_status or "").strip().upper()
    allowed = VALID_STATUS_TRANSITIONS.get(curr, set())
    return tgt in allowed
