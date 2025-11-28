#!/bin/bash
# IronGate RCON Portal - 一键管理脚本
# IronGate RCON Portal - All-in-One Management Script
# 
# 功能 / Features:
#   - 自动安装 / Auto Installation
#   - 更新部署 / Update Deployment  
#   - 服务管理 / Service Management
#   - 状态监控 / Status Monitoring
#   - 日志查看 / Log Viewing

set -e  # 遇到错误立即退出 / Exit on error

# ============================================================
# 配置 / Configuration
# ============================================================

SCRIPT_VERSION="2.0.0"
PROJECT_NAME="irongate"
DEFAULT_INSTALL_DIR="/opt/irongate"
REPO_URL="https://github.com/MoYuK1ng/MC_rcon_manage.git"
PYTHON_MIN_VERSION="3.10"

# 颜色定义 / Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ============================================================
# 工具函数 / Utility Functions
# ============================================================

print_banner() {
    clear
    echo -e "${CYAN}"
    echo "============================================================"
    echo "   ___                  ____       _       "
    echo "  |_ _|_ __ ___  _ __  / ___| __ _| |_ ___ "
    echo "   | || '__/ _ \| '_ \| |  _ / _\` | __/ _ \\"
    echo "   | || | | (_) | | | | |_| | (_| | ||  __/"
    echo "  |___|_|  \___/|_| |_|\____|\__,_|\__\___|"
    echo ""
    echo "  Minecraft RCON Web Portal - 管理脚本 v${SCRIPT_VERSION}"
    echo "  Minecraft RCON Web Portal - Management Script v${SCRIPT_VERSION}"
    echo "============================================================"
    echo -e "${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

check_root() {
    if [ "$EUID" -ne 0 ]; then 
        print_error "请使用 root 权限运行此脚本"
        print_error "Please run this script as root"
        print_info "使用: sudo bash $0"
        exit 1
    fi
}

press_any_key() {
    echo ""
    read -n 1 -s -r -p "按任意键继续... / Press any key to continue..."
    echo ""
}

# ============================================================
# 主菜单 / Main Menu
# ============================================================

show_menu() {
    print_banner
    echo -e "${CYAN}请选择操作 / Please select an option:${NC}"
    echo ""
    echo "  ${GREEN}安装 / Installation${NC}"
    echo "  1) 全新安装 / Fresh Install"
    echo ""
    echo "  ${BLUE}管理 / Management${NC}"
    echo "  2) 更新代码 / Update Code"
    echo "  3) 启动服务 / Start Service"
    echo "  4) 停止服务 / Stop Service"
    echo "  5) 重启服务 / Restart Service"
    echo "  6) 查看状态 / View Status"
    echo "  7) 查看日志 / View Logs"
    echo ""
    echo "  ${YELLOW}维护 / Maintenance${NC}"
    echo "  8) 备份数据 / Backup Data"
    echo "  9) 恢复数据 / Restore Data"
    echo ""
    echo "  ${RED}其他 / Others${NC}"
    echo "  0) 退出 / Exit"
    echo ""
    echo -n "请输入选项 / Enter option [0-9]: "
}

# ============================================================
# 1. 全新安装 / Fresh Install
# ============================================================

install_fresh() {
    print_banner
    echo -e "${GREEN}=== 全新安装 / Fresh Installation ===${NC}"
    echo ""
    
    # 询问安装路径
    read -p "安装路径 / Install path [${DEFAULT_INSTALL_DIR}]: " INSTALL_DIR
    INSTALL_DIR=${INSTALL_DIR:-$DEFAULT_INSTALL_DIR}
    
    # 询问域名
    read -p "域名 / Domain (例如: mc.moyuu.online): " DOMAIN
    if [ -z "$DOMAIN" ]; then
        print_error "域名不能为空 / Domain cannot be empty"
        press_any_key
        return
    fi
    
    print_info "开始安装到: $INSTALL_DIR"
    print_info "Starting installation to: $INSTALL_DIR"
    
    # 1. 检查并安装依赖
    print_info "步骤 1/10: 检查系统依赖..."
    if ! command_exists python3; then
        print_info "安装 Python3..."
        apt update
        apt install -y python3 python3-pip python3-venv
    fi
    
    if ! command_exists git; then
        print_info "安装 Git..."
        apt install -y git
    fi
    
    if ! command_exists nginx; then
        print_info "安装 Nginx..."
        apt install -y nginx
    fi
    
    apt install -y gettext  # 用于翻译
    print_success "系统依赖检查完成"
    
    # 2. 克隆代码
    print_info "步骤 2/10: 克隆代码仓库..."
    if [ -d "$INSTALL_DIR" ]; then
        print_warning "目录已存在，将删除并重新克隆"
        rm -rf "$INSTALL_DIR"
    fi
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    print_success "代码克隆完成"
    
    # 3. 创建虚拟环境
    print_info "步骤 3/10: 创建 Python 虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    print_success "虚拟环境创建完成"
    
    # 4. 安装 Python 依赖
    print_info "步骤 4/10: 安装 Python 依赖..."
    pip install --upgrade pip
    pip install -r requirements.txt
    print_success "Python 依赖安装完成"
    
    # 5. 生成加密密钥
    print_info "步骤 5/10: 生成加密密钥..."
    python generate_key.py
    print_success "加密密钥生成完成"
    
    # 6. 配置 .env 文件
    print_info "步骤 6/10: 配置环境变量..."
    # 生成随机 SECRET_KEY
    SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
    
    # 更新 .env 文件
    sed -i "s/^DEBUG=.*/DEBUG=False/" .env
    sed -i "s/^SECRET_KEY=.*/SECRET_KEY=${SECRET_KEY}/" .env
    echo "ALLOWED_HOSTS=localhost,127.0.0.1,${DOMAIN}" >> .env
    echo "CSRF_TRUSTED_ORIGINS=https://${DOMAIN},http://localhost:8000" >> .env
    print_success "环境变量配置完成"
    
    # 7. 初始化数据库
    print_info "步骤 7/10: 初始化数据库..."
    python manage.py migrate
    print_success "数据库初始化完成"
    
    # 8. 创建超级用户
    print_info "步骤 8/10: 创建管理员账户..."
    echo ""
    python manage.py createsuperuser
    print_success "管理员账户创建完成"
    
    # 9. 收集静态文件
    print_info "步骤 9/10: 收集静态文件..."
    python manage.py collectstatic --noinput
    python manage.py compilemessages
    print_success "静态文件收集完成"
    
    # 10. 配置 Systemd 服务
    print_info "步骤 10/10: 配置系统服务..."
    
    # 创建 Gunicorn 服务文件
    cat > /etc/systemd/system/irongate.service <<EOF
[Unit]
Description=IronGate RCON Portal
After=network.target

[Service]
Type=notify
User=root
Group=root
WorkingDirectory=${INSTALL_DIR}
Environment="PATH=${INSTALL_DIR}/venv/bin"
ExecStart=${INSTALL_DIR}/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 irongate.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

    # 创建 Nginx 配置
    cat > /etc/nginx/sites-available/irongate <<EOF
server {
    listen 80;
    server_name ${DOMAIN};
    
    location /static/ {
        alias ${INSTALL_DIR}/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

    # 启用 Nginx 配置
    ln -sf /etc/nginx/sites-available/irongate /etc/nginx/sites-enabled/
    nginx -t
    
    # 启动服务
    systemctl daemon-reload
    systemctl enable irongate
    systemctl start irongate
    systemctl restart nginx
    
    print_success "系统服务配置完成"
    
    # 完成
    echo ""
    echo -e "${GREEN}============================================================${NC}"
    echo -e "${GREEN}🎉 安装完成！/ Installation Complete!${NC}"
    echo -e "${GREEN}============================================================${NC}"
    echo ""
    echo -e "${CYAN}访问地址 / Access URL:${NC}"
    echo "  http://${DOMAIN}"
    echo "  http://${DOMAIN}/admin (管理后台)"
    echo ""
    echo -e "${CYAN}下一步 / Next Steps:${NC}"
    echo "  1. 配置 SSL 证书 (推荐使用 certbot)"
    echo "  2. 在管理后台添加 Minecraft 服务器"
    echo "  3. 创建用户组并分配权限"
    echo ""
    echo -e "${YELLOW}重要文件位置 / Important Files:${NC}"
    echo "  项目目录: ${INSTALL_DIR}"
    echo "  配置文件: ${INSTALL_DIR}/.env"
    echo "  数据库: ${INSTALL_DIR}/db.sqlite3"
    echo ""
    
    press_any_key
}

# ============================================================
# 2. 更新代码 / Update Code
# ============================================================

update_code() {
    print_banner
    echo -e "${BLUE}=== 更新代码 / Update Code ===${NC}"
    echo ""
    
    # 检查项目目录
    if [ ! -f "manage.py" ]; then
        print_error "未找到项目目录，请先安装"
        print_error "Project directory not found, please install first"
        press_any_key
        return
    fi
    
    INSTALL_DIR=$(pwd)
    
    print_info "开始更新..."
    
    # 1. 备份数据库
    print_info "步骤 1/8: 备份数据库..."
    if [ -f "db.sqlite3" ]; then
        cp db.sqlite3 "db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)"
        print_success "数据库已备份"
    fi
    
    # 2. 停止服务
    print_info "步骤 2/8: 停止服务..."
    systemctl stop irongate 2>/dev/null || print_warning "服务未运行"
    
    # 3. 拉取最新代码
    print_info "步骤 3/8: 拉取最新代码..."
    git pull origin main
    print_success "代码已更新"
    
    # 4. 激活虚拟环境
    print_info "步骤 4/8: 激活虚拟环境..."
    source venv/bin/activate
    
    # 5. 更新依赖
    print_info "步骤 5/8: 更新依赖..."
    pip install -r requirements.txt --upgrade
    print_success "依赖已更新"
    
    # 6. 运行迁移
    print_info "步骤 6/8: 运行数据库迁移..."
    python manage.py migrate
    print_success "数据库迁移完成"
    
    # 7. 收集静态文件
    print_info "步骤 7/8: 收集静态文件..."
    python manage.py collectstatic --noinput
    python manage.py compilemessages 2>/dev/null || true
    print_success "静态文件已收集"
    
    # 8. 重启服务
    print_info "步骤 8/8: 重启服务..."
    systemctl start irongate
    systemctl restart nginx
    print_success "服务已重启"
    
    echo ""
    print_success "🎉 更新完成！/ Update Complete!"
    echo ""
    print_info "当前版本:"
    git log -1 --oneline
    echo ""
    
    press_any_key
}

# ============================================================
# 3-5. 服务管理 / Service Management
# ============================================================

start_service() {
    print_banner
    echo -e "${GREEN}=== 启动服务 / Start Service ===${NC}"
    echo ""
    
    systemctl start irongate
    systemctl start nginx
    
    print_success "服务已启动"
    sleep 2
    view_status
}

stop_service() {
    print_banner
    echo -e "${YELLOW}=== 停止服务 / Stop Service ===${NC}"
    echo ""
    
    systemctl stop irongate
    
    print_success "服务已停止"
    press_any_key
}

restart_service() {
    print_banner
    echo -e "${BLUE}=== 重启服务 / Restart Service ===${NC}"
    echo ""
    
    systemctl restart irongate
    systemctl restart nginx
    
    print_success "服务已重启"
    sleep 2
    view_status
}

# ============================================================
# 6. 查看状态 / View Status
# ============================================================

view_status() {
    print_banner
    echo -e "${CYAN}=== 服务状态 / Service Status ===${NC}"
    echo ""
    
    echo -e "${BLUE}IronGate 服务:${NC}"
    systemctl status irongate --no-pager -l || true
    echo ""
    
    echo -e "${BLUE}Nginx 服务:${NC}"
    systemctl status nginx --no-pager -l || true
    echo ""
    
    press_any_key
}

# ============================================================
# 7. 查看日志 / View Logs
# ============================================================

view_logs() {
    print_banner
    echo -e "${CYAN}=== 查看日志 / View Logs ===${NC}"
    echo ""
    echo "1) IronGate 应用日志"
    echo "2) Nginx 访问日志"
    echo "3) Nginx 错误日志"
    echo "0) 返回主菜单"
    echo ""
    read -p "选择 / Select [0-3]: " log_choice
    
    case $log_choice in
        1)
            print_info "显示最近 50 行日志 (按 Ctrl+C 退出)..."
            sleep 2
            journalctl -u irongate -n 50 -f
            ;;
        2)
            print_info "显示 Nginx 访问日志 (按 Ctrl+C 退出)..."
            sleep 2
            tail -f /var/log/nginx/access.log
            ;;
        3)
            print_info "显示 Nginx 错误日志 (按 Ctrl+C 退出)..."
            sleep 2
            tail -f /var/log/nginx/error.log
            ;;
        0)
            return
            ;;
        *)
            print_error "无效选项"
            press_any_key
            ;;
    esac
}

# ============================================================
# 8-9. 备份和恢复 / Backup and Restore
# ============================================================

backup_data() {
    print_banner
    echo -e "${YELLOW}=== 备份数据 / Backup Data ===${NC}"
    echo ""
    
    if [ ! -f "manage.py" ]; then
        print_error "未找到项目目录"
        press_any_key
        return
    fi
    
    BACKUP_DIR="backups"
    mkdir -p "$BACKUP_DIR"
    
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="${BACKUP_DIR}/irongate_backup_${TIMESTAMP}.tar.gz"
    
    print_info "创建备份..."
    tar -czf "$BACKUP_FILE" \
        db.sqlite3 \
        .env \
        staticfiles/ \
        2>/dev/null || true
    
    print_success "备份已创建: $BACKUP_FILE"
    ls -lh "$BACKUP_FILE"
    
    press_any_key
}

restore_data() {
    print_banner
    echo -e "${RED}=== 恢复数据 / Restore Data ===${NC}"
    echo ""
    
    if [ ! -d "backups" ]; then
        print_error "未找到备份目录"
        press_any_key
        return
    fi
    
    print_info "可用的备份文件:"
    ls -lh backups/*.tar.gz 2>/dev/null || {
        print_error "未找到备份文件"
        press_any_key
        return
    }
    
    echo ""
    read -p "输入备份文件名 / Enter backup filename: " backup_file
    
    if [ ! -f "backups/$backup_file" ]; then
        print_error "备份文件不存在"
        press_any_key
        return
    fi
    
    print_warning "这将覆盖当前数据！"
    read -p "确认恢复? (yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        print_info "已取消"
        press_any_key
        return
    fi
    
    print_info "停止服务..."
    systemctl stop irongate
    
    print_info "恢复数据..."
    tar -xzf "backups/$backup_file"
    
    print_info "启动服务..."
    systemctl start irongate
    
    print_success "数据已恢复"
    press_any_key
}

# ============================================================
# 主程序 / Main Program
# ============================================================

main() {
    # 检查 root 权限
    check_root
    
    while true; do
        show_menu
        read choice
        
        case $choice in
            1) install_fresh ;;
            2) update_code ;;
            3) start_service ;;
            4) stop_service ;;
            5) restart_service ;;
            6) view_status ;;
            7) view_logs ;;
            8) backup_data ;;
            9) restore_data ;;
            0) 
                print_info "再见! / Goodbye!"
                exit 0
                ;;
            *)
                print_error "无效选项 / Invalid option"
                press_any_key
                ;;
        esac
    done
}

# 运行主程序
main
