# IronGate Deployment Guide | IronGate 部署指南

[English](#english) | [中文](#中文)

---

## English

### Table of Contents
1. [Quick Start (Development)](#quick-start-development)
2. [Production Deployment](#production-deployment)
3. [Security Checklist](#security-checklist)
4. [Translation Setup](#translation-setup)
5. [Troubleshooting](#troubleshooting)

---

### Quick Start (Development)

#### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

#### Step 1: Clone and Install

```bash
# Clone the repository
git clone https://github.com/MoYuK1ng/MC_rcon_manage.git
cd irongate

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 2: Generate Encryption Key

```bash
python generate_key.py
```

This creates a `.env` file with your RCON encryption key. **Keep this file secure!**

#### Step 3: Database Setup

```bash
# Run migrations
python manage.py migrate

# Create superuser account
python manage.py createsuperuser
```

#### Step 4: Run Development Server

```bash
python manage.py runserver
```

Visit:
- **Dashboard**: http://localhost:8000/dashboard/
- **Admin Panel**: http://localhost:8000/admin/

#### Step 5: Configure Servers

1. Log in to admin panel at `/admin/`
2. Create **Groups** (e.g., "SMP Players", "Creative Players")
3. Add **Users** and assign them to groups
4. Create **Servers**:
   - Name: Display name for the server
   - IP Address: Minecraft server IPv4 address
   - RCON Port: Usually 25575
   - RCON Password: Will be encrypted automatically
   - Groups: Select which groups can access this server

---

### Production Deployment

#### Prerequisites
- Ubuntu 20.04+ or similar Linux distribution
- PostgreSQL 12+
- Nginx
- Domain name with DNS configured
- SSL certificate (Let's Encrypt recommended)

#### Step 1: System Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib nginx gettext

# Install certbot for SSL
sudo apt install -y certbot python3-certbot-nginx
```

#### Step 2: Database Setup

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE irongate;
CREATE USER irongate WITH PASSWORD 'your-secure-password';
ALTER ROLE irongate SET client_encoding TO 'utf8';
ALTER ROLE irongate SET default_transaction_isolation TO 'read committed';
ALTER ROLE irongate SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE irongate TO irongate;
\q
```

#### Step 3: Application Setup

```bash
# Create application user
sudo useradd -m -s /bin/bash irongate
sudo su - irongate

# Clone repository
git clone https://github.com/MoYuK1ng/MC_rcon_manage.git
cd irongate

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

#### Step 4: Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file
nano .env
```

Set the following in `.env`:

```bash
SECRET_KEY=your-very-long-random-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_NAME=irongate
DB_USER=irongate
DB_PASSWORD=your-secure-password
DB_HOST=localhost
DB_PORT=5432

# RCON Encryption Key
RCON_ENCRYPTION_KEY=your-fernet-key-from-generate_key.py
```

#### Step 5: Generate Secret Key

```python
# Generate a secure SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output to your `.env` file.

#### Step 6: Compile Translations

```bash
# Compile translation files
python manage.py compilemessages

# If you get errors, install gettext:
sudo apt install gettext
```

#### Step 7: Database Migration

```bash
# Set production settings
export DJANGO_SETTINGS_MODULE=irongate.settings_production

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

#### Step 8: Gunicorn Setup

Create systemd service file:

```bash
sudo nano /etc/systemd/system/irongate.service
```

Add the following:

```ini
[Unit]
Description=IronGate Gunicorn daemon
After=network.target

[Service]
User=irongate
Group=irongate
WorkingDirectory=/home/irongate/irongate
Environment="PATH=/home/irongate/irongate/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=irongate.settings_production"
ExecStart=/home/irongate/irongate/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/home/irongate/irongate/irongate.sock \
    irongate.wsgi:application

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl start irongate
sudo systemctl enable irongate
sudo systemctl status irongate
```

#### Step 9: Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/irongate
```

Add the following:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /home/irongate/irongate/staticfiles/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/irongate/irongate/irongate.sock;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/irongate /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### Step 10: SSL Certificate

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

Follow the prompts to configure SSL.

#### Step 11: Firewall Configuration

```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

---

### Security Checklist

#### �?Before Production Deployment

- [ ] Set `DEBUG = False` in production settings
- [ ] Generate strong `SECRET_KEY` (50+ characters)
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable HTTPS with valid SSL certificate
- [ ] Set secure cookie flags (`SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`)
- [ ] Enable HSTS headers
- [ ] Configure firewall (UFW/iptables)
- [ ] Set up regular database backups
- [ ] Restrict `.env` file permissions: `chmod 600 .env`
- [ ] Never commit `.env` to version control
- [ ] Use strong passwords for database and admin accounts
- [ ] Keep dependencies updated: `pip list --outdated`
- [ ] Set up logging and monitoring
- [ ] Configure fail2ban for SSH protection

#### Run Security Check

```bash
python manage.py check --deploy
```

Fix any warnings before going live.

---

### Translation Setup

#### Compiling Translations

The application includes Chinese translations. To enable them:

```bash
# Install gettext tools
sudo apt install gettext  # Linux
brew install gettext       # macOS

# Compile messages
python manage.py compilemessages
```

#### Adding New Translations

1. Mark strings for translation in code:
   ```python
   from django.utils.translation import gettext_lazy as _
   message = _("Hello World")
   ```

2. Generate message files:
   ```bash
   python manage.py makemessages -l zh_hans
   ```

3. Edit `locale/zh_hans/LC_MESSAGES/django.po`

4. Compile:
   ```bash
   python manage.py compilemessages
   ```

---

### Troubleshooting

#### Translation Not Working

**Problem**: Interface still shows English

**Solution**:
```bash
# Ensure gettext is installed
which msgfmt

# Compile messages
python manage.py compilemessages

# Check for .mo files
ls locale/zh_hans/LC_MESSAGES/

# Restart server
sudo systemctl restart irongate
```

#### RCON Connection Failed

**Problem**: "Connection refused" or "Connection timeout"

**Solution**:
1. Verify Minecraft server has RCON enabled in `server.properties`:
   ```properties
   enable-rcon=true
   rcon.port=25575
   rcon.password=your-password
   ```
2. Check firewall allows RCON port
3. Verify IP address and port in IronGate admin

#### Static Files Not Loading

**Problem**: CSS/JS not loading in production

**Solution**:
```bash
python manage.py collectstatic --noinput
sudo systemctl restart nginx
```

#### Permission Denied Errors

**Problem**: Gunicorn can't access files

**Solution**:
```bash
sudo chown -R irongate:irongate /home/irongate/irongate
chmod 755 /home/irongate/irongate
```

---

## 中文

### 目录
1. [快速开始（开发环境）](#快速开始开发环�?
2. [生产环境部署](#生产环境部署)
3. [安全检查清单](#安全检查清�?
4. [翻译设置](#翻译设置)
5. [故障排除](#故障排除)

---

### 快速开始（开发环境）

#### 前置要求
- Python 3.10 或更高版�?
- pip（Python 包管理器�?

#### 步骤 1：克隆并安装

```bash
# 克隆仓库
git clone https://github.com/MoYuK1ng/MC_rcon_manage.git
cd irongate

# 创建虚拟环境
python -m venv venv

# 激活虚拟环�?
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 步骤 2：生成加密密�?

```bash
python generate_key.py
```

这将创建一个包�?RCON 加密密钥�?`.env` 文件�?*请妥善保管此文件�?*

#### 步骤 3：数据库设置

```bash
# 运行迁移
python manage.py migrate

# 创建超级用户账户
python manage.py createsuperuser
```

#### 步骤 4：运行开发服务器

```bash
python manage.py runserver
```

访问�?
- **仪表�?*: http://localhost:8000/dashboard/
- **管理面板**: http://localhost:8000/admin/

#### 步骤 5：配置服务器

1. �?`/admin/` 登录管理面板
2. 创建**�?*（例如："SMP 玩家"�?创造玩�?�?
3. 添加**用户**并将其分配到�?
4. 创建**服务�?*�?
   - 名称：服务器的显示名�?
   - IP 地址：Minecraft 服务器的 IPv4 地址
   - RCON 端口：通常�?25575
   - RCON 密码：将自动加密
   - 组：选择哪些组可以访问此服务�?

---

### 生产环境部署

#### 前置要求
- Ubuntu 20.04+ 或类似的 Linux 发行�?
- PostgreSQL 12+
- Nginx
- 已配�?DNS 的域�?
- SSL 证书（推荐使�?Let's Encrypt�?

#### 步骤 1：系统设�?

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装依赖
sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib nginx gettext

# 安装 certbot 用于 SSL
sudo apt install -y certbot python3-certbot-nginx
```

#### 步骤 2：数据库设置

```bash
# 切换�?postgres 用户
sudo -u postgres psql

# 创建数据库和用户
CREATE DATABASE irongate;
CREATE USER irongate WITH PASSWORD 'your-secure-password';
ALTER ROLE irongate SET client_encoding TO 'utf8';
ALTER ROLE irongate SET default_transaction_isolation TO 'read committed';
ALTER ROLE irongate SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE irongate TO irongate;
\q
```

#### 步骤 3：应用程序设�?

```bash
# 创建应用程序用户
sudo useradd -m -s /bin/bash irongate
sudo su - irongate

# 克隆仓库
git clone https://github.com/MoYuK1ng/MC_rcon_manage.git
cd irongate

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

#### 步骤 4：环境配�?

```bash
# 复制示例环境文件
cp .env.example .env

# 编辑 .env 文件
nano .env
```

�?`.env` 中设置以下内容：

```bash
SECRET_KEY=your-very-long-random-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# 数据�?
DB_NAME=irongate
DB_USER=irongate
DB_PASSWORD=your-secure-password
DB_HOST=localhost
DB_PORT=5432

# RCON 加密密钥
RCON_ENCRYPTION_KEY=your-fernet-key-from-generate_key.py
```

#### 步骤 5：生成密�?

```python
# 生成安全�?SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

将输出复制到您的 `.env` 文件中�?

#### 步骤 6：编译翻�?

```bash
# 编译翻译文件
python manage.py compilemessages

# 如果出现错误，安�?gettext�?
sudo apt install gettext
```

#### 步骤 7：数据库迁移

```bash
# 设置生产环境配置
export DJANGO_SETTINGS_MODULE=irongate.settings_production

# 运行迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 收集静态文�?
python manage.py collectstatic --noinput
```

#### 步骤 8：Gunicorn 设置

创建 systemd 服务文件�?

```bash
sudo nano /etc/systemd/system/irongate.service
```

添加以下内容�?

```ini
[Unit]
Description=IronGate Gunicorn daemon
After=network.target

[Service]
User=irongate
Group=irongate
WorkingDirectory=/home/irongate/irongate
Environment="PATH=/home/irongate/irongate/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=irongate.settings_production"
ExecStart=/home/irongate/irongate/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/home/irongate/irongate/irongate.sock \
    irongate.wsgi:application

[Install]
WantedBy=multi-user.target
```

启用并启动服务：

```bash
sudo systemctl start irongate
sudo systemctl enable irongate
sudo systemctl status irongate
```

#### 步骤 9：Nginx 配置

```bash
sudo nano /etc/nginx/sites-available/irongate
```

添加以下内容�?

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /home/irongate/irongate/staticfiles/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/irongate/irongate/irongate.sock;
    }
}
```

启用站点�?

```bash
sudo ln -s /etc/nginx/sites-available/irongate /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 步骤 10：SSL 证书

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

按照提示配置 SSL�?

#### 步骤 11：防火墙配置

```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

---

### 安全检查清�?

#### �?生产部署�?

- [ ] 在生产设置中设置 `DEBUG = False`
- [ ] 生成�?`SECRET_KEY`�?0+ 字符�?
- [ ] 使用您的域名配置 `ALLOWED_HOSTS`
- [ ] 使用 PostgreSQL 而不�?SQLite
- [ ] 使用有效�?SSL 证书启用 HTTPS
- [ ] 设置安全 cookie 标志（`SESSION_COOKIE_SECURE`、`CSRF_COOKIE_SECURE`�?
- [ ] 启用 HSTS �?
- [ ] 配置防火墙（UFW/iptables�?
- [ ] 设置定期数据库备�?
- [ ] 限制 `.env` 文件权限：`chmod 600 .env`
- [ ] 永远不要�?`.env` 提交到版本控�?
- [ ] 为数据库和管理员账户使用强密�?
- [ ] 保持依赖项更新：`pip list --outdated`
- [ ] 设置日志记录和监�?
- [ ] 配置 fail2ban 以保�?SSH

#### 运行安全检�?

```bash
python manage.py check --deploy
```

在上线前修复所有警告�?

---

### 翻译设置

#### 编译翻译

应用程序包含中文翻译。要启用它们�?

```bash
# 安装 gettext 工具
sudo apt install gettext  # Linux
brew install gettext       # macOS

# 编译消息
python manage.py compilemessages
```

#### 添加新翻�?

1. 在代码中标记要翻译的字符串：
   ```python
   from django.utils.translation import gettext_lazy as _
   message = _("Hello World")
   ```

2. 生成消息文件�?
   ```bash
   python manage.py makemessages -l zh_hans
   ```

3. 编辑 `locale/zh_hans/LC_MESSAGES/django.po`

4. 编译�?
   ```bash
   python manage.py compilemessages
   ```

---

### 故障排除

#### 翻译不工�?

**问题**：界面仍显示英文

**解决方案**�?
```bash
# 确保已安�?gettext
which msgfmt

# 编译消息
python manage.py compilemessages

# 检�?.mo 文件
ls locale/zh_hans/LC_MESSAGES/

# 重启服务�?
sudo systemctl restart irongate
```

#### RCON 连接失败

**问题**�?连接被拒�?�?连接超时"

**解决方案**�?
1. 验证 Minecraft 服务器在 `server.properties` 中启用了 RCON�?
   ```properties
   enable-rcon=true
   rcon.port=25575
   rcon.password=your-password
   ```
2. 检查防火墙是否允许 RCON 端口
3. 验证 IronGate 管理面板中的 IP 地址和端�?

#### 静态文件未加载

**问题**：生产环境中 CSS/JS 未加�?

**解决方案**�?
```bash
python manage.py collectstatic --noinput
sudo systemctl restart nginx
```

#### 权限被拒绝错�?

**问题**：Gunicorn 无法访问文件

**解决方案**�?
```bash
sudo chown -R irongate:irongate /home/irongate/irongate
chmod 755 /home/irongate/irongate
```

---

## License | 许可�?

Copyright © 2024 IronGate

## Support | 支持

For issues or questions, please open an issue on GitHub.

如有问题或疑问，请在 GitHub 上提�?issue�?
