#!/bin/bash
# MC RCON Manager - Management Script
# Developed by MoYuK1ng
# https://github.com/MoYuK1ng/MC_rcon_manage

set -e

# ============================================================
# Configuration
# ============================================================

SCRIPT_VERSION="2.0.0"
PROJECT_NAME="mc_rcon"
DEFAULT_INSTALL_DIR="/opt/mc_rcon"
REPO_URL="https://github.com/MoYuK1ng/MC_rcon_manage.git"
PYTHON_MIN_VERSION="3.10"

# Language setting (will be set by user)
LANG_CHOICE=""

# ============================================================
# Language Selection
# ============================================================

select_language() {
    clear
    echo "============================================================"
    echo "  MC RCON Manager - Management Script v${SCRIPT_VERSION}"
    echo "  Developed by MoYuK1ng"
    echo "============================================================"
    echo ""
    echo "Please select language / 请选择语言:"
    echo ""
    echo "  1) English"
    echo "  2) 简体中文 (Simplified Chinese)"
    echo ""
    read -p "Enter choice [1-2]: " lang_input
    
    case $lang_input in
        1)
            LANG_CHOICE="en"
            ;;
        2)
            LANG_CHOICE="zh"
            ;;
        *)
            echo "Invalid choice, using English"
            LANG_CHOICE="en"
            ;;
    esac
}

# ============================================================
# Multilingual Messages
# ============================================================

msg() {
    local key=$1
    
    if [ "$LANG_CHOICE" = "zh" ]; then
        case $key in
            "banner_title") echo "MC RCON 管理器 - 管理脚本 v${SCRIPT_VERSION}" ;;
            "banner_dev") echo "开发者: MoYuK1ng" ;;
            "menu_title") echo "请选择操作:" ;;
            "menu_install") echo "安装" ;;
            "menu_management") echo "管理" ;;
            "menu_maintenance") echo "维护" ;;
            "menu_others") echo "其他" ;;
            "opt_fresh_install") echo "全新安装" ;;
            "opt_update") echo "更新代码" ;;
            "opt_start") echo "启动服务" ;;
            "opt_stop") echo "停止服务" ;;
            "opt_restart") echo "重启服务" ;;
            "opt_status") echo "查看状态" ;;
            "opt_logs") echo "查看日志" ;;
            "opt_backup") echo "备份数据" ;;
            "opt_restore") echo "恢复数据" ;;
            "opt_exit") echo "退出" ;;
            "press_key") echo "按任意键继续..." ;;
            "need_root") echo "请使用 root 权限运行此脚本" ;;
            "use_sudo") echo "使用: sudo bash $0" ;;
            "invalid_option") echo "无效选项" ;;
            "goodbye") echo "再见!" ;;
            *) echo "$key" ;;
        esac
    else
        case $key in
            "banner_title") echo "MC RCON Manager - Management Script v${SCRIPT_VERSION}" ;;
            "banner_dev") echo "Developed by: MoYuK1ng" ;;
            "menu_title") echo "Please select an option:" ;;
            "menu_install") echo "Installation" ;;
            "menu_management") echo "Management" ;;
            "menu_maintenance") echo "Maintenance" ;;
            "menu_others") echo "Others" ;;
            "opt_fresh_install") echo "Fresh Install" ;;
            "opt_update") echo "Update Code" ;;
            "opt_start") echo "Start Service" ;;
            "opt_stop") echo "Stop Service" ;;
            "opt_restart") echo "Restart Service" ;;
            "opt_status") echo "View Status" ;;
            "opt_logs") echo "View Logs" ;;
            "opt_backup") echo "Backup Data" ;;
            "opt_restore") echo "Restore Data" ;;
            "opt_exit") echo "Exit" ;;
            "press_key") echo "Press any key to continue..." ;;
            "need_root") echo "Please run this script as root" ;;
            "use_sudo") echo "Usage: sudo bash $0" ;;
            "invalid_option") echo "Invalid option" ;;
            "goodbye") echo "Goodbye!" ;;
            *) echo "$key" ;;
        esac
    fi
}

# ============================================================
# Utility Functions
# ============================================================

print_banner() {
    clear
    echo "============================================================"
    echo "  $(msg banner_title)"
    echo "  $(msg banner_dev)"
    echo "============================================================"
    echo ""
}

print_info() {
    echo "[INFO] $1"
}

print_success() {
    echo "[OK] $1"
}

print_warning() {
    echo "[WARN] $1"
}

print_error() {
    echo "[ERROR] $1"
}

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

check_root() {
    if [ "$EUID" -ne 0 ]; then 
        print_error "$(msg need_root)"
        print_info "$(msg use_sudo)"
        exit 1
    fi
}

press_any_key() {
    echo ""
    read -n 1 -s -r -p "$(msg press_key)"
    echo ""
}

# ============================================================
# Main Menu
# ============================================================

show_menu() {
    print_banner
    echo "$(msg menu_title)"
    echo ""
    echo "  [$(msg menu_install)]"
    echo "  1) $(msg opt_fresh_install)"
    echo ""
    echo "  [$(msg menu_management)]"
    echo "  2) $(msg opt_update)"
    echo "  3) $(msg opt_start)"
    echo "  4) $(msg opt_stop)"
    echo "  5) $(msg opt_restart)"
    echo "  6) $(msg opt_status)"
    echo "  7) $(msg opt_logs)"
    echo ""
    echo "  [$(msg menu_maintenance)]"
    echo "  8) $(msg opt_backup)"
    echo "  9) $(msg opt_restore)"
    echo ""
    echo "  [$(msg menu_others)]"
    echo "  0) $(msg opt_exit)"
    echo ""
    echo -n "Enter option [0-9]: "
}

# ============================================================
# 1. Fresh Install
# ============================================================

install_fresh() {
    print_banner
    if [ "$LANG_CHOICE" = "zh" ]; then
        echo "=== 全新安装 ==="
    else
        echo "=== Fresh Installation ==="
    fi
    echo ""
    
    # Ask for install path
    if [ "$LANG_CHOICE" = "zh" ]; then
        read -p "安装路径 [${DEFAULT_INSTALL_DIR}]: " INSTALL_DIR
    else
        read -p "Install path [${DEFAULT_INSTALL_DIR}]: " INSTALL_DIR
    fi
    INSTALL_DIR=${INSTALL_DIR:-$DEFAULT_INSTALL_DIR}
    
    # Ask for port
    if [ "$LANG_CHOICE" = "zh" ]; then
        read -p "应用端口 [8000]: " APP_PORT
    else
        read -p "Application port [8000]: " APP_PORT
    fi
    APP_PORT=${APP_PORT:-8000}
    
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_info "开始安装到: $INSTALL_DIR"
    else
        print_info "Starting installation to: $INSTALL_DIR"
    fi
    
    # 1. Check and install dependencies
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_info "步骤 1/10: 检查系统依赖..."
    else
        print_info "Step 1/10: Checking system dependencies..."
    fi
    
    if ! command_exists python3; then
        print_info "Installing Python3..."
        apt update
        apt install -y python3 python3-pip python3-venv
    fi
    
    if ! command_exists git; then
        print_info "Installing Git..."
        apt install -y git
    fi
    
    apt install -y gettext
    print_success "Dependencies installed"
    
    # 2. Clone repository
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_info "步骤 2/10: 克隆代码仓库..."
    else
        print_info "Step 2/10: Cloning repository..."
    fi
    
    if [ -d "$INSTALL_DIR" ]; then
        if [ "$LANG_CHOICE" = "zh" ]; then
            print_warning "目录已存在，将删除并重新克隆"
        else
            print_warning "Directory exists, will remove and re-clone"
        fi
        rm -rf "$INSTALL_DIR"
    fi
    
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    print_success "Repository cloned"
    
    # 3. Create virtual environment
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_info "步骤 3/10: 创建 Python 虚拟环境..."
    else
        print_info "Step 3/10: Creating Python virtual environment..."
    fi
    
    python3 -m venv venv
    source venv/bin/activate
    print_success "Virtual environment created"
    
    # 4. Install Python dependencies
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_info "步骤 4/10: 安装 Python 依赖..."
    else
        print_info "Step 4/10: Installing Python dependencies..."
    fi
    
    pip install --upgrade pip
    pip install -r requirements.txt
    print_success "Python dependencies installed"
    
    # 5. Generate encryption key
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_info "步骤 5/10: 生成加密密钥..."
    else
        print_info "Step 5/10: Generating encryption key..."
    fi
    
    python generate_key.py
    print_success "Encryption key generated"
    
    # 6. Configure .env file
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_info "步骤 6/10: 配置环境变量..."
    else
        print_info "Step 6/10: Configuring environment variables..."
    fi
    
    SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
    
    sed -i "s/^DEBUG=.*/DEBUG=False/" .env
    sed -i "s/^SECRET_KEY=.*/SECRET_KEY=${SECRET_KEY}/" .env
    echo "ALLOWED_HOSTS=localhost,127.0.0.1,${DOMAIN}" >> .env
    echo "CSRF_TRUSTED_ORIGINS=https://${DOMAIN},http://localhost:8000" >> .env
    print_success "Environment configured"
    
    # 7. Initialize database
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_info "步骤 7/10: 初始化数据库..."
    else
        print_info "Step 7/10: Initializing database..."
    fi
    
    python manage.py migrate
    print_success "Database initialized"
    
    # 8. Create superuser
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_info "步骤 8/10: 创建管理员账户..."
    else
        print_info "Step 8/10: Creating admin account..."
    fi
    
    echo ""
    python manage.py createsuperuser
    print_success "Admin account created"
    
    # 9. Collect static files
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_info "步骤 9/10: 收集静态文件..."
    else
        print_info "Step 9/10: Collecting static files..."
    fi
    
    python manage.py collectstatic --noinput
    
    # Compile translations (ignore errors if gettext not installed or translations incomplete)
    if command_exists msgfmt; then
        python manage.py compilemessages 2>/dev/null || print_warning "Translation compilation skipped (non-critical)"
    else
        print_warning "gettext not installed, skipping translation compilation"
    fi
    
    print_success "Static files collected"
    
    # 10. Configure systemd service
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_info "步骤 10/10: 配置系统服务..."
    else
        print_info "Step 10/10: Configuring system services..."
    fi
    
    # Create Gunicorn service file
    cat > /etc/systemd/system/mc-rcon.service <<EOF
[Unit]
Description=MC RCON Manager
After=network.target

[Service]
Type=notify
User=root
Group=root
WorkingDirectory=${INSTALL_DIR}
Environment="PATH=${INSTALL_DIR}/venv/bin"
ExecStart=${INSTALL_DIR}/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:${APP_PORT} irongate.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable mc-rcon
    systemctl start mc-rcon
    
    print_success "System service configured"
    
    # Complete
    echo ""
    echo "============================================================"
    if [ "$LANG_CHOICE" = "zh" ]; then
        echo "安装完成！"
        echo "============================================================"
        echo ""
        echo "应用信息:"
        echo "  本地访问: http://127.0.0.1:${APP_PORT}"
        echo "  管理后台: http://127.0.0.1:${APP_PORT}/admin"
        echo "  安装路径: ${INSTALL_DIR}"
        echo ""
        echo "下一步:"
        echo "  1. 配置域名反向代理 (运行: bash setup_nginx.sh)"
        echo "  2. 在管理后台添加 Minecraft 服务器"
        echo "  3. 创建用户组并分配权限"
        echo ""
        echo "提示: 如需配置域名访问，请运行 Nginx 配置脚本"
    else
        echo "Installation Complete!"
        echo "============================================================"
        echo ""
        echo "Application Info:"
        echo "  Local access: http://127.0.0.1:${APP_PORT}"
        echo "  Admin panel: http://127.0.0.1:${APP_PORT}/admin"
        echo "  Install path: ${INSTALL_DIR}"
        echo ""
        echo "Next Steps:"
        echo "  1. Configure domain reverse proxy (run: bash setup_nginx.sh)"
        echo "  2. Add Minecraft servers in admin panel"
        echo "  3. Create user groups and assign permissions"
        echo ""
        echo "Tip: To configure domain access, run the Nginx setup script"
    fi
    echo ""
    
    press_any_key
}

# ============================================================
# 2. Update Code
# ============================================================

update_code() {
    print_banner
    if [ "$LANG_CHOICE" = "zh" ]; then
        echo "=== 更新代码 ==="
    else
        echo "=== Update Code ==="
    fi
    echo ""
    
    if [ ! -f "manage.py" ]; then
        if [ "$LANG_CHOICE" = "zh" ]; then
            print_error "未找到项目目录，请先安装"
        else
            print_error "Project directory not found, please install first"
        fi
        press_any_key
        return
    fi
    
    INSTALL_DIR=$(pwd)
    
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_info "开始更新..."
    else
        print_info "Starting update..."
    fi
    
    # Backup database
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_info "步骤 1/8: 备份数据库..."
    else
        print_info "Step 1/8: Backing up database..."
    fi
    
    if [ -f "db.sqlite3" ]; then
        cp db.sqlite3 "db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)"
        print_success "Database backed up"
    fi
    
    # Stop service
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_info "步骤 2/8: 停止服务..."
    else
        print_info "Step 2/8: Stopping service..."
    fi
    
    systemctl stop mc-rcon 2>/dev/null || print_warning "Service not running"
    
    # Pull latest code
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_info "步骤 3/8: 拉取最新代码..."
    else
        print_info "Step 3/8: Pulling latest code..."
    fi
    
    git pull origin main
    print_success "Code updated"
    
    # Activate virtual environment
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_info "步骤 4/8: 激活虚拟环境..."
    else
        print_info "Step 4/8: Activating virtual environment..."
    fi
    
    source venv/bin/activate
    
    # Update dependencies
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_info "步骤 5/8: 更新依赖..."
    else
        print_info "Step 5/8: Updating dependencies..."
    fi
    
    pip install -r requirements.txt --upgrade
    print_success "Dependencies updated"
    
    # Run migrations
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_info "步骤 6/8: 运行数据库迁移..."
    else
        print_info "Step 6/8: Running database migrations..."
    fi
    
    python manage.py migrate
    print_success "Database migrated"
    
    # Collect static files
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_info "步骤 7/8: 收集静态文件..."
    else
        print_info "Step 7/8: Collecting static files..."
    fi
    
    python manage.py collectstatic --noinput
    
    # Compile translations (ignore errors)
    if command_exists msgfmt; then
        python manage.py compilemessages 2>/dev/null || print_warning "Translation compilation skipped (non-critical)"
    fi
    
    print_success "Static files collected"
    
    # Restart service
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_info "步骤 8/8: 重启服务..."
    else
        print_info "Step 8/8: Restarting service..."
    fi
    
    systemctl start mc-rcon
    systemctl restart nginx
    print_success "Service restarted"
    
    echo ""
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_success "更新完成！"
    else
        print_success "Update complete!"
    fi
    echo ""
    
    press_any_key
}

# ============================================================
# 3-5. Service Management
# ============================================================

start_service() {
    print_banner
    if [ "$LANG_CHOICE" = "zh" ]; then
        echo "=== 启动服务 ==="
    else
        echo "=== Start Service ==="
    fi
    echo ""
    
    systemctl start mc-rcon
    systemctl start nginx
    
    print_success "Service started"
    sleep 2
    view_status
}

stop_service() {
    print_banner
    if [ "$LANG_CHOICE" = "zh" ]; then
        echo "=== 停止服务 ==="
    else
        echo "=== Stop Service ==="
    fi
    echo ""
    
    systemctl stop mc-rcon
    
    print_success "Service stopped"
    press_any_key
}

restart_service() {
    print_banner
    if [ "$LANG_CHOICE" = "zh" ]; then
        echo "=== 重启服务 ==="
    else
        echo "=== Restart Service ==="
    fi
    echo ""
    
    systemctl restart mc-rcon
    systemctl restart nginx
    
    print_success "Service restarted"
    sleep 2
    view_status
}

# ============================================================
# 6. View Status
# ============================================================

view_status() {
    print_banner
    if [ "$LANG_CHOICE" = "zh" ]; then
        echo "=== 服务状态 ==="
    else
        echo "=== Service Status ==="
    fi
    echo ""
    
    echo "MC RCON Service:"
    systemctl status mc-rcon --no-pager -l || true
    echo ""
    
    echo "Nginx Service:"
    systemctl status nginx --no-pager -l || true
    echo ""
    
    press_any_key
}

# ============================================================
# 7. View Logs
# ============================================================

view_logs() {
    print_banner
    if [ "$LANG_CHOICE" = "zh" ]; then
        echo "=== 查看日志 ==="
        echo ""
        echo "1) 应用日志"
        echo "2) Nginx 访问日志"
        echo "3) Nginx 错误日志"
        echo "0) 返回主菜单"
    else
        echo "=== View Logs ==="
        echo ""
        echo "1) Application logs"
        echo "2) Nginx access logs"
        echo "3) Nginx error logs"
        echo "0) Return to main menu"
    fi
    echo ""
    read -p "Select [0-3]: " log_choice
    
    case $log_choice in
        1)
            if [ "$LANG_CHOICE" = "zh" ]; then
                print_info "显示最近 50 行日志 (按 Ctrl+C 退出)..."
            else
                print_info "Showing last 50 lines (Press Ctrl+C to exit)..."
            fi
            sleep 2
            journalctl -u mc-rcon -n 50 -f
            ;;
        2)
            if [ "$LANG_CHOICE" = "zh" ]; then
                print_info "显示 Nginx 访问日志 (按 Ctrl+C 退出)..."
            else
                print_info "Showing Nginx access logs (Press Ctrl+C to exit)..."
            fi
            sleep 2
            tail -f /var/log/nginx/access.log
            ;;
        3)
            if [ "$LANG_CHOICE" = "zh" ]; then
                print_info "显示 Nginx 错误日志 (按 Ctrl+C 退出)..."
            else
                print_info "Showing Nginx error logs (Press Ctrl+C to exit)..."
            fi
            sleep 2
            tail -f /var/log/nginx/error.log
            ;;
        0)
            return
            ;;
        *)
            print_error "$(msg invalid_option)"
            press_any_key
            ;;
    esac
}

# ============================================================
# 8-9. Backup and Restore
# ============================================================

backup_data() {
    print_banner
    if [ "$LANG_CHOICE" = "zh" ]; then
        echo "=== 备份数据 ==="
    else
        echo "=== Backup Data ==="
    fi
    echo ""
    
    if [ ! -f "manage.py" ]; then
        print_error "Project directory not found"
        press_any_key
        return
    fi
    
    BACKUP_DIR="backups"
    mkdir -p "$BACKUP_DIR"
    
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="${BACKUP_DIR}/backup_${TIMESTAMP}.tar.gz"
    
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_info "创建备份..."
    else
        print_info "Creating backup..."
    fi
    
    tar -czf "$BACKUP_FILE" \
        db.sqlite3 \
        .env \
        staticfiles/ \
        2>/dev/null || true
    
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_success "备份已创建: $BACKUP_FILE"
    else
        print_success "Backup created: $BACKUP_FILE"
    fi
    
    ls -lh "$BACKUP_FILE"
    
    press_any_key
}

restore_data() {
    print_banner
    if [ "$LANG_CHOICE" = "zh" ]; then
        echo "=== 恢复数据 ==="
    else
        echo "=== Restore Data ==="
    fi
    echo ""
    
    if [ ! -d "backups" ]; then
        print_error "Backup directory not found"
        press_any_key
        return
    fi
    
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_info "可用的备份文件:"
    else
        print_info "Available backup files:"
    fi
    
    ls -lh backups/*.tar.gz 2>/dev/null || {
        print_error "No backup files found"
        press_any_key
        return
    }
    
    echo ""
    if [ "$LANG_CHOICE" = "zh" ]; then
        read -p "输入备份文件名: " backup_file
    else
        read -p "Enter backup filename: " backup_file
    fi
    
    if [ ! -f "backups/$backup_file" ]; then
        print_error "Backup file not found"
        press_any_key
        return
    fi
    
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_warning "这将覆盖当前数据！"
        read -p "确认恢复? (yes/no): " confirm
    else
        print_warning "This will overwrite current data!"
        read -p "Confirm restore? (yes/no): " confirm
    fi
    
    if [ "$confirm" != "yes" ]; then
        if [ "$LANG_CHOICE" = "zh" ]; then
            print_info "已取消"
        else
            print_info "Cancelled"
        fi
        press_any_key
        return
    fi
    
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_info "停止服务..."
    else
        print_info "Stopping service..."
    fi
    systemctl stop mc-rcon
    
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_info "恢复数据..."
    else
        print_info "Restoring data..."
    fi
    tar -xzf "backups/$backup_file"
    
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_info "启动服务..."
    else
        print_info "Starting service..."
    fi
    systemctl start mc-rcon
    
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_success "数据已恢复"
    else
        print_success "Data restored"
    fi
    press_any_key
}

# ============================================================
# Main Program
# ============================================================

main() {
    # Check root permission
    check_root
    
    # Select language first
    select_language
    
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
                print_info "$(msg goodbye)"
                exit 0
                ;;
            *)
                print_error "$(msg invalid_option)"
                press_any_key
                ;;
        esac
    done
}

# Run main program
main
