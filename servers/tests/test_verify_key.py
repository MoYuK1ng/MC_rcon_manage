"""
Unit tests for verify_key.py script
"""

import pytest
from cryptography.fernet import Fernet
from unittest.mock import patch, MagicMock

from servers.utils.key_validator import KeyValidator
from servers.utils.encryption import EncryptionUtility


class TestVerifyKeyFunctionality:
    """Tests for verify_key.py functionality"""
    
    def test_verification_with_valid_key(self):
        """Test verification with a valid key"""
        key = Fernet.generate_key().decode('utf-8')
        
        # Validate the key
        is_valid, error_message = KeyValidator.validate_key(key)
        assert is_valid
        assert error_message == ""
        
        # Test encryption
        util = EncryptionUtility(key=key)
        assert util.verify_encryption("test_password")
    
    def test_verification_with_invalid_key(self):
        """Test verification with an invalid key"""
        invalid_key = "invalid-key-format"
        
        # Validate the key
        is_valid, error_message = KeyValidator.validate_key(invalid_key)
        assert not is_valid
        assert len(error_message) > 0
        assert "generate_key.py" in error_message
    
    def test_key_info_display(self):
        """Test that key info is correctly retrieved"""
        key = Fernet.generate_key().decode('utf-8')
        
        info = KeyValidator.get_key_info(key)
        
        assert info['length'] == 44
        assert info['encoding'] == 'utf8'
        assert info['is_url_safe'] is True
        assert info['decoded_length'] == 32
    
    def test_encryption_decryption_test(self):
        """Test that encryption/decryption verification works"""
        key = Fernet.generate_key()
        util = EncryptionUtility(key=key)
        
        # Test with various passwords
        test_passwords = [
            "simple",
            "complex_P@ssw0rd!",
            "unicode_密码",
            "long_" * 100,
        ]
        
        for password in test_passwords:
            assert util.verify_encryption(password), f"Failed for password: {password}"
    
    @pytest.mark.django_db
    def test_password_decryption_verification(self):
        """Test verification of stored password decryption"""
        from servers.models import Server
        from servers.utils.encryption import get_encryption_utility
        
        # Create a test server with encrypted password
        # Use the default encryption utility (from settings)
        server = Server.objects.create(
            name="Test Server",
            ip_address="127.0.0.1",
            rcon_port=25575
        )
        
        test_password = "test_rcon_password"
        server.set_password(test_password)
        server.save()
        
        # Verify we can decrypt it
        decrypted = server.get_password()
        assert decrypted == test_password
        
        # Verify with can_decrypt using the same utility
        util = get_encryption_utility()
        assert util.can_decrypt(server.rcon_password_encrypted)
    
    @pytest.mark.django_db
    def test_password_decryption_with_wrong_key(self):
        """Test that wrong key fails to decrypt passwords"""
        from servers.models import Server
        
        # Create server with one key
        key1 = Fernet.generate_key()
        util1 = EncryptionUtility(key=key1)
        
        server = Server.objects.create(
            name="Test Server",
            ip_address="127.0.0.1",
            rcon_port=25575
        )
        
        server.set_password("test_password")
        server.save()
        
        # Try to decrypt with different key
        key2 = Fernet.generate_key()
        util2 = EncryptionUtility(key=key2)
        
        assert not util2.can_decrypt(server.rcon_password_encrypted)
    
    def test_command_line_argument_parsing(self):
        """Test that command-line arguments would be parsed correctly"""
        import argparse
        
        # Simulate the argument parser from verify_key.py
        parser = argparse.ArgumentParser()
        parser.add_argument('--key', type=str)
        parser.add_argument('--test-passwords', action='store_true')
        
        # Test no arguments
        args = parser.parse_args([])
        assert args.key is None
        assert args.test_passwords is False
        
        # Test --key argument
        test_key = "test_key_value"
        args = parser.parse_args(['--key', test_key])
        assert args.key == test_key
        assert args.test_passwords is False
        
        # Test --test-passwords argument
        args = parser.parse_args(['--test-passwords'])
        assert args.key is None
        assert args.test_passwords is True
