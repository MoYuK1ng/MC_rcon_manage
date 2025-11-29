"""
Encryption Utility for IronGate RCON Portal
Provides Fernet symmetric encryption for RCON passwords
"""

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from servers.utils.key_validator import KeyValidator
from servers.utils.exceptions import (
    InvalidKeyFormatError,
    MissingKeyError,
    InvalidPlaintextError,
    EncryptionFailedError,
    KeyMismatchError,
    CorruptedDataError,
    InvalidCiphertextError,
)


class EncryptionUtility:
    """
    Handles encryption and decryption of RCON passwords using Fernet symmetric encryption.
    
    The encryption key is loaded from Django settings (RCON_ENCRYPTION_KEY).
    """
    
    def __init__(self, key: str | bytes | None = None):
        """
        Initialize the encryption utility with optional key override.
        
        Args:
            key: Optional key override for testing/migration. 
                 If None, uses settings.RCON_ENCRYPTION_KEY
        
        Raises:
            MissingKeyError: If RCON_ENCRYPTION_KEY is not set
            InvalidKeyFormatError: If key format is invalid
        """
        # Use provided key or get from settings
        if key is None:
            encryption_key = getattr(settings, 'RCON_ENCRYPTION_KEY', None)
        else:
            encryption_key = key
        
        # Validate the key
        is_valid, error_message = KeyValidator.validate_key(encryption_key)
        
        if not is_valid:
            # Determine which exception to raise based on error type
            if encryption_key is None or (isinstance(encryption_key, str) and not encryption_key.strip()):
                raise MissingKeyError(error_message)
            else:
                raise InvalidKeyFormatError(error_message)
        
        # Ensure the key is in bytes format
        if isinstance(encryption_key, str):
            encryption_key = encryption_key.encode('utf-8')
        
        try:
            self.cipher_suite = Fernet(encryption_key)
        except Exception as e:
            raise InvalidKeyFormatError(f"Failed to initialize Fernet cipher: {str(e)}")
    
    def encrypt(self, plaintext: str) -> bytes:
        """
        Encrypt a plaintext string using Fernet encryption.
        
        Args:
            plaintext: The plaintext string to encrypt (e.g., RCON password)
        
        Returns:
            bytes: The encrypted data as bytes
        
        Raises:
            InvalidPlaintextError: If plaintext is empty or None
            EncryptionFailedError: If encryption operation fails
        """
        if not plaintext:
            raise InvalidPlaintextError("Cannot encrypt empty or None plaintext")
        
        try:
            # Convert string to bytes if needed
            if isinstance(plaintext, str):
                plaintext = plaintext.encode('utf-8')
            
            # Encrypt and return bytes
            encrypted_data = self.cipher_suite.encrypt(plaintext)
            return encrypted_data
        except InvalidPlaintextError:
            # Re-raise our custom exception
            raise
        except Exception as e:
            raise EncryptionFailedError(f"Encryption operation failed: {str(e)}")
    
    def decrypt(self, ciphertext: bytes) -> str:
        """
        Decrypt ciphertext bytes using Fernet decryption.
        
        Args:
            ciphertext: The encrypted data as bytes
        
        Returns:
            str: The decrypted plaintext string
        
        Raises:
            InvalidCiphertextError: If ciphertext is empty or None
            KeyMismatchError: If decryption fails due to key mismatch
            CorruptedDataError: If ciphertext is corrupted
        """
        if not ciphertext:
            raise InvalidCiphertextError("Cannot decrypt empty or None ciphertext")
        
        try:
            # Decrypt and convert bytes to string
            decrypted_data = self.cipher_suite.decrypt(ciphertext)
            return decrypted_data.decode('utf-8')
        except InvalidToken as e:
            # Try to determine if it's a key mismatch or corrupted data
            error_str = str(e).lower()
            if "signature" in error_str or "invalid" in error_str:
                raise KeyMismatchError(
                    "Decryption failed. The encryption key used to encrypt this data "
                    "is different from the current RCON_ENCRYPTION_KEY."
                )
            else:
                raise CorruptedDataError(f"Decryption failed: {str(e)}")
        except Exception as e:
            raise CorruptedDataError(f"Unexpected decryption error: {str(e)}")


    def verify_encryption(self, plaintext: str) -> bool:
        """
        Verify encryption works by performing a round-trip test.
        
        Args:
            plaintext: Test string to encrypt and decrypt
            
        Returns:
            bool: True if round-trip succeeds, False otherwise
        """
        try:
            if not plaintext:
                return False
            encrypted = self.encrypt(plaintext)
            decrypted = self.decrypt(encrypted)
            return decrypted == plaintext
        except Exception:
            return False
    
    def can_decrypt(self, ciphertext: bytes) -> bool:
        """
        Check if ciphertext can be decrypted with current key.
        
        Args:
            ciphertext: Encrypted data to test
            
        Returns:
            bool: True if decryption succeeds, False otherwise
        """
        try:
            if not ciphertext:
                return False
            self.decrypt(ciphertext)
            return True
        except Exception:
            return False


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
