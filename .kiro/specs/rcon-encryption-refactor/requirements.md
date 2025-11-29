# Requirements Document

## Introduction

This document specifies the requirements for refactoring the RCON encryption key management system in IronGate. The current implementation has issues with key validation, error messaging, and key lifecycle management. This refactor will improve security, user experience, and maintainability.

## Glossary

- **RCON**: Remote Console protocol for Minecraft server administration
- **Fernet**: Symmetric encryption algorithm from the cryptography library
- **Encryption Key**: A 32-byte URL-safe base64-encoded key used by Fernet
- **IronGate**: The Django-based RCON management portal
- **Environment Variable**: Configuration value stored in .env file
- **Key Rotation**: The process of replacing an old encryption key with a new one

## Requirements

### Requirement 1: Key Format Validation

**User Story:** As a system administrator, I want the system to validate encryption keys on startup, so that I receive clear error messages if the key format is invalid.

#### Acceptance Criteria

1. WHEN the system loads the RCON_ENCRYPTION_KEY from environment variables THEN the system SHALL validate that the key is a valid 32-byte URL-safe base64-encoded Fernet key
2. WHEN the encryption key validation fails THEN the system SHALL raise an exception with a clear message indicating the key format is invalid and instructions to run generate_key.py
3. WHEN the encryption key is missing THEN the system SHALL raise an exception with a clear message indicating the key is required and instructions to run generate_key.py
4. WHEN the encryption key contains invalid characters THEN the system SHALL detect this during validation and provide a specific error message about invalid base64 encoding

### Requirement 2: Key Generation Enhancement

**User Story:** As a system administrator, I want the key generation script to validate the generated key immediately, so that I can be confident the key will work correctly.

#### Acceptance Criteria

1. WHEN generate_key.py creates a new encryption key THEN the system SHALL validate the key format before saving it to .env
2. WHEN generate_key.py updates an existing .env file THEN the system SHALL create a backup of the old .env file with timestamp
3. WHEN generate_key.py completes successfully THEN the system SHALL verify the key can be loaded by the EncryptionUtility class
4. WHEN the key generation process fails THEN the system SHALL restore the backup .env file if one was created

### Requirement 3: Encryption Round-Trip Validation

**User Story:** As a developer, I want to ensure encryption and decryption work correctly, so that RCON passwords are never lost or corrupted.

#### Acceptance Criteria

1. WHEN a plaintext password is encrypted and then decrypted THEN the system SHALL return the original plaintext value
2. WHEN encrypting an empty string THEN the system SHALL raise a ValueError with a clear message
3. WHEN decrypting with a different key than was used for encryption THEN the system SHALL raise an InvalidToken exception with a clear message
4. WHEN decrypting corrupted ciphertext THEN the system SHALL raise an InvalidToken exception with a clear message

### Requirement 4: Key Lifecycle Management

**User Story:** As a system administrator, I want to rotate encryption keys safely, so that I can maintain security without losing access to existing encrypted passwords.

#### Acceptance Criteria

1. WHEN a key rotation is initiated THEN the system SHALL provide a migration script that re-encrypts all existing passwords with the new key
2. WHEN re-encrypting passwords during key rotation THEN the system SHALL decrypt with the old key and encrypt with the new key
3. WHEN key rotation completes successfully THEN the system SHALL verify all passwords can be decrypted with the new key
4. WHEN key rotation fails THEN the system SHALL rollback all changes and restore the original encryption key

### Requirement 5: Error Message Clarity

**User Story:** As a user, I want clear error messages when encryption fails, so that I can understand whether the problem is with my password or the system configuration.

#### Acceptance Criteria

1. WHEN encryption fails due to an invalid key THEN the system SHALL display an error message that clearly states the encryption key is invalid
2. WHEN decryption fails due to a key mismatch THEN the system SHALL display an error message indicating the key may have changed
3. WHEN encryption fails due to invalid input THEN the system SHALL display an error message that clearly identifies the input problem
4. WHEN the .env file is missing THEN the system SHALL display an error message with step-by-step instructions to create it

### Requirement 6: Key Security Best Practices

**User Story:** As a security-conscious administrator, I want the system to follow encryption best practices, so that RCON passwords are protected against common attacks.

#### Acceptance Criteria

1. WHEN generating a new encryption key THEN the system SHALL use cryptographically secure random number generation
2. WHEN storing the encryption key THEN the system SHALL ensure it is never logged or displayed in plain text except during initial generation
3. WHEN the application starts THEN the system SHALL verify the .env file has appropriate file permissions (readable only by owner)
4. WHEN encryption operations occur THEN the system SHALL use constant-time comparison operations to prevent timing attacks
