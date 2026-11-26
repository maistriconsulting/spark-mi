from app.core.security import create_access_token, decode_access_token, hash_password, verify_password


def test_password_hash_is_not_plaintext_and_verifies():
    hashed = hash_password("a-long-test-password")
    assert hashed != "a-long-test-password"
    assert verify_password("a-long-test-password", hashed)
    assert not verify_password("wrong-password", hashed)


def test_access_token_contains_user_and_tenant_context():
    token = create_access_token(user_id=12, tenant_id=34)
    payload = decode_access_token(token)
    assert payload["sub"] == "12"
    assert payload["tenant_id"] == 34
    assert payload["type"] == "access"
