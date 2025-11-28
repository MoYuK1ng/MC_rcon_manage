# Production Deployment Checklist | 生产环境部署清单

Use this checklist before deploying IronGate to your VPS.

在将 IronGate 部署到 VPS 之前使用此清单。

---

## Pre-Deployment | 部署前

### Environment Setup | 环境设置

- [ ] VPS with Ubuntu 20.04+ ready | VPS 准备就绪（Ubuntu 20.04+）
- [ ] Domain name configured with DNS | 域名已配置 DNS
- [ ] SSH access to VPS | 可通过 SSH 访问 VPS
- [ ] Non-root user created | 已创建非 root 用户

### Software Installation | 软件安装

- [ ] Python 3.10+ installed | 已安装 Python 3.10+
- [ ] PostgreSQL installed | 已安装 PostgreSQL
- [ ] Nginx installed | 已安装 Nginx
- [ ] Gettext tools installed | 已安装 Gettext 工具
- [ ] Certbot installed (for SSL) | 已安装 Certbot（用于 SSL）

---

## Configuration | 配置

### Database | 数据库

- [ ] PostgreSQL database created | 已创建 PostgreSQL 数据库
- [ ] Database user created with strong password | 已创建数据库用户（强密码）
- [ ] Database permissions granted | 已授予数据库权限

### Application | 应用程序

- [ ] Repository cloned | 已克隆仓库
- [ ] Virtual environment created | 已创建虚拟环境
- [ ] Dependencies installed | 已安装依赖
- [ ] `.env` file configured | 已配置 `.env` 文件
- [ ] Strong `SECRET_KEY` generated (50+ chars) | 已生成强 `SECRET_KEY`（50+ 字符）
- [ ] `RCON_ENCRYPTION_KEY` generated | 已生成 `RCON_ENCRYPTION_KEY`
- [ ] `ALLOWED_HOSTS` set to your domain | `ALLOWED_HOSTS` 已设置为您的域名
- [ ] `DEBUG=False` in production | 生产环境中 `DEBUG=False`

### Translations | 翻译

- [ ] Translation files compiled: `python manage.py compilemessages` | 已编译翻译文件
- [ ] `.mo` files exist in `locale/zh_hans/LC_MESSAGES/` | `.mo` 文件存在

### Database Migration | 数据库迁移

- [ ] Migrations run: `python manage.py migrate` | 已运行迁移
- [ ] Superuser created | 已创建超级用户
- [ ] Static files collected | 已收集静态文件

---

## Security | 安全

### Django Security | Django 安全

- [ ] `DEBUG = False` | 已设置 `DEBUG = False`
- [ ] Strong `SECRET_KEY` (not default) | 强 `SECRET_KEY`（非默认值）
- [ ] `ALLOWED_HOSTS` configured | 已配置 `ALLOWED_HOSTS`
- [ ] `SECURE_SSL_REDIRECT = True` | 已启用 SSL 重定向
- [ ] `SESSION_COOKIE_SECURE = True` | 已启用安全会话 cookie
- [ ] `CSRF_COOKIE_SECURE = True` | 已启用安全 CSRF cookie
- [ ] HSTS headers enabled | 已启用 HSTS 头

### File Permissions | 文件权限

- [ ] `.env` file: `chmod 600` | `.env` 文件权限：`chmod 600`
- [ ] Application owned by `irongate` user | 应用程序归 `irongate` 用户所有
- [ ] No world-writable files | 无全局可写文件

### Firewall | 防火墙

- [ ] UFW enabled | 已启用 UFW
- [ ] Only ports 80, 443, 22 open | 仅开放端口 80、443、22
- [ ] fail2ban configured (optional) | 已配置 fail2ban（可选）

### SSL Certificate | SSL 证书

- [ ] SSL certificate installed | 已安装 SSL 证书
- [ ] HTTPS working | HTTPS 正常工作
- [ ] HTTP redirects to HTTPS | HTTP 重定向到 HTTPS
- [ ] Certificate auto-renewal configured | 已配置证书自动续期

---

## Services | 服务

### Gunicorn | Gunicorn

- [ ] Systemd service file created | 已创建 systemd 服务文件
- [ ] Service enabled: `sudo systemctl enable irongate` | 已启用服务
- [ ] Service running: `sudo systemctl status irongate` | 服务正在运行
- [ ] No errors in service logs | 服务日志无错误

### Nginx | Nginx

- [ ] Site configuration created | 已创建站点配置
- [ ] Configuration syntax valid: `sudo nginx -t` | 配置语法有效
- [ ] Site enabled | 站点已启用
- [ ] Nginx restarted | 已重启 Nginx
- [ ] Static files serving correctly | 静态文件正确提供

---

## Testing | 测试

### Functionality Tests | 功能测试

- [ ] Can access website via domain | 可通过域名访问网站
- [ ] HTTPS working (no certificate errors) | HTTPS 正常工作（无证书错误）
- [ ] Can log in to admin panel | 可登录管理面板
- [ ] Can create groups and users | 可创建组和用户
- [ ] Can add servers | 可添加服务器
- [ ] Dashboard loads correctly | 仪表板正确加载
- [ ] Player list updates (test with real server) | 玩家列表更新（使用真实服务器测试）
- [ ] Whitelist command works | 白名单命令有效
- [ ] Language switcher works | 语言切换器有效
- [ ] Chinese translations display | 中文翻译显示

### Security Tests | 安全测试

- [ ] Unauthenticated users redirected to login | 未认证用户重定向到登录
- [ ] Users can only access their group's servers | 用户只能访问其组的服务器
- [ ] Invalid usernames rejected | 无效用户名被拒绝
- [ ] RCON passwords encrypted in database | RCON 密码在数据库中加密
- [ ] No sensitive data in logs | 日志中无敏感数据

### Performance Tests | 性能测试

- [ ] Page load time < 2 seconds | 页面加载时间 < 2 秒
- [ ] HTMX polling works smoothly | HTMX 轮询流畅工作
- [ ] Multiple concurrent users supported | 支持多个并发用户

---

## Post-Deployment | 部署后

### Monitoring | 监控

- [ ] Set up log monitoring | 设置日志监控
- [ ] Configure error alerts | 配置错误警报
- [ ] Set up uptime monitoring | 设置正常运行时间监控
- [ ] Monitor disk space | 监控磁盘空间

### Backup | 备份

- [ ] Database backup configured | 已配置数据库备份
- [ ] Backup schedule automated | 备份计划自动化
- [ ] Backup restoration tested | 已测试备份恢复
- [ ] `.env` file backed up securely | `.env` 文件已安全备份

### Maintenance | 维护

- [ ] Update schedule planned | 已计划更新时间表
- [ ] Security advisory monitoring | 安全公告监控
- [ ] Log rotation configured | 已配置日志轮换

---

## Final Verification | 最终验证

Run these commands to verify everything:

运行这些命令以验证一切：

```bash
# Security check
python manage.py check --deploy

# Test suite
pytest servers/tests/

# Check services
sudo systemctl status irongate
sudo systemctl status nginx
sudo systemctl status postgresql

# Check logs
sudo journalctl -u irongate -n 50
sudo tail -f /var/log/nginx/error.log
```

---

## Emergency Contacts | 紧急联系方式

- **System Admin**: [Your contact] | 系统管理员：[您的联系方式]
- **Database Admin**: [Your contact] | 数据库管理员：[您的联系方式]
- **GitHub Issues**: https://github.com/MoYuK1ng/MC_rcon_manage/issues

---

## Rollback Plan | 回滚计划

If something goes wrong:

如果出现问题：

```bash
# Stop services
sudo systemctl stop irongate
sudo systemctl stop nginx

# Restore database backup
sudo -u postgres psql irongate < backup.sql

# Revert code
git checkout <previous-commit>

# Restart services
sudo systemctl start irongate
sudo systemctl start nginx
```

---

<div align="center">

✅ **Checklist Complete?** You're ready to deploy!

✅ **清单完成？** 您已准备好部署！

</div>
