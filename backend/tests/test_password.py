from app.services.password import hash_password, verify_password


class TestPasswordHashing:
    """Tests for password hashing functions"""

    def test_hash_password_returns_different_from_input(self):
        """Test that hashing returns a different string"""
        password = "mysecretpassword"
        hashed = hash_password(password)
        assert hashed != password

    def test_hash_password_is_deterministic_salt(self):
        """Test that hashing the same password twice gives different results"""
        password = "mysecretpassword"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2

    def test_verify_password_correct(self):
        """Test that correct password verifies"""
        password = "mysecretpassword"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test that incorrect password fails verification"""
        password = "mysecretpassword"
        hashed = hash_password(password)
        assert verify_password("wrongpassword", hashed) is False

    def test_verify_password_empty(self):
        """Test that empty password fails against valid hash"""
        password = "mysecretpassword"
        hashed = hash_password(password)
        assert verify_password("", hashed) is False
