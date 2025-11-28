"""
Encryption Utility for IronGate RCON Portal
Provides Fernet symmetric encryption for RCON passwords
"""

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class EncryptionUtility:
    """
    Handles encryption and decryption of RCON passwords using Fernet symmetric encryption.
    
    The encryption key is loaded from Django settings (RCON_ENCRYPTION_KEY).
    """
    
    def __init__(self):
        """
        Initialize the encryption utility with the key from settings.
        
        Raises:
            ImproperlyConfigured: If RCON_ENCRYPTION_KEY is not set or invalid
        """
        encryption_key = getattr(settings, 'RCON_ENCRYPTION_KEY', None)
        
        if not encryption_key:
            raise ImproperlyConfigured(
                "RCON_ENCRYPTION_KEY is not set in settings. "
                "Please run generate_key.py to create an encryption key."
            )
        
        try:
            # Ensure the key is in bytes format
            if isinstance(encryption_key, str):
                encryption_key = encryption_key.encode('utf-8')
            
            self.cipher_suite = Fernet(encryption_key)
        except Exception as e:
            raise ImproperlyConfigured(
                f"Invalid RCON_ENCRYPTION_KEY format: {str(e)}. "
                "Please run generate_key.py to generate a valid key."
            )
    
    def encrypt(self, plaintext: str) -> bytes:
        """
        Encrypt a plaintext string using Fernet encryption.
        
        Args:
            plaintext: The plaintext string to encrypt (e.g., RCON password)
        
        Returns:
            bytes: The encrypted data as bytes
        
        Raises:
            ValueError: If plaintext is empty or None
        """
        if not plaintext:
            raise ValueError("Cannot encrypt empty or None plaintext")
        
        # Convert string to bytes if needed
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')
        
        # Encrypt and return bytes
        encrypted_data = self.cipher_suite.encrypt(plaintext)
        return encrypted_data
    
    def decrypt(self, ciphertext: bytes) -> str:
        """
        Decrypt ciphertext bytes using Fernet decryption.
        
        Args:
            ciphertext: The encrypted data as bytes
        
        Returns:
            str: The decrypted plaintext string
        
        Raises:
            ValueError: If ciphertext is empty or None
            InvalidToken: If decryption fails (corrupted data or wrong key)
        """
        if not ciphertext:
            raise ValueError("Cannot decrypt empty or None ciphertext")
        
        try:
            # Decrypt and convert bytes to string
            decrypted_data = self.cipher_suite.decrypt(ciphertext)
            return decrypted_data.decode('utf-8')
        except InvalidToken:
            raise InvalidToken(
                "Failed to decrypt data. The encryption key may have changed "
                "or the data may be corrupted."
            )


# Singleton instance for easy access throughout the application
_encryption_utility = None


def get_encryption_utility() -> EncryptionUtility:
    """
    Get or create the singleton EncryptionUtility instance.
    
    Returns:
        EncryptionUtility: The encryption utility instance
    """
    global _encryption_utility
    if _encryption_utility is None:
        _encryption_utility = EncryptionUtility()
    return _encryption_utility
