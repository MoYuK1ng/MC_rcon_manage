# IronGate 服务器启动器使用指南

## 📋 概述

IronGate 提供了灵活的服务器启动方式，支持自定义端口、随机端口等功能。

## 🚀 快速开始

### 方式 1：使用 Python 脚本（推荐）

```bash
# 默认端口 8000（如果被占用会自动使用下一个可用端口）
python run_server.py

# 指定端口
python run_server.py -p 8080

# 使用随机端口（8000-9000 之间）
python run_server.py --random

# 监听所有网络接口（允许局域网访问）
python run_server.py --host 0.0.0.0

# 禁用自动重载（调试时有用）
python run_server.py --noreload

# 组合使用
python run_server.py -p 8080 --host 0.0.0.0
```

### 方式 2：使用快捷脚本

**Windows:**
```cmd
# 默认端口
run.bat

# 指定端口
run.bat 8080

# 随机端口
run.bat random
```

**Linux/Mac:**
```bash
# 给脚本添加执行权限（首次使用）
chmod +x run.sh

# 默认端口
./run.sh

# 指定端口
./run.sh 8080

# 随机端口
./run.sh random
```

### 方式 3：传统 Django 命令

```bash
# 默认端口 8000
python manage.py runserver

# 指定端口
python manage.py runserver 8080

# 指定主机和端口
python manage.py runserver 0.0.0.0:8080
```

## 📖 详细说明

### 端口选择逻辑

1. **默认模式** (`python run_server.py`)
   - 尝试使用端口 8000
   - 如果 8000 被占用，自动查找下一个可用端口
   - 显示实际使用的端口

2. **指定端口** (`python run_server.py -p 8080`)
   - 尝试使用指定的端口
   - 如果被占用，自动查找下一个可用端口
   - 提示用户端口变更

3. **随机端口** (`python run_server.py --random`)
   - 在 8000-9000 范围内随机选择可用端口
   - 适合同时运行多个实例

### 主机绑定选项

| 选项 | 说明 | 访问方式 |
|------|------|----------|
| `127.0.0.1` (默认) | 只能本机访问 | `http://localhost:端口` |
| `0.0.0.0` | 允许局域网访问 | `http://你的IP:端口` |

**示例：**
```bash
# 只能本机访问
python run_server.py -p 8080 --host 127.0.0.1

# 允许局域网其他设备访问
python run_server.py -p 8080 --host 0.0.0.0
```

### 自动重载

Django 开发服务器默认会监控代码变化并自动重载。

```bash
# 启用自动重载（默认）
python run_server.py

# 禁用自动重载（调试时有用）
python run_server.py --noreload
```

## 🎯 使用场景

### 场景 1：本地开发

```bash
# 最简单的方式
python run_server.py
```

访问：`http://localhost:8000`

### 场景 2：同时运行多个项目

```bash
# 项目 A
cd project_a
python run_server.py -p 8000

# 项目 B（另一个终端）
cd project_b
python run_server.py -p 8001

# 或者使用随机端口
python run_server.py --random
```

### 场景 3：局域网测试

```bash
# 允许手机或其他设备访问
python run_server.py --host 0.0.0.0 -p 8000
```

然后在其他设备上访问：`http://你的电脑IP:8000`

查看你的 IP：
- **Windows**: `ipconfig`
- **Linux/Mac**: `ifconfig` 或 `ip addr`

### 场景 4：端口被占用

```bash
# 自动处理端口冲突
python run_server.py

# 输出示例：
# ⚠ Port 8000 is in use. Using port: 8001
# ✓ Server running on http://127.0.0.1:8001
```

## 🔧 高级用法

### 查看所有选项

```bash
python run_server.py --help
```

### 使用不同的设置文件

```bash
python run_server.py --settings irongate.settings_production
```

### 组合多个选项

```bash
# 随机端口 + 允许局域网访问 + 禁用重载
python run_server.py --random --host 0.0.0.0 --noreload
```

## 📊 输出示例

```
🎲 Using random port: 8347

============================================================
🎮 IronGate RCON Portal - Development Server
============================================================
Host:     127.0.0.1
Port:     8347
URL:      http://localhost:8347/
Admin:    http://localhost:8347/admin/
Reload:   Enabled
============================================================

Press Ctrl+C to stop the server

Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
November 28, 2024 - 15:30:00
Django version 5.0.14, using settings 'irongate.settings'
Starting development server at http://127.0.0.1:8347/
Quit the server with CTRL-BREAK.
```

## 🐛 故障排除

### 问题 1：端口被占用

**错误信息：**
```
Error: That port is already in use.
```

**解决方案：**
```bash
# 使用启动器会自动处理
python run_server.py

# 或手动指定其他端口
python run_server.py -p 8001
```

### 问题 2：找不到 Django

**错误信息：**
```
ModuleNotFoundError: No module named 'django'
```

**解决方案：**
```bash
# 确认虚拟环境已激活
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 问题 3：权限错误（Linux/Mac）

**错误信息：**
```
Permission denied: './run.sh'
```

**解决方案：**
```bash
# 添加执行权限
chmod +x run.sh

# 然后运行
./run.sh
```

### 问题 4：局域网无法访问

**检查清单：**

1. 确认使用了 `--host 0.0.0.0`
2. 检查防火墙设置
3. 确认设备在同一局域网
4. 更新 Django 设置：

```python
# irongate/settings.py
ALLOWED_HOSTS = ['*']  # 开发环境可以使用，生产环境要指定具体域名
```

## 🔒 安全提示

### 开发环境

- ✅ 使用 `127.0.0.1`（默认）
- ✅ `DEBUG = True`
- ✅ 使用开发服务器

### 生产环境

- ❌ 不要使用 `python manage.py runserver`
- ❌ 不要使用 `--host 0.0.0.0` 直接暴露
- ✅ 使用 Gunicorn/uWSGI
- ✅ 使用 Nginx 反向代理
- ✅ 设置 `DEBUG = False`
- ✅ 配置正确的 `ALLOWED_HOSTS`

## 📚 相关文档

- [Django runserver 文档](https://docs.djangoproject.com/en/5.0/ref/django-admin/#runserver)
- [部署指南](DEPLOYMENT.md)
- [Nginx 配置](NGINX_SETUP.md)

## 💡 提示

1. **开发时推荐使用启动器**：自动处理端口冲突，显示清晰的服务器信息
2. **多项目开发**：使用随机端口避免冲突
3. **移动端测试**：使用 `--host 0.0.0.0` 允许局域网访问
4. **调试问题**：使用 `--noreload` 禁用自动重载

## 🎓 快速参考

```bash
# 常用命令速查
python run_server.py              # 默认启动
python run_server.py -p 8080      # 指定端口
python run_server.py --random     # 随机端口
python run_server.py --host 0.0.0.0  # 局域网访问
python run_server.py --help       # 查看帮助

# Windows 快捷方式
run.bat                           # 默认启动
run.bat 8080                      # 指定端口
run.bat random                    # 随机端口

# Linux/Mac 快捷方式
./run.sh                          # 默认启动
./run.sh 8080                     # 指定端口
./run.sh random                   # 随机端口
```
