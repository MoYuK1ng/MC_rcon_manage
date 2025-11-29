# Implementation Plan

- [x] 1. Create KeyValidator component


  - Create `servers/utils/key_validator.py` with KeyValidator class
  - Implement `validate_key()` method with comprehensive format checking
  - Implement `is_valid_fernet_key()` method for quick validation
  - Implement `get_key_info()` method for key analysis
  - Add detailed error messages for each validation failure type
  - _Requirements: 1.1, 1.2, 1.4_



- [ ] 1.1 Write property test for valid key detection
  - **Property 1: Valid key detection**

  - **Validates: Requirements 1.1**

- [x] 1.2 Write property test for invalid key error messages

  - **Property 2: Invalid key error messages**
  - **Validates: Requirements 1.2**


- [ ] 1.3 Write property test for invalid base64 detection
  - **Property 3: Invalid base64 detection**
  - **Validates: Requirements 1.4**



- [ ] 1.4 Write unit tests for KeyValidator edge cases
  - Test empty/None key handling
  - Test key with wrong length
  - Test key with invalid padding
  - _Requirements: 1.3_

- [ ] 2. Create custom exception classes
  - Create `servers/utils/exceptions.py` with exception hierarchy


  - Implement EncryptionError base class
  - Implement KeyValidationError and subclasses (InvalidKeyFormatError, MissingKeyError, InvalidBase64Error)
  - Implement EncryptionOperationError and subclasses
  - Implement DecryptionOperationError and subclasses
  - Implement KeyRotationError and subclasses
  - Add formatted error messages to each exception class
  - _Requirements: 5.1, 5.2, 5.3_

- [x] 3. Enhance EncryptionUtility class


  - Update `servers/utils/encryption.py`
  - Add key parameter to `__init__` for testing/migration support

  - Integrate KeyValidator in `__init__` method
  - Enhance error handling in `encrypt()` method with custom exceptions
  - Enhance error handling in `decrypt()` method with custom exceptions

  - Add `verify_encryption()` method for round-trip testing
  - Add `can_decrypt()` method for ciphertext validation
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 5.1, 5.2, 5.3_


- [ ] 3.1 Write property test for encryption round-trip
  - **Property 8: Encryption round-trip**
  - **Validates: Requirements 3.1**


- [ ] 3.2 Write property test for key mismatch detection
  - **Property 9: Key mismatch detection**
  - **Validates: Requirements 3.3**



- [ ] 3.3 Write property test for corrupted ciphertext detection
  - **Property 10: Corrupted ciphertext detection**
  - **Validates: Requirements 3.4**

- [ ] 3.4 Write unit tests for EncryptionUtility edge cases
  - Test empty string encryption (should raise ValueError)


  - Test None input encryption (should raise ValueError)
  - Test empty ciphertext decryption (should raise ValueError)
  - _Requirements: 3.2_

- [ ] 3.5 Write property tests for error message clarity
  - **Property 14: Invalid key error message clarity**
  - **Property 15: Key mismatch error message clarity**
  - **Property 16: Invalid input error message clarity**


  - **Validates: Requirements 5.1, 5.2, 5.3**


- [ ] 4. Add key validation to Django settings
  - Update `irongate/settings.py`
  - Import KeyValidator

  - Add key validation after loading RCON_ENCRYPTION_KEY
  - Provide clear error message if validation fails
  - Add startup message confirming valid key loaded

  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 5. Enhance generate_key.py script

  - Update `generate_key.py`
  - Add key validation before saving to .env
  - Implement timestamped backup creation for existing .env files
  - Add verification that generated key works with EncryptionUtility
  - Implement rollback on failure (restore backup if created)


  - Add success/failure messages with clear instructions
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [ ] 5.1 Write property test for generated keys validity
  - **Property 4: Generated keys are valid**
  - **Validates: Requirements 2.1**

- [ ] 5.2 Write property test for backup creation
  - **Property 5: Backup creation with timestamp**


  - **Validates: Requirements 2.2**

- [ ] 5.3 Write property test for generated keys compatibility
  - **Property 6: Generated keys work with EncryptionUtility**


  - **Validates: Requirements 2.3**

- [ ] 5.4 Write property test for backup restoration
  - **Property 7: Backup restoration on failure**
  - **Validates: Requirements 2.4**

- [ ] 5.5 Write unit tests for generate_key.py
  - Test key generation with no existing .env
  - Test key generation with existing .env
  - Test user cancellation when .env exists
  - Test backup file naming format


  - _Requirements: 2.1, 2.2, 2.3, 2.4_


- [ ] 6. Create verify_key.py script
  - Create `verify_key.py` in project root
  - Implement command-line argument parsing (--key, --test-passwords)

  - Add current key verification (load from .env and validate)
  - Add specific key verification (validate provided key)
  - Add test mode to verify all stored passwords can be decrypted

  - Display key information (length, encoding, validity)
  - Provide clear success/failure messages
  - _Requirements: 1.1, 3.1, 3.3, 3.4_

- [ ] 6.1 Write unit tests for verify_key.py
  - Test verification with valid key
  - Test verification with invalid key
  - Test password decryption verification


  - Test command-line argument parsing
  - _Requirements: 1.1, 3.1_

- [ ] 7. Create rotate_key.py script
  - Create `rotate_key.py` in project root
  - Implement command-line argument parsing (--old-key, --new-key, --generate-new, --verify-only)
  - Add validation for both old and new keys


  - Implement database backup creation
  - Implement password re-encryption logic (decrypt with old, encrypt with new)
  - Implement .env file update with new key
  - Add verification step (test all passwords decrypt with new key)
  - Implement rollback on failure (restore database and .env from backups)
  - Add progress indicators for long operations
  - _Requirements: 4.1, 4.2, 4.3, 4.4_



- [ ] 7.1 Write property test for key rotation password preservation
  - **Property 11: Key rotation preserves passwords**



  - **Validates: Requirements 4.2**

- [ ] 7.2 Write property test for post-rotation decryption
  - **Property 12: All passwords decryptable after rotation**
  - **Validates: Requirements 4.3**

- [ ] 7.3 Write property test for rotation rollback
  - **Property 13: Rollback on rotation failure**
  - **Validates: Requirements 4.4**

- [ ] 7.4 Write unit tests for rotate_key.py
  - Test rotation with valid keys
  - Test rotation with invalid old key
  - Test rotation with invalid new key
  - Test automatic new key generation
  - Test verify-only mode
  - Test rollback on database error
  - Test rollback on verification failure
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ] 8. Update documentation
  - Update README.md with key management section
  - Add key generation instructions
  - Add key rotation instructions
  - Add troubleshooting section for key-related errors
  - Update .env.example with better comments
  - Create ENCRYPTION.md with detailed encryption documentation
  - _Requirements: 1.2, 1.3, 2.1, 4.1, 5.4_

- [ ] 9. Add file permission checking
  - Create `servers/utils/file_security.py`
  - Implement function to check .env file permissions
  - Add permission check to Django settings startup
  - Add warning if .env has overly permissive permissions
  - Add instructions to fix permissions in warning message
  - _Requirements: 6.3_

- [ ] 9.1 Write unit test for file permission checking
  - Test detection of correct permissions (owner read-only)
  - Test detection of overly permissive permissions
  - Test handling of missing .env file
  - _Requirements: 6.3_

- [ ] 10. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
