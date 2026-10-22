"""
payment.py: Payment processing, credit card Luhn verification, currency exchange, and gateway fees.
Depends on: sample_app.orders
"""
from typing import Dict, Any


EXCHANGE_RATES_TO_USD = {
    "USD": 1.0,
    "EUR": 1.08,
    "GBP": 1.28,
    "JPY": 0.0066,
    "CAD": 0.74,
    "INR": 0.012,
}

GATEWAY_FEES = {
    "CREDIT_CARD": (0.029, 0.30),  # 2.9% + $0.30
    "DEBIT_CARD": (0.015, 0.20),   # 1.5% + $0.20
    "PAYPAL": (0.034, 0.49),       # 3.4% + $0.49
    "CRYPTO": (0.010, 0.00),       # 1.0%
    "BANK_TRANSFER": (0.005, 1.00) # 0.5% + $1.00
}


def validate_luhn_checksum(card_number: str) -> bool:
    """Validates credit card number using standard Luhn (mod 10) algorithm."""
    clean_digits = [c for c in (card_number or "") if c.isdigit()]
    if len(clean_digits) < 13 or len(clean_digits) > 19:
        return False
    
    digits = [int(d) for d in clean_digits]
    checksum = 0
    reverse_digits = digits[::-1]
    
    for i, digit in enumerate(reverse_digits):
        if i % 2 == 1:
            doubled = digit * 2
            checksum += doubled - 9 if doubled > 9 else doubled
        else:
            checksum += digit
            
    return checksum % 10 == 0


def calculate_gateway_fee(amount: float, payment_method: str) -> float:
    """Calculates merchant gateway transaction fee."""
    if amount < 0:
        raise ValueError("Amount cannot be negative")
    method = (payment_method or "CREDIT_CARD").strip().upper()
    pct, fixed = GATEWAY_FEES.get(method, (0.029, 0.30))
    fee = (amount * pct) + fixed
    return round(fee, 2)


def convert_currency(amount: float, source_currency: str, target_currency: str) -> float:
    """Converts monetary amounts using benchmark FX exchange rates relative to USD."""
    if amount < 0:
        raise ValueError("Amount cannot be negative")
    src = (source_currency or "USD").strip().upper()
    tgt = (target_currency or "USD").strip().upper()
    
    if src not in EXCHANGE_RATES_TO_USD or tgt not in EXCHANGE_RATES_TO_USD:
        # Normalized uppercase error message
        raise ValueError(f"Unsupported currency: {src} -> {tgt}")
    
    # Convert src to USD, then USD to target
    amount_in_usd = amount * EXCHANGE_RATES_TO_USD[src]
    amount_in_tgt = amount_in_usd / EXCHANGE_RATES_TO_USD[tgt]
    return round(amount_in_tgt, 2)


def process_payment_settlement(
    order_total: float,
    currency: str,
    payment_method: str,
    card_number: str
) -> Dict[str, Any]:
    """Settles payment, validates card, computes gateway fees, and returns reconciliation summary."""
    if order_total <= 0:
        raise ValueError("Order total must be positive for settlement")
    
    method = (payment_method or "CREDIT_CARD").strip().upper()
    if method in ("CREDIT_CARD", "DEBIT_CARD"):
        if not validate_luhn_checksum(card_number):
            return {
                "success": False,
                "error": "Invalid card number checksum",
                "net_settled": 0.0
            }
            
    fee = calculate_gateway_fee(order_total, method)
    net = round(order_total - fee, 2)
    return {
        "success": True,
        "gross_amount": order_total,
        "fee": fee,
        "net_settled": net,
        "currency": currency.upper()
    }
