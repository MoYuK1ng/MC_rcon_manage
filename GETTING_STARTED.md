# Getting Started with IronGate | IronGate 入门指南

Quick reference guide for getting IronGate up and running.

快速参考指南，帮助您启动和运行 IronGate�?

---

## English

### �?5-Minute Setup

```bash
# 1. Clone and install
git clone https://github.com/MoYuK1ng/MC_rcon_manage.git
cd irongate
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Generate encryption key
python generate_key.py

# 3. Setup database
python manage.py migrate
python manage.py createsuperuser

# 4. Start server
python manage.py runserver
```

### 🎯 First Steps

1. **Access Admin Panel**: http://localhost:8000/admin/
2. **Create a Group**: e.g., "SMP Players"
3. **Add Users**: Create users and assign to groups
4. **Add Server**:
   - Name: "My Minecraft Server"
   - IP: Your server IP
   - Port: 25575 (default RCON port)
   - Password: Your RCON password
   - Groups: Select "SMP Players"
5. **Access Dashboard**: http://localhost:8000/dashboard/

### 🔧 Minecraft Server Configuration

Edit your Minecraft `server.properties`:

```properties
enable-rcon=true
rcon.port=25575
rcon.password=your-secure-password
```

Restart your Minecraft server.

### 🌍 Enable Chinese Translation

```bash
# Install gettext (if not already installed)
# Linux:
sudo apt install gettext

# macOS:
brew install gettext

# Compile translations
python manage.py compilemessages

# Restart server
python manage.py runserver
```

Switch language using the dropdown in the navigation bar.

### 📚 Next Steps

- **Production Deployment**: See [DEPLOYMENT.md](DEPLOYMENT.md)
- **Security Hardening**: Review security checklist in deployment guide
- **Troubleshooting**: Check the troubleshooting section in DEPLOYMENT.md

---

## 中文

### �?5 分钟设置

```bash
# 1. 克隆并安�?
git clone https://github.com/MoYuK1ng/MC_rcon_manage.git
cd irongate
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. 生成加密密钥
python generate_key.py

# 3. 设置数据�?
python manage.py migrate
python manage.py createsuperuser

# 4. 启动服务�?
python manage.py runserver
```

### 🎯 首要步骤

1. **访问管理面板**：http://localhost:8000/admin/
2. **创建�?*：例�?"SMP 玩家"
3. **添加用户**：创建用户并分配到组
4. **添加服务�?*�?
   - 名称�?我的 Minecraft 服务�?
   - IP：您的服务器 IP
   - 端口�?5575（默�?RCON 端口�?
   - 密码：您�?RCON 密码
   - 组：选择 "SMP 玩家"
5. **访问仪表�?*：http://localhost:8000/dashboard/

### 🔧 Minecraft 服务器配�?

编辑您的 Minecraft `server.properties`�?

```properties
enable-rcon=true
rcon.port=25575
rcon.password=your-secure-password
```

重启您的 Minecraft 服务器�?

### 🌍 启用中文翻译

```bash
# 安装 gettext（如果尚未安装）
# Linux:
sudo apt install gettext

# macOS:
brew install gettext

# 编译翻译
python manage.py compilemessages

# 重启服务�?
python manage.py runserver
```

使用导航栏中的下拉菜单切换语言�?

### 📚 下一�?

- **生产环境部署**：查�?[DEPLOYMENT.md](DEPLOYMENT.md)
- **安全加固**：查看部署指南中的安全检查清�?
- **故障排除**：查�?DEPLOYMENT.md 中的故障排除部分

---

## Common Issues | 常见问题

### Translation Not Working | 翻译不工�?

**Problem**: Interface still in English
**问题**：界面仍为英�?

**Solution**:
```bash
# Ensure gettext is installed
which msgfmt

# Compile messages
python manage.py compilemessages

# Check for .mo files
ls locale/zh_hans/LC_MESSAGES/

# Should see: django.mo
```

### RCON Connection Failed | RCON 连接失败

**Problem**: "Connection refused"
**问题**�?连接被拒�?

**Solution**:
1. Check Minecraft server has RCON enabled
2. Verify firewall allows RCON port (25575)
3. Test connection: `telnet <server-ip> 25575`

---

## Support | 支持

- **Documentation**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Issues**: [GitHub Issues](https://github.com/MoYuK1ng/MC_rcon_manage/issues)
- **Discussions**: [GitHub Discussions](https://github.com/MoYuK1ng/MC_rcon_manage/discussions)
