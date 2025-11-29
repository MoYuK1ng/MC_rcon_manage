"""
Unit tests for file security utilities
"""

import os
import sys
import tempfile
import pytest

from servers.utils.file_security import check_env_file_permissions, get_file_permissions_info


class TestFilePermissionChecking:
    """Tests for file permission checking"""
    
    @pytest.mark.skipif(sys.platform == 'win32', reason="Permission checks not applicable on Windows")
    def test_detection_of_correct_permissions(self):
        """Test detection of correct permissions (owner read-only)"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write('TEST_KEY=value\n')
            temp_file = f.name
        
        try:
            # Set secure permissions (owner read/write only)
            os.chmod(temp_file, 0o600)
            
            is_secure, warning = check_env_file_permissions(temp_file)
            
            assert is_secure, "Secure permissions should be detected as secure"
            assert warning == "", "No warning should be given for secure permissions"
        finally:
            os.unlink(temp_file)
    
    @pytest.mark.skipif(sys.platform == 'win32', reason="Permission checks not applicable on Windows")
    def test_detection_of_overly_permissive_permissions(self):
        """Test detection of overly permissive permissions"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write('TEST_KEY=value\n')
            temp_file = f.name
        
        try:
            # Set overly permissive permissions (world readable)
            os.chmod(temp_file, 0o644)
            
            is_secure, warning = check_env_file_permissions(temp_file)
            
            assert not is_secure, "Overly permissive permissions should be detected"
            assert len(warning) > 0, "Warning should be provided"
            assert "chmod 600" in warning, "Warning should include fix command"
        finally:
            os.unlink(temp_file)
    
    @pytest.mark.skipif(sys.platform == 'win32', reason="Permission checks not applicable on Windows")
    def test_handling_of_missing_env_file(self):
        """Test handling of missing .env file"""
        non_existent_file = '/tmp/non_existent_file_12345.env'
        
        is_secure, warning = check_env_file_permissions(non_existent_file)
        
        assert not is_secure, "Missing file should not be considered secure"
        assert "not found" in warning.lower(), "Warning should mention file not found"
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    def test_windows_permission_check_skipped(self):
        """Test that permission checks are skipped on Windows"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write('TEST_KEY=value\n')
            temp_file = f.name
        
        try:
            is_secure, warning = check_env_file_permissions(temp_file)
            
            # On Windows, should always return True (checks skipped)
            assert is_secure, "Permission checks should be skipped on Windows"
            assert warning == "", "No warning on Windows"
        finally:
            os.unlink(temp_file)
    
    def test_get_file_permissions_info_existing_file(self):
        """Test getting permissions info for existing file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write('TEST_KEY=value\n')
            temp_file = f.name
        
        try:
            info = get_file_permissions_info(temp_file)
            
            assert info['exists'] is True
            assert info['readable'] is True
            assert info['writable'] is True
            
            if sys.platform != 'win32':
                assert info['mode_octal'] is not None
                assert info['owner_uid'] is not None
                assert info['group_gid'] is not None
        finally:
            os.unlink(temp_file)
    
    def test_get_file_permissions_info_nonexistent_file(self):
        """Test getting permissions info for non-existent file"""
        non_existent_file = '/tmp/non_existent_file_12345.env'
        
        info = get_file_permissions_info(non_existent_file)
        
        assert info['exists'] is False
        assert info['readable'] is False
        assert info['writable'] is False
        assert info['executable'] is False
        assert info['mode_octal'] is None
    
    @pytest.mark.skipif(sys.platform == 'win32', reason="Unix-specific test")
    def test_permission_info_includes_octal_mode(self):
        """Test that permission info includes octal mode on Unix"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write('TEST_KEY=value\n')
            temp_file = f.name
        
        try:
            # Set specific permissions
            os.chmod(temp_file, 0o600)
            
            info = get_file_permissions_info(temp_file)
            
            assert info['mode_octal'] == '0o600'
        finally:
            os.unlink(temp_file)
    
    @pytest.mark.skipif(sys.platform == 'win32', reason="Unix-specific test")
    def test_various_permission_combinations(self):
        """Test detection of various permission combinations"""
        test_cases = [
            (0o600, True, "Owner read/write only - secure"),
            (0o400, True, "Owner read only - secure"),
            (0o644, False, "World readable - insecure"),
            (0o666, False, "World read/write - insecure"),
            (0o640, False, "Group readable - insecure"),
        ]
        
        for mode, expected_secure, description in test_cases:
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                f.write('TEST_KEY=value\n')
                temp_file = f.name
            
            try:
                os.chmod(temp_file, mode)
                is_secure, warning = check_env_file_permissions(temp_file)
                
                assert is_secure == expected_secure, f"Failed for {description}: mode {oct(mode)}"
                
                if not expected_secure:
                    assert len(warning) > 0, f"Warning expected for {description}"
            finally:
                os.unlink(temp_file)
