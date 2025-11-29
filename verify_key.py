#!/usr/bin/env python
"""
Encryption Key Verification Tool for IronGate RCON Portal
Verifies encryption keys and tests password decryption
"""

import os
import sys
import argparse
import django

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'irongate.settings')
django.setup()

from servers.utils.key_validator import KeyValidator
from servers.utils.encryption import EncryptionUtility
from servers.models import Server


def verify_current_key():
    """Verify the current key from .env file"""
    print("=" * 70)
    print("VERIFYING CURRENT ENCRYPTION KEY")
    print("=" * 70)
    
    # Load key from environment
    from dotenv import load_dotenv
    load_dotenv()
    
    key = os.getenv('RCON_ENCRYPTION_KEY')
    
    if not key:
        print("\n❌ ERROR: RCON_ENCRYPTION_KEY not found in .env file")
        print("\nSolution: Run 'python generate_key.py' to generate a new encryption key")
        return False
    
    print(f"\n📋 Key Information:")
    info = KeyValidator.get_key_info(key)
    print(f"   Length: {info['length']} characters")
    print(f"   Encoding: {info['encoding']}")
    print(f"   URL-safe: {info['is_url_safe']}")
    print(f"   Decoded length: {info['decoded_length']} bytes")
    
    # Validate the key
    print(f"\n🔍 Validating key format...")
    is_valid, error_message = KeyValidator.validate_key(key)
    
    if not is_valid:
        print(f"\n❌ VALIDATION FAILED:")
        print(error_message)
        return False
    
    print("✅ Key format is valid")
    
    # Test encryption/decryption
    print(f"\n🔐 Testing encryption/decryption...")
    try:
        util = EncryptionUtility(key=key)
        test_password = "test_password_123"
        
        if util.verify_encryption(test_password):
            print("✅ Encryption/decryption works correctly")
        else:
            print("❌ Encryption/decryption test failed")
            return False
    except Exception as e:
        print(f"❌ Encryption test failed: {e}")
        return False
    
    print("\n" + "=" * 70)
    print("✅ ALL CHECKS PASSED - Encryption key is valid and working")
    print("=" * 70)
    return True


def verify_specific_key(key):
    """Verify a specific key provided as argument"""
    print("=" * 70)
    print("VERIFYING PROVIDED ENCRYPTION KEY")
    print("=" * 70)
    
    print(f"\n📋 Key Information:")
    info = KeyValidator.get_key_info(key)
    print(f"   Length: {info['length']} characters")
    print(f"   Encoding: {info['encoding']}")
    print(f"   URL-safe: {info['is_url_safe']}")
    print(f"   Decoded length: {info['decoded_length']} bytes")
    
    # Validate the key
    print(f"\n🔍 Validating key format...")
    is_valid, error_message = KeyValidator.validate_key(key)
    
    if not is_valid:
        print(f"\n❌ VALIDATION FAILED:")
        print(error_message)
        return False
    
    print("✅ Key format is valid")
    
    # Test encryption/decryption
    print(f"\n🔐 Testing encryption/decryption...")
    try:
        util = EncryptionUtility(key=key)
        test_password = "test_password_123"
        
        if util.verify_encryption(test_password):
            print("✅ Encryption/decryption works correctly")
        else:
            print("❌ Encryption/decryption test failed")
            return False
    except Exception as e:
        print(f"❌ Encryption test failed: {e}")
        return False
    
    print("\n" + "=" * 70)
    print("✅ ALL CHECKS PASSED - Provided key is valid and working")
    print("=" * 70)
    return True


def test_stored_passwords():
    """Test that all stored passwords can be decrypted"""
    print("=" * 70)
    print("TESTING STORED PASSWORD DECRYPTION")
    print("=" * 70)
    
    servers = Server.objects.all()
    
    if not servers.exists():
        print("\n⚠️  No servers found in database")
        return True
    
    print(f"\n📊 Found {servers.count()} server(s) to test\n")
    
    success_count = 0
    fail_count = 0
    
    for server in servers:
        print(f"Testing: {server.name} ({server.ip_address}:{server.rcon_port})")
        
        if not server.rcon_password_encrypted:
            print("  ⚠️  No password stored")
            continue
        
        try:
            # Try to decrypt the password
            password = server.get_password()
            print(f"  ✅ Successfully decrypted (length: {len(password)} characters)")
            success_count += 1
        except Exception as e:
            print(f"  ❌ Decryption failed: {e}")
            fail_count += 1
    
    print("\n" + "=" * 70)
    print(f"RESULTS: {success_count} successful, {fail_count} failed")
    print("=" * 70)
    
    if fail_count > 0:
        print("\n⚠️  Some passwords could not be decrypted!")
        print("This may indicate:")
        print("  1. The encryption key has changed")
        print("  2. The data is corrupted")
        print("\nSolution: Run 'python rotate_key.py' to re-encrypt with current key")
        return False
    
    print("\n✅ All stored passwords can be decrypted successfully")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Verify RCON encryption key and test password decryption',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python verify_key.py                    # Verify current key from .env
  python verify_key.py --key <key>        # Verify specific key
  python verify_key.py --test-passwords   # Test all stored passwords
        """
    )
    
    parser.add_argument(
        '--key',
        type=str,
        help='Specific key to verify (instead of current key from .env)'
    )
    
    parser.add_argument(
        '--test-passwords',
        action='store_true',
        help='Test that all stored passwords can be decrypted'
    )
    
    args = parser.parse_args()
    
    success = True
    
    if args.key:
        # Verify specific key
        success = verify_specific_key(args.key)
    elif args.test_passwords:
        # Test stored passwords
        success = test_stored_passwords()
    else:
        # Verify current key
        success = verify_current_key()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
