"""
Property-based and unit tests for enhanced EncryptionUtility
"""

import pytest
from hypothesis import given, strategies as st
from cryptography.fernet import Fernet

from servers.utils.encryption import EncryptionUtility
from servers.utils.exceptions import (
    InvalidKeyFormatError,
    MissingKeyError,
    InvalidPlaintextError,
    EncryptionFailedError,
    KeyMismatchError,
    CorruptedDataError,
    InvalidCiphertextError,
)


# Feature: rcon-encryption-refactor, Property 8: Encryption round-trip
@given(st.text(min_size=1, max_size=1000))
def test_encryption_round_trip(plaintext):
    """
    Property 8: Encryption round-trip
    For any plaintext password string, encrypting then decrypting should return the original plaintext value.
    """
    # Generate a valid key for testing
    key = Fernet.generate_key()
    util = EncryptionUtility(key=key)
    
    # Encrypt then decrypt
    encrypted = util.encrypt(plaintext)
    decrypted = util.decrypt(encrypted)
    
    # Should get back the original
    assert decrypted == plaintext, f"Round-trip failed: {plaintext} != {decrypted}"
    
    # verify_encryption should also work
    assert util.verify_encryption(plaintext)


# Feature: rcon-encryption-refactor, Property 9: Key mismatch detection
@given(st.text(min_size=1, max_size=100))
def test_key_mismatch_detection(plaintext):
    """
    Property 9: Key mismatch detection
    For any plaintext encrypted with one key, attempting to decrypt with a different key
    should raise a KeyMismatchError with a clear message.
    """
    # Generate two different keys
    key1 = Fernet.generate_key()
    key2 = Fernet.generate_key()
    
    # Encrypt with key1
    util1 = EncryptionUtility(key=key1)
    encrypted = util1.encrypt(plaintext)
    
    # Try to decrypt with key2
    util2 = EncryptionUtility(key=key2)
    
    with pytest.raises((KeyMismatchError, CorruptedDataError)) as exc_info:
        util2.decrypt(encrypted)
    
    # Error message should be clear
    error_message = str(exc_info.value)
    assert len(error_message) > 0, "Error message should not be empty"
    
    # can_decrypt should return False
    assert not util2.can_decrypt(encrypted)


# Feature: rcon-encryption-refactor, Property 10: Corrupted ciphertext detection
@given(st.binary(min_size=10, max_size=100))
def test_corrupted_ciphertext_detection(random_bytes):
    """
    Property 10: Corrupted ciphertext detection
    For any corrupted ciphertext (random bytes), decryption should raise an exception with a clear message.
    """
    key = Fernet.generate_key()
    util = EncryptionUtility(key=key)
    
    # Try to decrypt random bytes (corrupted data)
    with pytest.raises((KeyMismatchError, CorruptedDataError, InvalidCiphertextError)) as exc_info:
        util.decrypt(random_bytes)
    
    # Error message should be clear
    error_message = str(exc_info.value)
    assert len(error_message) > 0, "Error message should not be empty"
    
    # can_decrypt should return False
    assert not util.can_decrypt(random_bytes)


class TestEncryptionUtilityEdgeCases:
    """Unit tests for EncryptionUtility edge cases"""
    
    def test_empty_string_encryption(self):
        """Test that empty string raises InvalidPlaintextError"""
        key = Fernet.generate_key()
        util = EncryptionUtility(key=key)
        
        with pytest.raises(InvalidPlaintextError) as exc_info:
            util.encrypt("")
        
        assert "empty" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()
    
    def test_none_input_encryption(self):
        """Test that None input raises InvalidPlaintextError"""
        key = Fernet.generate_key()
        util = EncryptionUtility(key=key)
        
        with pytest.raises(InvalidPlaintextError):
            util.encrypt(None)
    
    def test_empty_ciphertext_decryption(self):
        """Test that empty ciphertext raises InvalidCiphertextError"""
        key = Fernet.generate_key()
        util = EncryptionUtility(key=key)
        
        with pytest.raises(InvalidCiphertextError) as exc_info:
            util.decrypt(b"")
        
        assert "empty" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()
    
    def test_none_ciphertext_decryption(self):
        """Test that None ciphertext raises InvalidCiphertextError"""
        key = Fernet.generate_key()
        util = EncryptionUtility(key=key)
        
        with pytest.raises(InvalidCiphertextError):
            util.decrypt(None)
    
    def test_invalid_key_initialization(self):
        """Test that invalid key raises InvalidKeyFormatError"""
        with pytest.raises(InvalidKeyFormatError):
            EncryptionUtility(key="invalid-key")
    
    def test_missing_key_initialization(self):
        """Test that missing key raises MissingKeyError"""
        # When key=None, it tries to load from settings
        # We test with empty string instead
        with pytest.raises(MissingKeyError):
            EncryptionUtility(key="")
    
    def test_verify_encryption_with_valid_text(self):
        """Test verify_encryption with valid text"""
        key = Fernet.generate_key()
        util = EncryptionUtility(key=key)
        
        assert util.verify_encryption("test password")
        assert util.verify_encryption("another test 123!@#")
    
    def test_verify_encryption_with_empty_text(self):
        """Test verify_encryption with empty text returns False"""
        key = Fernet.generate_key()
        util = EncryptionUtility(key=key)
        
        assert not util.verify_encryption("")
        assert not util.verify_encryption(None)
    
    def test_can_decrypt_with_valid_ciphertext(self):
        """Test can_decrypt with valid ciphertext"""
        key = Fernet.generate_key()
        util = EncryptionUtility(key=key)
        
        encrypted = util.encrypt("test")
        assert util.can_decrypt(encrypted)
    
    def test_can_decrypt_with_invalid_ciphertext(self):
        """Test can_decrypt with invalid ciphertext returns False"""
        key = Fernet.generate_key()
        util = EncryptionUtility(key=key)
        
        assert not util.can_decrypt(b"invalid")
        assert not util.can_decrypt(b"")
        assert not util.can_decrypt(None)
    
    def test_unicode_password_encryption(self):
        """Test encryption of Unicode passwords"""
        key = Fernet.generate_key()
        util = EncryptionUtility(key=key)
        
        unicode_passwords = [
            "密码123",
            "пароль",
            "🔒🔑password",
            "café_résumé",
        ]
        
        for password in unicode_passwords:
            encrypted = util.encrypt(password)
            decrypted = util.decrypt(encrypted)
            assert decrypted == password


# Feature: rcon-encryption-refactor, Property 14, 15, 16: Error message clarity
class TestErrorMessageClarity:
    """Tests for error message clarity"""
    
    def test_invalid_key_error_message(self):
        """
        Property 14: Invalid key error message clarity
        For any encryption operation with an invalid key, the error message should clearly state
        the encryption key is invalid.
        """
        with pytest.raises(InvalidKeyFormatError) as exc_info:
            EncryptionUtility(key="invalid-key-format")
        
        error_message = str(exc_info.value)
        assert "invalid" in error_message.lower() or "key" in error_message.lower()
        assert "generate_key.py" in error_message
    
    def test_key_mismatch_error_message(self):
        """
        Property 15: Key mismatch error message clarity
        For any decryption failure due to key mismatch, the error message should indicate
        the key may have changed.
        """
        key1 = Fernet.generate_key()
        key2 = Fernet.generate_key()
        
        util1 = EncryptionUtility(key=key1)
        encrypted = util1.encrypt("test")
        
        util2 = EncryptionUtility(key=key2)
        
        with pytest.raises((KeyMismatchError, CorruptedDataError)) as exc_info:
            util2.decrypt(encrypted)
        
        error_message = str(exc_info.value)
        assert any(keyword in error_message.lower() for keyword in ["key", "mismatch", "changed", "different", "decrypt"])
    
    def test_invalid_input_error_message(self):
        """
        Property 16: Invalid input error message clarity
        For any invalid input to encryption, the error message should clearly identify the input problem.
        """
        key = Fernet.generate_key()
        util = EncryptionUtility(key=key)
        
        # Test empty string
        with pytest.raises(InvalidPlaintextError) as exc_info:
            util.encrypt("")
        
        error_message = str(exc_info.value)
        assert "empty" in error_message.lower() or "invalid" in error_message.lower()
        
        # Test None
        with pytest.raises(InvalidPlaintextError) as exc_info:
            util.encrypt(None)
        
        error_message = str(exc_info.value)
        assert "none" in error_message.lower() or "empty" in error_message.lower() or "invalid" in error_message.lower()
