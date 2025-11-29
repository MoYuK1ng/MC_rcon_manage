#!/usr/bin/env python
"""
Encryption Key Rotation Tool for MC RCON Manager
Safely rotates encryption keys and re-encrypts all stored passwords
"""

import os
import sys
import argparse
import shutil
import django
from datetime import datetime
from cryptography.fernet import Fernet

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'irongate.settings')

# Temporarily disable key validation during rotation
os.environ['SKIP_KEY_VALIDATION'] = '1'

django.setup()

from servers.utils.key_validator import KeyValidator
from servers.utils.encryption import EncryptionUtility
from servers.models import Server


def create_database_backup():
    """Create a backup of the database"""
    db_file = 'db.sqlite3'
    
    if not os.path.exists(db_file):
        print("⚠️  Warning: Database file not found")
        return None
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'db.sqlite3.backup_{timestamp}'
    
    try:
        shutil.copy2(db_file, backup_file)
        print(f"✅ Database backup created: {backup_file}")
        return backup_file
    except Exception as e:
        print(f"❌ Failed to create database backup: {e}")
        return None


def create_env_backup():
    """Create a backup of the .env file"""
    env_file = '.env'
    
    if not os.path.exists(env_file):
        print("⚠️  Warning: .env file not found")
        return None
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'.env.backup_{timestamp}'
    
    try:
        shutil.copy2(env_file, backup_file)
        print(f"✅ .env backup created: {backup_file}")
        return backup_file
    except Exception as e:
        print(f"❌ Failed to create .env backup: {e}")
        return None


def update_env_file(new_key):
    """Update the .env file with the new key"""
    env_file = '.env'
    
    if not os.path.exists(env_file):
        print(f"❌ .env file not found")
        return False
    
    try:
        # Read existing content
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Update the key
        with open(env_file, 'w', encoding='utf-8') as f:
            key_updated = False
            for line in lines:
                if line.startswith('RCON_ENCRYPTION_KEY='):
                    f.write(f'RCON_ENCRYPTION_KEY={new_key}\n')
                    key_updated = True
                else:
                    f.write(line)
            
            # If key wasn't in file, add it
            if not key_updated:
                f.write(f'\nRCON_ENCRYPTION_KEY={new_key}\n')
        
        print(f"✅ .env file updated with new key")
        return True
    except Exception as e:
        print(f"❌ Failed to update .env file: {e}")
        return False


def rotate_keys(old_key, new_key, verify_only=False):
    """Rotate encryption keys and re-encrypt all passwords"""
    
    print("=" * 70)
    print("ENCRYPTION KEY ROTATION")
    print("=" * 70)
    
    # Validate old key
    print("\n🔍 Validating old key...")
    is_valid, error_message = KeyValidator.validate_key(old_key)
    if not is_valid:
        print(f"❌ Old key is invalid:")
        print(error_message)
        return False
    print("✅ Old key is valid")
    
    # Validate new key
    print("\n🔍 Validating new key...")
    is_valid, error_message = KeyValidator.validate_key(new_key)
    if not is_valid:
        print(f"❌ New key is invalid:")
        print(error_message)
        return False
    print("✅ New key is valid")
    
    # Create encryption utilities
    old_util = EncryptionUtility(key=old_key)
    new_util = EncryptionUtility(key=new_key)
    
    # Get all servers
    servers = Server.objects.all()
    
    if not servers.exists():
        print("\n⚠️  No servers found in database")
        if verify_only:
            return True
        # Still update the .env file
        return update_env_file(new_key)
    
    print(f"\n📊 Found {servers.count()} server(s) with passwords to rotate")
    
    if verify_only:
        print("\n🔍 VERIFY-ONLY MODE: Testing decryption with old key...")
        fail_count = 0
        for server in servers:
            if not server.rcon_password_encrypted:
                continue
            try:
                password = old_util.decrypt(server.rcon_password_encrypted)
                print(f"  ✅ {server.name}: Can decrypt")
            except Exception as e:
                print(f"  ❌ {server.name}: Cannot decrypt - {e}")
                fail_count += 1
        
        if fail_count > 0:
            print(f"\n❌ {fail_count} password(s) cannot be decrypted with old key")
            return False
        else:
            print(f"\n✅ All passwords can be decrypted with old key")
            return True
    
    # Create backups
    print("\n💾 Creating backups...")
    db_backup = create_database_backup()
    env_backup = create_env_backup()
    
    if not db_backup:
        print("❌ Cannot proceed without database backup")
        return False
    
    # Re-encrypt passwords
    print("\n🔄 Re-encrypting passwords...")
    success_count = 0
    fail_count = 0
    failed_servers = []
    
    for server in servers:
        if not server.rcon_password_encrypted:
            print(f"  ⚠️  {server.name}: No password stored")
            continue
        
        try:
            # Decrypt with old key
            password = old_util.decrypt(server.rcon_password_encrypted)
            
            # Encrypt with new key
            new_encrypted = new_util.encrypt(password)
            
            # Update server
            server.rcon_password_encrypted = new_encrypted
            server.save()
            
            print(f"  ✅ {server.name}: Re-encrypted successfully")
            success_count += 1
        except Exception as e:
            print(f"  ❌ {server.name}: Failed - {e}")
            fail_count += 1
            failed_servers.append(server.name)
    
    if fail_count > 0:
        print(f"\n❌ {fail_count} password(s) failed to re-encrypt")
        print("Rolling back changes...")
        
        # Restore database backup
        if db_backup and os.path.exists(db_backup):
            try:
                shutil.copy2(db_backup, 'db.sqlite3')
                print(f"✅ Database restored from backup")
            except Exception as e:
                print(f"❌ CRITICAL: Failed to restore database: {e}")
                print(f"   Manual restoration required from: {db_backup}")
                return False
        
        return False
    
    # Update .env file
    print("\n📝 Updating .env file...")
    if not update_env_file(new_key):
        print("❌ Failed to update .env file")
        print("Rolling back changes...")
        
        # Restore database backup
        if db_backup and os.path.exists(db_backup):
            shutil.copy2(db_backup, 'db.sqlite3')
            print(f"✅ Database restored from backup")
        
        return False
    
    # Verify all passwords can be decrypted with new key
    print("\n🔍 Verifying all passwords with new key...")
    verification_failed = False
    
    for server in servers:
        if not server.rcon_password_encrypted:
            continue
        
        try:
            password = new_util.decrypt(server.rcon_password_encrypted)
            print(f"  ✅ {server.name}: Verification passed")
        except Exception as e:
            print(f"  ❌ {server.name}: Verification failed - {e}")
            verification_failed = True
    
    if verification_failed:
        print("\n❌ Verification failed! Rolling back...")
        
        # Restore backups
        if db_backup and os.path.exists(db_backup):
            shutil.copy2(db_backup, 'db.sqlite3')
            print(f"✅ Database restored from backup")
        
        if env_backup and os.path.exists(env_backup):
            shutil.copy2(env_backup, '.env')
            print(f"✅ .env restored from backup")
        
        return False
    
    print("\n" + "=" * 70)
    print(f"✅ KEY ROTATION SUCCESSFUL")
    print("=" * 70)
    print(f"  Re-encrypted: {success_count} password(s)")
    print(f"  Backups saved:")
    if db_backup:
        print(f"    - {db_backup}")
    if env_backup:
        print(f"    - {env_backup}")
    print("=" * 70)
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Rotate RCON encryption key and re-encrypt all passwords',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python rotate_key.py --old-key <old> --new-key <new>  # Rotate with specific keys
  python rotate_key.py --generate-new                   # Generate new key automatically
  python rotate_key.py --verify-only                    # Verify current key works
        """
    )
    
    parser.add_argument(
        '--old-key',
        type=str,
        help='Current encryption key (from .env if not specified)'
    )
    
    parser.add_argument(
        '--new-key',
        type=str,
        help='New encryption key to use'
    )
    
    parser.add_argument(
        '--generate-new',
        action='store_true',
        help='Automatically generate a new key'
    )
    
    parser.add_argument(
        '--verify-only',
        action='store_true',
        help='Only verify that all passwords can be decrypted (no rotation)'
    )
    
    args = parser.parse_args()
    
    # Load old key from .env if not specified
    if not args.old_key:
        from dotenv import load_dotenv
        load_dotenv()
        args.old_key = os.getenv('RCON_ENCRYPTION_KEY')
        
        if not args.old_key:
            print("❌ ERROR: No old key specified and RCON_ENCRYPTION_KEY not found in .env")
            print("Use --old-key to specify the current key")
            sys.exit(1)
    
    # Handle verify-only mode
    if args.verify_only:
        success = rotate_keys(args.old_key, args.old_key, verify_only=True)
        sys.exit(0 if success else 1)
    
    # Generate new key if requested
    if args.generate_new:
        args.new_key = Fernet.generate_key().decode('utf-8')
        print(f"🔑 Generated new key: {args.new_key}\n")
    
    # Validate arguments
    if not args.new_key:
        print("❌ ERROR: No new key specified")
        print("Use --new-key to specify a key or --generate-new to generate one")
        sys.exit(1)
    
    # Confirm rotation
    print("\n⚠️  WARNING: This will re-encrypt all RCON passwords")
    print("Make sure you have backups before proceeding!")
    response = input("\nContinue with key rotation? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y']:
        print("\n❌ Operation cancelled")
        sys.exit(1)
    
    # Perform rotation
    success = rotate_keys(args.old_key, args.new_key)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
