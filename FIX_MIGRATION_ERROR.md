# 修复迁移错误指南

## 问题描述

在运行迁移时遇到以下错误：
```
django.db.utils.IntegrityError: UNIQUE constraint failed: servers_whitelistrequest.server_id, servers_whitelistrequest.minecraft_username
```

这是因为数据库中已经存在重复的白名单请求记录，而新的迁移试图添加唯一约束。

## 解决方案

### 方案 1: 修复现有数据库（推荐用于生产环境）

如果你的数据库中有重要数据，使用此方案：

```bash
# 1. 回滚到迁移 0003
python manage.py migrate servers 0003

# 2. 运行修复脚本清理重复数据
python fix_duplicate_whitelist.py

# 3. 重新运行迁移
python manage.py migrate
```

### 方案 2: 重置数据库（适用于测试/开发环境）

如果数据库中没有重要数据，可以直接重置：

```bash
# 1. 删除数据库文件
rm db.sqlite3

# 2. 重新运行迁移
python manage.py migrate

# 3. 创建超级用户
python create_superuser_no_email.py
```

### 方案 3: 手动清理（高级用户）

如果你想手动清理重复数据：

```bash
# 1. 进入 Django shell
python manage.py shell

# 2. 运行以下 Python 代码
from servers.models import WhitelistRequest
from django.db.models import Count

# 找出重复的记录
duplicates = (
    WhitelistRequest.objects
    .values('server_id', 'minecraft_username')
    .annotate(count=Count('id'))
    .filter(count__gt=1)
)

# 对每个重复组，保留最新的，删除其他的
for dup in duplicates:
    requests = WhitelistRequest.objects.filter(
        server_id=dup['server_id'],
        minecraft_username=dup['minecraft_username']
    ).order_by('-created_at')
    
    # 保留第一个（最新的），删除其他的
    requests.exclude(id=requests.first().id).delete()

# 3. 退出 shell 并重新运行迁移
exit()
python manage.py migrate
```

## 预防措施

为了避免将来出现此问题，迁移 `0004` 已经添加了唯一约束：

```python
unique_together = [['server', 'minecraft_username']]
```

这确保了每个服务器上的每个 Minecraft 用户名只能有一个白名单请求。

## 验证修复

运行以下命令验证迁移成功：

```bash
python manage.py showmigrations servers
```

应该看到所有迁移都标记为 `[X]`：

```
servers
 [X] 0001_initial
 [X] 0002_announcement_displaysettings
 [X] 0003_initialize_display_settings
 [X] 0004_alter_whitelistrequest_unique_together
```

## 需要帮助？

如果以上方案都不能解决问题，请查看：
- FAQ.md - 常见问题解答
- QUICK_START.md - 快速开始指南
- 或在 GitHub 上提交 issue
