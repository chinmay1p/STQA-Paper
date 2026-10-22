"""
Unit tests for sample_app/authentication.py
"""
import pytest
from sample_app.authentication import (
    sanitize_username,
    validate_password_strength,
    generate_session_token,
    verify_session_token,
    check_user_permission,
)


def test_username_sanitization():
    assert sanitize_username("  John_Doe123  ") == "john_doe123"
    assert sanitize_username("User@Name!#") == "username"
    with pytest.raises(ValueError):
        sanitize_username("")
    with pytest.raises(ValueError):
        sanitize_username("ab")  # less than 3 chars


def test_password_strength_criteria():
    assert validate_password_strength("ValidP@ssw0rd!") is True
    assert validate_password_strength("short1!") is False  # length < 8
    assert validate_password_strength("nouppercase123!") is False
    assert validate_password_strength("NOLOWERCASE123!") is False
    assert validate_password_strength("NoDigitsHere!@#") is False
    assert validate_password_strength("NoSymbols12345") is False


def test_session_token_generation():
    token = generate_session_token(42, "secret_key_123")
    assert isinstance(token, str)
    assert len(token) == 64  # SHA-256 hex string length
    with pytest.raises(ValueError):
        generate_session_token(-1, "salt")
    with pytest.raises(ValueError):
        generate_session_token(42, "")


def test_session_token_verification():
    token = generate_session_token(101, "my_salt_xyz")
    assert verify_session_token(token, 101, "my_salt_xyz") is True
    assert verify_session_token(token, 102, "my_salt_xyz") is False
    assert verify_session_token("invalid_token", 101, "my_salt_xyz") is False
    assert verify_session_token(token, 101, "wrong_salt") is False


def test_rbac_permissions():
    assert check_user_permission("ADMIN", "delete") is True
    assert check_user_permission("ADMIN", "manage_users") is True
    assert check_user_permission("MANAGER", "delete") is False
    assert check_user_permission("MANAGER", "refund") is True
    assert check_user_permission("CUSTOMER", "checkout") is True
    assert check_user_permission("CUSTOMER", "refund") is False
    assert check_user_permission("GUEST", "read") is True
    assert check_user_permission("GUEST", "checkout") is False
