# Design Document

## Overview

This document describes the design for refactoring the RCON encryption key management system in IronGate. The refactor addresses critical issues with key validation, error handling, and lifecycle management while maintaining backward compatibility with existing encrypted passwords.

The current system uses Fernet symmetric encryption from the `cryptography` library to protect RCON passwords. However, it lacks proper key validation, clear error messages, and key rotation capabilities. This refactor will introduce a robust key management layer with comprehensive validation and migration tools.

## Architecture

### Current Architecture Issues

1. **Weak Key Validation**: Keys are only validated when first used, not at startup
2. **Poor Error Messages**: Users cannot distinguish between key problems and password problems
3. **No Key Rotation**: No mechanism to safely change encryption keys
4. **Scattered Logic**: Key handling logic is distributed across multiple files

### Proposed Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Django Settings                       │
│  - Loads RCON_ENCRYPTION_KEY from .env                  │
│  - Validates key format at startup                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              KeyValidator (New)                          │
│  - Validates Fernet key format                          │
│  - Provides clear error messages                        │
│  - Checks key strength                                  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│           EncryptionUtility (Enhanced)                   │
│  - Encrypts/decrypts RCON passwords                     │
│  - Uses validated key from settings                     │
│  - Provides detailed error context                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Server Model                                │
│  - Stores encrypted passwords                           │
│  - Uses EncryptionUtility for operations                │
└─────────────────────────────────────────────────────────┘

Supporting Tools:
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  generate_key.py │  │  rotate_key.py   │  │  verify_key.py   │
│  (Enhanced)      │  │  (New)           │  │  (New)           │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

## Components and Interfaces

### 1. KeyValidator (New Component)

**Purpose**: Centralized key validation logic with clear error messages

**Location**: `servers/utils/key_validator.py`

**Interface**:
```python
class KeyValidator:
    @staticmethod
    def validate_key(key: str | bytes) -> tuple[bool, str]:
        """
        Validate a Fernet encryption key.
        
        Args:
            key: The key to validate (string or bytes)
            
        Returns:
            tuple: (is_valid, error_message)
                - is_valid: True if key is valid, False otherwise
                - error_message: Empty string if valid, detailed error if invalid
        """
        
    @staticmethod
    def is_valid_fernet_key(key: str | bytes) -> bool:
        """
        Quick check if a key is valid Fernet format.
        
        Args:
            key: The key to check
            
        Returns:
            bool: True if valid, False otherwise
        """
        
    @staticmethod
    def get_key_info(key: str | bytes) -> dict:
        """
        Get information about a key.
        
        Args:
            key: The key to analyze
            
        Returns:
            dict: {
                'length': int,
                'encoding': str,
                'is_url_safe': bool,
                'has_padding': bool
            }
        """
```

### 2. EncryptionUtility (Enhanced)

**Purpose**: Encrypt and decrypt RCON passwords with improved error handling

**Location**: `servers/utils/encryption.py` (existing, will be enhanced)

**Changes**:
- Add key validation in `__init__`
- Improve error messages with context
- Add encryption verification method
- Add support for key rotation

**Enhanced Interface**:
```python
class EncryptionUtility:
    def __init__(self, key: str | bytes | None = None):
        """
        Initialize with optional key override (for testing/migration).
        
        Args:
            key: Optional key override, defaults to settings.RCON_ENCRYPTION_KEY
        """
        
    def encrypt(self, plaintext: str) -> bytes:
        """Encrypt plaintext with enhanced error handling"""
        
    def decrypt(self, ciphertext: bytes) -> str:
        """Decrypt ciphertext with enhanced error handling"""
        
    def verify_encryption(self, plaintext: str) -> bool:
        """
        Verify encryption works by round-trip test.
        
        Args:
            plaintext: Test string to encrypt and decrypt
            
        Returns:
            bool: True if round-trip succeeds
        """
        
    def can_decrypt(self, ciphertext: bytes) -> bool:
        """
        Check if ciphertext can be decrypted with current key.
        
        Args:
            ciphertext: Encrypted data to test
            
        Returns:
            bool: True if decryption succeeds
        """
```

### 3. Key Generation Script (Enhanced)

**Purpose**: Generate and validate encryption keys

**Location**: `generate_key.py` (existing, will be enhanced)

**Changes**:
- Validate generated key before saving
- Create timestamped backup of existing .env
- Verify key works with EncryptionUtility
- Add rollback on failure

### 4. Key Rotation Script (New)

**Purpose**: Safely rotate encryption keys and re-encrypt passwords

**Location**: `rotate_key.py` (new)

**Interface**:
```bash
python rotate_key.py --old-key <old_key> --new-key <new_key>
python rotate_key.py --generate-new  # Generate new key automatically
python rotate_key.py --verify-only   # Verify all passwords can be decrypted
```

**Process**:
1. Validate both old and new keys
2. Create database backup
3. Decrypt all passwords with old key
4. Encrypt all passwords with new key
5. Update .env file
6. Verify all passwords decrypt correctly
7. Rollback on any failure

### 5. Key Verification Script (New)

**Purpose**: Verify encryption key and test encryption operations

**Location**: `verify_key.py` (new)

**Interface**:
```bash
python verify_key.py                    # Verify current key
python verify_key.py --key <key>        # Verify specific key
python verify_key.py --test-passwords   # Test all stored passwords
```

## Data Models

No changes to existing data models. The `Server` model already stores encrypted passwords in `rcon_password_encrypted` as `BinaryField`.

## Corr
ectness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Valid key detection

*For any* string input, the key validator should correctly identify whether it is a valid 32-byte URL-safe base64-encoded Fernet key
**Validates: Requirements 1.1**

### Property 2: Invalid key error messages

*For any* invalid key format, validation failure should produce an error message containing instructions to run generate_key.py
**Validates: Requirements 1.2**

### Property 3: Invalid base64 detection

*For any* string containing invalid base64 characters, the validator should detect it and provide a specific error message about invalid encoding
**Validates: Requirements 1.4**

### Property 4: Generated keys are valid

*For any* key generated by generate_key.py, the key should pass validation as a valid Fernet key
**Validates: Requirements 2.1**

### Property 5: Backup creation with timestamp

*For any* existing .env file, when generate_key.py updates it, a backup file should be created with a timestamp in the filename
**Validates: Requirements 2.2**

### Property 6: Generated keys work with EncryptionUtility

*For any* key generated by generate_key.py, the EncryptionUtility should be able to use it for encryption operations
**Validates: Requirements 2.3**

### Property 7: Backup restoration on failure

*For any* .env file, if key generation fails after creating a backup, the original .env file should be restored from the backup
**Validates: Requirements 2.4**

### Property 8: Encryption round-trip

*For any* plaintext password string, encrypting then decrypting should return the original plaintext value
**Validates: Requirements 3.1**

### Property 9: Key mismatch detection

*For any* plaintext encrypted with one key, attempting to decrypt with a different key should raise an InvalidToken exception with a clear message
**Validates: Requirements 3.3**

### Property 10: Corrupted ciphertext detection

*For any* corrupted ciphertext (modified bytes), decryption should raise an InvalidToken exception with a clear message
**Validates: Requirements 3.4**

### Property 11: Key rotation preserves passwords

*For any* password encrypted with an old key, after key rotation, decrypting with the new key should return the same original password
**Validates: Requirements 4.2**

### Property 12: All passwords decryptable after rotation

*For any* set of encrypted passwords, after successful key rotation, all passwords should be decryptable with the new key
**Validates: Requirements 4.3**

### Property 13: Rollback on rotation failure

*For any* key rotation that fails, the system should rollback all changes and restore the original encryption key
**Validates: Requirements 4.4**

### Property 14: Invalid key error message clarity

*For any* encryption operation with an invalid key, the error message should clearly state the encryption key is invalid
**Validates: Requirements 5.1**

### Property 15: Key mismatch error message clarity

*For any* decryption failure due to key mismatch, the error message should indicate the key may have changed
**Validates: Requirements 5.2**

### Property 16: Invalid input error message clarity

*For any* invalid input to encryption (e.g., None, empty string), the error message should clearly identify the input problem
**Validates: Requirements 5.3**

## Error Handling

### Error Categories

1. **Key Validation Errors**
   - Invalid key format
   - Missing key
   - Wrong key length
   - Invalid base64 encoding

2. **Encryption Errors**
   - Empty plaintext
   - Invalid input type
   - Key initialization failure

3. **Decryption Errors**
   - Key mismatch
   - Corrupted ciphertext
   - Empty ciphertext
   - Invalid token

4. **Key Rotation Errors**
   - Old key invalid
   - New key invalid
   - Database access failure
   - Backup creation failure
   - Rollback failure

### Error Message Format

All error messages should follow this format:

```
[ERROR_TYPE] Brief description

Details: Specific information about what went wrong

Solution: Clear steps to fix the problem
```

Example:
```
[INVALID_KEY] Encryption key format is invalid

Details: The RCON_ENCRYPTION_KEY in your .env file is not a valid Fernet key.
Expected: 32-byte URL-safe base64-encoded string (44 characters)
Found: 38 characters with invalid base64 characters

Solution: Run 'python generate_key.py' to generate a new valid encryption key
```

### Exception Hierarchy

```
EncryptionError (base)
├── KeyValidationError
│   ├── InvalidKeyFormatError
│   ├── MissingKeyError
│   └── InvalidBase64Error
├── EncryptionOperationError
│   ├── InvalidPlaintextError
│   └── EncryptionFailedError
├── DecryptionOperationError
│   ├── KeyMismatchError
│   ├── CorruptedDataError
│   └── InvalidCiphertextError
└── KeyRotationError
    ├── RotationFailedError
    └── RollbackFailedError
```

## Testing Strategy

### Unit Testing

Unit tests will cover specific examples and edge cases:

1. **Key Validation Tests**
   - Valid Fernet key passes validation
   - Invalid length key fails validation
   - Invalid base64 characters fail validation
   - Empty/None key fails validation
   - Key with wrong padding fails validation

2. **Encryption Tests**
   - Encrypt simple ASCII password
   - Encrypt Unicode password
   - Encrypt password with special characters
   - Empty string raises ValueError
   - None input raises ValueError

3. **Decryption Tests**
   - Decrypt valid ciphertext
   - Wrong key raises InvalidToken
   - Corrupted ciphertext raises InvalidToken
   - Empty ciphertext raises ValueError

4. **Key Generation Tests**
   - Generated key is valid Fernet format
   - Generated key is 44 characters
   - Generated key is URL-safe base64
   - Backup file is created with timestamp
   - .env file is updated correctly

5. **Key Rotation Tests**
   - Rotation with valid keys succeeds
   - Rotation with invalid old key fails
   - Rotation with invalid new key fails
   - Rollback restores original state
   - All passwords decrypt after rotation

### Property-Based Testing

Property-based tests will verify universal properties across many inputs using the `hypothesis` library (already in use based on `.hypothesis` directory):

1. **Property Tests for Key Validation**
   - Property 1: Valid key detection
   - Property 2: Invalid key error messages
   - Property 3: Invalid base64 detection

2. **Property Tests for Key Generation**
   - Property 4: Generated keys are valid
   - Property 5: Backup creation with timestamp
   - Property 6: Generated keys work with EncryptionUtility
   - Property 7: Backup restoration on failure

3. **Property Tests for Encryption**
   - Property 8: Encryption round-trip
   - Property 9: Key mismatch detection
   - Property 10: Corrupted ciphertext detection

4. **Property Tests for Key Rotation**
   - Property 11: Key rotation preserves passwords
   - Property 12: All passwords decryptable after rotation
   - Property 13: Rollback on rotation failure

5. **Property Tests for Error Messages**
   - Property 14: Invalid key error message clarity
   - Property 15: Key mismatch error message clarity
   - Property 16: Invalid input error message clarity

**Testing Framework**: `pytest` with `hypothesis` for property-based testing

**Test Configuration**: Each property-based test will run a minimum of 100 iterations to ensure thorough coverage of the input space.

**Test Tagging**: Each property-based test will be tagged with a comment referencing the correctness property:
```python
# Feature: rcon-encryption-refactor, Property 8: Encryption round-trip
@given(st.text(min_size=1))
def test_encryption_round_trip(plaintext):
    ...
```

### Integration Testing

Integration tests will verify the complete workflow:

1. **End-to-End Key Generation**
   - Generate key → Save to .env → Load in Django → Encrypt password → Decrypt password

2. **End-to-End Key Rotation**
   - Create servers with passwords → Rotate key → Verify all passwords still work

3. **Django Admin Integration**
   - Save server with password → Retrieve password → Verify decryption works

### Test Organization

```
servers/tests/
├── test_key_validator.py          # Unit tests for KeyValidator
├── test_encryption_enhanced.py    # Unit tests for EncryptionUtility
├── test_key_generation.py         # Unit tests for generate_key.py
├── test_key_rotation.py           # Unit tests for rotate_key.py
├── test_properties_encryption.py  # Property-based tests for encryption
└── test_integration_encryption.py # Integration tests
```

## Security Considerations

1. **Key Storage**
   - Keys stored in .env file (already in .gitignore)
   - File permissions checked on startup (owner read-only)
   - Keys never logged except during initial generation

2. **Key Generation**
   - Uses `Fernet.generate_key()` which uses `os.urandom()` (cryptographically secure)
   - Keys are 32 bytes (256 bits) of entropy

3. **Encryption Algorithm**
   - Fernet uses AES-128-CBC with HMAC-SHA256
   - Authenticated encryption prevents tampering
   - Includes timestamp for key rotation support

4. **Key Rotation**
   - Atomic operation with rollback on failure
   - Database backup before rotation
   - Verification step after rotation

5. **Error Messages**
   - Never include sensitive data in error messages
   - Never log decrypted passwords
   - Provide enough information for debugging without exposing secrets

## Migration Plan

### Phase 1: Add New Components (Non-Breaking)

1. Create `KeyValidator` class
2. Create `verify_key.py` script
3. Add validation to settings.py startup
4. Enhance error messages in `EncryptionUtility`

### Phase 2: Enhance Existing Components (Non-Breaking)

1. Update `generate_key.py` with validation and backup
2. Add verification methods to `EncryptionUtility`
3. Update documentation

### Phase 3: Add Key Rotation (New Feature)

1. Create `rotate_key.py` script
2. Add Django management command for rotation
3. Create migration guide

### Backward Compatibility

- All changes are backward compatible
- Existing encrypted passwords will continue to work
- No database migrations required
- Existing .env files will work (but will show warnings if key is invalid)

## Performance Considerations

1. **Key Validation**: O(1) operation, negligible impact on startup time
2. **Encryption/Decryption**: No performance change, same Fernet operations
3. **Key Rotation**: O(n) where n = number of servers, run offline during maintenance

## Deployment Notes

1. **Development Environment**
   - Run `python generate_key.py` to create/update key
   - Run `python verify_key.py` to test encryption

2. **Production Environment**
   - Generate key on production server (never copy from dev)
   - Set appropriate file permissions on .env
   - Test encryption before deploying application

3. **Key Rotation**
   - Schedule during maintenance window
   - Create database backup first
   - Run `python rotate_key.py --generate-new`
   - Verify all servers accessible after rotation
