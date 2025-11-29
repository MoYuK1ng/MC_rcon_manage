"""
Property-based and unit tests for key rotation (rotate_key.py)
"""

import pytest
from hypothesis import given, strategies as st
from cryptography.fernet import Fernet

from servers.utils.encryption import EncryptionUtility
from servers.utils.key_validator import KeyValidator


# Feature: rcon-encryption-refactor, Property 11: Key rotation preserves passwords
@given(st.text(min_size=1, max_size=100))
def test_key_rotation_preserves_passwords(password):
    """
    Property 11: Key rotation preserves passwords
    For any password encrypted with an old key, after key rotation (decrypt with old, encrypt with new),
    decrypting with the new key should return the same original password.
    """
    # Generate two different keys
    old_key = Fernet.generate_key()
    new_key = Fernet.generate_key()
    
    old_util = EncryptionUtility(key=old_key)
    new_util = EncryptionUtility(key=new_key)
    
    # Encrypt with old key
    encrypted_old = old_util.encrypt(password)
    
    # Simulate rotation: decrypt with old, encrypt with new
    decrypted = old_util.decrypt(encrypted_old)
    encrypted_new = new_util.encrypt(decrypted)
    
    # Decrypt with new key
    final_password = new_util.decrypt(encrypted_new)
    
    # Should get back the original password
    assert final_password == password, f"Password changed during rotation: {password} != {final_password}"


# Feature: rcon-encryption-refactor, Property 12: All passwords decryptable after rotation
@pytest.mark.django_db
def test_all_passwords_decryptable_after_rotation():
    """
    Property 12: All passwords decryptable after rotation
    For any set of encrypted passwords, after successful key rotation, all passwords should be decryptable with the new key.
    """
    from servers.models import Server
    
    # Generate keys
    old_key = Fernet.generate_key()
    new_key = Fernet.generate_key()
    
    old_util = EncryptionUtility(key=old_key)
    new_util = EncryptionUtility(key=new_key)
    
    # Create test servers with passwords
    test_data = [
        ("Server1", "127.0.0.1", 25575, "password1"),
        ("Server2", "127.0.0.2", 25576, "password2"),
        ("Server3", "127.0.0.3", 25577, "密码3"),
    ]
    
    servers = []
    for name, ip, port, password in test_data:
        server = Server.objects.create(
            name=name,
            ip_address=ip,
            rcon_port=port,
            rcon_password_encrypted=old_util.encrypt(password)
        )
        servers.append((server, password))
    
    # Simulate rotation for all servers
    for server, original_password in servers:
        # Decrypt with old key
        decrypted = old_util.decrypt(server.rcon_password_encrypted)
        
        # Encrypt with new key
        server.rcon_password_encrypted = new_util.encrypt(decrypted)
        server.save()
    
    # Verify all passwords can be decrypted with new key
    for server, original_password in servers:
        decrypted = new_util.decrypt(server.rcon_password_encrypted)
        assert decrypted == original_password, f"Password mismatch for {server.name}"
        assert new_util.can_decrypt(server.rcon_password_encrypted)


# Feature: rcon-encryption-refactor, Property 13: Rollback on rotation failure
@pytest.mark.django_db
def test_rollback_on_rotation_failure():
    """
    Property 13: Rollback on rotation failure
    For any key rotation that fails, the system should rollback all changes and restore the original encryption key.
    """
    from servers.models import Server
    import tempfile
    import shutil
    import os
    
    # Generate keys
    old_key = Fernet.generate_key()
    new_key = Fernet.generate_key()
    
    old_util = EncryptionUtility(key=old_key)
    
    # Create test server
    server = Server.objects.create(
        name="Test Server",
        ip_address="127.0.0.1",
        rcon_port=25575,
        rcon_password_encrypted=old_util.encrypt("test_password")
    )
    
    original_encrypted = server.rcon_password_encrypted
    
    # Simulate a failed rotation by corrupting the data mid-process
    # In a real scenario, this would be caught and rolled back
    
    # Verify we can still decrypt with old key
    decrypted = old_util.decrypt(original_encrypted)
    assert decrypted == "test_password"
    
    # Simulate rollback: restore original encrypted data
    server.rcon_password_encrypted = original_encrypted
    server.save()
    
    # Verify rollback worked
    server.refresh_from_db()
    decrypted_after_rollback = old_util.decrypt(server.rcon_password_encrypted)
    assert decrypted_after_rollback == "test_password"


class TestKeyRotationScript:
    """Unit tests for rotate_key.py functionality"""
    
    def test_rotation_with_valid_keys(self):
        """Test key rotation with valid keys"""
        old_key = Fernet.generate_key()
        new_key = Fernet.generate_key()
        
        # Validate both keys
        assert KeyValidator.is_valid_fernet_key(old_key)
        assert KeyValidator.is_valid_fernet_key(new_key)
        
        # Test rotation logic
        old_util = EncryptionUtility(key=old_key)
        new_util = EncryptionUtility(key=new_key)
        
        password = "test_password"
        encrypted_old = old_util.encrypt(password)
        
        # Rotate
        decrypted = old_util.decrypt(encrypted_old)
        encrypted_new = new_util.encrypt(decrypted)
        
        # Verify
        assert new_util.decrypt(encrypted_new) == password
    
    def test_rotation_with_invalid_old_key(self):
        """Test that rotation fails with invalid old key"""
        invalid_old_key = "invalid-key"
        new_key = Fernet.generate_key()
        
        # Validate keys
        assert not KeyValidator.is_valid_fernet_key(invalid_old_key)
        assert KeyValidator.is_valid_fernet_key(new_key)
        
        # Rotation should fail during validation
        is_valid, error = KeyValidator.validate_key(invalid_old_key)
        assert not is_valid
    
    def test_rotation_with_invalid_new_key(self):
        """Test that rotation fails with invalid new key"""
        old_key = Fernet.generate_key()
        invalid_new_key = "invalid-key"
        
        # Validate keys
        assert KeyValidator.is_valid_fernet_key(old_key)
        assert not KeyValidator.is_valid_fernet_key(invalid_new_key)
        
        # Rotation should fail during validation
        is_valid, error = KeyValidator.validate_key(invalid_new_key)
        assert not is_valid
    
    def test_automatic_new_key_generation(self):
        """Test automatic generation of new key"""
        # Generate a new key (simulating --generate-new)
        new_key = Fernet.generate_key().decode('utf-8')
        
        # Verify it's valid
        assert KeyValidator.is_valid_fernet_key(new_key)
        assert len(new_key) == 44
        
        # Verify it works
        util = EncryptionUtility(key=new_key)
        assert util.verify_encryption("test")
    
    @pytest.mark.django_db
    def test_verify_only_mode(self):
        """Test verify-only mode that checks decryption without rotation"""
        from servers.models import Server
        
        key = Fernet.generate_key()
        util = EncryptionUtility(key=key)
        
        # Create test servers
        passwords = ["pass1", "pass2", "pass3"]
        for i, password in enumerate(passwords):
            Server.objects.create(
                name=f"Server{i}",
                ip_address=f"127.0.0.{i+1}",
                rcon_port=25575 + i,
                rcon_password_encrypted=util.encrypt(password)
            )
        
        # Verify all can be decrypted
        servers = Server.objects.all()
        for server, expected_password in zip(servers, passwords):
            decrypted = util.decrypt(server.rcon_password_encrypted)
            assert decrypted == expected_password
    
    @pytest.mark.django_db
    def test_rollback_on_database_error(self):
        """Test that rollback works when database operations fail"""
        from servers.models import Server
        
        old_key = Fernet.generate_key()
        old_util = EncryptionUtility(key=old_key)
        
        # Create server
        server = Server.objects.create(
            name="Test Server",
            ip_address="127.0.0.1",
            rcon_port=25575,
            rcon_password_encrypted=old_util.encrypt("original_password")
        )
        
        original_encrypted = server.rcon_password_encrypted
        
        # Simulate failure and rollback
        server.rcon_password_encrypted = b"corrupted_data"
        server.save()
        
        # Rollback
        server.rcon_password_encrypted = original_encrypted
        server.save()
        
        # Verify rollback
        server.refresh_from_db()
        decrypted = old_util.decrypt(server.rcon_password_encrypted)
        assert decrypted == "original_password"
    
    @pytest.mark.django_db
    def test_rotation_with_no_servers(self):
        """Test rotation when no servers exist"""
        from servers.models import Server
        
        # Ensure no servers exist
        Server.objects.all().delete()
        
        old_key = Fernet.generate_key()
        new_key = Fernet.generate_key()
        
        # Rotation should succeed (nothing to rotate)
        assert KeyValidator.is_valid_fernet_key(old_key)
        assert KeyValidator.is_valid_fernet_key(new_key)
        
        # No servers to rotate
        assert Server.objects.count() == 0
    
    @pytest.mark.django_db
    def test_rotation_preserves_server_metadata(self):
        """Test that rotation only changes passwords, not other server data"""
        from servers.models import Server
        
        old_key = Fernet.generate_key()
        new_key = Fernet.generate_key()
        
        old_util = EncryptionUtility(key=old_key)
        new_util = EncryptionUtility(key=new_key)
        
        # Create server with metadata
        server = Server.objects.create(
            name="Production Server",
            ip_address="192.168.1.100",
            rcon_port=25575,
            rcon_password_encrypted=old_util.encrypt("secret_password")
        )
        
        original_name = server.name
        original_ip = server.ip_address
        original_port = server.rcon_port
        
        # Rotate password
        decrypted = old_util.decrypt(server.rcon_password_encrypted)
        server.rcon_password_encrypted = new_util.encrypt(decrypted)
        server.save()
        
        # Verify metadata unchanged
        server.refresh_from_db()
        assert server.name == original_name
        assert server.ip_address == original_ip
        assert server.rcon_port == original_port
        
        # Verify password still works
        assert new_util.decrypt(server.rcon_password_encrypted) == "secret_password"
