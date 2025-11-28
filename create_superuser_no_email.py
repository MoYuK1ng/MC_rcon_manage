#!/usr/bin/env python
"""
Create superuser without email prompt
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'irongate.settings')
django.setup()

from django.contrib.auth.models import User
from django.core.management import call_command


def create_superuser():
    """Create superuser without email"""
    print("\n创建管理员账户 / Create Administrator Account")
    print("="*60)
    
    while True:
        username = input("\n用户名 / Username: ").strip()
        
        if not username:
            print("用户名不能为空 / Username cannot be empty")
            continue
        
        if User.objects.filter(username=username).exists():
            print(f"用户名 '{username}' 已存在 / Username '{username}' already exists")
            continue
        
        break
    
    while True:
        password = input("密码 / Password: ").strip()
        
        if not password:
            print("密码不能为空 / Password cannot be empty")
            continue
        
        if len(password) < 8:
            print("密码至少需要8个字符 / Password must be at least 8 characters")
            continue
        
        password_confirm = input("确认密码 / Confirm Password: ").strip()
        
        if password != password_confirm:
            print("两次密码不一致 / Passwords do not match")
            continue
        
        break
    
    # Create superuser
    user = User.objects.create_superuser(
        username=username,
        password=password,
        email=''  # No email required
    )
    
    print(f"\n✓ 管理员账户创建成功 / Administrator account created successfully")
    print(f"  用户名 / Username: {username}")
    print(f"  角色 / Role: 管理员 / Administrator")
    
    return True


if __name__ == '__main__':
    try:
        create_superuser()
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\n已取消 / Cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n错误 / Error: {e}")
        sys.exit(1)
