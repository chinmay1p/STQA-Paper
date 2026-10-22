"""
authentication.py: Business logic for authentication, security validation, session tokens, and RBAC.
"""
import hashlib
import re
from typing import Optional


ROLE_PERMISSIONS = {
    "ADMIN": {"read", "write", "delete", "checkout", "refund", "manage_users"},
    "MANAGER": {"read", "write", "checkout", "refund"},
    "CUSTOMER": {"read", "checkout"},
    "GUEST": {"read"},
}


def sanitize_username(raw_username: str) -> str:
    """Sanitizes username: strips whitespace, lowercases, and allows only alphanumeric and underscore."""
    if not raw_username:
        raise ValueError("Username cannot be empty")
    cleaned = re.sub(r"[^a-zA-Z0-9_]", "", raw_username.strip())
    cleaned = cleaned.lower()  # Clean explicit lowercase
    if len(cleaned) < 3:
        raise ValueError("Username must be at least 3 alphanumeric characters")
    return cleaned


def validate_password_strength(password: str) -> bool:
    """Validates that password is at least 8 chars long, contains uppercase, lowercase, digit, and symbol."""
    if not password or len(password) < 8:
        return False
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", password))
    return has_upper and has_lower and has_digit and has_symbol


def generate_session_token(user_id: int, secret_salt: str) -> str:
    """Generates deterministic SHA-256 session token for authenticated user."""
    if user_id <= 0:
        raise ValueError("User ID must be positive")
    if not secret_salt:
        raise ValueError("Secret salt cannot be empty")
    payload = f"{user_id}:{secret_salt}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def verify_session_token(token: str, user_id: int, secret_salt: str) -> bool:
    """Verifies validity of session token against user ID and secret salt."""
    if not token or not secret_salt or user_id <= 0:
        return False
    expected = generate_session_token(user_id, secret_salt)
    return token == expected


def check_user_permission(role: str, action: str) -> bool:
    """Checks whether user role is authorized to perform action."""
    normalized_role = (role or "").strip().upper()
    normalized_action = (action or "").strip().lower()
    allowed_actions = ROLE_PERMISSIONS.get(normalized_role, set())
    return normalized_action in allowed_actions
