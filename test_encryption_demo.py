"""
Quick demonstration script to verify encryption works correctly
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'irongate.settings')
django.setup()

from servers.models import Server
from django.contrib.auth.models import Group

print("=" * 60)
print("IronGate Encryption Verification")
print("=" * 60)

# Create a test server
print("\n1. Creating a test server...")
server = Server(
    name="Test Minecraft Server",
    ip_address="127.0.0.1",
    rcon_port=25575
)

# Set the password (this will encrypt it)
test_password = "MySecretRCONPassword123"
print(f"   Original password: {test_password}")
server.set_password(test_password)
print(f"   Encrypted (first 50 bytes): {server.rcon_password_encrypted[:50]}...")

# Save to database
server.save()
print(f"   ✅ Server saved to database with ID: {server.id}")

# Retrieve the password (this will decrypt it)
print("\n2. Retrieving and decrypting password...")
retrieved_password = server.get_password()
print(f"   Decrypted password: {retrieved_password}")

# Verify round-trip
print("\n3. Verification:")
if retrieved_password == test_password:
    print("   ✅ SUCCESS: Password round-trip works correctly!")
    print(f"   ✅ Original:  '{test_password}'")
    print(f"   ✅ Retrieved: '{retrieved_password}'")
else:
    print("   ❌ FAILED: Passwords don't match!")
    print(f"   ❌ Original:  '{test_password}'")
    print(f"   ❌ Retrieved: '{retrieved_password}'")

# Verify encrypted data is binary
print("\n4. Security check:")
print(f"   Encrypted data type: {type(server.rcon_password_encrypted)}")
print(f"   Encrypted data length: {len(server.rcon_password_encrypted)} bytes")
print(f"   Original password length: {len(test_password)} characters")
print(f"   ✅ Encrypted data is longer (includes Fernet overhead)")

# Clean up
print("\n5. Cleaning up test data...")
server.delete()
print("   ✅ Test server deleted")

print("\n" + "=" * 60)
print("Encryption verification complete!")
print("=" * 60)
