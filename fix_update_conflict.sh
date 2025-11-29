#!/bin/bash
# Fix git merge conflict during update
# This script resolves the django.mo conflict and updates the code

echo "修复更新冲突 / Fixing update conflict..."

cd /opt/mc_rcon || exit 1

# Remove the conflicting file
echo "删除冲突文件 / Removing conflicting file..."
rm -f locale/zh_hans/LC_MESSAGES/django.mo

# Reset any local changes
echo "重置本地更改 / Resetting local changes..."
git reset --hard HEAD

# Pull latest code
echo "拉取最新代码 / Pulling latest code..."
git pull origin main

# Compile translations
echo "编译翻译文件 / Compiling translations..."
python compile_translations.py || python manage.py compilemessages

# Run migrations
echo "运行数据库迁移 / Running migrations..."
python manage.py migrate

# Collect static files
echo "收集静态文件 / Collecting static files..."
python manage.py collectstatic --noinput

# Restart service
echo "重启服务 / Restarting service..."
systemctl restart mc_rcon

echo "✅ 修复完成！/ Fix complete!"
