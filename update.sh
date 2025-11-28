#!/bin/bash
# IronGate 自动更新脚本
# Auto Update Script for IronGate

set -e  # 遇到错误立即退出 / Exit on error

# 颜色定义 / Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置 / Configuration
PROJECT_DIR="${PROJECT_DIR:-$(pwd)}"
VENV_DIR="${VENV_DIR:-$PROJECT_DIR/venv}"
BACKUP_DIR="${BACKUP_DIR:-$PROJECT_DIR/backups}"
SERVICE_NAME="${SERVICE_NAME:-gunicorn}"

# 函数：打印带颜色的消息 / Function: Print colored messages
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

# 函数：检查命令是否存在 / Function: Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 打印横幅 / Print banner
echo "============================================================"
echo "🎮 IronGate RCON Portal - 自动更新脚本"
echo "   IronGate RCON Portal - Auto Update Script"
echo "============================================================"
echo ""

# 检查是否在项目目录 / Check if in project directory
if [ ! -f "manage.py" ]; then
    print_error "错误：未找到 manage.py 文件"
    print_error "Error: manage.py not found"
    print_info "请在项目根目录运行此脚本"
    print_info "Please run this script from the project root directory"
    exit 1
fi

# 创建备份目录 / Create backup directory
if [ ! -d "$BACKUP_DIR" ]; then
    mkdir -p "$BACKUP_DIR"
    print_success "创建备份目录: $BACKUP_DIR"
fi

# 1. 备份数据库 / Backup database
print_info "步骤 1/10: 备份数据库..."
print_info "Step 1/10: Backing up database..."
if [ -f "db.sqlite3" ]; then
    BACKUP_FILE="$BACKUP_DIR/db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)"
    cp db.sqlite3 "$BACKUP_FILE"
    print_success "数据库已备份到: $BACKUP_FILE"
    print_success "Database backed up to: $BACKUP_FILE"
else
    print_warning "未找到数据库文件，跳过备份"
    print_warning "Database file not found, skipping backup"
fi

# 2. 备份 .env 文件 / Backup .env file
print_info "步骤 2/10: 备份配置文件..."
print_info "Step 2/10: Backing up configuration..."
if [ -f ".env" ]; then
    cp .env "$BACKUP_DIR/.env.backup.$(date +%Y%m%d_%H%M%S)"
    print_success "配置文件已备份"
    print_success "Configuration backed up"
else
    print_warning "未找到 .env 文件"
    print_warning ".env file not found"
fi

# 3. 停止服务 / Stop service
print_info "步骤 3/10: 停止服务..."
print_info "Step 3/10: Stopping service..."
if command_exists systemctl && systemctl is-active --quiet "$SERVICE_NAME"; then
    sudo systemctl stop "$SERVICE_NAME"
    print_success "服务已停止: $SERVICE_NAME"
    print_success "Service stopped: $SERVICE_NAME"
else
    print_warning "服务未运行或不使用 systemd"
    print_warning "Service not running or not using systemd"
fi

# 4. 拉取最新代码 / Pull latest code
print_info "步骤 4/10: 拉取最新代码..."
print_info "Step 4/10: Pulling latest code..."
if command_exists git; then
    git pull origin main
    print_success "代码已更新"
    print_success "Code updated"
else
    print_error "Git 未安装"
    print_error "Git not installed"
    exit 1
fi

# 5. 激活虚拟环境 / Activate virtual environment
print_info "步骤 5/10: 激活虚拟环境..."
print_info "Step 5/10: Activating virtual environment..."
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
    print_success "虚拟环境已激活"
    print_success "Virtual environment activated"
else
    print_error "虚拟环境未找到: $VENV_DIR"
    print_error "Virtual environment not found: $VENV_DIR"
    exit 1
fi

# 6. 更新依赖 / Update dependencies
print_info "步骤 6/10: 更新依赖..."
print_info "Step 6/10: Updating dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --upgrade --quiet
    print_success "依赖已更新"
    print_success "Dependencies updated"
else
    print_warning "未找到 requirements.txt"
    print_warning "requirements.txt not found"
fi

# 7. 运行数据库迁移 / Run database migrations
print_info "步骤 7/10: 运行数据库迁移..."
print_info "Step 7/10: Running database migrations..."
python manage.py migrate --noinput
print_success "数据库迁移完成"
print_success "Database migrations completed"

# 8. 收集静态文件 / Collect static files
print_info "步骤 8/10: 收集静态文件..."
print_info "Step 8/10: Collecting static files..."
python manage.py collectstatic --noinput --clear
print_success "静态文件已收集"
print_success "Static files collected"

# 9. 编译翻译文件 / Compile translations
print_info "步骤 9/10: 编译翻译文件..."
print_info "Step 9/10: Compiling translations..."
if command_exists msgfmt; then
    python manage.py compilemessages 2>/dev/null || {
        print_warning "翻译编译失败（非关键错误，可忽略）"
        print_warning "Translation compilation failed (non-critical, can be ignored)"
    }
else
    print_warning "gettext 未安装，跳过翻译编译"
    print_warning "gettext not installed, skipping translation compilation"
fi

# 10. 重启服务 / Restart services
print_info "步骤 10/10: 重启服务..."
print_info "Step 10/10: Restarting services..."
if command_exists systemctl; then
    # Restart application service
    if systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
        sudo systemctl restart "$SERVICE_NAME"
        print_success "应用服务已重启 / Application service restarted"
    else
        sudo systemctl start "$SERVICE_NAME"
        print_success "应用服务已启动 / Application service started"
    fi
    
    print_success "服务已重启 / Services restarted"
else
    print_warning "systemd 不可用，请手动重启服务"
    print_warning "systemd not available, please restart services manually"
fi

# 验证服务状态 / Verify service status
echo ""
print_info "验证服务状态..."
print_info "Verifying service status..."
if command_exists systemctl; then
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_success "$SERVICE_NAME 运行正常"
        print_success "$SERVICE_NAME is running"
    else
        print_error "$SERVICE_NAME 未运行"
        print_error "$SERVICE_NAME is not running"
        print_info "查看日志: sudo journalctl -u $SERVICE_NAME -n 50"
        print_info "View logs: sudo journalctl -u $SERVICE_NAME -n 50"
    fi
    
    if systemctl is-active --quiet nginx; then
        print_success "Nginx 运行正常"
        print_success "Nginx is running"
    else
        print_warning "Nginx 未运行或未安装"
        print_warning "Nginx is not running or not installed"
    fi
fi

# 显示版本信息 / Show version info
echo ""
print_info "当前版本信息 / Current version:"
git log -1 --oneline 2>/dev/null || echo "Git 信息不可用 / Git info not available"

# 完成 / Complete
echo ""
echo "============================================================"
print_success "🎉 更新完成！"
print_success "🎉 Update completed!"
echo "============================================================"
echo ""
print_info "下一步 / Next steps:"
echo "  1. 访问网站检查功能 / Visit website to check functionality"
echo "  2. 查看日志确认无错误 / Check logs for errors"
echo "  3. 测试 RCON 连接 / Test RCON connections"
echo ""
print_info "有用的命令 / Useful commands:"
echo "  查看服务状态 / Check service status:"
echo "    sudo systemctl status $SERVICE_NAME"
echo "  查看日志 / View logs:"
echo "    sudo journalctl -u $SERVICE_NAME -n 50"
echo "  重启服务 / Restart service:"
echo "    sudo systemctl restart $SERVICE_NAME"
echo ""
