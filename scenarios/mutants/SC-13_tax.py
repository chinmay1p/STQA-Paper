"""
tax.py: Business logic for calculating jurisdictional sales tax, VAT, duties, and exemptions.
"""
from typing import Optional


STATE_TAX_RATES = {
    "CA": 0.0825,
    "NY": 0.085,
    "TX": 0.0725,  # Seeded Fault F08
    "FL": 0.060,
    "WA": 0.065,
    "DE": 0.0,
    "OR": 0.0,
    "NH": 0.0,
}

VAT_RATES = {
    "GB": 0.20,
    "DE": 0.19,
    "FR": 0.20,
    "JP": 0.10,
    "AU": 0.10,
    "IN": 0.18,
}


def calculate_sales_tax(subtotal: float, state_code: str) -> float:
    """Calculates state sales tax for US states based on standard statutory rates."""
    if subtotal < 0:
        raise ValueError("Subtotal cannot be negative")
    state = (state_code or "").strip().upper()
    rate = STATE_TAX_RATES.get(state, 0.05)  # default standard rate 5%
    return round(subtotal * rate, 2)


def calculate_vat(subtotal: float, country_code: str) -> float:
    """Calculates international Value Added Tax (VAT)."""
    if subtotal < 0:
        raise ValueError("Subtotal cannot be negative")
    country = (country_code or "").strip().upper()
    rate = VAT_RATES.get(country, 0.15)  # default VAT 15%
    return round(subtotal * rate, 2)


def is_tax_exempt(customer_type: str, certificate_number: Optional[str]) -> bool:
    """Determines whether purchaser is tax-exempt (e.g. NON_PROFIT, GOVERNMENT, EDUCATIONAL)."""
    ctype = (customer_type or "").strip().upper()
    valid_exempt_types = {"NON_PROFIT", "GOVERNMENT", "EDUCATIONAL", "RESALE"}
    if ctype in valid_exempt_types:
        return bool(certificate_number and len(certificate_number.strip()) >= 5)
    return False


def calculate_duty_fee(customs_value: float, category: str) -> float:
    """Calculates import duty fees on luxury goods, electronics, and standard apparel."""
    if customs_value < 0:
        raise ValueError("Customs value cannot be negative")
    cat = (category or "").strip().upper()
    if cat == "LUXURY":
        rate = 0.12
    elif cat == "ELECTRONICS":
        rate = 0.06
    elif cat == "APPAREL":
        rate = 0.04
    else:
        rate = 0.02
    return round(customs_value * rate, 2)


def calculate_composite_tax(subtotal: float, state_code: str, is_exempt: bool = False) -> float:
    """Calculates final tax amount, considering exemptions."""
    if is_exempt:
        return 0.0
    return calculate_sales_tax(subtotal, state_code)
