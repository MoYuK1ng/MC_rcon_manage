# 🚀 快速开始指南 / Quick Start Guide

## 中文版

### 1️⃣ 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt
```

### 2️⃣ 初始化数据库

```bash
# 运行数据库迁移
python manage.py migrate

# 创建管理员账号
python manage.py createsuperuser
```

### 3️⃣ 启动服务器

**方式1：使用启动脚本（推荐）**
```bash
# Windows
start_server.bat

# Linux/Mac
./manage.sh runserver
```

**方式2：手动启动**
```bash
python manage.py runserver
```

### 4️⃣ 访问应用

打开浏览器访问：
- **前端首页**: http://localhost:8000/
- **注册页面**: http://localhost:8000/register/
- **登录页面**: http://localhost:8000/accounts/login/
- **Admin后台**: http://localhost:8000/admin/

### 5️⃣ 配置服务器

1. 使用管理员账号登录Admin后台
2. 创建用户组（例如："VIP玩家"）
3. 添加Minecraft服务器：
   - 名称：服务器名称
   - IP地址：服务器IP
   - RCON端口：默认25575
   - RCON密码：服务器RCON密码
   - 访问组：选择用户组
4. 创建普通用户并分配到组

### 6️⃣ 测试功能

1. **注册新用户**
   - 访问注册页面
   - 填写表单（包括验证码）
   - 注册成功后自动登录

2. **添加白名单**
   - 登录后访问仪表板
   - 找到可访问的服务器
   - 输入MC用户名并提交

3. **查看申请历史**
   - 点击用户菜单
   - 选择"我的白名单"
   - 查看所有申请记录

---

## English Version

### 1️⃣ Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt
```

### 2️⃣ Initialize Database

```bash
# Run database migrations
python manage.py migrate

# Create superuser account
python manage.py createsuperuser
```

### 3️⃣ Start Server

**Method 1: Using startup script (Recommended)**
```bash
# Windows
start_server.bat

# Linux/Mac
./manage.sh runserver
```

**Method 2: Manual start**
```bash
python manage.py runserver
```

### 4️⃣ Access Application

Open browser and visit:
- **Frontend**: http://localhost:8000/
- **Register**: http://localhost:8000/register/
- **Login**: http://localhost:8000/accounts/login/
- **Admin**: http://localhost:8000/admin/

### 5️⃣ Configure Servers

1. Login to Admin panel with superuser account
2. Create user groups (e.g., "VIP Players")
3. Add Minecraft servers:
   - Name: Server name
   - IP Address: Server IP
   - RCON Port: Default 25575
   - RCON Password: Server RCON password
   - Access Groups: Select user groups
4. Create regular users and assign to groups

### 6️⃣ Test Features

1. **Register New User**
   - Visit registration page
   - Fill form (including captcha)
   - Auto-login after successful registration

2. **Add to Whitelist**
   - Login and visit dashboard
   - Find accessible servers
   - Enter MC username and submit

3. **View Application History**
   - Click user menu
   - Select "My Whitelist"
   - View all application records

---

## 🔧 常见问题 / Common Issues

### 问题1：验证码不显示
**解决方案**：
```bash
pip install Pillow
python manage.py migrate
```

### 问题2：静态文件404
**解决方案**：
```bash
python manage.py collectstatic --noinput
```

### 问题3：RCON连接失败
**检查清单**：
- ✅ 服务器IP和端口正确
- ✅ RCON密码正确
- ✅ 服务器已启用RCON
- ✅ 防火墙允许RCON端口

### Issue 1: Captcha not showing
**Solution**:
```bash
pip install Pillow
python manage.py migrate
```

### Issue 2: Static files 404
**Solution**:
```bash
python manage.py collectstatic --noinput
```

### Issue 3: RCON connection failed
**Checklist**:
- ✅ Server IP and port are correct
- ✅ RCON password is correct
- ✅ RCON is enabled on server
- ✅ Firewall allows RCON port

---

## 📚 更多文档 / More Documentation

- **完整文档**: [README.md](README.md)
- **测试指南**: [TESTING_GUIDE.md](TESTING_GUIDE.md)
- **实施状态**: [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md)
- **加密说明**: [ENCRYPTION.md](ENCRYPTION.md)
- **常见问题**: [FAQ.md](FAQ.md)

---

## 🎯 下一步 / Next Steps

1. ✅ 创建管理员账号
2. ✅ 配置第一个服务器
3. ✅ 创建用户组
4. ✅ 测试白名单功能
5. ✅ 自定义Admin主题（可选）
6. ✅ 配置邮件通知（可选）

---

## 💡 提示 / Tips

### 开发环境
- 使用 `DEBUG=True` 进行开发
- 查看详细错误信息
- 自动重载代码更改

### 生产环境
- 设置 `DEBUG=False`
- 配置 `ALLOWED_HOSTS`
- 使用 `gunicorn` 或 `uwsgi`
- 配置 Nginx 反向代理
- 启用 HTTPS

### 安全建议
- 定期更新依赖
- 使用强密码
- 定期备份数据库
- 监控日志文件
- 限制Admin访问IP

---

## 📞 获取帮助 / Get Help

- **GitHub Issues**: 报告Bug和功能请求
- **文档**: 查看完整文档
- **社区**: 加入讨论

---

**🎉 祝您使用愉快！/ Enjoy using MC RCON Manager!**
