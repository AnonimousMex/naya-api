"""
Tests para utilidades de seguridad:
- Hashing/verificación de passwords (bcrypt)
- decode_token (con y sin prefijo Bearer)
- get_user_id_from_token (incluyendo casos de fallo que deben dar 401)
"""
import time
from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi import HTTPException

from app.core.settings import settings
from app.utils.security import (
    create_access_token,
    decode_token,
    get_password_hash,
    get_user_id_from_token,
    verify_password,
)


# --- password hashing --------------------------------------------------


class TestPasswordHashing:
    def test_hash_then_verify_succeeds(self):
        h = get_password_hash("MyPassword123")
        assert verify_password("MyPassword123", h) is True

    def test_wrong_password_fails(self):
        h = get_password_hash("MyPassword123")
        assert verify_password("WrongPassword", h) is False

    def test_hash_uses_salt_so_two_hashes_differ(self):
        # bcrypt hashes the same input differently each call
        h1 = get_password_hash("samepass")
        h2 = get_password_hash("samepass")
        assert h1 != h2
        # Both still verify
        assert verify_password("samepass", h1)
        assert verify_password("samepass", h2)

    def test_hash_is_bcrypt_format(self):
        h = get_password_hash("anything")
        # bcrypt hashes start with $2 (e.g. $2b$)
        assert h.startswith("$2")


# --- create_access_token + decode_token --------------------------------


class TestTokenRoundtrip:
    def test_decode_returns_user_payload(self):
        token = create_access_token({"user_id": "abc-123", "email": "x@y.com", "user_type": "PATIENT"})
        decoded = decode_token(token)
        assert decoded is not None
        assert decoded["sub"] == "abc-123"
        assert decoded["user"]["email"] == "x@y.com"
        assert decoded["user"]["user_type"] == "PATIENT"

    def test_decode_strips_bearer_prefix(self):
        token = create_access_token({"user_id": "u-1"})
        decoded = decode_token(f"Bearer {token}")
        assert decoded is not None
        assert decoded["sub"] == "u-1"

    def test_decode_strips_bearer_lowercase(self):
        token = create_access_token({"user_id": "u-2"})
        decoded = decode_token(f"bearer {token}")
        assert decoded is not None

    def test_decode_invalid_token_returns_none(self):
        assert decode_token("not.a.valid.jwt") is None

    def test_decode_empty_returns_none(self):
        assert decode_token("") is None

    def test_decode_expired_returns_none(self):
        # Construye un JWT con exp en el pasado
        expired_payload = {
            "sub": "u-1",
            "user": {"user_id": "u-1"},
            "exp": int(time.time()) - 10,  # expirado hace 10s
            "iat": int(time.time()) - 100,
        }
        expired = jwt.encode(
            expired_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        assert decode_token(expired) is None

    def test_decode_with_wrong_secret_returns_none(self):
        forged = jwt.encode({"sub": "x", "exp": int(time.time()) + 60}, "wrong-secret", algorithm="HS256")
        assert decode_token(forged) is None


# --- get_user_id_from_token --------------------------------------------


class TestGetUserIdFromToken:
    def test_returns_sub_for_valid_token(self):
        token = create_access_token({"user_id": "abc-456"})
        assert get_user_id_from_token(token) == "abc-456"

    def test_works_with_bearer_prefix(self):
        token = create_access_token({"user_id": "abc-789"})
        assert get_user_id_from_token(f"Bearer {token}") == "abc-789"

    def test_invalid_token_raises_401(self):
        with pytest.raises(HTTPException) as exc:
            get_user_id_from_token("garbage")
        assert exc.value.status_code == 401

    def test_empty_token_raises_401(self):
        with pytest.raises(HTTPException) as exc:
            get_user_id_from_token("")
        assert exc.value.status_code == 401

    def test_expired_token_raises_401(self):
        expired = jwt.encode(
            {"sub": "u", "exp": int(time.time()) - 10},
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        with pytest.raises(HTTPException) as exc:
            get_user_id_from_token(expired)
        assert exc.value.status_code == 401

    def test_token_without_sub_raises_401(self):
        # JWT válido pero sin `sub`
        payload_no_sub = {
            "user": {"foo": "bar"},
            "exp": int(time.time()) + 60,
        }
        no_sub = jwt.encode(
            payload_no_sub, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        with pytest.raises(HTTPException) as exc:
            get_user_id_from_token(no_sub)
        assert exc.value.status_code == 401


class TestAccessTokenExpiry:
    def test_default_expiry_is_in_the_future(self):
        token = create_access_token({"user_id": "u"})
        decoded = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        assert decoded["exp"] > int(time.time())

    def test_custom_expiry_is_respected(self):
        delta = timedelta(seconds=30)
        token = create_access_token({"user_id": "u"}, expires_delta=delta)
        decoded = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        # exp debe estar entre ahora+25s y ahora+35s (margen para latencia del test)
        now = int(time.time())
        assert now + 25 <= decoded["exp"] <= now + 35
