#!/usr/bin/env python
"""
Fernet Key Generator for IronGate RCON Portal
Generates a secure encryption key and creates/updates the .env file
"""

from cryptography.fernet import Fernet
import os
import sys
import shutil
from datetime import datetime

# Add the project directory to the path so we can import from servers
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def generate_and_save_key(auto_yes=False):
    """Generate a Fernet key and save it to .env file with validation and backup
    
    Args:
        auto_yes: If True, automatically answer 'yes' to prompts (for automated installation)
    """
    
    # Generate a new Fernet key
    key = Fernet.generate_key()
    key_string = key.decode('utf-8').strip()  # Remove any whitespace/newlines
    
    print("=" * 60)
    print("IronGate - Fernet Encryption Key Generator")
    print("=" * 60)
    print(f"\nGenerated Encryption Key:\n{key_string}\n")
    
    # Validate the generated key before proceeding
    try:
        from servers.utils.key_validator import KeyValidator
        is_valid, error_message = KeyValidator.validate_key(key_string)
        if not is_valid:
            print("❌ ERROR: Generated key failed validation!")
            print(error_message)
            return False
        print("✅ Key validation passed\n")
    except ImportError:
        print("⚠️  Warning: Could not import KeyValidator. Skipping validation.")
    
    # Check if .env file exists
    env_file = '.env'
    env_exists = os.path.exists(env_file)
    backup_file = None
    
    if env_exists:
        print(f"⚠️  Warning: {env_file} already exists!")
        if auto_yes:
            response = 'yes'
            print("Auto-mode: Updating existing .env file...")
        else:
            response = input("Do you want to update it? (yes/no): ").strip().lower()
        
        if response not in ['yes', 'y']:
            print("\n❌ Operation cancelled. Your existing .env file was not modified.")
            print(f"\nIf you want to use this key, manually add this line to your .env file:")
            print(f"RCON_ENCRYPTION_KEY={key_string}")
            return False
        
        # Create timestamped backup
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f'.env.backup_{timestamp}'
        try:
            shutil.copy2(env_file, backup_file)
            print(f"✅ Backup created: {backup_file}")
        except Exception as e:
            print(f"❌ Failed to create backup: {e}")
            return False
    
    try:
        # Read existing .env content if it exists
        existing_content = []
        key_exists = False
        
        if env_exists:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('RCON_ENCRYPTION_KEY='):
                        key_exists = True
                        existing_content.append(f'RCON_ENCRYPTION_KEY={key_string}\n')
                    else:
                        existing_content.append(line)
        
        # Write to .env file
        with open(env_file, 'w', encoding='utf-8') as f:
            if existing_content:
                f.writelines(existing_content)
                if not key_exists:
                    # Ensure file ends with newline before appending
                    if existing_content and not existing_content[-1].endswith('\n'):
                        f.write('\n')
                    f.write(f'RCON_ENCRYPTION_KEY={key_string}\n')
            else:
                # Create new .env file with Django secret key and RCON key
                f.write('# Django Settings\n')
                f.write('SECRET_KEY=your-secret-key-here-change-this-in-production\n')
                f.write('DEBUG=True\n\n')
                f.write('# RCON Encryption Key (DO NOT SHARE OR COMMIT THIS)\n')
                f.write(f'RCON_ENCRYPTION_KEY={key_string}\n')
        
        # Verify the key can be loaded by EncryptionUtility
        try:
            from servers.utils.encryption import EncryptionUtility
            util = EncryptionUtility(key=key_string)
            # Test encryption/decryption
            test_text = "test_password_123"
            if util.verify_encryption(test_text):
                print("✅ Key verification passed - encryption/decryption works correctly")
            else:
                raise Exception("Encryption verification failed")
        except ImportError:
            print("⚠️  Warning: Could not import EncryptionUtility. Skipping verification.")
        except Exception as e:
            print(f"❌ Key verification failed: {e}")
            # Restore backup if verification fails
            if backup_file and os.path.exists(backup_file):
                shutil.copy2(backup_file, env_file)
                print(f"✅ Restored backup from {backup_file}")
            return False
        
        print(f"\n✅ Success! Encryption key has been {'updated' if env_exists else 'created'} in {env_file}")
        print("\n" + "=" * 60)
        print("IMPORTANT SECURITY NOTES:")
        print("=" * 60)
        print("1. Keep this key SECRET - never commit it to version control")
        print("2. The .env file is already in .gitignore")
        print("3. If you lose this key, you won't be able to decrypt existing passwords")
        print("4. For production, also update the SECRET_KEY in .env")
        if backup_file:
            print(f"5. Backup saved as: {backup_file}")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        # Restore backup on failure
        if backup_file and os.path.exists(backup_file):
            try:
                shutil.copy2(backup_file, env_file)
                print(f"✅ Restored backup from {backup_file}")
            except Exception as restore_error:
                print(f"❌ Failed to restore backup: {restore_error}")
        return False

if __name__ == '__main__':
    # Check for --auto-yes flag for automated installation
    auto_yes = '--auto-yes' in sys.argv or '-y' in sys.argv
    success = generate_and_save_key(auto_yes=auto_yes)
    sys.exit(0 if success else 1)
