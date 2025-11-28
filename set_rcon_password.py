#!/usr/bin/env python
"""
Set RCON password for a server
Usage: python set_rcon_password.py
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'irongate.settings')
django.setup()

from servers.models import Server
from getpass import getpass


def main():
    print("=" * 60)
    print("设置服务器 RCON 密码 / Set Server RCON Password")
    print("=" * 60)
    print()
    
    # List all servers
    servers = Server.objects.all()
    
    if not servers.exists():
        print("❌ 没有找到服务器 / No servers found")
        print("请先在管理后台添加服务器 / Please add servers in admin panel first")
        return 1
    
    print("可用服务器 / Available Servers:")
    print()
    for i, server in enumerate(servers, 1):
        print(f"  {i}) {server.name} ({server.ip_address}:{server.rcon_port})")
    print()
    
    # Select server
    try:
        choice = input("选择服务器编号 / Select server number: ").strip()
        server_index = int(choice) - 1
        
        if server_index < 0 or server_index >= len(servers):
            print("❌ 无效的选择 / Invalid choice")
            return 1
        
        server = servers[server_index]
    except (ValueError, IndexError):
        print("❌ 无效的输入 / Invalid input")
        return 1
    
    print()
    print(f"设置服务器: {server.name}")
    print(f"Setting password for: {server.name}")
    print()
    
    # Get password
    password = getpass("输入 RCON 密码 / Enter RCON password: ")
    
    if not password:
        print("❌ 密码不能为空 / Password cannot be empty")
        return 1
    
    # Confirm password
    password_confirm = getpass("确认密码 / Confirm password: ")
    
    if password != password_confirm:
        print("❌ 密码不匹配 / Passwords do not match")
        return 1
    
    # Set password
    try:
        server.set_password(password)
        server.save()
        print()
        print("✅ 密码设置成功！/ Password set successfully!")
        print(f"   服务器 / Server: {server.name}")
        print(f"   地址 / Address: {server.ip_address}:{server.rcon_port}")
        print()
        return 0
    except Exception as e:
        print()
        print(f"❌ 设置失败 / Failed to set password: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
