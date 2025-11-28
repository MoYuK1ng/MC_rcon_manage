#!/bin/bash
# 紧急修复脚本 - 更新到最新版本

echo "=========================================="
echo "紧急修复 - 更新管理脚本"
echo "=========================================="
echo ""

# 检查是否在项目目录
if [ ! -f "manage.py" ]; then
    echo "[ERROR] 请在项目目录运行"
    echo "使用: cd /opt/mc_rcon && bash emergency_fix.sh"
    exit 1
fi

echo "1. 备份当前脚本..."
if [ -f "manage.sh" ]; then
    cp manage.sh manage.sh.backup.$(date +%Y%m%d_%H%M%S)
    echo "[OK] 已备份"
else
    echo "[WARN] manage.sh 不存在"
fi
echo ""

echo "2. 下载最新版本..."
wget -q https://raw.githubusercontent.com/MoYuK1ng/MC_rcon_manage/main/manage.sh -O manage.sh.new

if [ ! -f "manage.sh.new" ]; then
    echo "[ERROR] 下载失败"
    exit 1
fi

chmod +x manage.sh.new
mv manage.sh.new manage.sh
echo "[OK] 脚本已更新"
echo ""

echo "3. 检查 Nginx 状态..."
if systemctl is-active --quiet nginx; then
    echo "[INFO] Nginx 正在运行"
    echo "[INFO] 注意: 新版本不再管理 Nginx"
    echo "[INFO] 如果不需要 Nginx，可以停止它: systemctl stop nginx"
else
    echo "[OK] Nginx 未运行"
fi
echo ""

echo "4. 检查应用服务..."
if systemctl is-active --quiet mc-rcon; then
    echo "[OK] mc-rcon 服务正在运行"
else
    echo "[WARN] mc-rcon 服务未运行"
    read -p "是否启动服务? (y/n): " start_service
    if [ "$start_service" = "y" ]; then
        systemctl start mc-rcon
        echo "[OK] 服务已启动"
    fi
fi
echo ""

echo "=========================================="
echo "修复完成！"
echo "=========================================="
echo ""
echo "现在可以使用: bash manage.sh"
echo ""
