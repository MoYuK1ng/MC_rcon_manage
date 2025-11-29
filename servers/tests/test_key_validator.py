"""
Property-based and unit tests for KeyValidator
"""

import base64
import pytest
from hypothesis import given, strategies as st
from cryptography.fernet import Fernet

from servers.utils.key_validator import KeyValidator


# Feature: rcon-encryption-refactor, Property 1: Valid key detection
@given(st.binary(min_size=32, max_size=32))
def test_valid_key_detection(key_bytes):
    """
    Property 1: Valid key detection
    For any 32-byte value, when properly base64-encoded, it should be recognized as a valid Fernet key.
    """
    # Encode as URL-safe base64 (this is what Fernet.generate_key() does)
    key_string = base64.urlsafe_b64encode(key_bytes).decode('utf-8')
    
    # Validate the key
    is_valid, error_message = KeyValidator.validate_key(key_string)
    
    # Should be valid
    assert is_valid, f"Valid key was rejected: {error_message}"
    assert error_message == "", "Valid key should have empty error message"
    
    # Quick check should also return True
    assert KeyValidator.is_valid_fernet_key(key_string)


# Feature: rcon-encryption-refactor, Property 2: Invalid key error messages
@given(st.one_of(
    st.text(min_size=1, max_size=43),  # Too short
    st.text(min_size=45, max_size=100),  # Too long
    st.just(""),  # Empty
    st.just("not-base64-at-all!!!"),  # Invalid characters
))
def test_invalid_key_error_messages(invalid_key):
    """
    Property 2: Invalid key error messages
    For any invalid key format, validation should fail and provide an error message
    with instructions to run generate_key.py.
    """
    is_valid, error_message = KeyValidator.validate_key(invalid_key)
    
    # Should be invalid
    assert not is_valid, f"Invalid key was accepted: {invalid_key}"
    
    # Error message should contain instructions
    assert "generate_key.py" in error_message, \
        "Error message should mention generate_key.py"
    assert len(error_message) > 0, "Error message should not be empty"
    
    # Quick check should also return False
    assert not KeyValidator.is_valid_fernet_key(invalid_key)


# Feature: rcon-encryption-refactor, Property 3: Invalid base64 detection
@given(st.text(min_size=44, max_size=44).filter(
    lambda s: not all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_=' for c in s) and len(s.strip()) == 44
))
def test_invalid_base64_detection(invalid_base64_key):
    """
    Property 3: Invalid base64 detection
    For any 44-character string containing invalid base64 characters,
    the validator should detect it and provide a specific error about invalid encoding.
    """
    is_valid, error_message = KeyValidator.validate_key(invalid_base64_key)
    
    # Should be invalid
    assert not is_valid, f"Invalid base64 key was accepted: {invalid_base64_key}"
    
    # Error message should mention base64, encoding, or invalid key
    assert any(keyword in error_message.lower() for keyword in ["base64", "encoding", "invalid", "decode"]), \
        f"Error message should mention validation issue, got: {error_message}"
    assert "generate_key.py" in error_message, \
        "Error message should mention generate_key.py"


class TestKeyValidatorEdgeCases:
    """Unit tests for KeyValidator edge cases"""
    
    def test_none_key(self):
        """Test that None key is rejected with clear message"""
        is_valid, error_message = KeyValidator.validate_key(None)
        
        assert not is_valid
        assert "MISSING_KEY" in error_message
        assert "generate_key.py" in error_message
    
    def test_empty_string_key(self):
        """Test that empty string is rejected"""
        is_valid, error_message = KeyValidator.validate_key("")
        
        assert not is_valid
        assert "MISSING_KEY" in error_message or "empty" in error_message.lower()
        assert "generate_key.py" in error_message
    
    def test_whitespace_only_key(self):
        """Test that whitespace-only string is rejected"""
        is_valid, error_message = KeyValidator.validate_key("   \t\n  ")
        
        assert not is_valid
        assert "generate_key.py" in error_message
    
    def test_wrong_length_key(self):
        """Test that keys with wrong length are rejected"""
        # Too short
        is_valid, error_message = KeyValidator.validate_key("abc123")
        assert not is_valid
        assert "length" in error_message.lower()
        
        # Too long
        is_valid, error_message = KeyValidator.validate_key("a" * 100)
        assert not is_valid
        assert "length" in error_message.lower()
    
    def test_invalid_padding(self):
        """Test that keys with invalid padding are rejected"""
        # Valid base64 but wrong padding for Fernet
        invalid_key = "YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXoxMjM0NTY"  # 43 chars
        is_valid, error_message = KeyValidator.validate_key(invalid_key)
        
        assert not is_valid
        assert "generate_key.py" in error_message
    
    def test_valid_generated_key(self):
        """Test that a properly generated Fernet key is valid"""
        # Generate a real Fernet key
        key = Fernet.generate_key().decode('utf-8')
        
        is_valid, error_message = KeyValidator.validate_key(key)
        
        assert is_valid
        assert error_message == ""
        assert KeyValidator.is_valid_fernet_key(key)
    
    def test_bytes_key_input(self):
        """Test that bytes input is handled correctly"""
        # Valid key as bytes
        key = Fernet.generate_key()
        is_valid, error_message = KeyValidator.validate_key(key)
        
        assert is_valid
        assert error_message == ""
    
    def test_invalid_utf8_bytes(self):
        """Test that invalid UTF-8 bytes are rejected"""
        invalid_bytes = b'\xff\xfe\xfd\xfc'
        is_valid, error_message = KeyValidator.validate_key(invalid_bytes)
        
        assert not is_valid
        assert "UTF-8" in error_message or "decode" in error_message.lower()
    
    def test_get_key_info_valid_key(self):
        """Test get_key_info with a valid key"""
        key = Fernet.generate_key().decode('utf-8')
        info = KeyValidator.get_key_info(key)
        
        assert info['length'] == 44
        assert info['encoding'] == 'utf8'
        assert info['is_url_safe'] is True
        assert info['decoded_length'] == 32
    
    def test_get_key_info_none(self):
        """Test get_key_info with None"""
        info = KeyValidator.get_key_info(None)
        
        assert info['length'] == 0
        assert info['encoding'] == 'none'
        assert info['is_url_safe'] is False
        assert info['decoded_length'] is None
    
    def test_get_key_info_invalid_base64(self):
        """Test get_key_info with invalid base64"""
        info = KeyValidator.get_key_info("not-valid-base64!!!")
        
        assert info['length'] > 0
        assert info['is_url_safe'] is False
        # Note: Some invalid base64 strings may still decode (base64 is lenient)
        # The key point is that is_url_safe is False
