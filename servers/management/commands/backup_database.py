"""
Django management command for automatic database backup with retention policy.
自动数据库备份管理命令，支持保留策略

Usage:
    python manage.py backup_database
    python manage.py backup_database --dry-run
    python manage.py backup_database --force
"""
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    """
    自动数据库备份管理命令
    
    功能:
    - 创建带时间戳的数据库备份
    - 执行严格的文件保留策略
    - 自动清理超出限制的旧备份
    - 支持自定义备份路径和保留数量
    """
    help = '创建数据库备份并执行保留策略 / Create database backup with retention policy'

    def add_arguments(self, parser):
        """添加命令行参数"""
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='显示将要执行的操作但不实际执行 / Show what would be done without executing',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制执行备份，即使自动备份被禁用 / Force backup even if auto backup is disabled',
        )
        parser.add_argument(
            '--max-count',
            type=int,
            help='覆盖默认的最大备份数量 / Override default maximum backup count',
        )
        parser.add_argument(
            '--backup-path',
            type=str,
            help='覆盖默认的备份路径 / Override default backup path',
        )

    def handle(self, *args, **options):
        """执行备份命令的主要逻辑"""
        try:
            # 检查是否启用自动备份
            if not self._is_backup_enabled() and not options['force']:
                self.stdout.write(
                    self.style.WARNING(
                        '自动备份已禁用。使用 --force 强制执行备份。\n'
                        'Automatic backup is disabled. Use --force to force backup.'
                    )
                )
                return

            # 获取配置
            backup_config = self._get_backup_config(options)
            
            if options['dry_run']:
                self.stdout.write(
                    self.style.WARNING('=== 模拟运行模式 / DRY RUN MODE ===')
                )

            # 显示配置信息
            self._display_config(backup_config)

            # 执行备份流程
            if options['dry_run']:
                self._simulate_backup_process(backup_config)
            else:
                self._execute_backup_process(backup_config)

        except Exception as e:
            raise CommandError(f'备份失败 / Backup failed: {str(e)}')

    def _is_backup_enabled(self) -> bool:
        """检查是否启用了自动备份"""
        return getattr(settings, 'ENABLE_AUTO_BACKUP', False) or \
               os.getenv('ENABLE_AUTO_BACKUP', 'False').lower() == 'true'

    def _get_backup_config(self, options) -> dict:
        """获取备份配置参数"""
        # 备份路径优先级: 命令行参数 > 环境变量 > 设置 > 默认值
        backup_path = (
            options.get('backup_path') or
            os.getenv('BACKUP_PATH') or
            getattr(settings, 'BACKUP_PATH', None) or
            '/opt/mc_rcon/backups'
        )

        # 最大备份数量优先级: 命令行参数 > 环境变量 > 设置 > 默认值5
        max_count = (
            options.get('max_count') or
            int(os.getenv('BACKUP_MAX_COUNT', '0')) or
            getattr(settings, 'BACKUP_MAX_COUNT', 5)
        )

        # 确保最小值为1
        max_count = max(1, max_count)

        return {
            'backup_path': Path(backup_path),
            'max_count': max_count,
            'database_path': self._get_database_path(),
            'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S')
        }

    def _get_database_path(self) -> Path:
        """获取数据库文件路径"""
        db_config = settings.DATABASES['default']
        
        if db_config['ENGINE'] == 'django.db.backends.sqlite3':
            db_path = db_config['NAME']
            if not os.path.isabs(db_path):
                # 相对路径，转换为绝对路径
                db_path = os.path.join(settings.BASE_DIR, db_path)
            return Path(db_path)
        else:
            raise CommandError(
                '当前仅支持SQLite数据库备份 / Currently only SQLite database backup is supported'
            )

    def _display_config(self, config: dict):
        """显示备份配置信息"""
        self.stdout.write('=== 备份配置 / Backup Configuration ===')
        self.stdout.write(f'数据库路径 / Database Path: {config["database_path"]}')
        self.stdout.write(f'备份目录 / Backup Directory: {config["backup_path"]}')
        self.stdout.write(f'最大备份数 / Max Backup Count: {config["max_count"]}')
        self.stdout.write(f'时间戳 / Timestamp: {config["timestamp"]}')
        self.stdout.write('')

    def _simulate_backup_process(self, config: dict):
        """模拟备份过程（干运行模式）"""
        backup_path = config['backup_path']
        
        # 检查备份目录
        if not backup_path.exists():
            self.stdout.write(f'[模拟] 将创建备份目录: {backup_path}')

        # 检查现有备份
        existing_backups = self._get_existing_backups(backup_path)
        self.stdout.write(f'现有备份数量 / Existing Backups: {len(existing_backups)}')
        
        if existing_backups:
            self.stdout.write('现有备份文件 / Existing Backup Files:')
            for backup in existing_backups:
                self.stdout.write(f'  - {backup.name}')

        # 模拟保留策略
        if len(existing_backups) >= config['max_count']:
            files_to_delete = existing_backups[:-config['max_count']+1]
            self.stdout.write(f'[模拟] 将删除 {len(files_to_delete)} 个旧备份:')
            for file_path in files_to_delete:
                self.stdout.write(f'  - 删除: {file_path.name}')

        # 模拟创建新备份
        new_backup_name = f'db_backup_{config["timestamp"]}.sqlite3'
        self.stdout.write(f'[模拟] 将创建新备份: {new_backup_name}')
        
        self.stdout.write(self.style.SUCCESS('模拟完成 / Simulation completed'))

    def _execute_backup_process(self, config: dict):
        """执行实际的备份过程"""
        backup_path = config['backup_path']

        # 创建备份目录
        self._ensure_backup_directory(backup_path)

        # 执行保留策略（在创建新备份前清理）
        self._enforce_retention_policy(backup_path, config['max_count'])

        # 创建新备份
        new_backup_path = self._create_backup(config)

        # 验证备份
        if self._verify_backup(new_backup_path, config['database_path']):
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ 备份成功创建: {new_backup_path.name}\n'
                    f'✅ Backup successfully created: {new_backup_path.name}'
                )
            )
        else:
            raise CommandError('备份验证失败 / Backup verification failed')

    def _ensure_backup_directory(self, backup_path: Path):
        """确保备份目录存在"""
        try:
            backup_path.mkdir(parents=True, exist_ok=True)
            self.stdout.write(f'备份目录已准备: {backup_path}')
        except PermissionError:
            raise CommandError(f'无权限创建备份目录: {backup_path}')
        except Exception as e:
            raise CommandError(f'创建备份目录失败: {e}')

    def _get_existing_backups(self, backup_path: Path) -> List[Path]:
        """获取现有备份文件列表，按修改时间排序（最旧的在前）"""
        if not backup_path.exists():
            return []

        # 查找所有备份文件
        backup_files = list(backup_path.glob('db_backup_*.sqlite3'))
        
        # 按修改时间排序（最旧的在前）
        backup_files.sort(key=lambda x: x.stat().st_mtime)
        
        return backup_files

    def _enforce_retention_policy(self, backup_path: Path, max_count: int):
        """
        执行严格的保留策略
        当现有备份数量达到或超过最大限制时，删除最旧的备份文件
        确保在创建新备份后总数不超过max_count
        """
        existing_backups = self._get_existing_backups(backup_path)
        
        if len(existing_backups) >= max_count:
            # 计算需要删除的文件数量
            # 由于要创建一个新备份，需要为其腾出空间
            files_to_delete_count = len(existing_backups) - max_count + 1
            files_to_delete = existing_backups[:files_to_delete_count]
            
            self.stdout.write(
                f'执行保留策略: 删除 {len(files_to_delete)} 个旧备份\n'
                f'Enforcing retention policy: deleting {len(files_to_delete)} old backups'
            )
            
            for file_path in files_to_delete:
                try:
                    file_path.unlink()
                    self.stdout.write(f'  ✅ 已删除: {file_path.name}')
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'  ⚠️  删除失败: {file_path.name} - {e}')
                    )

    def _create_backup(self, config: dict) -> Path:
        """创建数据库备份"""
        database_path = config['database_path']
        backup_path = config['backup_path']
        timestamp = config['timestamp']

        # 生成备份文件名
        backup_filename = f'db_backup_{timestamp}.sqlite3'
        backup_file_path = backup_path / backup_filename

        try:
            # 检查源数据库文件是否存在
            if not database_path.exists():
                raise CommandError(f'数据库文件不存在: {database_path}')

            # 复制数据库文件
            self.stdout.write(f'正在创建备份: {backup_filename}')
            shutil.copy2(database_path, backup_file_path)
            
            return backup_file_path

        except Exception as e:
            raise CommandError(f'创建备份失败: {e}')

    def _verify_backup(self, backup_path: Path, original_path: Path) -> bool:
        """验证备份文件的完整性"""
        try:
            # 检查文件是否存在
            if not backup_path.exists():
                return False

            # 检查文件大小
            backup_size = backup_path.stat().st_size
            original_size = original_path.stat().st_size

            if backup_size == 0:
                self.stdout.write(self.style.WARNING('备份文件为空'))
                return False

            # 简单的大小比较（允许小幅差异）
            size_diff_ratio = abs(backup_size - original_size) / original_size
            if size_diff_ratio > 0.1:  # 允许10%的差异
                self.stdout.write(
                    self.style.WARNING(
                        f'备份文件大小差异较大: 原始={original_size}, 备份={backup_size}'
                    )
                )

            self.stdout.write(f'备份验证通过: 大小={backup_size} 字节')
            return True

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'备份验证失败: {e}'))
            return False
