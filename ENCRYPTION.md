# Encryption Documentation

## Overview

IronGate uses Fernet symmetric encryption to protect RCON passwords stored in the database. This document explains how encryption works, how to manage encryption keys, and how to troubleshoot encryption-related issues.

## Encryption Algorithm

- **Algorithm**: Fernet (AES-128-CBC with HMAC-SHA256)
- **Key Size**: 32 bytes (256 bits)
- **Key Format**: URL-safe base64-encoded (44 characters)
- **Library**: Python `cryptography` package

## Key Management

### Generating a New Key

To generate a new encryption key:

```bash
python generate_key.py
```

This will:
1. Generate a cryptographically secure 32-byte key
2. Validate the key format
3. Create a timestamped backup of your existing `.env` file (if it exists)
4. Update or create the `.env` file with the new key
5. Verify the key works with the encryption system

**Important**: Keep this key secret! Never commit it to version control.

### Verifying Your Key

To verify that your current encryption key is valid and working:

```bash
python verify_key.py
```

To verify a specific key:

```bash
python verify_key.py --key YOUR_KEY_HERE
```

To test that all stored passwords can be decrypted:

```bash
python verify_key.py --test-passwords
```

### Rotating Keys

If you need to change your encryption key (for security reasons or if the key was compromised):

```bash
python rotate_key.py --generate-new
```

Or with specific keys:

```bash
python rotate_key.py --old-key OLD_KEY --new-key NEW_KEY
```

The rotation process will:
1. Validate both old and new keys
2. Create backups of your database and `.env` file
3. Decrypt all passwords with the old key
4. Re-encrypt all passwords with the new key
5. Update the `.env` file
6. Verify all passwords can be decrypted with the new key
7. Rollback automatically if any step fails

**Before rotating keys**:
- Create a manual backup of your database
- Ensure no one is using the system
- Have the old key available in case you need to rollback

## Environment Configuration

### .env File

Your `.env` file should contain:

```bash
# RCON Encryption Key (DO NOT SHARE OR COMMIT THIS)
RCON_ENCRYPTION_KEY=your-44-character-key-here
```

### Key Validation on Startup

IronGate validates the encryption key when the application starts. If validation fails, you'll see a clear error message with instructions on how to fix it.

## Security Best Practices

### 1. Key Storage

- ✅ Store keys in `.env` file (already in `.gitignore`)
- ✅ Set appropriate file permissions: `chmod 600 .env` (owner read/write only)
- ❌ Never commit keys to version control
- ❌ Never share keys via email, chat, or other insecure channels
- ❌ Never log or display keys in application output

### 2. Key Generation

- ✅ Always use `generate_key.py` to create keys
- ✅ Use cryptographically secure random generation
- ❌ Never create keys manually
- ❌ Never reuse keys from other systems

### 3. Key Rotation

- ✅ Rotate keys periodically (e.g., every 6-12 months)
- ✅ Rotate keys immediately if compromised
- ✅ Create backups before rotation
- ✅ Test the new key before deploying to production

### 4. Backups

- ✅ Keep encrypted backups of your database
- ✅ Store backup encryption keys securely (separate from main key)
- ✅ Test backup restoration regularly
- ❌ Never store backups with keys in the same location

## Troubleshooting

### Error: "RCON_ENCRYPTION_KEY is not set"

**Cause**: The `.env` file is missing or doesn't contain the encryption key.

**Solution**:
```bash
python generate_key.py
```

### Error: "Invalid RCON_ENCRYPTION_KEY format"

**Cause**: The key in your `.env` file is not a valid Fernet key.

**Possible reasons**:
- Key was manually edited
- Key was copied incorrectly
- Key is from a different encryption system

**Solution**:
```bash
# Generate a new key
python generate_key.py

# If you have servers with passwords, you'll need to rotate
python rotate_key.py --old-key OLD_KEY --generate-new
```

### Error: "Failed to decrypt data. The encryption key may have changed"

**Cause**: The current key is different from the key used to encrypt the data.

**Possible reasons**:
- Key was changed without rotating passwords
- `.env` file was restored from an old backup
- Wrong `.env` file is being used

**Solution**:
```bash
# If you have the old key
python rotate_key.py --old-key OLD_KEY --new-key CURRENT_KEY

# If you don't have the old key, you'll need to re-enter all passwords manually
```

### Error: "Key rotation failed"

**Cause**: Something went wrong during key rotation.

**What happens**:
- The system automatically rolls back all changes
- Your database and `.env` file are restored from backups
- No data is lost

**Solution**:
1. Check the error message for specific details
2. Verify both old and new keys are valid:
   ```bash
   python verify_key.py --key OLD_KEY
   python verify_key.py --key NEW_KEY
   ```
3. Ensure the database is not corrupted:
   ```bash
   python verify_key.py --test-passwords
   ```
4. Try rotation again with verbose output

### Passwords Cannot Be Decrypted

**Symptoms**:
- Cannot access servers via RCON
- Admin panel shows decryption errors
- `verify_key.py --test-passwords` fails

**Diagnosis**:
```bash
# Check if key is valid
python verify_key.py

# Test password decryption
python verify_key.py --test-passwords
```

**Solutions**:

1. **If you have the correct key**: Ensure it's in your `.env` file
2. **If key was changed**: Rotate back to the old key or re-enter passwords
3. **If data is corrupted**: Restore from backup

## Technical Details

### Encryption Process

1. User enters RCON password in admin panel
2. Password is validated (non-empty)
3. Password is encrypted using Fernet with the current key
4. Encrypted bytes are stored in `rcon_password_encrypted` field
5. Original password is never stored in plaintext

### Decryption Process

1. Application retrieves encrypted password from database
2. Encrypted bytes are decrypted using Fernet with the current key
3. Decrypted password is used for RCON connection
4. Password is never logged or displayed

### Key Validation

Keys are validated on:
- Application startup
- Key generation
- Key rotation
- Manual verification

Validation checks:
- Key is not None or empty
- Key is exactly 44 characters
- Key is valid URL-safe base64
- Key decodes to exactly 32 bytes
- Key can be used to create a Fernet cipher

### Error Handling

All encryption operations use custom exceptions with clear error messages:

- `MissingKeyError`: Key is not set
- `InvalidKeyFormatError`: Key format is invalid
- `InvalidPlaintextError`: Input to encrypt is invalid
- `KeyMismatchError`: Decryption failed due to wrong key
- `CorruptedDataError`: Encrypted data is corrupted
- `RotationFailedError`: Key rotation failed
- `RollbackFailedError`: Rollback after rotation failure failed

Each exception includes:
- Clear error message
- Detailed explanation
- Step-by-step solution

## Production Deployment

### Initial Setup

1. Generate a production key on the production server:
   ```bash
   python generate_key.py
   ```

2. Set appropriate file permissions:
   ```bash
   chmod 600 .env
   ```

3. Verify the key:
   ```bash
   python verify_key.py
   ```

4. Start the application

### Key Rotation in Production

1. Schedule during maintenance window
2. Notify users of downtime
3. Create manual database backup
4. Run rotation:
   ```bash
   python rotate_key.py --generate-new
   ```
5. Verify all servers are accessible
6. Monitor for any issues

### Disaster Recovery

If you lose your encryption key:

1. **Stop the application immediately**
2. **Do not generate a new key** (this will make existing passwords unrecoverable)
3. Check for key backups:
   - `.env.backup_*` files
   - Server configuration backups
   - Secure key storage (if you have one)
4. If key cannot be recovered:
   - You will need to re-enter all RCON passwords manually
   - Generate a new key: `python generate_key.py`
   - Update all server passwords in admin panel

## API Reference

### KeyValidator

```python
from servers.utils.key_validator import KeyValidator

# Validate a key
is_valid, error_message = KeyValidator.validate_key(key)

# Quick validation
if KeyValidator.is_valid_fernet_key(key):
    # Key is valid
    pass

# Get key information
info = KeyValidator.get_key_info(key)
# Returns: {'length': 44, 'encoding': 'utf8', 'is_url_safe': True, 'decoded_length': 32}
```

### EncryptionUtility

```python
from servers.utils.encryption import EncryptionUtility, get_encryption_utility

# Get singleton instance (uses key from settings)
util = get_encryption_utility()

# Or create with specific key
util = EncryptionUtility(key=my_key)

# Encrypt
encrypted = util.encrypt("my_password")

# Decrypt
password = util.decrypt(encrypted)

# Verify encryption works
if util.verify_encryption("test"):
    # Encryption is working
    pass

# Check if ciphertext can be decrypted
if util.can_decrypt(encrypted_data):
    # Can decrypt
    pass
```

## Support

If you encounter issues not covered in this documentation:

1. Check the error message carefully - it usually contains the solution
2. Run `python verify_key.py` to diagnose key issues
3. Check application logs for detailed error information
4. Ensure you're using the latest version of IronGate
5. Create an issue on GitHub with:
   - Error message (remove any sensitive information)
   - Steps to reproduce
   - Output of `python verify_key.py` (remove the actual key)
