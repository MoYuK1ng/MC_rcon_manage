#!/usr/bin/env python
"""
Change user password script for MC RCON Manager
Allows changing password for any user by username
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'irongate.settings')
django.setup()

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password


def list_users():
    """List all users in the system"""
    users = User.objects.all().order_by('username')
    
    if not users:
        print("No users found in the system.")
        return []
    
    print("\n" + "="*60)
    print("Current Users:")
    print("="*60)
    print(f"{'Username':<20} {'Staff':<10} {'Superuser':<12} {'Active':<10}")
    print("-"*60)
    
    for user in users:
        staff = "✓" if user.is_staff else "✗"
        superuser = "✓" if user.is_superuser else "✗"
        active = "✓" if user.is_active else "✗"
        print(f"{user.username:<20} {staff:<10} {superuser:<12} {active:<10}")
    
    print("="*60 + "\n")
    return users


def get_user_by_username(username):
    """Get user by username"""
    try:
        return User.objects.get(username=username)
    except User.DoesNotExist:
        return None


def change_user_password(username, new_password):
    """Change password for a user"""
    user = get_user_by_username(username)
    
    if not user:
        return False, f"User '{username}' not found."
    
    # Validate password
    try:
        validate_password(new_password, user)
    except ValidationError as e:
        return False, f"Password validation failed:\n" + "\n".join(e.messages)
    
    # Set new password
    user.set_password(new_password)
    user.save()
    
    return True, f"Password changed successfully for user '{username}'."


def interactive_mode():
    """Interactive mode for changing password"""
    print("\n" + "="*60)
    print("MC RCON Manager - Change User Password")
    print("="*60 + "\n")
    
    # List all users
    users = list_users()
    
    if not users:
        print("Please create a user first using: python manage.py createsuperuser")
        return False
    
    # Get username
    while True:
        username = input("Enter username (or 'q' to quit): ").strip()
        
        if username.lower() == 'q':
            print("Cancelled.")
            return False
        
        if not username:
            print("Username cannot be empty. Please try again.\n")
            continue
        
        user = get_user_by_username(username)
        if not user:
            print(f"User '{username}' not found. Please try again.\n")
            continue
        
        break
    
    # Show user info
    print(f"\nUser Information:")
    print(f"  Username: {user.username}")
    print(f"  Staff: {'Yes' if user.is_staff else 'No'}")
    print(f"  Superuser: {'Yes' if user.is_superuser else 'No'}")
    print(f"  Active: {'Yes' if user.is_active else 'No'}")
    print()
    
    # Confirm
    confirm = input(f"Change password for '{username}'? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        return False
    
    # Get new password
    print("\nPassword Requirements:")
    print("  - At least 8 characters")
    print("  - Cannot be too similar to username")
    print("  - Cannot be entirely numeric")
    print("  - Cannot be a commonly used password")
    print()
    
    while True:
        new_password = input("Enter new password: ").strip()
        
        if not new_password:
            print("Password cannot be empty. Please try again.\n")
            continue
        
        confirm_password = input("Confirm new password: ").strip()
        
        if new_password != confirm_password:
            print("Passwords do not match. Please try again.\n")
            continue
        
        # Try to change password
        success, message = change_user_password(username, new_password)
        
        if success:
            print(f"\n✓ {message}")
            return True
        else:
            print(f"\n✗ {message}\n")
            retry = input("Try again? (y/n): ").strip().lower()
            if retry != 'y':
                print("Cancelled.")
                return False


def main():
    """Main function"""
    if len(sys.argv) > 1:
        # Command line mode
        if sys.argv[1] == '--list':
            list_users()
        elif sys.argv[1] == '--help':
            print("Usage:")
            print("  python change_password.py              # Interactive mode")
            print("  python change_password.py --list       # List all users")
            print("  python change_password.py --help       # Show this help")
        else:
            print("Unknown option. Use --help for usage information.")
            sys.exit(1)
    else:
        # Interactive mode
        success = interactive_mode()
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
