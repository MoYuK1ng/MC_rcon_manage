# 🎮 MC RCON Manager - Minecraft RCON Web Portal

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/Django-5.0-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.0.0-brightgreen.svg)](VERSION)
[![Tests](https://img.shields.io/badge/Tests-Passing-success.svg)](#testing)
[![Security](https://img.shields.io/badge/Security-Hardened-blue.svg)](#security-features)

**A secure, modern web portal for managing Minecraft servers via RCON protocol**

**Developed by MoYuK1ng**

[English](#english) | [中文](#中文)

</div>

---

## English

### 🌟 Features

- 🔐 **Enterprise-Grade Security** - Fernet encryption for RCON passwords, CSRF protection, input validation
- 🎮 **Multi-Server Management** - Manage unlimited Minecraft servers from a single dashboard
- 👥 **Real-Time Player Monitoring** - Auto-refreshing player lists with 30-second polling
- ✅ **Whitelist Management** - Add players to server whitelists via RCON commands
- 🔒 **Encrypted Credentials** - All RCON passwords encrypted at rest, never stored in plaintext
- 🔧 **Flexible Display Settings** - Control visibility of server IP/port information
- 📢 **Announcement System** - Post system-wide announcements to all users
- 🌍 **Full Internationalization** - Complete support for English and Simplified Chinese
- 📱 **Responsive Design** - Modern Tailwind CSS UI optimized for all devices
- ⚡ **Dynamic Updates** - HTMX for seamless updates without page reloads
- 🎨 **Beautiful Interface** - Clean, modern design inspired by Vercel and Linear
- 🧪 **Comprehensive Testing** - 70+ tests including property-based testing with Hypothesis
- 🚀 **Production-Ready** - Optimized for deployment with Gunicorn + Nginx
- 📦 **Easy Deployment** - One-command installation script for Linux VPS


### 📸 Screenshots

*Coming soon - Add your screenshots here*

### 🚀 Quick Start

#### Prerequisites

- **Python 3.10 or higher**
- **pip** (Python package manager)
- **Linux VPS** (for production deployment)
- **Minecraft Server** with RCON enabled

#### Installation Methods

**Option 1: One-Click Installation (Recommended for Production)**

Perfect for Linux VPS deployment with automatic setup of all dependencies, Nginx, and systemd service.

```bash
# Download and run the management script
wget https://raw.githubusercontent.com/MoYuK1ng/MC_rcon_manage/main/manage.sh
chmod +x manage.sh
sudo bash manage.sh

# Select language (English/Chinese)
# Then choose: 1) Fresh Install
```

The script automatically handles:
- ✅ System dependency installation (Python, Nginx, Git)
- ✅ Repository cloning and virtual environment setup
- ✅ Database initialization and migrations
- ✅ Admin account creation
- ✅ Gunicorn + Nginx configuration
- ✅ Systemd service setup and auto-start
- ✅ SSL/TLS support (optional)

**Option 2: Manual Installation (Development)**

For local development or custom deployments:

```bash
# Clone the repository
git clone https://github.com/MoYuK1ng/MC_rcon_manage.git
cd MC_rcon_manage

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install production dependencies
pip install -r requirements.txt

# Generate encryption key
python generate_key.py

# Configure environment variables
cp .env.example .env
# Edit .env and set your SECRET_KEY, ALLOWED_HOSTS, etc.

# Run database migrations
python manage.py migrate

# Create superuser account
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Start development server
python manage.py runserver
```

Visit `http://localhost:8000/admin` to configure servers and groups.


### 🔐 Security Configuration

#### Setting RCON Passwords

RCON passwords are encrypted using Fernet symmetric encryption and cannot be set through the admin interface for security reasons.

```bash
# Method 1: Using the provided script (Recommended)
python set_rcon_password.py

# Method 2: Using Django shell
python manage.py shell
>>> from servers.models import Server
>>> server = Server.objects.get(name="Your Server Name")
>>> server.set_password("your_rcon_password")
>>> server.save()
```

#### Encryption Key Management

The application uses Fernet symmetric encryption to protect RCON passwords. Proper key management is critical for security.

```bash
# Generate a new encryption key (first-time setup)
python generate_key.py

# Verify current key is valid
python verify_key.py

# Test all stored passwords can be decrypted
python verify_key.py --test-passwords

# Rotate encryption key (re-encrypts all passwords)
python rotate_key.py --generate-new
```

**🔒 Security Best Practices:**
- ✅ Never commit encryption keys to version control
- ✅ Store keys securely in `.env` file (already in `.gitignore`)
- ✅ Rotate keys periodically (every 6-12 months recommended)
- ✅ Create database backups before key rotation
- ✅ Use strong, unique passwords for admin accounts
- ✅ Enable HTTPS in production (use Let's Encrypt)
- ✅ Keep Django and dependencies updated


### 💾 Database Backup & Restore

#### Backup Database

```bash
# Run the management script
sudo bash manage.sh

# Select option 8) Backup Data
# Enter backup directory (or press Enter for current directory)
```

Creates a timestamped backup: `db_backup_YYYYMMDD_HHMMSS.sqlite3`

#### Restore Database

```bash
# Run the management script
sudo bash manage.sh

# Select option 9) Restore Data
# Enter the full path to your backup file
```

The restore process automatically:
1. Shows backup file information
2. Creates a safety backup of current database
3. Stops the service
4. Restores the backup
5. Restarts the service

#### Automated Backups (Recommended)

```bash
# Create automated backup script
cat > /opt/mc_rcon/auto_backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/mc_rcon/backups"
mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
cp /opt/mc_rcon/db.sqlite3 "$BACKUP_DIR/db_backup_${TIMESTAMP}.sqlite3"
# Keep only last 7 days of backups
find "$BACKUP_DIR" -name "db_backup_*.sqlite3" -mtime +7 -delete
EOF

chmod +x /opt/mc_rcon/auto_backup.sh

# Set up daily backups at 2 AM
crontab -e
# Add: 0 2 * * * /opt/mc_rcon/auto_backup.sh >> /var/log/mc_rcon_backup.log 2>&1
```


### 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Web Browser (Client)                     │
│              Tailwind CSS + HTMX + Lucide Icons             │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Nginx (Reverse Proxy)                       │
│              - SSL/TLS Termination                           │
│              - Static File Serving                           │
│              - Request Forwarding                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Gunicorn WSGI Server                            │
│              - Multiple Worker Processes                     │
│              - Load Balancing                                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Django Application                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Views      │  │  Templates   │  │    Models    │     │
│  │  - Auth      │◄─┤  - i18n      │  │  - Server    │     │
│  │  - RCON      │  │  - Jazzmin   │  │  - Whitelist │     │
│  │  - Dashboard │  └──────────────┘  │  - Announce  │     │
│  └──────┬───────┘                    └──────┬───────┘     │
│         │                                    │              │
│         ▼                                    ▼              │
│  ┌──────────────────────┐         ┌──────────────────┐    │
│  │   RCON Service       │         │  Encryption      │    │
│  │   - Connection Pool  │         │  - Fernet        │    │
│  │   - Command Exec     │         │  - Key Mgmt      │    │
│  └──────┬───────────────┘         └──────────────────┘    │
└─────────┼──────────────────────────────────────────────────┘
          │ RCON Protocol (TCP)
          ▼
┌─────────────────────────────────────────────────────────────┐
│              Minecraft Servers (RCON enabled)                │
└─────────────────────────────────────────────────────────────┘
```

### 🔒 Security Features

- **Password Encryption**: RCON passwords encrypted with Fernet (AES-128-CBC)
- **Input Validation**: Regex validation prevents command injection attacks
- **Access Control**: Group-based permissions with `@user_has_server_access` decorator
- **CSRF Protection**: Django CSRF tokens configured for HTMX requests
- **Secure Defaults**: Production settings include HSTS, secure cookies, X-Frame-Options
- **SQL Injection Protection**: Django ORM prevents SQL injection
- **XSS Protection**: Template auto-escaping prevents cross-site scripting
- **Session Security**: Secure session cookies with HTTPOnly and SameSite flags


### 🧪 Testing

The project includes comprehensive testing with both unit tests and property-based tests.

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest servers/tests.py -v

# Run with coverage report
pytest servers/tests.py --cov=servers --cov-report=html

# Run property-based tests with statistics
pytest servers/tests.py --hypothesis-show-statistics

# Run specific test class
pytest servers/tests.py::ServerModelTests -v
```

**Test Coverage:**
- ✅ 70+ tests total
- ✅ 12 property-based tests (Hypothesis)
- ✅ 58 unit tests (Django TestCase)
- ✅ 100% passing rate
- ✅ Tests cover models, views, services, and utilities

### 📦 Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Backend Framework | Django | 5.0+ |
| Database | SQLite / PostgreSQL | - |
| RCON Client | mcrcon | 0.7.0+ |
| Encryption | cryptography (Fernet) | 41.0.0+ |
| Frontend CSS | Tailwind CSS | 3.x |
| Dynamic Updates | HTMX | 1.9.x |
| Icons | Lucide Icons | Latest |
| Admin UI | Django Jazzmin | 3.0+ |
| Testing | pytest + Hypothesis | Latest |
| WSGI Server | Gunicorn | 21.2.0+ |
| Static Files | Whitenoise | 6.6.0+ |

### 🌐 API Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/` | GET | Landing page | No |
| `/dashboard/` | GET | Main dashboard with server list | Yes |
| `/server/<id>/players/` | GET | HTMX endpoint for player list | Yes |
| `/server/<id>/whitelist/` | POST | Add player to whitelist | Yes |
| `/my-whitelist/` | GET | User's whitelist requests | Yes |
| `/i18n/setlang/` | POST | Language switcher | No |
| `/admin/` | GET | Django admin panel | Admin |
| `/accounts/login/` | GET/POST | User login | No |
| `/accounts/register/` | GET/POST | User registration | No |


### 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/AmazingFeature`
3. **Install development dependencies**: `pip install -r requirements-dev.txt`
4. **Make your changes** and add tests
5. **Run tests**: `pytest servers/tests.py`
6. **Run linters**: `flake8 . && pylint servers/`
7. **Commit your changes**: `git commit -m 'Add some AmazingFeature'`
8. **Push to the branch**: `git push origin feature/AmazingFeature`
9. **Open a Pull Request**

**Code Style:**
- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Write tests for new features
- Keep commits atomic and well-described

**Translation Contributions:**
- Translation files are in `locale/zh_hans/LC_MESSAGES/`
- Use `python manage.py makemessages` to update translation files
- Use `python manage.py compilemessages` to compile translations
- See `locale/README.md` for detailed translation guide

### 📝 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024-2025 MoYuK1ng

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

**Third-Party Licenses:**
- Django: BSD License
- mcrcon: MIT License
- cryptography: Apache License 2.0 / BSD License
- Tailwind CSS: MIT License
- HTMX: BSD 2-Clause License
- Hypothesis: Mozilla Public License 2.0


### 🙏 Acknowledgments

- Built with [Django](https://www.djangoproject.com/) - The web framework for perfectionists with deadlines
- RCON client: [mcrcon](https://github.com/barneygale/MCRcon) - Minecraft RCON client library
- UI Framework: [Tailwind CSS](https://tailwindcss.com/) - A utility-first CSS framework
- Icons: [Lucide Icons](https://lucide.dev/) - Beautiful & consistent icon toolkit
- Dynamic updates: [HTMX](https://htmx.org/) - High power tools for HTML
- Admin theme: [Django Jazzmin](https://django-jazzmin.readthedocs.io/) - Drop-in Django admin theme
- Testing: [Hypothesis](https://hypothesis.readthedocs.io/) - Property-based testing for Python
- Encryption: [cryptography](https://cryptography.io/) - Cryptographic recipes and primitives

### 📧 Support

- **Issues**: [GitHub Issues](https://github.com/MoYuK1ng/MC_rcon_manage/issues)
- **Discussions**: [GitHub Discussions](https://github.com/MoYuK1ng/MC_rcon_manage/discussions)
- **Documentation**: [Project Wiki](https://github.com/MoYuK1ng/MC_rcon_manage/wiki)

### 🗺️ Roadmap

- [ ] PostgreSQL support and migration guide
- [ ] Docker containerization
- [ ] Multi-language support (Japanese, Korean, Spanish)
- [ ] Advanced RCON command templates
- [ ] Server performance monitoring
- [ ] Automated server backups
- [ ] Discord webhook integration
- [ ] API for external integrations

---

## 中文

### 🌟 功能特性

- 🔐 **企业级安全** - Fernet 加密 RCON 密码，CSRF 保护，输入验证
- 🎮 **多服务器管理** - 从单一仪表板管理无限数量的 Minecraft 服务器
- 👥 **实时玩家监控** - 30 秒轮询自动刷新玩家列表
- ✅ **白名单管理** - 通过 RCON 命令将玩家添加到服务器白名单
- 🔒 **加密凭证** - 所有 RCON 密码静态加密，永不明文存储
- 🔧 **灵活显示设置** - 控制服务器 IP/端口信息的可见性
- 📢 **公告系统** - 向所有用户发布系统范围的公告
- 🌍 **完整国际化** - 完全支持英语和简体中文
- 📱 **响应式设计** - 现代化 Tailwind CSS UI 优化所有设备
- ⚡ **动态更新** - HTMX 实现无需页面重载的无缝更新
- 🎨 **精美界面** - 灵感来自 Vercel 和 Linear 的简洁现代设计
- 🧪 **全面测试** - 70+ 测试，包括使用 Hypothesis 的基于属性的测试
- 🚀 **生产就绪** - 使用 Gunicorn + Nginx 优化部署
- 📦 **轻松部署** - Linux VPS 一键安装脚本


### 📸 截图

*即将推出 - 在此添加您的截图*

### 🚀 快速开始

#### 前置要求

- **Python 3.10 或更高版本**
- **pip**（Python 包管理器）
- **Linux VPS**（用于生产部署）
- **Minecraft 服务器**（启用 RCON）

#### 安装方法

**方式 1：一键安装（推荐用于生产环境）**

适用于 Linux VPS 部署，自动设置所有依赖、Nginx 和 systemd 服务。

```bash
# 下载并运行管理脚本
wget https://raw.githubusercontent.com/MoYuK1ng/MC_rcon_manage/main/manage.sh
chmod +x manage.sh
sudo bash manage.sh

# 选择语言（中文/英文）
# 然后选择：1) 全新安装
```

脚本自动处理：
- ✅ 系统依赖安装（Python、Nginx、Git）
- ✅ 仓库克隆和虚拟环境设置
- ✅ 数据库初始化和迁移
- ✅ 管理员账户创建
- ✅ Gunicorn + Nginx 配置
- ✅ Systemd 服务设置和自动启动
- ✅ SSL/TLS 支持（可选）

**方式 2：手动安装（开发环境）**

用于本地开发或自定义部署：

```bash
# 克隆仓库
git clone https://github.com/MoYuK1ng/MC_rcon_manage.git
cd MC_rcon_manage

# 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装生产依赖
pip install -r requirements.txt

# 生成加密密钥
python generate_key.py

# 配置环境变量
cp .env.example .env
# 编辑 .env 并设置您的 SECRET_KEY、ALLOWED_HOSTS 等

# 运行数据库迁移
python manage.py migrate

# 创建超级用户账户
python manage.py createsuperuser

# 收集静态文件
python manage.py collectstatic --noinput

# 启动开发服务器
python manage.py runserver
```

访问 `http://localhost:8000/admin` 配置服务器和组。


### 🔐 安全配置

#### 设置 RCON 密码

RCON 密码使用 Fernet 对称加密，出于安全原因无法通过管理界面设置。

```bash
# 方法 1：使用提供的脚本（推荐）
python set_rcon_password.py

# 方法 2：使用 Django shell
python manage.py shell
>>> from servers.models import Server
>>> server = Server.objects.get(name="您的服务器名称")
>>> server.set_password("your_rcon_password")
>>> server.save()
```

#### 加密密钥管理

应用程序使用 Fernet 对称加密保护 RCON 密码。正确的密钥管理对安全至关重要。

```bash
# 生成新的加密密钥（首次设置）
python generate_key.py

# 验证当前密钥是否有效
python verify_key.py

# 测试所有存储的密码是否可以解密
python verify_key.py --test-passwords

# 轮换加密密钥（重新加密所有密码）
python rotate_key.py --generate-new
```

**🔒 安全最佳实践：**
- ✅ 切勿将加密密钥提交到版本控制
- ✅ 将密钥安全存储在 `.env` 文件中（已在 `.gitignore` 中）
- ✅ 定期轮换密钥（建议每 6-12 个月）
- ✅ 密钥轮换前创建数据库备份
- ✅ 为管理员账户使用强大、唯一的密码
- ✅ 在生产环境中启用 HTTPS（使用 Let's Encrypt）
- ✅ 保持 Django 和依赖项更新

### 💾 数据库备份与恢复

#### 备份数据库

```bash
# 运行管理脚本
sudo bash manage.sh

# 选择选项 8) 备份数据
# 输入备份目录（或按 Enter 使用当前目录）
```

创建带时间戳的备份：`db_backup_YYYYMMDD_HHMMSS.sqlite3`

#### 恢复数据库

```bash
# 运行管理脚本
sudo bash manage.sh

# 选择选项 9) 恢复数据
# 输入备份文件的完整路径
```

恢复过程自动：
1. 显示备份文件信息
2. 创建当前数据库的安全备份
3. 停止服务
4. 恢复备份
5. 重启服务

#### 自动备份（推荐）

```bash
# 创建自动备份脚本
cat > /opt/mc_rcon/auto_backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/mc_rcon/backups"
mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
cp /opt/mc_rcon/db.sqlite3 "$BACKUP_DIR/db_backup_${TIMESTAMP}.sqlite3"
# 只保留最近 7 天的备份
find "$BACKUP_DIR" -name "db_backup_*.sqlite3" -mtime +7 -delete
EOF

chmod +x /opt/mc_rcon/auto_backup.sh

# 设置每天凌晨 2 点自动备份
crontab -e
# 添加：0 2 * * * /opt/mc_rcon/auto_backup.sh >> /var/log/mc_rcon_backup.log 2>&1
```


### 🏗️ 架构

```
┌─────────────────────────────────────────────────────────────┐
│                     Web 浏览器（客户端）                      │
│              Tailwind CSS + HTMX + Lucide Icons             │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Nginx（反向代理）                            │
│              - SSL/TLS 终止                                  │
│              - 静态文件服务                                   │
│              - 请求转发                                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Gunicorn WSGI 服务器                            │
│              - 多个工作进程                                   │
│              - 负载均衡                                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Django 应用程序                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   视图       │  │   模板       │  │    模型      │     │
│  │  - 认证      │◄─┤  - i18n      │  │  - 服务器    │     │
│  │  - RCON      │  │  - Jazzmin   │  │  - 白名单    │     │
│  │  - 仪表板    │  └──────────────┘  │  - 公告      │     │
│  └──────┬───────┘                    └──────┬───────┘     │
│         │                                    │              │
│         ▼                                    ▼              │
│  ┌──────────────────────┐         ┌──────────────────┐    │
│  │   RCON 服务          │         │  加密             │    │
│  │   - 连接池           │         │  - Fernet         │    │
│  │   - 命令执行         │         │  - 密钥管理       │    │
│  └──────┬───────────────┘         └──────────────────┘    │
└─────────┼──────────────────────────────────────────────────┘
          │ RCON 协议 (TCP)
          ▼
┌─────────────────────────────────────────────────────────────┐
│              Minecraft 服务器（启用 RCON）                    │
└─────────────────────────────────────────────────────────────┘
```

### 🔒 安全特性

- **密码加密**：RCON 密码使用 Fernet 加密（AES-128-CBC）
- **输入验证**：正则表达式验证防止命令注入攻击
- **访问控制**：基于组的权限和 `@user_has_server_access` 装饰器
- **CSRF 保护**：为 HTMX 请求配置 Django CSRF 令牌
- **安全默认值**：生产设置包括 HSTS、安全 cookie、X-Frame-Options
- **SQL 注入保护**：Django ORM 防止 SQL 注入
- **XSS 保护**：模板自动转义防止跨站脚本攻击
- **会话安全**：使用 HTTPOnly 和 SameSite 标志的安全会话 cookie


### 🧪 测试

项目包含全面的测试，包括单元测试和基于属性的测试。

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行所有测试
pytest servers/tests.py -v

# 运行并生成覆盖率报告
pytest servers/tests.py --cov=servers --cov-report=html

# 运行基于属性的测试并显示统计信息
pytest servers/tests.py --hypothesis-show-statistics

# 运行特定测试类
pytest servers/tests.py::ServerModelTests -v
```

**测试覆盖率：**
- ✅ 总共 70+ 测试
- ✅ 12 个基于属性的测试（Hypothesis）
- ✅ 58 个单元测试（Django TestCase）
- ✅ 100% 通过率
- ✅ 测试覆盖模型、视图、服务和工具

### 📦 技术栈

| 组件 | 技术 | 版本 |
|------|------|------|
| 后端框架 | Django | 5.0+ |
| 数据库 | SQLite / PostgreSQL | - |
| RCON 客户端 | mcrcon | 0.7.0+ |
| 加密 | cryptography (Fernet) | 41.0.0+ |
| 前端 CSS | Tailwind CSS | 3.x |
| 动态更新 | HTMX | 1.9.x |
| 图标 | Lucide Icons | 最新 |
| 管理界面 | Django Jazzmin | 3.0+ |
| 测试 | pytest + Hypothesis | 最新 |
| WSGI 服务器 | Gunicorn | 21.2.0+ |
| 静态文件 | Whitenoise | 6.6.0+ |

### 🌐 API 端点

| 端点 | 方法 | 描述 | 需要认证 |
|------|------|------|----------|
| `/` | GET | 登陆页面 | 否 |
| `/dashboard/` | GET | 主仪表板和服务器列表 | 是 |
| `/server/<id>/players/` | GET | 玩家列表的 HTMX 端点 | 是 |
| `/server/<id>/whitelist/` | POST | 将玩家添加到白名单 | 是 |
| `/my-whitelist/` | GET | 用户的白名单请求 | 是 |
| `/i18n/setlang/` | POST | 语言切换器 | 否 |
| `/admin/` | GET | Django 管理面板 | 管理员 |
| `/accounts/login/` | GET/POST | 用户登录 | 否 |
| `/accounts/register/` | GET/POST | 用户注册 | 否 |


### 🤝 贡献

欢迎贡献！请遵循以下指南：

1. **Fork 本仓库**
2. **创建功能分支**：`git checkout -b feature/AmazingFeature`
3. **安装开发依赖**：`pip install -r requirements-dev.txt`
4. **进行更改**并添加测试
5. **运行测试**：`pytest servers/tests.py`
6. **运行代码检查**：`flake8 . && pylint servers/`
7. **提交更改**：`git commit -m 'Add some AmazingFeature'`
8. **推送到分支**：`git push origin feature/AmazingFeature`
9. **打开 Pull Request**

**代码风格：**
- 遵循 PEP 8 指南
- 使用有意义的变量和函数名
- 为所有函数和类添加文档字符串
- 为新功能编写测试
- 保持提交原子化和描述清晰

**翻译贡献：**
- 翻译文件位于 `locale/zh_hans/LC_MESSAGES/`
- 使用 `python manage.py makemessages` 更新翻译文件
- 使用 `python manage.py compilemessages` 编译翻译
- 详细翻译指南请参阅 `locale/README.md`

### 📝 许可证

本项目采用 **MIT 许可证** - 详见 [LICENSE](LICENSE) 文件。

```
MIT License

Copyright (c) 2024-2025 MoYuK1ng

特此免费授予任何获得本软件及相关文档文件（"软件"）副本的人不受限制地处理
软件的权利，包括但不限于使用、复制、修改、合并、发布、分发、再许可和/或
出售软件副本的权利，并允许向其提供软件的人这样做，但须符合以下条件：

上述版权声明和本许可声明应包含在软件的所有副本或主要部分中。

本软件按"原样"提供，不提供任何形式的明示或暗示保证，包括但不限于对适销性、
特定用途适用性和非侵权性的保证。在任何情况下，作者或版权持有人均不对任何
索赔、损害或其他责任负责，无论是在合同诉讼、侵权行为还是其他方面，由软件
或软件的使用或其他交易引起、产生或与之相关。
```

**第三方许可证：**
- Django：BSD 许可证
- mcrcon：MIT 许可证
- cryptography：Apache License 2.0 / BSD 许可证
- Tailwind CSS：MIT 许可证
- HTMX：BSD 2-Clause 许可证
- Hypothesis：Mozilla Public License 2.0

### 🙏 致谢

- 使用 [Django](https://www.djangoproject.com/) 构建 - 为追求完美的开发者提供的 Web 框架
- RCON 客户端：[mcrcon](https://github.com/barneygale/MCRcon) - Minecraft RCON 客户端库
- UI 框架：[Tailwind CSS](https://tailwindcss.com/) - 实用优先的 CSS 框架
- 图标：[Lucide Icons](https://lucide.dev/) - 美观一致的图标工具包
- 动态更新：[HTMX](https://htmx.org/) - HTML 的高性能工具
- 管理主题：[Django Jazzmin](https://django-jazzmin.readthedocs.io/) - Django 管理主题
- 测试：[Hypothesis](https://hypothesis.readthedocs.io/) - Python 的基于属性的测试
- 加密：[cryptography](https://cryptography.io/) - 加密配方和原语

### 📧 支持

- **问题**：[GitHub Issues](https://github.com/MoYuK1ng/MC_rcon_manage/issues)
- **讨论**：[GitHub Discussions](https://github.com/MoYuK1ng/MC_rcon_manage/discussions)
- **文档**：[项目 Wiki](https://github.com/MoYuK1ng/MC_rcon_manage/wiki)

### 🗺️ 路线图

- [ ] PostgreSQL 支持和迁移指南
- [ ] Docker 容器化
- [ ] 多语言支持（日语、韩语、西班牙语）
- [ ] 高级 RCON 命令模板
- [ ] 服务器性能监控
- [ ] 自动服务器备份
- [ ] Discord webhook 集成
- [ ] 外部集成 API

---

<div align="center">

**Developed with ❤️ by MoYuK1ng**

**Copyright © 2024-2025 MoYuK1ng. All Rights Reserved.**

**Licensed under the MIT License**

[⬆ Back to Top](#-mc-rcon-manager---minecraft-rcon-web-portal)

</div>
