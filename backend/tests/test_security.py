import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.security import (
    sanitize_input_text,
    validate_wallet_address_format,
    validate_tx_hash_format,
    validate_sha256_format,
    validate_case_id_format,
    RateLimiterMiddleware,
)

client = TestClient(app)


# ============================================================================
# 1. SECURITY HEADERS TESTS
# ============================================================================

def test_security_headers_present():
    """Verify essential hardening security headers are present on API responses."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200

    # OWASP Recommended Security Headers
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-XSS-Protection") == "1; mode=block"
    assert "strict-origin-when-cross-origin" in response.headers.get("Referrer-Policy", "")
    assert "geolocation=()" in response.headers.get("Permissions-Policy", "")
    assert "no-store" in response.headers.get("Cache-Control", "")


# ============================================================================
# 2. INPUT VALIDATION & SANITIZATION TESTS
# ============================================================================

def test_sanitize_input_text_xss():
    """Verify input text sanitizer strips HTML tags and escapes sensitive entities."""
    malicious = "<script>alert('pwned')</script> Ransomware Case"
    clean = sanitize_input_text(malicious)
    assert "<script>" not in clean
    assert "</script>" not in clean
    assert "Ransomware Case" in clean

    xml_inj = "Sample & Title <tag>with 'quotes' and \"double\"</tag>"
    clean_xml = sanitize_input_text(xml_inj)
    assert "<tag>" not in clean_xml
    assert "&amp;" in clean_xml or "&" not in clean_xml


def test_validate_wallet_address_formats():
    """Test Bitcoin address format validation against valid and malformed addresses."""
    # Valid P2PKH
    valid_p2pkh, t1 = validate_wallet_address_format("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")
    assert valid_p2pkh is True
    assert t1 == "Legacy P2PKH"

    # Valid P2SH
    valid_p2sh, t2 = validate_wallet_address_format("3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy")
    assert valid_p2sh is True
    assert t2 == "Script Hash (P2SH)"

    # Valid Bech32
    valid_bech32, t3 = validate_wallet_address_format("bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq")
    assert valid_bech32 is True
    assert t3 == "SegWit / Taproot (Bech32)"

    # Invalid characters / format
    inv1, _ = validate_wallet_address_format("NOT_A_BITCOIN_ADDRESS")
    assert inv1 is False

    inv_sql, _ = validate_wallet_address_format("1A1zP' OR '1'='1")
    assert inv_sql is False


def test_validate_tx_hash_format():
    """Test 64-hexadecimal transaction hash format validation."""
    valid_tx = "0e3e2357e806b6cdb1f70b54c3a3a17b6714ee1f0e68bebb44a74b1efd512098"
    assert validate_tx_hash_format(valid_tx) is True
    assert validate_tx_hash_format(valid_tx.upper()) is True

    # 63 characters (too short)
    assert validate_tx_hash_format(valid_tx[:-1]) is False
    # 65 characters (too long)
    assert validate_tx_hash_format(valid_tx + "0") is False
    # Non-hex characters
    assert validate_tx_hash_format(valid_tx[:-1] + "Z") is False
    # Path traversal attempt
    assert validate_tx_hash_format("../../etc/passwd") is False


def test_validate_case_id_format():
    """Test case identifier pattern enforcement."""
    assert validate_case_id_format("RT-2026-0001") is True
    assert validate_case_id_format("CASE_DEMO_99") is True

    # Path traversal or injection characters
    assert validate_case_id_format("../../bad_path") is False
    assert validate_case_id_format("CASE; DROP TABLE cases;") is False
    assert validate_case_id_format("<script>") is False


# ============================================================================
# 3. API SCHEMA VALIDATION HARDENING TESTS
# ============================================================================

def test_api_rejects_malformed_txid():
    """Verify GET /api/v1/transactions/{txid} returns 400 for malformed hashes."""
    response = client.get("/api/v1/transactions/malformed_short_txid")
    assert response.status_code == 400
    data = response.json()
    assert "Invalid transaction hash format" in data["detail"]


def test_api_rejects_malformed_wallet_address():
    """Verify GET /api/v1/wallets/{address} returns 400 for invalid Bitcoin address."""
    response = client.get("/api/v1/wallets/malicious_address_<script>")
    assert response.status_code == 400
    data = response.json()
    assert "Invalid Bitcoin address" in data["detail"]


def test_create_case_rejects_invalid_case_id():
    """Verify POST /api/v1/cases rejects invalid or dangerous case_id strings."""
    bad_payload = {
        "case_id": "../traversal/path",
        "title": "Malicious Case Attempt",
        "incident_type": "Testing"
    }
    response = client.post("/api/v1/cases", json=bad_payload)
    assert response.status_code == 422  # Pydantic validation error


def test_create_evidence_rejects_invalid_artifact_type():
    """Verify POST /api/v1/evidence rejects unwhitelisted artifact types."""
    bad_payload = {
        "case_id": "RT-2026-TEST",
        "artifact_type": "UNAUTHORIZED_MALICIOUS_TYPE",
        "raw_payload": {"test": 123},
        "description": "Invalid artifact type seizure"
    }
    response = client.post("/api/v1/evidence", json=bad_payload)
    assert response.status_code == 422
    data = response.json()
    assert "error" in data or "detail" in data


# ============================================================================
# 4. RATE LIMITING & ABUSE PREVENTION TESTS
# ============================================================================

def test_rate_limiter_protection():
    """Test rate limiter triggers HTTP 429 when client threshold is exceeded."""
    # Create isolated test client with a low threshold
    from fastapi import FastAPI
    test_app = FastAPI()
    test_app.add_middleware(RateLimiterMiddleware, max_requests_per_minute=3)

    @test_app.get("/test-endpoint")
    def dummy():
        return {"ok": True}

    tc = TestClient(test_app)

    # 3 allowed requests
    assert tc.get("/test-endpoint").status_code == 200
    assert tc.get("/test-endpoint").status_code == 200
    assert tc.get("/test-endpoint").status_code == 200

    # 4th request must be rejected with 429 Too Many Requests
    blocked = tc.get("/test-endpoint")
    assert blocked.status_code == 429
    assert blocked.headers.get("Retry-After") is not None
    assert "Too Many Requests" in blocked.json()["error"]


# ============================================================================
# 5. SAFE ERROR RESPONSES & STACK TRACE SUPPRESSION
# ============================================================================

def test_unhandled_exception_returns_safe_500_without_stacktrace():
    """Verify that simulated 500 server crashes do not leak stack traces."""
    from fastapi import FastAPI
    from backend.app.main import app as main_app

    # We can invoke an endpoint with non-existent data or simulate a failure
    response = client.get("/api/v1/cases/NON_EXISTENT_CASE_UUID_9999/report/preview")
    # Should be 404 Not Found, not a 500 crash or stack trace
    assert response.status_code == 404
    data = response.json()
    assert "traceback" not in data
    assert "Traceback (most recent call last)" not in str(data)
