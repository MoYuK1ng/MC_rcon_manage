#!/usr/bin/env python
"""Test server creation with password"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'irongate.settings')
django.setup()

from servers.models import Server

print("Testing server creation...")

# Delete test server if exists
Server.objects.filter(name="Test Server").delete()

# Create new server
try:
    server = Server(
        name="Test Server",
        ip_address="127.0.0.1",
        rcon_port=25575
    )
    server.set_password("test_password_123")
    server.save()
    
    print(f"✅ Server created successfully!")
    print(f"   Name: {server.name}")
    print(f"   IP: {server.ip_address}:{server.rcon_port}")
    print(f"   Password encrypted: {bool(server.rcon_password_encrypted)}")
    
    # Test password retrieval
    decrypted = server.get_password()
    if decrypted == "test_password_123":
        print(f"✅ Password encryption/decryption works!")
    else:
        print(f"❌ Password mismatch!")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
