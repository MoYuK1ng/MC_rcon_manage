"""
Custom exceptions for MC RCON Manager encryption system
Provides clear, actionable error messages for encryption-related failures
"""


class EncryptionError(Exception):
    """Base exception for all encryption-related errors"""
    
    def __init__(self, message: str, details: str = "", solution: str = ""):
        """
        Initialize encryption error with structured message.
        
        Args:
            message: Brief error description
            details: Specific information about what went wrong
            solution: Clear steps to fix the problem
        """
        self.message = message
        self.details = details
        self.solution = solution
        
        # Build formatted error message
        parts = [message]
        if details:
            parts.append(f"\nDetails: {details}")
        if solution:
            parts.append(f"\nSolution: {solution}")
        
        super().__init__("\n".join(parts))


# Key Validation Errors
class KeyValidationError(EncryptionError):
    """Base exception for key validation failures"""
    pass


class InvalidKeyFormatError(KeyValidationError):
    """Raised when encryption key format is invalid"""
    
    def __init__(self, details: str = ""):
        super().__init__(
            message="[INVALID_KEY] Encryption key format is invalid",
            details=details or "The RCON_ENCRYPTION_KEY does not match the required Fernet key format.",
            solution="Run 'python generate_key.py' to generate a new valid encryption key"
        )


class MissingKeyError(KeyValidationError):
    """Raised when encryption key is missing or empty"""
    
    def __init__(self, details: str = ""):
        super().__init__(
            message="[MISSING_KEY] Encryption key is missing",
            details=details or "The RCON_ENCRYPTION_KEY is not set in your environment.",
            solution="Run 'python generate_key.py' to generate a new encryption key"
        )


class InvalidBase64Error(KeyValidationError):
    """Raised when encryption key contains invalid base64 characters"""
    
    def __init__(self, details: str = ""):
        super().__init__(
            message="[INVALID_BASE64] Encryption key contains invalid base64 characters",
            details=details or "The key cannot be decoded as URL-safe base64.",
            solution="Run 'python generate_key.py' to generate a new valid encryption key"
        )


# Encryption Operation Errors
class EncryptionOperationError(EncryptionError):
    """Base exception for encryption operation failures"""
    pass


class InvalidPlaintextError(EncryptionOperationError):
    """Raised when plaintext input is invalid"""
    
    def __init__(self, details: str = ""):
        super().__init__(
            message="[INVALID_INPUT] Cannot encrypt invalid input",
            details=details or "The plaintext input is empty or None.",
            solution="Provide a non-empty string to encrypt"
        )


class EncryptionFailedError(EncryptionOperationError):
    """Raised when encryption operation fails"""
    
    def __init__(self, details: str = ""):
        super().__init__(
            message="[ENCRYPTION_FAILED] Encryption operation failed",
            details=details,
            solution="Check that the encryption key is valid. Run 'python verify_key.py' to test your key."
        )


# Decryption Operation Errors
class DecryptionOperationError(EncryptionError):
    """Base exception for decryption operation failures"""
    pass


class KeyMismatchError(DecryptionOperationError):
    """Raised when decryption fails due to key mismatch"""
    
    def __init__(self, details: str = ""):
        super().__init__(
            message="[KEY_MISMATCH] Failed to decrypt data",
            details=details or (
                "The encryption key may have changed or the data may be corrupted. "
                "Decryption failed because the key used to encrypt this data is different "
                "from the current RCON_ENCRYPTION_KEY."
            ),
            solution=(
                "If you recently changed your encryption key, you need to re-encrypt all passwords. "
                "Run 'python rotate_key.py' to safely rotate keys and re-encrypt data."
            )
        )


class CorruptedDataError(DecryptionOperationError):
    """Raised when ciphertext is corrupted"""
    
    def __init__(self, details: str = ""):
        super().__init__(
            message="[CORRUPTED_DATA] Ciphertext is corrupted",
            details=details or "The encrypted data cannot be decrypted because it has been modified or corrupted.",
            solution="The data may need to be re-encrypted. Check database integrity."
        )


class InvalidCiphertextError(DecryptionOperationError):
    """Raised when ciphertext input is invalid"""
    
    def __init__(self, details: str = ""):
        super().__init__(
            message="[INVALID_INPUT] Cannot decrypt invalid input",
            details=details or "The ciphertext input is empty or None.",
            solution="Provide valid encrypted data to decrypt"
        )


# Key Rotation Errors
class KeyRotationError(EncryptionError):
    """Base exception for key rotation failures"""
    pass


class RotationFailedError(KeyRotationError):
    """Raised when key rotation fails"""
    
    def __init__(self, details: str = ""):
        super().__init__(
            message="[ROTATION_FAILED] Key rotation failed",
            details=details,
            solution="Check the error details above. The system will attempt to rollback changes."
        )


class RollbackFailedError(KeyRotationError):
    """Raised when rollback after failed rotation fails"""
    
    def __init__(self, details: str = ""):
        super().__init__(
            message="[ROLLBACK_FAILED] Failed to rollback after rotation failure",
            details=details,
            solution=(
                "CRITICAL: Manual intervention required. "
                "Restore database from backup and verify .env file contains the correct key."
            )
        )
