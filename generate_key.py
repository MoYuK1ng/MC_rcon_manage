#!/usr/bin/env python
"""
Fernet Key Generator for IronGate RCON Portal
Generates a secure encryption key and creates/updates the .env file
"""

from cryptography.fernet import Fernet
import os

def generate_and_save_key():
    """Generate a Fernet key and save it to .env file"""
    
    # Generate a new Fernet key
    key = Fernet.generate_key()
    key_string = key.decode('utf-8')
    
    print("=" * 60)
    print("IronGate - Fernet Encryption Key Generator")
    print("=" * 60)
    print(f"\nGenerated Encryption Key:\n{key_string}\n")
    
    # Check if .env file exists
    env_file = '.env'
    env_exists = os.path.exists(env_file)
    
    if env_exists:
        print(f"⚠️  Warning: {env_file} already exists!")
        response = input("Do you want to update it? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("\n❌ Operation cancelled. Your existing .env file was not modified.")
            print(f"\nIf you want to use this key, manually add this line to your .env file:")
            print(f"RCON_ENCRYPTION_KEY={key_string}")
            return
    
    # Read existing .env content if it exists
    existing_content = []
    key_exists = False
    
    if env_exists:
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('RCON_ENCRYPTION_KEY='):
                    key_exists = True
                    existing_content.append(f'RCON_ENCRYPTION_KEY={key_string}\n')
                else:
                    existing_content.append(line)
    
    # Write to .env file
    with open(env_file, 'w') as f:
        if existing_content:
            f.writelines(existing_content)
            if not key_exists:
                f.write(f'\nRCON_ENCRYPTION_KEY={key_string}\n')
        else:
            # Create new .env file with Django secret key and RCON key
            f.write('# Django Settings\n')
            f.write('SECRET_KEY=your-secret-key-here-change-this-in-production\n')
            f.write('DEBUG=True\n\n')
            f.write('# RCON Encryption Key (DO NOT SHARE OR COMMIT THIS)\n')
            f.write(f'RCON_ENCRYPTION_KEY={key_string}\n')
    
    print(f"\n✅ Success! Encryption key has been {'updated' if env_exists else 'created'} in {env_file}")
    print("\n" + "=" * 60)
    print("IMPORTANT SECURITY NOTES:")
    print("=" * 60)
    print("1. Keep this key SECRET - never commit it to version control")
    print("2. The .env file is already in .gitignore")
    print("3. If you lose this key, you won't be able to decrypt existing passwords")
    print("4. For production, also update the SECRET_KEY in .env")
    print("=" * 60)

if __name__ == '__main__':
    generate_and_save_key()
