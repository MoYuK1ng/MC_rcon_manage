#!/usr/bin/env python
"""
Test script for change_password.py
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'irongate.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import TestCase


def test_password_change():
    """Test password change functionality"""
    print("\n" + "="*60)
    print("Testing Password Change Functionality")
    print("="*60 + "\n")
    
    # Test 1: Create test user
    print("Test 1: Creating test user...")
    test_username = "test_user_temp"
    
    # Clean up if exists
    User.objects.filter(username=test_username).delete()
    
    user = User.objects.create_user(
        username=test_username,
        password="old_password_123"
    )
    print(f"✓ Created user: {test_username}")
    
    # Test 2: Verify old password works
    print("\nTest 2: Verifying old password...")
    if user.check_password("old_password_123"):
        print("✓ Old password works")
    else:
        print("✗ Old password doesn't work")
        return False
    
    # Test 3: Change password
    print("\nTest 3: Changing password...")
    new_password = "new_password_456"
    user.set_password(new_password)
    user.save()
    
    # Refresh from database
    user = User.objects.get(username=test_username)
    print("✓ Password changed")
    
    # Test 4: Verify new password works
    print("\nTest 4: Verifying new password...")
    if user.check_password(new_password):
        print("✓ New password works")
    else:
        print("✗ New password doesn't work")
        return False
    
    # Test 5: Verify old password doesn't work
    print("\nTest 5: Verifying old password no longer works...")
    if not user.check_password("old_password_123"):
        print("✓ Old password correctly rejected")
    else:
        print("✗ Old password still works (should not)")
        return False
    
    # Test 6: Test password validation
    print("\nTest 6: Testing password validation...")
    from django.contrib.auth.password_validation import validate_password
    from django.core.exceptions import ValidationError
    
    # Test weak password
    try:
        validate_password("123", user)
        print("✗ Weak password was accepted (should reject)")
        return False
    except ValidationError:
        print("✓ Weak password correctly rejected")
    
    # Test numeric-only password
    try:
        validate_password("12345678", user)
        print("✗ Numeric-only password was accepted (should reject)")
        return False
    except ValidationError:
        print("✓ Numeric-only password correctly rejected")
    
    # Test common password
    try:
        validate_password("password", user)
        print("✗ Common password was accepted (should reject)")
        return False
    except ValidationError:
        print("✓ Common password correctly rejected")
    
    # Test 7: Clean up
    print("\nTest 7: Cleaning up...")
    user.delete()
    print(f"✓ Deleted test user: {test_username}")
    
    print("\n" + "="*60)
    print("All tests passed! ✓")
    print("="*60 + "\n")
    
    return True


if __name__ == '__main__':
    try:
        success = test_password_change()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
