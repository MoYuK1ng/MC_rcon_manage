"""
Key Validator for MC RCON Manager
Validates Fernet encryption keys with detailed error messages
"""

import base64
from typing import Tuple
from cryptography.fernet import Fernet


class KeyValidator:
    """
    Validates Fernet encryption keys and provides detailed error information.
    
    Fernet keys must be:
    - 32 bytes of data
    - URL-safe base64 encoded
    - Resulting in a 44-character string (32 bytes * 4/3 + padding)
    """
    
    EXPECTED_KEY_LENGTH = 44  # 32 bytes base64-encoded = 44 characters
    EXPECTED_DECODED_LENGTH = 32  # 32 bytes of actual key data
    
    @staticmethod
    def validate_key(key: str | bytes) -> Tuple[bool, str]:
        """
        Validate a Fernet encryption key with comprehensive format checking.
        
        Args:
            key: The key to validate (string or bytes)
            
        Returns:
            tuple: (is_valid, error_message)
                - is_valid: True if key is valid, False otherwise
                - error_message: Empty string if valid, detailed error if invalid
        """
        # Check if key is None or empty
        if key is None:
            return False, (
                "[MISSING_KEY] Encryption key is missing\n\n"
                "Details: The RCON_ENCRYPTION_KEY is not set in your environment.\n"
                "Expected: 32-byte URL-safe base64-encoded string (44 characters)\n"
                "Found: None\n\n"
                "Solution: Run 'python generate_key.py' to generate a new valid encryption key"
            )
        
        # Convert bytes to string if needed
        if isinstance(key, bytes):
            try:
                key = key.decode('utf-8')
            except UnicodeDecodeError:
                return False, (
                    "[INVALID_KEY] Encryption key contains invalid UTF-8 bytes\n\n"
                    "Details: The key cannot be decoded as UTF-8 text.\n\n"
                    "Solution: Run 'python generate_key.py' to generate a new valid encryption key"
                )
        
        # Check if key is empty string
        if not key or len(key.strip()) == 0:
            return False, (
                "[MISSING_KEY] Encryption key is empty\n\n"
                "Details: The RCON_ENCRYPTION_KEY is set but contains no data.\n"
                "Expected: 32-byte URL-safe base64-encoded string (44 characters)\n"
                "Found: Empty string\n\n"
                "Solution: Run 'python generate_key.py' to generate a new valid encryption key"
            )
        
        key = key.strip()
        
        # Check key length
        if len(key) != KeyValidator.EXPECTED_KEY_LENGTH:
            return False, (
                f"[INVALID_KEY] Encryption key has incorrect length\n\n"
                f"Details: Fernet keys must be exactly {KeyValidator.EXPECTED_KEY_LENGTH} characters.\n"
                f"Expected: {KeyValidator.EXPECTED_KEY_LENGTH} characters\n"
                f"Found: {len(key)} characters\n\n"
                f"Solution: Run 'python generate_key.py' to generate a new valid encryption key"
            )
        
        # Check if key is valid base64
        try:
            decoded = base64.urlsafe_b64decode(key)
        except Exception as e:
            return False, (
                "[INVALID_BASE64] Encryption key contains invalid base64 characters\n\n"
                f"Details: The key cannot be decoded as URL-safe base64.\n"
                f"Error: {str(e)}\n\n"
                "Solution: Run 'python generate_key.py' to generate a new valid encryption key"
            )
        
        # Check decoded length
        if len(decoded) != KeyValidator.EXPECTED_DECODED_LENGTH:
            return False, (
                f"[INVALID_KEY] Encryption key decodes to incorrect length\n\n"
                f"Details: Fernet keys must decode to exactly {KeyValidator.EXPECTED_DECODED_LENGTH} bytes.\n"
                f"Expected: {KeyValidator.EXPECTED_DECODED_LENGTH} bytes\n"
                f"Found: {len(decoded)} bytes\n\n"
                f"Solution: Run 'python generate_key.py' to generate a new valid encryption key"
            )
        
        # Try to create a Fernet instance to verify the key works
        try:
            Fernet(key.encode('utf-8') if isinstance(key, str) else key)
        except Exception as e:
            return False, (
                "[INVALID_KEY] Encryption key format is invalid\n\n"
                f"Details: The key cannot be used to create a Fernet cipher.\n"
                f"Error: {str(e)}\n\n"
                "Solution: Run 'python generate_key.py' to generate a new valid encryption key"
            )
        
        return True, ""
    
    @staticmethod
    def is_valid_fernet_key(key: str | bytes) -> bool:
        """
        Quick check if a key is valid Fernet format.
        
        Args:
            key: The key to check
            
        Returns:
            bool: True if valid, False otherwise
        """
        is_valid, _ = KeyValidator.validate_key(key)
        return is_valid
    
    @staticmethod
    def get_key_info(key: str | bytes) -> dict:
        """
        Get information about a key for debugging purposes.
        
        Args:
            key: The key to analyze
            
        Returns:
            dict: {
                'length': int,
                'encoding': str,
                'is_url_safe': bool,
                'has_padding': bool,
                'decoded_length': int or None
            }
        """
        if key is None:
            return {
                'length': 0,
                'encoding': 'none',
                'is_url_safe': False,
                'has_padding': False,
                'decoded_length': None
            }
        
        # Convert bytes to string if needed
        if isinstance(key, bytes):
            try:
                key_str = key.decode('utf-8')
            except UnicodeDecodeError:
                return {
                    'length': len(key),
                    'encoding': 'invalid_utf8',
                    'is_url_safe': False,
                    'has_padding': False,
                    'decoded_length': None
                }
        else:
            key_str = key
        
        key_str = key_str.strip()
        
        # Check if it's URL-safe base64 (only contains valid characters)
        url_safe_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_=')
        is_url_safe = all(c in url_safe_chars for c in key_str)
        
        # Check for padding
        has_padding = key_str.endswith('=')
        
        # Try to decode
        decoded_length = None
        try:
            decoded = base64.urlsafe_b64decode(key_str)
            decoded_length = len(decoded)
        except Exception:
            pass
        
        return {
            'length': len(key_str),
            'encoding': 'utf8',
            'is_url_safe': is_url_safe,
            'has_padding': has_padding,
            'decoded_length': decoded_length
        }
