from app.auth.security import create_access_token, decode_token, hash_password, verify_password


def test_password_hash_is_one_way_and_verifiable() -> None:
    encoded = hash_password("correct horse battery staple")
    assert encoded.startswith("scrypt$")
    assert verify_password("correct horse battery staple", encoded)
    assert not verify_password("incorrect password", encoded)


def test_access_token_contains_subject_and_roles() -> None:
    token = create_access_token("user-123", ["CUSTOMER"])
    claims = decode_token(token)
    assert claims["sub"] == "user-123"
    assert claims["roles"] == ["CUSTOMER"]
    assert claims["type"] == "access"
