# VPS 更新部署指南 | VPS Update Deployment Guide

## 中文

### 📋 更新前准备

在更新之前，建议先备份重要数据：

```bash
# 1. 备份数据库
cd /path/to/your/project
cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)

# 2. 备份 .env 文件（包含加密密钥）
cp .env .env.backup

# 3. 备份静态文件（可选）
cp -r staticfiles staticfiles.backup
```

### 🚀 更新步骤

#### 方式 1：标准更新流程（推荐）

```bash
# 1. SSH 登录到你的 VPS
ssh user@your-vps-ip

# 2. 进入项目目录
cd /path/to/your/project
# 例如：cd /var/www/irongate

# 3. 激活虚拟环境
source venv/bin/activate

# 4. 停止服务（如果使用 Gunicorn + Systemd）
sudo systemctl stop gunicorn

# 5. 拉取最新代码
git pull origin main

# 6. 更新依赖（如果 requirements.txt 有变化）
pip install -r requirements.txt --upgrade

# 7. 更新 .env 文件（添加新的配置项）
nano .env
# 添加以下内容（如果还没有）：
# ALLOWED_HOSTS=localhost,127.0.0.1,mc.moyuu.online
# CSRF_TRUSTED_ORIGINS=https://mc.moyuu.online

# 8. 运行数据库迁移（如果有新的迁移）
python manage.py migrate

# 9. 收集静态文件
python manage.py collectstatic --noinput

# 10. 编译翻译文件（如果使用中文）
python manage.py compilemessages

# 11. 重启服务
sudo systemctl start gunicorn
sudo systemctl restart nginx

# 12. 检查服务状态
sudo systemctl status gunicorn
sudo systemctl status nginx
```

#### 方式 2：使用更新脚本（自动化）

创建一个更新脚本 `update.sh`：

```bash
#!/bin/bash
# IronGate 更新脚本

set -e  # 遇到错误立即退出

echo "🔄 开始更新 IronGate..."

# 项目路径（根据实际情况修改）
PROJECT_DIR="/var/www/irongate"
VENV_DIR="$PROJECT_DIR/venv"

# 进入项目目录
cd $PROJECT_DIR

# 激活虚拟环境
source $VENV_DIR/bin/activate

# 备份数据库
echo "📦 备份数据库..."
cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)

# 停止服务
echo "⏸️  停止服务..."
sudo systemctl stop gunicorn

# 拉取最新代码
echo "⬇️  拉取最新代码..."
git pull origin main

# 更新依赖
echo "📚 更新依赖..."
pip install -r requirements.txt --upgrade

# 运行迁移
echo "🗄️  运行数据库迁移..."
python manage.py migrate

# 收集静态文件
echo "📁 收集静态文件..."
python manage.py collectstatic --noinput

# 编译翻译
echo "🌍 编译翻译文件..."
python manage.py compilemessages || echo "⚠️  翻译编译失败（可能未安装 gettext）"

# 重启服务
echo "🔄 重启服务..."
sudo systemctl start gunicorn
sudo systemctl restart nginx

# 检查状态
echo "✅ 检查服务状态..."
sudo systemctl status gunicorn --no-pager
sudo systemctl status nginx --no-pager

echo "🎉 更新完成！"
echo "访问: https://mc.moyuu.online"
```

保存后添加执行权限并运行：

```bash
# 创建脚本
nano update.sh
# 粘贴上面的内容，修改 PROJECT_DIR 路径

# 添加执行权限
chmod +x update.sh

# 运行更新
./update.sh
```

### 🔍 验证更新

```bash
# 1. 检查 Git 版本
git log -1 --oneline
# 应该显示最新的提交

# 2. 检查服务状态
sudo systemctl status gunicorn
sudo systemctl status nginx

# 3. 查看日志
sudo journalctl -u gunicorn -n 50 --no-pager
tail -f /var/log/nginx/irongate_error.log

# 4. 测试网站
curl -I https://mc.moyuu.online
# 应该返回 200 OK
```

### ⚠️ 重要配置更新

这次更新添加了新的配置项，需要在 `.env` 文件中添加：

```bash
# 编辑 .env 文件
nano .env

# 确保包含以下配置：
ALLOWED_HOSTS=localhost,127.0.0.1,mc.moyuu.online
CSRF_TRUSTED_ORIGINS=https://mc.moyuu.online,http://localhost:8000
```

**注意**：
- `ALLOWED_HOSTS`：只需域名，不要协议
- `CSRF_TRUSTED_ORIGINS`：必须包含完整协议（`https://`）

### 🐛 常见问题

#### 问题 1：Git 拉取失败

```bash
# 错误：Your local changes would be overwritten by merge

# 解决方案 1：暂存本地修改
git stash
git pull origin main
git stash pop

# 解决方案 2：强制覆盖（谨慎使用）
git fetch origin
git reset --hard origin/main
```

#### 问题 2：权限错误

```bash
# 错误：Permission denied

# 解决方案：修复文件权限
sudo chown -R $USER:$USER /path/to/your/project
chmod -R 755 /path/to/your/project
```

#### 问题 3：Gunicorn 启动失败

```bash
# 查看详细错误
sudo journalctl -u gunicorn -n 100 --no-pager

# 常见原因：
# 1. .env 文件配置错误
# 2. 数据库迁移未完成
# 3. 静态文件未收集

# 手动测试
cd /path/to/your/project
source venv/bin/activate
python manage.py check --deploy
```

#### 问题 4：静态文件 404

```bash
# 重新收集静态文件
python manage.py collectstatic --clear --noinput

# 检查 Nginx 配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

#### 问题 5：CSRF 403 错误

```bash
# 确认 .env 配置正确
cat .env | grep CSRF_TRUSTED_ORIGINS

# 应该包含你的域名：
# CSRF_TRUSTED_ORIGINS=https://mc.moyuu.online

# 重启服务
sudo systemctl restart gunicorn
```

### 🔄 回滚到之前版本

如果更新后出现问题，可以回滚：

```bash
# 1. 停止服务
sudo systemctl stop gunicorn

# 2. 回滚代码
git log --oneline -10  # 查看最近的提交
git reset --hard <commit-hash>  # 回滚到指定版本

# 3. 恢复数据库（如果需要）
cp db.sqlite3.backup.YYYYMMDD_HHMMSS db.sqlite3

# 4. 重启服务
sudo systemctl start gunicorn
sudo systemctl restart nginx
```

### 📊 更新检查清单

更新完成后，检查以下项目：

- [ ] Git 版本正确（`git log -1`）
- [ ] Gunicorn 运行正常（`systemctl status gunicorn`）
- [ ] Nginx 运行正常（`systemctl status nginx`）
- [ ] 网站可以访问（`curl -I https://mc.moyuu.online`）
- [ ] 登录功能正常
- [ ] RCON 连接正常
- [ ] 白名单功能正常
- [ ] 语言切换正常

### 🔒 安全建议

1. **定期备份**
   ```bash
   # 创建自动备份脚本
   crontab -e
   
   # 添加每天凌晨 2 点备份
   0 2 * * * cd /var/www/irongate && cp db.sqlite3 backups/db.$(date +\%Y\%m\%d).sqlite3
   ```

2. **保护 .env 文件**
   ```bash
   chmod 600 .env
   ```

3. **监控日志**
   ```bash
   # 实时监控错误日志
   tail -f /var/log/nginx/irongate_error.log
   sudo journalctl -u gunicorn -f
   ```

---

## English

### 📋 Pre-Update Preparation

Before updating, backup important data:

```bash
# 1. Backup database
cd /path/to/your/project
cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)

# 2. Backup .env file (contains encryption key)
cp .env .env.backup

# 3. Backup static files (optional)
cp -r staticfiles staticfiles.backup
```

### 🚀 Update Steps

#### Method 1: Standard Update Process (Recommended)

```bash
# 1. SSH into your VPS
ssh user@your-vps-ip

# 2. Navigate to project directory
cd /path/to/your/project
# Example: cd /var/www/irongate

# 3. Activate virtual environment
source venv/bin/activate

# 4. Stop service (if using Gunicorn + Systemd)
sudo systemctl stop gunicorn

# 5. Pull latest code
git pull origin main

# 6. Update dependencies (if requirements.txt changed)
pip install -r requirements.txt --upgrade

# 7. Update .env file (add new configuration)
nano .env
# Add the following (if not already present):
# ALLOWED_HOSTS=localhost,127.0.0.1,mc.moyuu.online
# CSRF_TRUSTED_ORIGINS=https://mc.moyuu.online

# 8. Run database migrations (if any new migrations)
python manage.py migrate

# 9. Collect static files
python manage.py collectstatic --noinput

# 10. Compile translations (if using Chinese)
python manage.py compilemessages

# 11. Restart services
sudo systemctl start gunicorn
sudo systemctl restart nginx

# 12. Check service status
sudo systemctl status gunicorn
sudo systemctl status nginx
```

#### Method 2: Using Update Script (Automated)

Create an update script `update.sh`:

```bash
#!/bin/bash
# IronGate Update Script

set -e  # Exit on error

echo "🔄 Starting IronGate update..."

# Project path (modify according to your setup)
PROJECT_DIR="/var/www/irongate"
VENV_DIR="$PROJECT_DIR/venv"

# Navigate to project directory
cd $PROJECT_DIR

# Activate virtual environment
source $VENV_DIR/bin/activate

# Backup database
echo "📦 Backing up database..."
cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)

# Stop service
echo "⏸️  Stopping service..."
sudo systemctl stop gunicorn

# Pull latest code
echo "⬇️  Pulling latest code..."
git pull origin main

# Update dependencies
echo "📚 Updating dependencies..."
pip install -r requirements.txt --upgrade

# Run migrations
echo "🗄️  Running database migrations..."
python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Compile translations
echo "🌍 Compiling translations..."
python manage.py compilemessages || echo "⚠️  Translation compilation failed (gettext may not be installed)"

# Restart services
echo "🔄 Restarting services..."
sudo systemctl start gunicorn
sudo systemctl restart nginx

# Check status
echo "✅ Checking service status..."
sudo systemctl status gunicorn --no-pager
sudo systemctl status nginx --no-pager

echo "🎉 Update complete!"
echo "Visit: https://mc.moyuu.online"
```

Save, add execute permission, and run:

```bash
# Create script
nano update.sh
# Paste the content above, modify PROJECT_DIR path

# Add execute permission
chmod +x update.sh

# Run update
./update.sh
```

### 🔍 Verify Update

```bash
# 1. Check Git version
git log -1 --oneline
# Should show the latest commit

# 2. Check service status
sudo systemctl status gunicorn
sudo systemctl status nginx

# 3. View logs
sudo journalctl -u gunicorn -n 50 --no-pager
tail -f /var/log/nginx/irongate_error.log

# 4. Test website
curl -I https://mc.moyuu.online
# Should return 200 OK
```

### ⚠️ Important Configuration Updates

This update adds new configuration items that need to be added to `.env`:

```bash
# Edit .env file
nano .env

# Ensure it contains:
ALLOWED_HOSTS=localhost,127.0.0.1,mc.moyuu.online
CSRF_TRUSTED_ORIGINS=https://mc.moyuu.online,http://localhost:8000
```

**Note**:
- `ALLOWED_HOSTS`: Domain only, no protocol
- `CSRF_TRUSTED_ORIGINS`: Must include full protocol (`https://`)

### 📊 Update Checklist

After update, verify:

- [ ] Git version correct (`git log -1`)
- [ ] Gunicorn running (`systemctl status gunicorn`)
- [ ] Nginx running (`systemctl status nginx`)
- [ ] Website accessible (`curl -I https://mc.moyuu.online`)
- [ ] Login works
- [ ] RCON connection works
- [ ] Whitelist function works
- [ ] Language switching works

---

## 快速命令参考 | Quick Command Reference

```bash
# 一键更新（创建并运行更新脚本）
cd /var/www/irongate && \
source venv/bin/activate && \
sudo systemctl stop gunicorn && \
git pull origin main && \
pip install -r requirements.txt --upgrade && \
python manage.py migrate && \
python manage.py collectstatic --noinput && \
python manage.py compilemessages && \
sudo systemctl start gunicorn && \
sudo systemctl restart nginx && \
echo "✅ 更新完成！"

# 查看服务状态
sudo systemctl status gunicorn nginx

# 查看日志
sudo journalctl -u gunicorn -n 50
tail -f /var/log/nginx/irongate_error.log

# 重启所有服务
sudo systemctl restart gunicorn nginx
```
