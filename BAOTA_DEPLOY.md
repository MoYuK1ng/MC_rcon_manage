# 宝塔面板部署指南 | BaoTa Panel Deployment Guide

## 中文

### 📋 前置要求

- 已安装宝塔面板
- Python 3.10+ (可通过宝塔安装)
- 已有域名并解析到服务器

### 🚀 部署步骤

#### 1. 安装 Python 环境

在宝塔面板：
1. 进入 **软件商店**
2. 搜索 **Python项目管理器**
3. 安装 Python 3.10 或更高版本

#### 2. 克隆项目

```bash
# SSH 登录服务器
cd /www/wwwroot
git clone https://github.com/MoYuK1ng/MC_rcon_manage.git mc_rcon
cd mc_rcon
```

#### 3. 创建虚拟环境并安装依赖

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 4. 生成加密密钥

```bash
python generate_key.py
```

这会创建 `.env` 文件并生成加密密钥。

#### 5. 配置环境变量

编辑 `.env` 文件，添加你的域名配置：

```bash
nano .env
```

**重要配置项：**

```bash
# 基础配置
SECRET_KEY=your-secret-key-here
DEBUG=False
RCON_ENCRYPTION_KEY=your-generated-key

# 域名配置（重要！）
ALLOWED_HOSTS=localhost,127.0.0.1,mc.moyuu.online
CSRF_TRUSTED_ORIGINS=https://mc.moyuu.online,http://localhost:8000

# 端口配置（可选）
APP_PORT=8000
```

**⚠️ 关键点：**
- `ALLOWED_HOSTS`: 只需域名，不要协议（http/https）
- `CSRF_TRUSTED_ORIGINS`: 必须包含完整协议（https://）
- 多个域名用逗号分隔，**不要有空格**

#### 6. 初始化数据库

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

#### 7. 在宝塔中创建 Python 项目

1. 进入宝塔面板 → **网站**
2. 点击 **Python项目**
3. 点击 **添加项目**

**配置信息：**
- **项目名称**: MC RCON Manager
- **项目路径**: `/www/wwwroot/mc_rcon`
- **Python版本**: 选择 3.10+
- **框架**: Django
- **启动方式**: Gunicorn
- **端口**: 8000 (或你在 .env 中设置的端口)
- **启动命令**: 
  ```bash
  /www/wwwroot/mc_rcon/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 irongate.wsgi:application
  ```

#### 8. 配置反向代理

1. 进入宝塔面板 → **网站**
2. 点击 **添加站点**
   - 域名: `mc.moyuu.online`
   - 根目录: 随意（不会用到）
   - PHP版本: 纯静态

3. 点击站点设置 → **反向代理**
4. 添加反向代理：
   - 代理名称: `mc_rcon`
   - 目标URL: `http://127.0.0.1:8000`
   - 发送域名: `$host`
   - 内容替换: 留空

5. **配置文件**（点击"配置文件"）添加以下内容：

```nginx
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Host $host;
    
    # 超时设置
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;
}

location /static/ {
    alias /www/wwwroot/mc_rcon/staticfiles/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

#### 9. 配置 SSL 证书（推荐）

1. 在站点设置中点击 **SSL**
2. 选择 **Let's Encrypt** 免费证书
3. 勾选你的域名
4. 点击申请

**申请成功后，更新 .env 文件：**

```bash
# 将 http 改为 https
CSRF_TRUSTED_ORIGINS=https://mc.moyuu.online
```

然后重启 Python 项目。

#### 10. 启动项目

在宝塔的 Python 项目管理中：
1. 找到你的项目
2. 点击 **启动**
3. 查看状态确认运行正常

### ✅ 验证部署

访问你的域名：
- 主页: `https://mc.moyuu.online`
- 管理后台: `https://mc.moyuu.online/admin`

### 🔧 常见问题

#### 问题 1: CSRF 403 错误

**症状**: 访问网站显示 "CSRF verification failed"

**解决方案**:

1. 检查 `.env` 文件配置：
```bash
# 确保包含你的域名和协议
ALLOWED_HOSTS=localhost,127.0.0.1,mc.moyuu.online
CSRF_TRUSTED_ORIGINS=https://mc.moyuu.online
```

2. 重启 Python 项目：
   - 宝塔面板 → Python项目 → 重启

3. 清除浏览器缓存并重新访问

#### 问题 2: 静态文件 404

**解决方案**:

```bash
cd /www/wwwroot/mc_rcon
source venv/bin/activate
python manage.py collectstatic --noinput
```

然后在 Nginx 配置中确保有 `/static/` location 块。

#### 问题 3: 项目无法启动

**检查日志**:
```bash
# 在宝塔 Python 项目管理中查看日志
# 或者手动查看
tail -f /www/wwwroot/mc_rcon/logs/*.log
```

**常见原因**:
- 端口被占用：更改 `.env` 中的 `APP_PORT`
- 依赖未安装：重新运行 `pip install -r requirements.txt`
- 数据库未迁移：运行 `python manage.py migrate`

#### 问题 4: 无法访问管理后台

**解决方案**:

1. 确认超级用户已创建：
```bash
cd /www/wwwroot/mc_rcon
source venv/bin/activate
python manage.py createsuperuser
```

2. 访问 `https://yourdomain.com/admin`

### 🔄 更新项目

```bash
cd /www/wwwroot/mc_rcon

# 备份数据库
cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d)

# 拉取最新代码
git pull origin main

# 激活虚拟环境
source venv/bin/activate

# 更新依赖
pip install -r requirements.txt --upgrade

# 运行迁移
python manage.py migrate

# 收集静态文件
python manage.py collectstatic --noinput

# 在宝塔面板中重启 Python 项目
```

### 📊 性能优化建议

1. **使用 PostgreSQL 替代 SQLite**（可选）
   - 在宝塔中安装 PostgreSQL
   - 修改 `settings.py` 数据库配置

2. **配置 Redis 缓存**（可选）
   - 在宝塔中安装 Redis
   - 配置 Django 缓存

3. **增加 Gunicorn workers**
   - 根据 CPU 核心数调整：`workers = CPU核心数 * 2 + 1`

### 🔒 安全建议

1. **定期备份数据库**
   ```bash
   # 在宝塔中设置计划任务
   0 2 * * * cp /www/wwwroot/mc_rcon/db.sqlite3 /www/backup/mc_rcon_$(date +\%Y\%m\%d).db
   ```

2. **设置防火墙规则**
   - 只开放 80, 443, 22 端口
   - 应用端口（8000）不要对外开放

3. **定期更新**
   - 定期 `git pull` 获取更新
   - 关注 GitHub 仓库的安全更新

---

## English

### 📋 Prerequisites

- BaoTa Panel installed
- Python 3.10+ (can be installed via BaoTa)
- Domain name pointing to your server

### 🚀 Deployment Steps

#### 1. Install Python Environment

In BaoTa Panel:
1. Go to **App Store**
2. Search for **Python Project Manager**
3. Install Python 3.10 or higher

#### 2. Clone Project

```bash
# SSH to server
cd /www/wwwroot
git clone https://github.com/MoYuK1ng/MC_rcon_manage.git mc_rcon
cd mc_rcon
```

#### 3. Create Virtual Environment and Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 4. Generate Encryption Key

```bash
python generate_key.py
```

This creates `.env` file with encryption key.

#### 5. Configure Environment Variables

Edit `.env` file:

```bash
nano .env
```

**Important settings:**

```bash
# Basic config
SECRET_KEY=your-secret-key-here
DEBUG=False
RCON_ENCRYPTION_KEY=your-generated-key

# Domain config (IMPORTANT!)
ALLOWED_HOSTS=localhost,127.0.0.1,mc.example.com
CSRF_TRUSTED_ORIGINS=https://mc.example.com,http://localhost:8000

# Port config (optional)
APP_PORT=8000
```

**⚠️ Key Points:**
- `ALLOWED_HOSTS`: Domain only, no protocol
- `CSRF_TRUSTED_ORIGINS`: Must include full protocol (https://)
- Multiple domains separated by comma, **no spaces**

#### 6. Initialize Database

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

#### 7. Create Python Project in BaoTa

1. BaoTa Panel → **Website**
2. Click **Python Project**
3. Click **Add Project**

**Configuration:**
- **Project Name**: MC RCON Manager
- **Project Path**: `/www/wwwroot/mc_rcon`
- **Python Version**: 3.10+
- **Framework**: Django
- **Start Method**: Gunicorn
- **Port**: 8000
- **Start Command**: 
  ```bash
  /www/wwwroot/mc_rcon/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 irongate.wsgi:application
  ```

#### 8. Configure Reverse Proxy

1. BaoTa Panel → **Website** → **Add Site**
   - Domain: `mc.example.com`
   - Root directory: any (won't be used)
   - PHP: Static

2. Site Settings → **Reverse Proxy**
3. Add proxy:
   - Proxy name: `mc_rcon`
   - Target URL: `http://127.0.0.1:8000`
   - Send domain: `$host`

4. **Config file** add:

```nginx
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Host $host;
    
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;
}

location /static/ {
    alias /www/wwwroot/mc_rcon/staticfiles/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

#### 9. Configure SSL (Recommended)

1. Site Settings → **SSL**
2. Select **Let's Encrypt**
3. Apply certificate

**After SSL, update .env:**

```bash
CSRF_TRUSTED_ORIGINS=https://mc.example.com
```

Restart Python project.

#### 10. Start Project

In BaoTa Python Project Manager:
1. Find your project
2. Click **Start**
3. Verify status

### ✅ Verify Deployment

Visit:
- Homepage: `https://mc.example.com`
- Admin: `https://mc.example.com/admin`

### 🔧 Troubleshooting

See Chinese section above for detailed troubleshooting steps.

---

## 快速配置检查清单 | Quick Config Checklist

- [ ] Python 3.10+ installed
- [ ] Project cloned to `/www/wwwroot/mc_rcon`
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] `.env` file configured with domain
- [ ] `ALLOWED_HOSTS` includes your domain
- [ ] `CSRF_TRUSTED_ORIGINS` includes `https://yourdomain.com`
- [ ] Database migrated
- [ ] Superuser created
- [ ] Static files collected
- [ ] Python project created in BaoTa
- [ ] Reverse proxy configured
- [ ] SSL certificate installed
- [ ] Project started and running

---

**开发者**: MoYuK1ng  
**项目地址**: https://github.com/MoYuK1ng/MC_rcon_manage
