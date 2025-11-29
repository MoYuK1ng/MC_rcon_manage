# 部署修复说明

## 已修复的所有 Bug

### ✅ Bug 1: 迁移唯一约束错误
**问题：** 升级时出现 `UNIQUE constraint failed` 错误  
**修复：** 迁移现在会自动清理重复数据

### ✅ Bug 2: 翻译文件重复定义
**问题：** `compilemessages` 失败，25 个重复定义  
**修复：** 清理了所有重复项

### ✅ Bug 3: 后台翻译不完整
**问题：** 管理后台显示英文而不是中文  
**修复：** 添加了完整的中文翻译并生成了 .mo 文件

## 一键部署命令

在你的服务器上执行以下命令即可完成所有修复：

```bash
#!/bin/bash
cd /opt/mc_rcon

# 1. 拉取最新代码
echo "正在拉取最新代码..."
git pull origin main

# 2. 激活虚拟环境（如果使用）
source venv/bin/activate  # 或 source env/bin/activate

# 3. 如果之前迁移失败，先回滚
echo "检查迁移状态..."
python manage.py migrate servers 0003 2>/dev/null || true

# 4. 运行迁移（会自动清理重复数据）
echo "运行数据库迁移..."
python manage.py migrate

# 5. 编译翻译文件（使用新的脚本）
echo "编译翻译文件..."
python compile_translations.py || python manage.py compilemessages

# 6. 收集静态文件
echo "收集静态文件..."
python manage.py collectstatic --noinput

# 7. 重启服务
echo "重启服务..."
systemctl restart mc_rcon  # 根据你的服务名调整

echo "✅ 部署完成！"
```

## 验证部署

### 1. 检查迁移状态
```bash
python manage.py showmigrations servers
```

应该看到：
```
servers
 [X] 0001_initial
 [X] 0002_announcement_displaysettings
 [X] 0003_initialize_display_settings
 [X] 0004_alter_whitelistrequest_unique_together
```

### 2. 检查翻译文件
```bash
ls -la locale/zh_hans/LC_MESSAGES/
```

应该看到 `django.mo` 文件存在。

### 3. 访问管理后台
访问 `http://your-domain/admin/` 并登录，所有界面应该显示中文。

## 如果还有问题

### 问题：翻译仍然不显示
**解决方案：**
```bash
# 确保 .mo 文件存在
python compile_translations.py

# 重启 Django 服务
systemctl restart mc_rcon

# 清除浏览器缓存
```

### 问题：迁移仍然失败
**解决方案：**
```bash
# 手动清理重复数据
python fix_duplicate_whitelist.py

# 重新运行迁移
python manage.py migrate
```

### 问题：静态文件不更新
**解决方案：**
```bash
# 强制收集静态文件
python manage.py collectstatic --noinput --clear

# 重启 web 服务器
systemctl restart nginx  # 或 apache2
```

## 文件清单

本次修复包含以下文件：

- `servers/migrations/0004_alter_whitelistrequest_unique_together.py` - 修复的迁移文件
- `locale/zh_hans/LC_MESSAGES/django.po` - 完整的翻译文件
- `locale/zh_hans/LC_MESSAGES/django.mo` - 编译后的翻译文件
- `compile_translations.py` - 跨平台翻译编译脚本
- `fix_duplicate_whitelist.py` - 手动清理重复数据脚本
- `FIX_MIGRATION_ERROR.md` - 迁移错误修复指南

## 技术细节

### 迁移修复
迁移 0004 现在包含一个 `RunPython` 操作，在添加唯一约束前：
1. 查找所有重复的 server_id + minecraft_username 组合
2. 对每个组合，保留最新的记录（按 created_at 排序）
3. 删除旧的重复记录
4. 然后安全地添加唯一约束

### 翻译修复
1. 清理了所有重复的 msgid 定义
2. 添加了缺失的管理后台翻译
3. 修复了引号转义问题
4. 生成了编译后的 .mo 文件

## 支持

如果遇到任何问题：
1. 查看 `FAQ.md`
2. 查看 `QUICK_START.md`
3. 在 GitHub 上提交 issue

---

**最后更新：** 2024-11-29  
**版本：** 1.0.1
