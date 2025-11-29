#!/usr/bin/env python
"""
Fix duplicate whitelist requests before applying unique constraint migration.
This script removes duplicate entries, keeping only the most recent one.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'irongate.settings')
django.setup()

from django.db import connection
from servers.models import WhitelistRequest

def fix_duplicates():
    """Remove duplicate whitelist requests, keeping the most recent one."""
    print("Checking for duplicate whitelist requests...")
    
    # Find duplicates using raw SQL
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT server_id, minecraft_username, COUNT(*) as count
            FROM servers_whitelistrequest
            GROUP BY server_id, minecraft_username
            HAVING COUNT(*) > 1
        """)
        duplicates = cursor.fetchall()
    
    if not duplicates:
        print("✅ No duplicates found!")
        return True
    
    print(f"Found {len(duplicates)} duplicate combinations:")
    
    for server_id, username, count in duplicates:
        print(f"  - Server {server_id}, Username '{username}': {count} entries")
        
        # Get all requests for this combination, ordered by created_at (newest first)
        requests = WhitelistRequest.objects.filter(
            server_id=server_id,
            minecraft_username=username
        ).order_by('-created_at')
        
        # Keep the first (newest) one, delete the rest
        keep = requests.first()
        to_delete = requests.exclude(id=keep.id)
        
        deleted_count = to_delete.count()
        to_delete.delete()
        
        print(f"    ✓ Kept request #{keep.id} (created {keep.created_at}), deleted {deleted_count} older entries")
    
    print(f"\n✅ Fixed {len(duplicates)} duplicate combinations!")
    return True

if __name__ == '__main__':
    try:
        success = fix_duplicates()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
