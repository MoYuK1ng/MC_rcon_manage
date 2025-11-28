# 常见问题 / FAQ

## 🤔 为什么删除了程序目录，应用还能访问？

### 现象
删除 `/opt/mc_rcon` 目录后，访问 `https://yourdomain.com` 仍然可以正常使用。

### 原因

#### 1. **进程已加载到内存**
```
磁盘文件 → 启动时加载 → 内存中运行
   ↓           ↓              ↓
删除文件    不影响        进程继续运行
```

当 gunicorn 启动时：
- Python 解释器和所有代码被加载到 **RAM（内存）**
- 进程不再依赖磁盘上的源文件
- 即使删除源文件，内存中的进程仍然运行

#### 2. **文件描述符机制**
Linux 的文件系统特性：
- 进程打开文件时获得**文件描述符**
- 删除文件只是删除**目录项**（文件名）
- 文件描述符仍然有效，进程可以继续访问
- 只有当所有文件描述符关闭后，文件才真正被删除

```bash
# 查看已删除但仍被占用的文件
lsof | grep deleted
```

#### 3. **缓存机制**
- **Nginx 缓存**：静态文件可能被 Nginx 缓存
- **浏览器缓存**：CSS/JS 等资源被浏览器缓存
- **操作系统缓存**：文件系统的页面缓存

### 验证方法

在 VPS 上运行以下命令：

```bash
# 1. 查看 gunicorn 进程
ps aux | grep gunicorn

# 2. 查看进程打开的文件
lsof -p $(pgrep -f gunicorn | head -1)

# 3. 查看进程的工作目录（会显示 (deleted)）
ls -la /proc/$(pgrep -f gunicorn | head -1)/cwd

# 4. 查看进程的可执行文件路径
readlink /proc/$(pgrep -f gunicorn | head -1)/exe

# 5. 查看进程的内存映射
cat /proc/$(pgrep -f gunicorn | head -1)/maps | grep python
```

### 潜在问题

虽然应用还能访问，但存在严重问题：

| 问题 | 说明 |
|------|------|
| ❌ **无法重启** | `systemctl restart mc-rcon` 会失败 |
| ❌ **无法更新** | 代码文件已不存在 |
| ❌ **数据风险** | 进程崩溃可能导致数据丢失 |
| ❌ **无法调试** | 无法查看日志或源代码 |
| ❌ **无法回滚** | 出问题时无法恢复 |

### 正确的操作顺序

#### ✅ 卸载应用
```bash
cd /opt/mc_rcon
bash manage.sh
# 选择选项 10 (完全卸载)
```

脚本会按正确顺序执行：
1. 停止服务 (`systemctl stop`)
2. 等待进程终止
3. 强制杀死残留进程
4. 删除 systemd 服务文件
5. 备份数据库（可选）
6. 删除项目目录

#### ✅ 手动清理（如果已经删除了目录）
```bash
# 1. 停止服务
systemctl stop mc-rcon
systemctl disable mc-rcon

# 2. 强制终止所有相关进程
pkill -9 -f "gunicorn.*irongate"

# 3. 删除服务文件
rm -f /etc/systemd/system/mc-rcon.service
systemctl daemon-reload

# 4. 验证进程已终止
ps aux | grep gunicorn
```

---

## 🔧 其他常见问题

### Q: 为什么出现 CSRF 403 错误？

**A:** 检查以下几点：

1. **`.env` 文件格式**
   ```bash
   cat /opt/mc_rcon/.env
   ```
   确保有正确的换行符，不是所有内容挤在一行

2. **CSRF_TRUSTED_ORIGINS 配置**
   ```ini
   CSRF_TRUSTED_ORIGINS=https://yourdomain.com,http://localhost:47777,http://127.0.0.1:47777
   ```
   必须包含你访问的完整 URL（包括协议）

3. **Nginx 反向代理配置**
   ```nginx
   location / {
       proxy_pass http://127.0.0.1:47777;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       proxy_set_header X-Forwarded-Proto $scheme;  # 重要！
   }
   ```

4. **重启服务**
   ```bash
   systemctl restart mc-rcon
   ```

### Q: 如何查看当前脚本版本？

**A:** 
```bash
cd /opt/mc_rcon
bash manage.sh
# 主菜单会显示版本号
```

或者：
```bash
grep "SCRIPT_VERSION=" /opt/mc_rcon/manage.sh | head -1
```

### Q: 如何更新到最新版本？

**A:** 使用脚本自更新功能：
```bash
cd /opt/mc_rcon
bash manage.sh
# 选择选项 11 (更新管理脚本)
```

### Q: 更新应用会影响数据吗？

**A:** 不会。更新应用（选项 2）会：
- ✅ 自动备份数据库
- ✅ 保留 `.env` 配置
- ✅ 保留用户数据
- ✅ 只更新代码和依赖

### Q: 如何备份数据？

**A:** 
```bash
cd /opt/mc_rcon
bash manage.sh
# 选择选项 8 (备份数据)
```

备份文件保存在 `/opt/mc_rcon/backups/` 目录。

### Q: 服务启动失败怎么办？

**A:** 查看日志：
```bash
# 查看服务状态
systemctl status mc-rcon

# 查看详细日志
journalctl -u mc-rcon -n 50

# 查看实时日志
journalctl -u mc-rcon -f
```

常见问题：
- gunicorn 未安装：`/opt/mc_rcon/venv/bin/pip install gunicorn`
- 端口被占用：`lsof -i :47777`
- 权限问题：确保使用 root 运行

---

## 📚 相关资源

- [GitHub 仓库](https://github.com/MoYuK1ng/MC_rcon_manage)
- [更新日志](CHANGELOG.md)
- [README](README.md)

---

## 💡 技术原理

### Linux 进程生命周期

```
1. 启动阶段
   fork() → exec() → 加载代码到内存

2. 运行阶段
   进程在内存中运行，不依赖磁盘文件

3. 终止阶段
   进程退出 → 释放内存 → 关闭文件描述符
```

### 文件删除机制

```
文件系统结构：
inode (文件数据) ← 硬链接计数
  ↑
目录项 (文件名)

删除文件：
1. 删除目录项（文件名消失）
2. 硬链接计数 -1
3. 如果计数 = 0 且无进程打开 → 真正删除
4. 如果有进程打开 → 标记为 deleted，但数据仍在
```

这就是为什么删除文件后进程还能运行的原因！
