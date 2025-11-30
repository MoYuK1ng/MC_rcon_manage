#!/usr/bin/env python3
"""
MC RCON Manager - Backup Management Utility
备份管理工具

This utility provides easy access to backup operations without needing
to use Django management commands directly.

Usage:
    python backup_manager.py --help
    python backup_manager.py backup
    python backup_manager.py list
    python backup_manager.py cleanup
"""
import os
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime


def setup_django():
    """设置Django环境"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'irongate.settings')
    import django
    django.setup()


def run_backup_command(args_list):
    """运行Django备份管理命令"""
    cmd = [sys.executable, 'manage.py', 'backup_database'] + args_list
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("错误输出:", result.stderr)
    return result.returncode == 0


def list_backups():
    """列出所有备份文件"""
    setup_django()
    from django.conf import settings
    
    backup_path = Path(getattr(settings, 'BACKUP_PATH', '/opt/mc_rcon/backups'))
    
    if not backup_path.exists():
        print(f"备份目录不存在: {backup_path}")
        return
    
    backup_files = list(backup_path.glob('db_backup_*.sqlite3'))
    
    if not backup_files:
        print("未找到备份文件")
        return
    
    # 按修改时间排序
    backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    print(f"备份目录: {backup_path}")
    print(f"找到 {len(backup_files)} 个备份文件:")
    print()
    
    for i, backup_file in enumerate(backup_files, 1):
        stat = backup_file.stat()
        size_mb = stat.st_size / (1024 * 1024)
        mtime = datetime.fromtimestamp(stat.st_mtime)
        
        print(f"{i:2d}. {backup_file.name}")
        print(f"    大小: {size_mb:.2f} MB")
        print(f"    时间: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        print()


def cleanup_old_backups():
    """清理旧备份（交互式）"""
    setup_django()
    from django.conf import settings
    
    backup_path = Path(getattr(settings, 'BACKUP_PATH', '/opt/mc_rcon/backups'))
    max_count = getattr(settings, 'BACKUP_MAX_COUNT', 5)
    
    if not backup_path.exists():
        print(f"备份目录不存在: {backup_path}")
        return
    
    backup_files = list(backup_path.glob('db_backup_*.sqlite3'))
    backup_files.sort(key=lambda x: x.stat().st_mtime)
    
    if len(backup_files) <= max_count:
        print(f"当前备份数量 ({len(backup_files)}) 未超过限制 ({max_count})")
        return
    
    files_to_delete = backup_files[:-max_count]
    
    print(f"当前备份数量: {len(backup_files)}")
    print(f"配置的最大数量: {max_count}")
    print(f"需要删除 {len(files_to_delete)} 个旧备份:")
    print()
    
    for file_path in files_to_delete:
        mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        print(f"  - {file_path.name} ({mtime.strftime('%Y-%m-%d %H:%M:%S')})")
    
    print()
    confirm = input("确认删除这些文件? (y/N): ")
    
    if confirm.lower() == 'y':
        for file_path in files_to_delete:
            try:
                file_path.unlink()
                print(f"✅ 已删除: {file_path.name}")
            except Exception as e:
                print(f"❌ 删除失败: {file_path.name} - {e}")
    else:
        print("操作已取消")


def main():
    parser = argparse.ArgumentParser(
        description='MC RCON Manager 备份管理工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python backup_manager.py backup              # 创建新备份
  python backup_manager.py backup --dry-run    # 模拟备份过程
  python backup_manager.py list                # 列出所有备份
  python backup_manager.py cleanup             # 清理旧备份
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 备份命令
    backup_parser = subparsers.add_parser('backup', help='创建数据库备份')
    backup_parser.add_argument('--dry-run', action='store_true', help='模拟运行')
    backup_parser.add_argument('--force', action='store_true', help='强制备份')
    backup_parser.add_argument('--max-count', type=int, help='覆盖最大备份数量')
    backup_parser.add_argument('--backup-path', help='覆盖备份路径')
    
    # 列表命令
    subparsers.add_parser('list', help='列出所有备份文件')
    
    # 清理命令
    subparsers.add_parser('cleanup', help='清理旧备份文件')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'backup':
            # 构建Django命令参数
            django_args = []
            if args.dry_run:
                django_args.append('--dry-run')
            if args.force:
                django_args.append('--force')
            if args.max_count:
                django_args.extend(['--max-count', str(args.max_count)])
            if args.backup_path:
                django_args.extend(['--backup-path', args.backup_path])
            
            success = run_backup_command(django_args)
            if not success:
                sys.exit(1)
                
        elif args.command == 'list':
            list_backups()
            
        elif args.command == 'cleanup':
            cleanup_old_backups()
            
    except KeyboardInterrupt:
        print("\n操作已中断")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
