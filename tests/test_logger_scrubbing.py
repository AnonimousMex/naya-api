"""
Tests para el scrubbing en el logger.

Garantizan que NUNCA dejamos pasar a logs:
- claves sensibles (password, token, authorization, secret, jwt)
- tokens completos dentro de strings con prefijo Bearer
"""
from app.core.logger import _BEARER_RE, _scrub, _truncate_token


class TestTruncateToken:
    def test_short_token_becomes_stars(self):
        assert _truncate_token("abc") == "***"
        assert _truncate_token("12345678") == "***"  # 8 chars exactos → ***

    def test_long_token_keeps_first_6(self):
        token = "abcdef" + "x" * 50
        result = _truncate_token(token)
        assert result.startswith("abcdef")
        assert "(+50)" in result


class TestScrubDict:
    def test_redacts_password(self):
        result = _scrub({"username": "u", "password": "secret123"})
        assert result["password"] == "***REDACTED***"
        assert result["username"] == "u"

    def test_redacts_authorization(self):
        assert _scrub({"authorization": "anything"})["authorization"] == "***REDACTED***"

    def test_redacts_token_variants(self):
        for key in ("token", "access_token", "refresh_token", "jwt", "secret", "api_key", "apikey"):
            assert _scrub({key: "data"})[key] == "***REDACTED***"

    def test_case_insensitive(self):
        assert _scrub({"PASSWORD": "x"})["PASSWORD"] == "***REDACTED***"
        assert _scrub({"Token": "x"})["Token"] == "***REDACTED***"

    def test_recursive_nested_dict(self):
        result = _scrub({"user": {"name": "u", "password": "s"}, "metadata": {"token": "t"}})
        assert result["user"]["password"] == "***REDACTED***"
        assert result["user"]["name"] == "u"
        assert result["metadata"]["token"] == "***REDACTED***"


class TestScrubList:
    def test_scrubs_dicts_inside_list(self):
        result = _scrub([{"password": "x"}, {"name": "ok"}])
        assert result[0]["password"] == "***REDACTED***"
        assert result[1]["name"] == "ok"


class TestScrubString:
    def test_truncates_bearer_token_in_string(self):
        msg = "Authorization header: Bearer abcdef1234567890xyz"
        result = _scrub(msg)
        assert "abcdef1234567890xyz" not in result
        assert "Bearer" in result
        assert "abcdef" in result  # primeros 6 chars sí quedan

    def test_passes_through_non_token_strings(self):
        s = "hello world without secrets"
        assert _scrub(s) == s

    def test_handles_multiple_bearer_tokens(self):
        s = "old=Bearer firsttoken12345 new=Bearer secondtoken67890"
        result = _scrub(s)
        assert "firsttoken12345" not in result
        assert "secondtoken67890" not in result


class TestScrubEdgeCases:
    def test_empty_inputs(self):
        assert _scrub({}) == {}
        assert _scrub([]) == []
        assert _scrub("") == ""

    def test_non_string_values_unchanged(self):
        assert _scrub({"count": 42, "active": True}) == {"count": 42, "active": True}

    def test_passes_through_none(self):
        # None se devuelve como None (no pasa por ninguna rama de string/dict/list)
        assert _scrub(None) is None


class TestBearerRegex:
    def test_matches_bearer_with_jwt_chars(self):
        assert _BEARER_RE.search("Bearer eyJhbG.abc-_.123") is not None

    def test_case_insensitive_match(self):
        assert _BEARER_RE.search("bearer xyz123") is not None
        assert _BEARER_RE.search("BEARER xyz123") is not None
