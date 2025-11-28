# Nginx 反向代理配置指南

## 问题说明

当使用 Nginx 反向代理访问 Django 应用时，可能会遇到 CSRF 验证失败的错误：

```
禁止访问 (403)
CSRF验证失败. 请求被中断.
Origin checking failed - https://yourdomain.com does not match any trusted origins.
```

## 解决方案

### 1. 配置 Django 设置

在 `.env` 文件中添加以下配置：

```bash
# 允许的主机名（逗号分隔，不要有空格）
ALLOWED_HOSTS=localhost,127.0.0.1,mc.moyuu.online

# CSRF 信任的源（逗号分隔，必须包含协议）
CSRF_TRUSTED_ORIGINS=https://mc.moyuu.online,http://localhost:8000
```

**重要提示**：
- `ALLOWED_HOSTS`：只需要域名，不需要协议
- `CSRF_TRUSTED_ORIGINS`：必须包含完整的协议（`https://` 或 `http://`）

### 2. Nginx 配置示例

```nginx
server {
    listen 80;
    server_name mc.moyuu.online;
    
    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name mc.moyuu.online;
    
    # SSL 证书配置
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    
    # SSL 安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # 日志
    access_log /var/log/nginx/irongate_access.log;
    error_log /var/log/nginx/irongate_error.log;
    
    # 静态文件
    location /static/ {
        alias /path/to/your/project/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # 代理到 Django 应用
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### 3. 重启服务

```bash
# 重新加载 Django 应用（如果使用 Gunicorn）
sudo systemctl restart gunicorn

# 重新加载 Nginx
sudo nginx -t  # 测试配置
sudo systemctl reload nginx
```

## 常见问题

### Q1: 为什么需要 CSRF_TRUSTED_ORIGINS？

**A**: Django 的 CSRF 保护会检查请求的 `Origin` 或 `Referer` 头。当使用 HTTPS 时，Django 会验证这些头是否来自可信的源。

### Q2: 可以使用通配符吗？

**A**: 可以，但不推荐。例如：
```python
CSRF_TRUSTED_ORIGINS = ['https://*.moyuu.online']
```

### Q3: 开发环境需要配置吗？

**A**: 如果只在本地访问（`localhost` 或 `127.0.0.1`），通常不需要。但如果使用自定义域名（如 `dev.local`），则需要添加。

### Q4: 配置后还是 403 错误？

检查以下几点：

1. **确认 .env 文件已加载**
   ```bash
   python manage.py shell
   >>> from django.conf import settings
   >>> print(settings.ALLOWED_HOSTS)
   >>> print(settings.CSRF_TRUSTED_ORIGINS)
   ```

2. **确认没有多余的空格**
   ```bash
   # 错误 ❌
   ALLOWED_HOSTS=localhost, 127.0.0.1, mc.moyuu.online
   
   # 正确 ✅
   ALLOWED_HOSTS=localhost,127.0.0.1,mc.moyuu.online
   ```

3. **确认协议正确**
   ```bash
   # 错误 ❌
   CSRF_TRUSTED_ORIGINS=mc.moyuu.online
   
   # 正确 ✅
   CSRF_TRUSTED_ORIGINS=https://mc.moyuu.online
   ```

4. **重启应用**
   ```bash
   # 开发服务器
   # Ctrl+C 停止，然后重新运行
   python manage.py runserver
   
   # 生产环境（Gunicorn）
   sudo systemctl restart gunicorn
   ```

## 安全建议

### 生产环境配置

在生产环境中，建议：

1. **关闭 DEBUG 模式**
   ```bash
   DEBUG=False
   ```

2. **使用强密钥**
   ```bash
   SECRET_KEY=your-very-long-random-secret-key
   ```

3. **只允许必要的主机**
   ```bash
   # 不要使用 * 通配符
   ALLOWED_HOSTS=mc.moyuu.online,www.mc.moyuu.online
   ```

4. **使用 HTTPS**
   ```bash
   # 只信任 HTTPS 源
   CSRF_TRUSTED_ORIGINS=https://mc.moyuu.online
   ```

5. **添加安全头**
   在 Nginx 配置中添加：
   ```nginx
   add_header X-Frame-Options "SAMEORIGIN" always;
   add_header X-Content-Type-Options "nosniff" always;
   add_header X-XSS-Protection "1; mode=block" always;
   ```

## 测试配置

```bash
# 1. 测试 Django 配置
python manage.py check --deploy

# 2. 测试 Nginx 配置
sudo nginx -t

# 3. 查看 Django 日志
tail -f /path/to/your/logs/django.log

# 4. 查看 Nginx 日志
tail -f /var/log/nginx/irongate_error.log
```

## 参考资料

- [Django CSRF Protection](https://docs.djangoproject.com/en/5.0/ref/csrf/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)
- [Nginx Reverse Proxy](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)
