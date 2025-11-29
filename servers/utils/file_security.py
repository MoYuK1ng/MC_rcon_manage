"""
File Security Utilities for IronGate RCON Portal
Checks file permissions for sensitive files like .env
"""

import os
import stat
import sys


def check_env_file_permissions(env_file='.env'):
    """
    Check if .env file has appropriate permissions (owner read/write only).
    
    Args:
        env_file: Path to .env file (default: '.env')
        
    Returns:
        tuple: (is_secure, warning_message)
            - is_secure: True if permissions are secure, False otherwise
            - warning_message: Empty string if secure, warning message if not
    """
    # Skip permission check on Windows (different permission model)
    if sys.platform == 'win32':
        return True, ""
    
    if not os.path.exists(env_file):
        return False, (
            f"⚠️  WARNING: {env_file} file not found\n"
            f"Run 'python generate_key.py' to create it"
        )
    
    try:
        # Get file stats
        file_stats = os.stat(env_file)
        file_mode = file_stats.st_mode
        
        # Check permissions
        # Secure: 0o600 (owner read/write only)
        # Also acceptable: 0o400 (owner read only)
        owner_read = bool(file_mode & stat.S_IRUSR)
        owner_write = bool(file_mode & stat.S_IWUSR)
        group_read = bool(file_mode & stat.S_IRGRP)
        group_write = bool(file_mode & stat.S_IWGRP)
        other_read = bool(file_mode & stat.S_IROTH)
        other_write = bool(file_mode & stat.S_IWOTH)
        
        # Check if permissions are too permissive
        if group_read or group_write or other_read or other_write:
            # Get octal representation
            octal_perms = oct(stat.S_IMODE(file_mode))
            
            warning = (
                f"⚠️  SECURITY WARNING: {env_file} has overly permissive permissions\n\n"
                f"Current permissions: {octal_perms}\n"
                f"Recommended: 0o600 (owner read/write only)\n\n"
                f"The .env file contains sensitive encryption keys and should only be\n"
                f"readable by the owner.\n\n"
                f"To fix this, run:\n"
                f"  chmod 600 {env_file}\n"
            )
            return False, warning
        
        # Permissions are secure
        return True, ""
        
    except Exception as e:
        return False, f"⚠️  WARNING: Could not check {env_file} permissions: {e}"


def get_file_permissions_info(filepath):
    """
    Get detailed information about file permissions.
    
    Args:
        filepath: Path to file
        
    Returns:
        dict: {
            'exists': bool,
            'readable': bool,
            'writable': bool,
            'executable': bool,
            'mode_octal': str,
            'owner_uid': int,
            'group_gid': int,
        }
    """
    if not os.path.exists(filepath):
        return {
            'exists': False,
            'readable': False,
            'writable': False,
            'executable': False,
            'mode_octal': None,
            'owner_uid': None,
            'group_gid': None,
        }
    
    try:
        file_stats = os.stat(filepath)
        file_mode = file_stats.st_mode
        
        return {
            'exists': True,
            'readable': os.access(filepath, os.R_OK),
            'writable': os.access(filepath, os.W_OK),
            'executable': os.access(filepath, os.X_OK),
            'mode_octal': oct(stat.S_IMODE(file_mode)),
            'owner_uid': file_stats.st_uid,
            'group_gid': file_stats.st_gid,
        }
    except Exception as e:
        return {
            'exists': True,
            'readable': False,
            'writable': False,
            'executable': False,
            'mode_octal': None,
            'owner_uid': None,
            'group_gid': None,
            'error': str(e),
        }
