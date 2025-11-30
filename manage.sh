#!/bin/bash
# MC RCON Manager - Management Script
# Developed by MoYuK1ng
# https://github.com/MoYuK1ng/MC_rcon_manage

set -e

# ============================================================
# Configuration
# ============================================================

SCRIPT_VERSION="2.3.0"
SCRIPT_DATE="2025-11-28"
PROJECT_NAME="mc_rcon"
DEFAULT_INSTALL_DIR="/opt/mc_rcon"
REPO_URL="https://github.com/MoYuK1ng/MC_rcon_manage.git"
VERSION_URL="https://raw.githubusercontent.com/MoYuK1ng/MC_rcon_manage/main/VERSION"
SCRIPT_URL="https://raw.githubusercontent.com/MoYuK1ng/MC_rcon_manage/main/manage.sh"
PYTHON_MIN_VERSION="3.10"

# Changelog for v2.3.0
# - Removed email input during user creation
# - Simplified permission system (Administrator/Regular User)
# - Modern UI design inspired by monitoring panels
# - Improved project directory detection
# - Added change password functionality
# - Removed all personal domain references

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
            "opt_update") echo "更新应用版本" ;;
            "opt_start") echo "启动服务" ;;
            "opt_stop") echo "停止服务" ;;
            "opt_restart") echo "重启服务" ;;
            "opt_status") echo "查看状态" ;;
            "opt_logs") echo "查看日志" ;;
            "opt_backup") echo "备份数据" ;;
            "opt_restore") echo "恢复数据" ;;
            "opt_change_password") echo "修改管理员密码" ;;
            "opt_update_script") echo "更新管理脚本" ;;
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
            "opt_update") echo "Update Application" ;;
            "opt_start") echo "Start Service" ;;
            "opt_stop") echo "Stop Service" ;;
            "opt_restart") echo "Restart Service" ;;
            "opt_status") echo "View Status" ;;
            "opt_logs") echo "View Logs" ;;
            "opt_backup") echo "Backup Data" ;;
            "opt_restore") echo "Restore Data" ;;
            "opt_change_password") echo "Change Admin Password" ;;
            "opt_update_script") echo "Update Script" ;;
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

check_and_enter_project_dir() {
    # Check if we're in the project directory, if not try to find and enter it
    # Returns 0 if successful, 1 if failed
    if [ -f "manage.py" ]; then
        return 0
    fi
    
    # Try to find the installation directory
    if [ -d "/opt/mc_rcon" ] && [ -f "/opt/mc_rcon/manage.py" ]; then
        if [ "$LANG_CHOICE" = "zh" ]; then
            print_info "检测到安装目录: /opt/mc_rcon"
        else
            print_info "Detected installation: /opt/mc_rcon"
        fi
        cd /opt/mc_rcon || return 1
        return 0
    fi
    
    # Not found
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_error "未找到项目目录"
        print_info "请在项目目录下运行: cd /opt/mc_rcon && bash manage.sh"
    else
        print_error "Project directory not found"
        print_info "Please run in project directory: cd /opt/mc_rcon && bash manage.sh"
    fi
    return 1
}

# ============================================================
# Main Menu
# ============================================================

show_menu() {
    print_banner
    
    # Display version info
    if [ "$LANG_CHOICE" = "zh" ]; then
        echo "  脚本版本: v${SCRIPT_VERSION} (${SCRIPT_DATE})"
    else
        echo "  Script Version: v${SCRIPT_VERSION} (${SCRIPT_DATE})"
    fi
    echo ""
    
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
    if [ "$LANG_CHOICE" = "zh" ]; then
        echo "  10) 修改管理员密码"
        echo "  11) 完全卸载"
        echo "  12) 更新管理脚本"
    else
        echo "  10) Change Admin Password"
        echo "  11) Uninstall"
        echo "  12) Update Script"
    fi
    echo "  0) $(msg opt_exit)"
    echo ""
    echo -n "Enter option [0-12]: "
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
    
    # Ask for access method
    echo ""
    if [ "$LANG_CHOICE" = "zh" ]; then
        echo "访问方式选择:"
        echo "  1) 直接访问 (http://IP:端口)"
        echo "  2) 反向代理 (通过域名访问，需要配置 Nginx/宝塔)"
        read -p "选择 [1-2]: " ACCESS_METHOD
    else
        echo "Access method:"
        echo "  1) Direct access (http://IP:port)"
        echo "  2) Reverse proxy (via domain, requires Nginx/BaoTa)"
        read -p "Choose [1-2]: " ACCESS_METHOD
    fi
    
    ACCESS_METHOD=${ACCESS_METHOD:-2}
    
    # Configure based on access method
    if [ "$ACCESS_METHOD" = "1" ]; then
        # Direct access - no domain needed
        DOMAIN=""
        USE_HTTPS="false"
        if [ "$LANG_CHOICE" = "zh" ]; then
            print_info "配置为直接访问模式"
        else
            print_info "Configured for direct access mode"
        fi
    else
        # Reverse proxy - ask for domain
        if [ "$LANG_CHOICE" = "zh" ]; then
            read -p "域名 (例如: mc.example.com): " DOMAIN
        else
            read -p "Domain (e.g., mc.example.com): " DOMAIN
        fi
        
        if [ -z "$DOMAIN" ]; then
            print_error "Domain cannot be empty for reverse proxy mode"
            press_any_key
            return
        fi
        
        # Ask if using HTTPS
        if [ "$LANG_CHOICE" = "zh" ]; then
            read -p "是否使用 HTTPS? (y/n) [y]: " USE_HTTPS_INPUT
        else
            read -p "Use HTTPS? (y/n) [y]: " USE_HTTPS_INPUT
        fi
        USE_HTTPS_INPUT=${USE_HTTPS_INPUT:-y}
        
        if [ "$USE_HTTPS_INPUT" = "y" ] || [ "$USE_HTTPS_INPUT" = "Y" ]; then
            USE_HTTPS="true"
            PROTOCOL="https"
        else
            USE_HTTPS="false"
            PROTOCOL="http"
        fi
    fi
    
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
    
    # Check if target directory exists
    if [ -d "$INSTALL_DIR" ]; then
        if [ "$LANG_CHOICE" = "zh" ]; then
            print_warning "目录已存在: $INSTALL_DIR"
            read -p "是否删除并重新安装? (y/n): " confirm_reinstall
        else
            print_warning "Directory exists: $INSTALL_DIR"
            read -p "Remove and reinstall? (y/n): " confirm_reinstall
        fi
        
        if [ "$confirm_reinstall" != "y" ] && [ "$confirm_reinstall" != "Y" ]; then
            if [ "$LANG_CHOICE" = "zh" ]; then
                print_info "已取消安装"
            else
                print_info "Installation cancelled"
            fi
            press_any_key
            return
        fi
        
        # Safety check: don't delete if we're inside the directory
        CURRENT_DIR=$(pwd)
        case "$CURRENT_DIR" in
            "$INSTALL_DIR"*)
                if [ "$LANG_CHOICE" = "zh" ]; then
                    print_error "错误: 当前在安装目录内，无法删除"
                    print_info "请先退出到其他目录: cd /tmp"
                else
                    print_error "Error: Currently inside install directory, cannot delete"
                    print_info "Please exit to another directory: cd /tmp"
                fi
                press_any_key
                return
                ;;
        esac
        
        rm -rf "$INSTALL_DIR"
    fi
    
    # Clone repository
    if ! git clone "$REPO_URL" "$INSTALL_DIR"; then
        if [ "$LANG_CHOICE" = "zh" ]; then
            print_error "克隆失败，请检查网络连接"
        else
            print_error "Clone failed, please check network connection"
        fi
        press_any_key
        return
    fi
    
    cd "$INSTALL_DIR" || {
        if [ "$LANG_CHOICE" = "zh" ]; then
            print_error "无法进入安装目录"
        else
            print_error "Cannot enter install directory"
        fi
        press_any_key
        return
    }
    
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
    
    # 5. Configure environment variables FIRST
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_info "步骤 5/10: 配置环境变量..."
    else
        print_info "Step 5/10: Configuring environment variables..."
    fi
    
    # Generate Django SECRET_KEY
    SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
    
    # Configure ALLOWED_HOSTS and CSRF based on access method
    if [ "$ACCESS_METHOD" = "1" ]; then
        # Direct access mode - allow all hosts
        ALLOWED_HOSTS="localhost,127.0.0.1,*"
        CSRF_ORIGINS="http://localhost:${APP_PORT},http://127.0.0.1:${APP_PORT}"
    else
        # Reverse proxy mode - specific domain
        ALLOWED_HOSTS="localhost,127.0.0.1,${DOMAIN}"
        if [ "$USE_HTTPS" = "true" ]; then
            CSRF_ORIGINS="https://${DOMAIN},http://localhost:${APP_PORT},http://127.0.0.1:${APP_PORT}"
        else
            CSRF_ORIGINS="http://${DOMAIN},http://localhost:${APP_PORT},http://127.0.0.1:${APP_PORT}"
        fi
    fi
    
    # Create .env file WITHOUT encryption key first
    cat > .env << EOF
# Django Settings
SECRET_KEY=${SECRET_KEY}
DEBUG=False

# Allowed Hosts (comma-separated, no spaces)
ALLOWED_HOSTS=${ALLOWED_HOSTS}

# CSRF Trusted Origins (comma-separated, include protocol)
CSRF_TRUSTED_ORIGINS=${CSRF_ORIGINS}

# Development Server Settings (optional)
# DEV_SERVER_PORT=${APP_PORT}
# DEV_SERVER_HOST=127.0.0.1
EOF
    
    print_success "Environment configured"
    
    # 6. Generate and append encryption key
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_info "步骤 6/10: 生成加密密钥..."
    else
        print_info "Step 6/10: Generating encryption key..."
    fi
    
    # Generate key and let it append to existing .env
    python generate_key.py --auto-yes
    print_success "Encryption key generated"
    
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
    
    # Use custom script to create superuser without email
    if [ -f "create_superuser_no_email.py" ]; then
        python create_superuser_no_email.py
    else
        # Fallback to default Django command
        python manage.py createsuperuser --noinput --username admin || python manage.py createsuperuser
    fi
    
    print_success "Admin account created"
    
    # Configure automatic backup
    echo ""
    echo "=== 自动备份配置 / Automatic Backup Configuration ==="
    read -p "是否启用自动服务器数据备份？Do you want to enable automatic server data backups? (Y/n): " enable_backup
    
    if [[ "$enable_backup" =~ ^[Yy]$ ]] || [[ -z "$enable_backup" ]]; then
        echo "ENABLE_AUTO_BACKUP=True" >> .env
        echo ""
        read -p "请输入备份目录的完整路径 Enter the full path for the backup directory (default: /opt/mc_rcon/backups): " backup_path
        
        if [[ -z "$backup_path" ]]; then
            backup_path="/opt/mc_rcon/backups"
        fi
        
        # Create backup directory if it doesn't exist
        mkdir -p "$backup_path"
        
        if [[ $? -eq 0 ]]; then
            echo "BACKUP_PATH=$backup_path" >> .env
            echo "BACKUP_MAX_COUNT=5" >> .env
            echo "✅ 自动备份已启用，备份目录: $backup_path"
            echo "✅ Automatic backup enabled, backup directory: $backup_path"
            
            # Set up cron job for daily backups
            echo ""
            read -p "是否设置每日自动备份？Do you want to set up daily automatic backups? (Y/n): " setup_cron
            
            if [[ "$setup_cron" =~ ^[Yy]$ ]] || [[ -z "$setup_cron" ]]; then
                # Add cron job for daily backup at 2 AM
                (crontab -l 2>/dev/null; echo "0 2 * * * cd $INSTALL_DIR && python3 manage.py backup_database >> /var/log/mc_rcon_backup.log 2>&1") | crontab -
                echo "✅ 每日备份任务已设置 (凌晨2点执行)"
                echo "✅ Daily backup task scheduled (runs at 2 AM)"
            fi
        else
            echo "❌ 无法创建备份目录，跳过自动备份配置"
            echo "❌ Failed to create backup directory, skipping automatic backup setup"
            echo "ENABLE_AUTO_BACKUP=False" >> .env
        fi
    else
        echo "ENABLE_AUTO_BACKUP=False" >> .env
        echo "⏭️  跳过自动备份配置"
        echo "⏭️  Skipping automatic backup configuration"
    fi
    
    # 9. Collect static files
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_info "步骤 8/9: 收集静态文件..."
    else
        print_info "Step 8/9: Collecting static files..."
    fi

    python manage.py collectstatic --noinput

    # 10. Configure systemd service
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_info "步骤 9/9: 配置系统服务..."
    else
        print_info "Step 9/9: Configuring system services..."
    fi
    
    # Create Gunicorn service file
    cat > /etc/systemd/system/mc-rcon.service <<EOF
[Unit]
Description=MC RCON Manager
After=network.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=${INSTALL_DIR}
Environment="PATH=${INSTALL_DIR}/venv/bin"
ExecStart=${INSTALL_DIR}/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:${APP_PORT} irongate.wsgi:application
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd
    systemctl daemon-reload
    
    # Enable service
    systemctl enable mc-rcon
    
    # Start service (capture error if fails)
    if ! systemctl start mc-rcon; then
        if [ "$LANG_CHOICE" = "zh" ]; then
            print_warning "服务启动失败，查看详细错误:"
            echo ""
            echo "运行以下命令查看错误:"
            echo "  systemctl status mc-rcon"
            echo "  journalctl -xeu mc-rcon -n 50"
            echo ""
            echo "常见问题:"
            echo "  1. 检查 gunicorn 是否安装: ${INSTALL_DIR}/venv/bin/gunicorn --version"
            echo "  2. 手动测试启动: cd ${INSTALL_DIR} && source venv/bin/activate && gunicorn irongate.wsgi:application"
        else
            print_warning "Service failed to start, check errors:"
            echo ""
            echo "Run these commands to see errors:"
            echo "  systemctl status mc-rcon"
            echo "  journalctl -xeu mc-rcon -n 50"
            echo ""
            echo "Common issues:"
            echo "  1. Check if gunicorn is installed: ${INSTALL_DIR}/venv/bin/gunicorn --version"
            echo "  2. Test manually: cd ${INSTALL_DIR} && source venv/bin/activate && gunicorn irongate.wsgi:application"
        fi
        press_any_key
        return
    fi
    
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
        if [ "$ACCESS_METHOD" = "2" ] && [ -n "$DOMAIN" ]; then
            echo "  域名访问: ${PROTOCOL}://${DOMAIN}"
        fi
        echo "  管理后台: http://127.0.0.1:${APP_PORT}/admin"
        echo "  安装路径: ${INSTALL_DIR}"
        echo ""
        echo "下一步:"
        if [ "$ACCESS_METHOD" = "2" ]; then
            echo "  1. 配置反向代理 (Nginx/宝塔面板)"
            echo "     - 目标地址: http://127.0.0.1:${APP_PORT}"
            echo "     - 域名: ${DOMAIN}"
            echo "  2. 在管理后台添加 Minecraft 服务器"
            echo "  3. 创建用户组并分配权限"
        else
            echo "  1. 通过 http://服务器IP:${APP_PORT} 访问"
            echo "  2. 在管理后台添加 Minecraft 服务器"
            echo "  3. 创建用户组并分配权限"
        fi
        echo ""
        echo "重要提示:"
        echo "  - CSRF 已自动配置，无需手动修改"
        echo "  - 查看配置: cat ${INSTALL_DIR}/.env"
    else
        echo "Installation Complete!"
        echo "============================================================"
        echo ""
        echo "Application Info:"
        echo "  Local access: http://127.0.0.1:${APP_PORT}"
        if [ "$ACCESS_METHOD" = "2" ] && [ -n "$DOMAIN" ]; then
            echo "  Domain access: ${PROTOCOL}://${DOMAIN}"
        fi
        echo "  Admin panel: http://127.0.0.1:${APP_PORT}/admin"
        echo "  Install path: ${INSTALL_DIR}"
        echo ""
        echo "Next Steps:"
        if [ "$ACCESS_METHOD" = "2" ]; then
            echo "  1. Configure reverse proxy (Nginx/BaoTa panel)"
            echo "     - Target: http://127.0.0.1:${APP_PORT}"
            echo "     - Domain: ${DOMAIN}"
            echo "  2. Add Minecraft servers in admin panel"
            echo "  3. Create user groups and assign permissions"
        else
            echo "  1. Access via http://ServerIP:${APP_PORT}"
            echo "  2. Add Minecraft servers in admin panel"
            echo "  3. Create user groups and assign permissions"
        fi
        echo ""
        echo "Important:"
        echo "  - CSRF auto-configured, no manual changes needed"
        echo "  - View config: cat ${INSTALL_DIR}/.env"
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
        echo "=== 更新应用版本 ==="
    else
        echo "=== Update Application ==="
    fi
    echo ""
    
    # Check and enter project directory
    if ! check_and_enter_project_dir; then
        press_any_key
        return
    fi
    
    INSTALL_DIR=$(pwd)
    
    # Show current version
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_info "当前版本:"
    else
        print_info "Current version:"
    fi
    
    # Get current version from VERSION file
    CURRENT_VERSION=""
    if [ -f "VERSION" ]; then
        CURRENT_VERSION=$(cat VERSION | tr -d '[:space:]')
        echo "v${CURRENT_VERSION}"
    else
        git log -1 --oneline 2>/dev/null || echo "Unknown"
    fi
    echo ""
    
    # Check for updates
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_info "检查更新..."
    else
        print_info "Checking for updates..."
    fi
    
    # Fetch latest version from GitHub
    REMOTE_VERSION=$(curl -s "${VERSION_URL}" | tr -d '[:space:]')
    
    if [ -z "$REMOTE_VERSION" ]; then
        if [ "$LANG_CHOICE" = "zh" ]; then
            print_warning "无法获取远程版本信息，继续更新..."
        else
            print_warning "Cannot fetch remote version, continuing update..."
        fi
    elif [ "$CURRENT_VERSION" = "$REMOTE_VERSION" ]; then
        if [ "$LANG_CHOICE" = "zh" ]; then
            print_success "已是最新版本 v${CURRENT_VERSION}"
            echo ""
            read -p "是否强制更新? (y/n) [n]: " force_update
        else
            print_success "Already up to date (v${CURRENT_VERSION})"
            echo ""
            read -p "Force update anyway? (y/n) [n]: " force_update
        fi
        
        force_update=${force_update:-n}
        if [ "$force_update" != "y" ] && [ "$force_update" != "Y" ]; then
            if [ "$LANG_CHOICE" = "zh" ]; then
                print_info "已取消更新"
            else
                print_info "Update cancelled"
            fi
            return
        fi
    else
        if [ "$LANG_CHOICE" = "zh" ]; then
            print_success "发现新版本: v${REMOTE_VERSION}"
        else
            print_success "New version available: v${REMOTE_VERSION}"
        fi
    fi
    echo ""
    
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
    
    # Remove compiled translation files to avoid conflicts
    rm -f locale/*/LC_MESSAGES/*.mo
    
    # Reset any local changes and pull
    git reset --hard HEAD
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
            print_success "Static files collected"
        
            # Restart service
            if [ "$LANG_CHOICE" = "zh" ]; then
                print_info "步骤 8/8: 重启服务..."
            else
                print_info "Step 8/8: Restarting service..."
            fi    
    systemctl start mc-rcon
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
        echo "1) 应用日志 (最近 50 行)"
        echo "2) 应用日志 (实时)"
        echo "0) 返回主菜单"
    else
        echo "=== View Logs ==="
        echo ""
        echo "1) Application logs (last 50 lines)"
        echo "2) Application logs (live)"
        echo "0) Return to main menu"
    fi
    echo ""
    read -p "Select [0-2]: " log_choice
    
    case $log_choice in
        1)
            if [ "$LANG_CHOICE" = "zh" ]; then
                print_info "显示最近 50 行日志..."
            else
                print_info "Showing last 50 lines..."
            fi
            echo ""
            journalctl -u mc-rcon -n 50 --no-pager
            echo ""
            press_any_key
            ;;
        2)
            if [ "$LANG_CHOICE" = "zh" ]; then
                print_info "显示实时日志 (按 Ctrl+C 退出)..."
            else
                print_info "Showing live logs (Press Ctrl+C to exit)..."
            fi
            sleep 2
            journalctl -u mc-rcon -f
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
# 8. Backup Management (Integrated with automatic backup system)
# ============================================================

backup_menu() {
    while true; do
        print_banner
        if [ "$LANG_CHOICE" = "zh" ]; then
            echo "=== 备份管理 ==="
            echo ""
            echo "  1) 立即创建备份"
            echo "  2) 列出所有备份"
            echo "  3) 清理旧备份"
            echo "  4) 查看备份配置"
            echo "  0) 返回主菜单"
        else
            echo "=== Backup Management ==="
            echo ""
            echo "  1) Create backup now"
            echo "  2) List all backups"
            echo "  3) Cleanup old backups"
            echo "  4) View backup configuration"
            echo "  0) Return to main menu"
        fi
        echo ""
        read -p "Enter option [0-4]: " backup_choice
        
        case $backup_choice in
            1) create_backup_now ;;
            2) list_backups ;;
            3) cleanup_old_backups ;;
            4) view_backup_config ;;
            0) return ;;
            *)
                if [ "$LANG_CHOICE" = "zh" ]; then
                    print_error "无效选项"
                else
                    print_error "Invalid option"
                fi
                press_any_key
                ;;
        esac
    done
}

create_backup_now() {
    print_banner
    if [ "$LANG_CHOICE" = "zh" ]; then
        echo "=== 立即创建备份 ==="
    else
        echo "=== Create Backup Now ==="
    fi
    echo ""
    
    if ! check_and_enter_project_dir; then
        press_any_key
        return
    fi
    
    # Activate virtual environment
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    # Run backup command
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_info "正在创建备份..."
    else
        print_info "Creating backup..."
    fi
    echo ""
    
    python manage.py backup_database --force
    
    echo ""
    press_any_key
}

list_backups() {
    print_banner
    if [ "$LANG_CHOICE" = "zh" ]; then
        echo "=== 备份列表 ==="
    else
        echo "=== Backup List ==="
    fi
    echo ""
    
    if ! check_and_enter_project_dir; then
        press_any_key
        return
    fi
    
    # Activate virtual environment
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    # Use backup manager to list backups
    python backup_manager.py list
    
    echo ""
    press_any_key
}

cleanup_old_backups() {
    print_banner
    if [ "$LANG_CHOICE" = "zh" ]; then
        echo "=== 清理旧备份 ==="
    else
        echo "=== Cleanup Old Backups ==="
    fi
    echo ""
    
    if ! check_and_enter_project_dir; then
        press_any_key
        return
    fi
    
    # Activate virtual environment
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    # Use backup manager to cleanup
    python backup_manager.py cleanup
    
    echo ""
    press_any_key
}

view_backup_config() {
    print_banner
    if [ "$LANG_CHOICE" = "zh" ]; then
        echo "=== 备份配置 ==="
    else
        echo "=== Backup Configuration ==="
    fi
    echo ""
    
    if ! check_and_enter_project_dir; then
        press_any_key
        return
    fi
    
    # Read configuration from .env file
    if [ -f ".env" ]; then
        ENABLE_AUTO_BACKUP=$(grep "^ENABLE_AUTO_BACKUP=" .env | cut -d'=' -f2)
        BACKUP_PATH=$(grep "^BACKUP_PATH=" .env | cut -d'=' -f2)
        BACKUP_MAX_COUNT=$(grep "^BACKUP_MAX_COUNT=" .env | cut -d'=' -f2)
        
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        if [ "$LANG_CHOICE" = "zh" ]; then
            echo "📋 当前配置:"
        else
            echo "📋 Current Configuration:"
        fi
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        if [ "$LANG_CHOICE" = "zh" ]; then
            echo "  自动备份: ${ENABLE_AUTO_BACKUP:-未配置}"
            echo "  备份路径: ${BACKUP_PATH:-未配置}"
            echo "  最大保留: ${BACKUP_MAX_COUNT:-5} 个备份"
        else
            echo "  Auto Backup: ${ENABLE_AUTO_BACKUP:-Not configured}"
            echo "  Backup Path: ${BACKUP_PATH:-Not configured}"
            echo "  Max Count:   ${BACKUP_MAX_COUNT:-5} backups"
        fi
        
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        
        # Check if backup directory exists and show stats
        if [ -n "$BACKUP_PATH" ] && [ -d "$BACKUP_PATH" ]; then
            BACKUP_COUNT=$(ls -1 "$BACKUP_PATH"/db_backup_*.sqlite3 2>/dev/null | wc -l)
            if [ "$LANG_CHOICE" = "zh" ]; then
                echo "  当前备份数量: $BACKUP_COUNT"
            else
                echo "  Current backup count: $BACKUP_COUNT"
            fi
            
            if [ $BACKUP_COUNT -gt 0 ]; then
                TOTAL_SIZE=$(du -sh "$BACKUP_PATH" 2>/dev/null | cut -f1)
                if [ "$LANG_CHOICE" = "zh" ]; then
                    echo "  占用空间: $TOTAL_SIZE"
                else
                    echo "  Total size: $TOTAL_SIZE"
                fi
            fi
        fi
        
        echo ""
        
        # Show cron job status
        if [ "$LANG_CHOICE" = "zh" ]; then
            echo "📅 定时任务状态:"
        else
            echo "📅 Scheduled Task Status:"
        fi
        
        if crontab -l 2>/dev/null | grep -q "backup_database"; then
            if [ "$LANG_CHOICE" = "zh" ]; then
                echo "  ✅ 已配置自动备份定时任务"
                echo ""
                echo "  定时任务详情:"
                crontab -l 2>/dev/null | grep "backup_database"
            else
                echo "  ✅ Automatic backup scheduled"
                echo ""
                echo "  Cron job details:"
                crontab -l 2>/dev/null | grep "backup_database"
            fi
        else
            if [ "$LANG_CHOICE" = "zh" ]; then
                echo "  ⚠️  未配置定时任务"
                echo ""
                echo "  要设置每日自动备份，运行:"
                echo "  (crontab -l 2>/dev/null; echo \"0 2 * * * cd $(pwd) && python3 manage.py backup_database >> /var/log/mc_rcon_backup.log 2>&1\") | crontab -"
            else
                echo "  ⚠️  No scheduled task configured"
                echo ""
                echo "  To set up daily automatic backup, run:"
                echo "  (crontab -l 2>/dev/null; echo \"0 2 * * * cd $(pwd) && python3 manage.py backup_database >> /var/log/mc_rcon_backup.log 2>&1\") | crontab -"
            fi
        fi
    else
        if [ "$LANG_CHOICE" = "zh" ]; then
            print_error "未找到 .env 配置文件"
        else
            print_error ".env configuration file not found"
        fi
    fi
    
    echo ""
    press_any_key
}

restore_data() {
    print_banner
    if [ "$LANG_CHOICE" = "zh" ]; then
        echo "=== 恢复数据库 ==="
    else
        echo "=== Restore Database ==="
    fi
    echo ""
    
    if ! check_and_enter_project_dir; then
        press_any_key
        return
    fi
    
    # Ask for backup file path
    if [ "$LANG_CHOICE" = "zh" ]; then
        echo "📁 请输入备份文件的完整路径:"
        read -p "备份文件路径: " BACKUP_FILE
    else
        echo "📁 Enter the full path to the backup file:"
        read -p "Backup file path: " BACKUP_FILE
    fi
    
    # Check if backup file exists
    if [ ! -f "$BACKUP_FILE" ]; then
        if [ "$LANG_CHOICE" = "zh" ]; then
            print_error "❌ 备份文件不存在: $BACKUP_FILE"
        else
            print_error "❌ Backup file not found: $BACKUP_FILE"
        fi
        press_any_key
        return
    fi
    
    # Show backup info
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo ""
    if [ "$LANG_CHOICE" = "zh" ]; then
        echo "📋 备份文件信息:"
        echo "  文件: $BACKUP_FILE"
        echo "  大小: $BACKUP_SIZE"
    else
        echo "📋 Backup file information:"
        echo "  File: $BACKUP_FILE"
        echo "  Size: $BACKUP_SIZE"
    fi
    echo ""
    
    # Confirm restore
    if [ "$LANG_CHOICE" = "zh" ]; then
        echo "⚠️  警告: 这将替换您当前的数据库！"
        echo "   请确保您已经备份了当前数据库。"
        echo ""
        read -p "是否继续? (yes/no): " CONFIRM
    else
        echo "⚠️  WARNING: This will replace your current database!"
        echo "   Make sure you have a backup of your current database."
        echo ""
        read -p "Do you want to continue? (yes/no): " CONFIRM
    fi
    
    if [ "$CONFIRM" != "yes" ]; then
        if [ "$LANG_CHOICE" = "zh" ]; then
            print_info "ℹ️  恢复已取消。"
        else
            print_info "ℹ️  Restore cancelled."
        fi
        press_any_key
        return
    fi
    
    # Create backup of current database before restore
    if [ -f "db.sqlite3" ]; then
        TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
        CURRENT_BACKUP="db_before_restore_${TIMESTAMP}.sqlite3"
        echo ""
        if [ "$LANG_CHOICE" = "zh" ]; then
            print_info "💾 正在备份当前数据库..."
        else
            print_info "💾 Creating backup of current database..."
        fi
        cp db.sqlite3 "$CURRENT_BACKUP"
        if [ "$LANG_CHOICE" = "zh" ]; then
            print_success "✅ 当前数据库已备份到: $CURRENT_BACKUP"
        else
            print_success "✅ Current database backed up to: $CURRENT_BACKUP"
        fi
    fi
    
    # Stop the service if running
    echo ""
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_info "🛑 正在停止 MC RCON 服务..."
    else
        print_info "🛑 Stopping MC RCON service..."
    fi
    
    if systemctl is-active --quiet mc-rcon; then
        systemctl stop mc-rcon
        if [ "$LANG_CHOICE" = "zh" ]; then
            print_success "✅ 服务已停止"
        else
            print_success "✅ Service stopped"
        fi
    else
        if [ "$LANG_CHOICE" = "zh" ]; then
            print_info "ℹ️  服务未运行"
        else
            print_info "ℹ️  Service is not running"
        fi
    fi
    
    # Restore database
    echo ""
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_info "🔄 正在恢复数据库..."
    else
        print_info "🔄 Restoring database..."
    fi
    
    cp "$BACKUP_FILE" db.sqlite3
    
    # Verify restore
    if [ -f "db.sqlite3" ]; then
        if [ "$LANG_CHOICE" = "zh" ]; then
            print_success "✅ 数据库恢复成功！"
        else
            print_success "✅ Database restored successfully!"
        fi
    else
        if [ "$LANG_CHOICE" = "zh" ]; then
            print_error "❌ 恢复失败！"
        else
            print_error "❌ Restore failed!"
        fi
        press_any_key
        return
    fi
    
    # Start the service
    echo ""
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_info "🚀 正在启动 MC RCON 服务..."
    else
        print_info "🚀 Starting MC RCON service..."
    fi
    
    systemctl start mc-rcon
    
    # Check service status
    sleep 2
    if systemctl is-active --quiet mc-rcon; then
        if [ "$LANG_CHOICE" = "zh" ]; then
            print_success "✅ 服务启动成功"
        else
            print_success "✅ Service started successfully"
        fi
    else
        if [ "$LANG_CHOICE" = "zh" ]; then
            print_error "❌ 警告: 服务启动失败"
            echo "   使用以下命令查看日志: journalctl -u mc-rcon -n 50"
        else
            print_error "❌ Warning: Service failed to start"
            echo "   Check logs with: journalctl -u mc-rcon -n 50"
        fi
    fi
    
    echo ""
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_success "🎉 数据库恢复完成！"
    else
        print_success "🎉 Database restore complete!"
    fi
    echo ""
    
    press_any_key
}

# ============================================================
# 10. Change Admin Password
# ============================================================

change_admin_password() {
    print_banner
    if [ "$LANG_CHOICE" = "zh" ]; then
        echo "=== 修改管理员密码 ==="
    else
        echo "=== Change Admin Password ==="
    fi
    echo ""
    
    if ! check_and_enter_project_dir; then
        press_any_key
        return
    fi
    
    # Check if change_password.py exists
    if [ ! -f "change_password.py" ]; then
        if [ "$LANG_CHOICE" = "zh" ]; then
            print_warning "密码修改脚本不存在，正在下载..."
        else
            print_warning "Password change script not found, downloading..."
        fi
        
        wget -q https://raw.githubusercontent.com/MoYuK1ng/MC_rcon_manage/main/change_password.py -O change_password.py
        
        if [ ! -f "change_password.py" ]; then
            if [ "$LANG_CHOICE" = "zh" ]; then
                print_error "下载失败"
            else
                print_error "Download failed"
            fi
            press_any_key
            return
        fi
        
        chmod +x change_password.py
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Run password change script
    python change_password.py
    
    # Check exit code
    if [ $? -eq 0 ]; then
        echo ""
        if [ "$LANG_CHOICE" = "zh" ]; then
            print_success "密码修改完成"
        else
            print_success "Password changed successfully"
        fi
    else
        echo ""
        if [ "$LANG_CHOICE" = "zh" ]; then
            print_warning "密码修改已取消或失败"
        else
            print_warning "Password change cancelled or failed"
        fi
    fi
    
    press_any_key
}

# ============================================================
# 11. Uninstall
# ============================================================

uninstall_all() {
    print_banner
    if [ "$LANG_CHOICE" = "zh" ]; then
        echo "=== 完全卸载 ==="
    else
        echo "=== Complete Uninstall ==="
    fi
    echo ""
    
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_warning "⚠️  警告：这将删除所有数据和配置！"
        echo ""
        echo "将要删除："
        echo "  - 项目文件"
        echo "  - 数据库"
        echo "  - 配置文件"
        echo "  - Systemd 服务"
        echo ""
    else
        print_warning "⚠️  WARNING: This will delete all data and configurations!"
        echo ""
        echo "Will delete:"
        echo "  - Project files"
        echo "  - Database"
        echo "  - Configuration files"
        echo "  - Systemd service"
        echo ""
    fi
    
    # Ask if user wants to backup first
    if [ "$LANG_CHOICE" = "zh" ]; then
        echo "💾 建议在卸载前备份数据库"
        read -p "是否现在进行备份? (y/n) [y]: " do_backup
    else
        echo "💾 It's recommended to backup your database before uninstalling"
        read -p "Do you want to backup now? (y/n) [y]: " do_backup
    fi
    
    do_backup=${do_backup:-y}
    
    if [ "$do_backup" = "y" ] || [ "$do_backup" = "Y" ]; then
        # Run backup function
        backup_data
        echo ""
        if [ "$LANG_CHOICE" = "zh" ]; then
            print_info "备份完成，继续卸载流程..."
        else
            print_info "Backup complete, continuing with uninstall..."
        fi
        echo ""
    fi
    
    # Final confirmation
    if [ "$LANG_CHOICE" = "zh" ]; then
        read -p "确认卸载? 输入 'YES' 继续: " confirm
    else
        read -p "Confirm uninstall? Type 'YES' to continue: " confirm
    fi
    
    if [ "$confirm" != "YES" ]; then
        if [ "$LANG_CHOICE" = "zh" ]; then
            print_info "已取消卸载"
        else
            print_info "Uninstall cancelled"
        fi
        press_any_key
        return
    fi
    
    # Ask for installation directory
    if [ "$LANG_CHOICE" = "zh" ]; then
        read -p "项目安装路径 [/opt/mc_rcon]: " INSTALL_DIR
    else
        read -p "Project installation path [/opt/mc_rcon]: " INSTALL_DIR
    fi
    INSTALL_DIR=${INSTALL_DIR:-/opt/mc_rcon}
    
    if [ ! -d "$INSTALL_DIR" ]; then
        if [ "$LANG_CHOICE" = "zh" ]; then
            print_error "目录不存在: $INSTALL_DIR"
        else
            print_error "Directory not found: $INSTALL_DIR"
        fi
        press_any_key
        return
    fi
    
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_info "开始卸载..."
    else
        print_info "Starting uninstall..."
    fi
    
    # 1. Stop and disable service
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_info "步骤 1/5: 停止并禁用服务..."
    else
        print_info "Step 1/5: Stopping and disabling service..."
    fi
    
    systemctl stop mc-rcon 2>/dev/null || true
    systemctl disable mc-rcon 2>/dev/null || true
    
    # Wait for processes to terminate
    sleep 2
    
    # Force kill any remaining gunicorn processes
    if pgrep -f "gunicorn.*irongate" > /dev/null; then
        if [ "$LANG_CHOICE" = "zh" ]; then
            print_warning "发现残留进程，强制终止..."
        else
            print_warning "Found remaining processes, force killing..."
        fi
        pkill -9 -f "gunicorn.*irongate" 2>/dev/null || true
        sleep 1
    fi
    
    print_success "Service stopped"
    
    # 2. Remove systemd service file
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_info "步骤 2/5: 删除 Systemd 服务..."
    else
        print_info "Step 2/5: Removing Systemd service..."
    fi
    
    rm -f /etc/systemd/system/mc-rcon.service
    systemctl daemon-reload
    print_success "Service file removed"
    
    # 3. Remove project directory
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_info "步骤 3/3: 删除项目文件..."
    else
        print_info "Step 3/3: Removing project files..."
    fi
    
    rm -rf "$INSTALL_DIR"
    print_success "Project files removed"
    
    # Complete
    echo ""
    echo "============================================================"
    if [ "$LANG_CHOICE" = "zh" ]; then
        echo "卸载完成！"
        echo "============================================================"
    else
        echo "Uninstall Complete!"
        echo "============================================================"
    fi
    echo ""
    
    press_any_key
    
    # Exit after uninstall
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_info "再见！"
    else
        print_info "Goodbye!"
    fi
    exit 0
}

# ============================================================
# 11. Update Script
# ============================================================

update_script() {
    print_banner
    if [ "$LANG_CHOICE" = "zh" ]; then
        echo "=== 更新管理脚本 ==="
    else
        echo "=== Update Management Script ==="
    fi
    echo ""
    
    if [ "$LANG_CHOICE" = "zh" ]; then
        print_info "当前版本: v${SCRIPT_VERSION}"
        print_info "正在检查更新..."
    else
        print_info "Current version: v${SCRIPT_VERSION}"
        print_info "Checking for updates..."
    fi
    
    # Download latest script to temp file (with cache busting)
    TEMP_SCRIPT="/tmp/manage.sh.new"
    TIMESTAMP=$(date +%s)
    if wget -q "${SCRIPT_URL}?t=${TIMESTAMP}" -O "$TEMP_SCRIPT"; then
        # Get new version
        NEW_VERSION=$(grep '^SCRIPT_VERSION=' "$TEMP_SCRIPT" | cut -d'"' -f2)
        
        if [ "$NEW_VERSION" != "$SCRIPT_VERSION" ]; then
            if [ "$LANG_CHOICE" = "zh" ]; then
                print_success "发现新版本: v${NEW_VERSION}"
                echo ""
                read -p "是否更新? (y/n) [y]: " update_confirm
            else
                print_success "New version available: v${NEW_VERSION}"
                echo ""
                read -p "Update now? (y/n) [y]: " update_confirm
            fi
            
            update_confirm=${update_confirm:-y}
            if [ "$update_confirm" = "y" ] || [ "$update_confirm" = "Y" ]; then
                # Backup current script
                if [ -f "$0" ]; then
                    cp "$0" "${0}.backup"
                fi
                
                # Replace with new script
                mv "$TEMP_SCRIPT" "$0"
                chmod +x "$0"
                
                if [ "$LANG_CHOICE" = "zh" ]; then
                    print_success "脚本已更新到 v${NEW_VERSION}"
                    print_info "重新启动脚本..."
                else
                    print_success "Script updated to v${NEW_VERSION}"
                    print_info "Restarting script..."
                fi
                
                sleep 2
                exec "$0"
            else
                rm -f "$TEMP_SCRIPT"
                if [ "$LANG_CHOICE" = "zh" ]; then
                    print_info "已取消更新"
                else
                    print_info "Update cancelled"
                fi
            fi
        else
            rm -f "$TEMP_SCRIPT"
            if [ "$LANG_CHOICE" = "zh" ]; then
                print_success "已是最新版本"
            else
                print_success "Already up to date"
            fi
        fi
    else
        rm -f "$TEMP_SCRIPT"
        if [ "$LANG_CHOICE" = "zh" ]; then
            print_error "无法连接到更新服务器"
        else
            print_error "Cannot connect to update server"
        fi
    fi
    
    echo ""
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
            8) backup_menu ;;
            9) restore_data ;;
            10) change_admin_password ;;
            11) uninstall_all ;;
            12) update_script ;;
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
