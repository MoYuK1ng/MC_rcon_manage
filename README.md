# 🎮 IronGate - Minecraft RCON Web Portal

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/Django-5.0-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-70%20Passing-brightgreen.svg)](#testing)

A secure, modern web portal for managing Minecraft servers via RCON protocol with group-based access control.

[English](#english) | [中文](#中文)

</div>

---

## English

### 🌟 Features

- 🔐 **Secure Authentication** - Django-based user authentication with group permissions
- 🎮 **Multi-Server Management** - Manage multiple Minecraft servers from one dashboard
- 👥 **Real-Time Player Monitoring** - Auto-refreshing player lists (30-second polling)
- ✅ **Whitelist Management** - Add players to server whitelists via RCON
- 🔒 **Encrypted Credentials** - RCON passwords encrypted with Fernet symmetric encryption
- 🌍 **Internationalization** - Full support for English and Simplified Chinese
- 📱 **Responsive Design** - Bootstrap 5 UI works seamlessly on all devices
- ⚡ **Modern Tech Stack** - HTMX for dynamic updates without page reloads
- 🧪 **Comprehensive Testing** - 70 tests including property-based testing with Hypothesis

### 📸 Screenshots

*Coming soon - Add your screenshots here*

### 🚀 Quick Start

#### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

#### Installation

```bash
# Clone the repository
git clone https://github.com/MoYuK1ng/MC_rcon_manage.git
cd MC_rcon_manage

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Generate encryption key
python generate_key.py

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server (multiple options)
python run_server.py              # Smart launcher (auto port selection)
python run_server.py -p 8080      # Custom port
python run_server.py --random     # Random port
python manage.py runserver        # Traditional Django command
```

Visit http://localhost:8000/admin to configure servers and groups.

### 📖 Documentation

- **[Server Launcher Guide](SERVER_LAUNCHER.md)** - Flexible server startup options
- **[Deployment Guide](DEPLOYMENT.md)** - Complete production deployment instructions (English & Chinese)
- **[Getting Started](GETTING_STARTED.md)** - Quick start guide (English & Chinese)
- **[Nginx Setup](NGINX_SETUP.md)** - Nginx reverse proxy configuration
- **[Production Checklist](PRODUCTION_CHECKLIST.md)** - Pre-deployment verification
- **[Translation Guide](locale/README.md)** - How to add or update translations

### 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Web Browser                          │
│              (Bootstrap 5 + HTMX for AJAX)                  │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Django Application                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Views      │  │  Templates   │  │    Models    │     │
│  │  (Auth +     │◄─┤  (i18n +     │  │  (Server,    │     │
│  │   Access     │  │   Bootstrap) │  │   Whitelist) │     │
│  │   Control)   │  └──────────────┘  └──────┬───────┘     │
│  └──────┬───────┘                            │              │
│         │                                    │              │
│         ▼                                    ▼              │
│  ┌──────────────────────┐         ┌──────────────────┐    │
│  │   RconHandler        │         │  Encryption      │    │
│  │   Service            │         │  Utility         │    │
│  │  (mcrcon wrapper)    │         │  (Fernet)        │    │
│  └──────┬───────────────┘         └──────────────────┘    │
└─────────┼──────────────────────────────────────────────────┘
          │ RCON Protocol
          ▼
┌─────────────────────────────────────────────────────────────┐
│              Minecraft Servers (RCON enabled)                │
└─────────────────────────────────────────────────────────────┘
```

### 🔒 Security Features

- **Password Encryption**: RCON passwords encrypted with Fernet (never plaintext)
- **Input Validation**: Regex validation prevents command injection (`^[a-zA-Z0-9_]{3,16}$`)
- **Access Control**: Group-based permissions with `@user_has_server_access` decorator
- **CSRF Protection**: Django CSRF tokens configured for HTMX requests
- **Secure Defaults**: Production settings include HSTS, secure cookies, and more

### 🧪 Testing

Run the comprehensive test suite:

```bash
# All tests (70 tests)
pytest servers/tests/

# Specific test categories
pytest servers/tests/test_models.py      # Model tests
pytest servers/tests/test_services.py    # RCON service tests
pytest servers/tests/test_views.py       # View tests
pytest servers/tests/test_properties.py  # Property-based tests
```

**Test Coverage:**
- 12 property-based tests (Hypothesis)
- 58 unit tests (Django TestCase + mocking)
- 100% passing rate

### 📦 Technology Stack

| Component | Technology |
|-----------|-----------|
| Backend Framework | Django 5.0 |
| Database | SQLite (dev) / PostgreSQL (prod) |
| RCON Client | mcrcon |
| Encryption | cryptography (Fernet) |
| Frontend | Bootstrap 5 + HTMX |
| Testing | pytest + Hypothesis |
| WSGI Server | Gunicorn (production) |

### 🌐 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/dashboard/` | GET | Main dashboard with server list |
| `/server/<id>/players/` | GET | HTMX endpoint for player list |
| `/server/<id>/whitelist/` | POST | Add player to whitelist |
| `/i18n/setlang/` | POST | Language switcher |
| `/admin/` | GET | Django admin panel |

### 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### 🙏 Acknowledgments

- Built with [Django](https://www.djangoproject.com/)
- RCON client: [mcrcon](https://github.com/barneygale/MCRcon)
- UI: [Bootstrap 5](https://getbootstrap.com/)
- Dynamic updates: [HTMX](https://htmx.org/)
- Testing: [Hypothesis](https://hypothesis.readthedocs.io/)

### 📧 Support

- **Issues**: [GitHub Issues](https://github.com/MoYuK1ng/MC_rcon_manage/issues)
- **Discussions**: [GitHub Discussions](https://github.com/MoYuK1ng/MC_rcon_manage/discussions)

---

## 中文

### 🌟 功能特性

- 🔐 **安全认证** - 基于 Django 的用户认证和组权限管理
- 🎮 **多服务器管理** - 从一个仪表板管理多个 Minecraft 服务器
- 👥 **实时玩家监控** - 自动刷新玩家列表（30 秒轮询）
- ✅ **白名单管理** - 通过 RCON 将玩家添加到服务器白名单
- 🔒 **加密凭证** - 使用 Fernet 对称加密保护 RCON 密码
- 🌍 **国际化** - 完整支持英语和简体中文
- 📱 **响应式设计** - Bootstrap 5 UI 在所有设备上无缝工作
- ⚡ **现代技术栈** - HTMX 实现无需页面重载的动态更新
- 🧪 **全面测试** - 70 个测试，包括使用 Hypothesis 的基于属性的测试

### 📸 截图

*即将推出 - 在此添加您的截图*

### 🚀 快速开始

#### 前置要求

- Python 3.10 或更高版本
- pip（Python 包管理器）

#### 安装

```bash
# 克隆仓库
git clone https://github.com/MoYuK1ng/MC_rcon_manage.git
cd MC_rcon_manage

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 生成加密密钥
python generate_key.py

# 运行迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 启动开发服务器（多种方式）
python run_server.py              # 智能启动器（自动端口选择）
python run_server.py -p 8080      # 自定义端口
python run_server.py --random     # 随机端口
python manage.py runserver        # 传统 Django 命令
```

访问 http://localhost:8000/admin 配置服务器和组。

### 📖 文档

- **[服务器启动指南](SERVER_LAUNCHER.md)** - 灵活的服务器启动选项
- **[部署指南](DEPLOYMENT.md)** - 完整的生产环境部署说明（中英文）
- **[快速开始](GETTING_STARTED.md)** - 快速入门指南（中英文）
- **[Nginx 配置](NGINX_SETUP.md)** - Nginx 反向代理配置
- **[生产检查清单](PRODUCTION_CHECKLIST.md)** - 部署前验证清单
- **[翻译指南](locale/README.md)** - 如何添加或更新翻译

### 🏗️ 架构

```
┌─────────────────────────────────────────────────────────────┐
│                        Web 浏览器                            │
│              (Bootstrap 5 + HTMX AJAX)                      │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Django 应用程序                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   视图       │  │   模板       │  │    模型      │     │
│  │  (认证 +     │◄─┤  (i18n +     │  │  (服务器,    │     │
│  │   访问控制)  │  │   Bootstrap) │  │   白名单)    │     │
│  └──────┬───────┘  └──────────────┘  └──────┬───────┘     │
│         │                                    │              │
│         ▼                                    ▼              │
│  ┌──────────────────────┐         ┌──────────────────┐    │
│  │   RCON处理器         │         │  加密工具        │    │
│  │   服务               │         │  (Fernet)        │    │
│  └──────┬───────────────┘         └──────────────────┘    │
└─────────┼──────────────────────────────────────────────────┘
          │ RCON 协议
          ▼
┌─────────────────────────────────────────────────────────────┐
│              Minecraft 服务器 (启用 RCON)                    │
└─────────────────────────────────────────────────────────────┘
```

### 🔒 安全特性

- **密码加密**：RCON 密码使用 Fernet 加密（永不明文存储）
- **输入验证**：正则表达式验证防止命令注入（`^[a-zA-Z0-9_]{3,16}$`）
- **访问控制**：基于组的权限和 `@user_has_server_access` 装饰器
- **CSRF 保护**：为 HTMX 请求配置 Django CSRF 令牌
- **安全默认值**：生产设置包括 HSTS、安全 cookie 等

### 🧪 测试

运行全面的测试套件：

```bash
# 所有测试（70 个测试）
pytest servers/tests/

# 特定测试类别
pytest servers/tests/test_models.py      # 模型测试
pytest servers/tests/test_services.py    # RCON 服务测试
pytest servers/tests/test_views.py       # 视图测试
pytest servers/tests/test_properties.py  # 基于属性的测试
```

**测试覆盖率：**
- 12 个基于属性的测试（Hypothesis）
- 58 个单元测试（Django TestCase + 模拟）
- 100% 通过率

### 📦 技术栈

| 组件 | 技术 |
|------|------|
| 后端框架 | Django 5.0 |
| 数据库 | SQLite（开发）/ PostgreSQL（生产）|
| RCON 客户端 | mcrcon |
| 加密 | cryptography (Fernet) |
| 前端 | Bootstrap 5 + HTMX |
| 测试 | pytest + Hypothesis |
| WSGI 服务器 | Gunicorn（生产）|

### 🌐 API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/dashboard/` | GET | 主仪表板和服务器列表 |
| `/server/<id>/players/` | GET | 玩家列表的 HTMX 端点 |
| `/server/<id>/whitelist/` | POST | 将玩家添加到白名单 |
| `/i18n/setlang/` | POST | 语言切换器 |
| `/admin/` | GET | Django 管理面板 |

### 🤝 贡献

欢迎贡献！请随时提交 Pull Request。

1. Fork 本仓库
2. 创建您的功能分支（`git checkout -b feature/AmazingFeature`）
3. 提交您的更改（`git commit -m 'Add some AmazingFeature'`）
4. 推送到分支（`git push origin feature/AmazingFeature`）
5. 打开 Pull Request

### 📝 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

### 🙏 致谢

- 使用 [Django](https://www.djangoproject.com/) 构建
- RCON 客户端：[mcrcon](https://github.com/barneygale/MCRcon)
- UI：[Bootstrap 5](https://getbootstrap.com/)
- 动态更新：[HTMX](https://htmx.org/)
- 测试：[Hypothesis](https://hypothesis.readthedocs.io/)

### 📧 支持

- **问题**：[GitHub Issues](https://github.com/MoYuK1ng/MC_rcon_manage/issues)
- **讨论**：[GitHub Discussions](https://github.com/MoYuK1ng/MC_rcon_manage/discussions)

---

<div align="center">

Made with ❤️ by the IronGate Team

[⬆ Back to Top](#-irongate---minecraft-rcon-web-portal)

</div>
