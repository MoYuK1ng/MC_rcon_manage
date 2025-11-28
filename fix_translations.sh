#!/bin/bash
# 修复翻译显示问题

echo "=========================================="
echo "修复中文翻译显示"
echo "=========================================="
echo ""

# 检查是否在项目目录
if [ ! -f "manage.py" ]; then
    echo "[ERROR] 请在项目目录运行"
    echo "使用: cd /opt/mc_rcon && bash fix_translations.sh"
    exit 1
fi

echo "1. 检查 gettext 是否安装..."
if ! command -v msgfmt &> /dev/null; then
    echo "[WARN] gettext 未安装，正在安装..."
    apt update
    apt install -y gettext
    echo "[OK] gettext 已安装"
else
    echo "[OK] gettext 已安装"
fi
echo ""

echo "2. 激活虚拟环境..."
source venv/bin/activate
echo "[OK] 虚拟环境已激活"
echo ""

echo "3. 编译翻译文件..."
python manage.py compilemessages

if [ $? -eq 0 ]; then
    echo "[OK] 翻译文件编译成功"
else
    echo "[ERROR] 翻译文件编译失败"
    exit 1
fi
echo ""

echo "4. 检查编译结果..."
if [ -f "locale/zh_hans/LC_MESSAGES/django.mo" ]; then
    echo "[OK] 找到编译后的文件: locale/zh_hans/LC_MESSAGES/django.mo"
    ls -lh locale/zh_hans/LC_MESSAGES/django.mo
else
    echo "[ERROR] 未找到编译后的文件"
    exit 1
fi
echo ""

echo "5. 重启服务..."
systemctl restart mc-rcon

if systemctl is-active --quiet mc-rcon; then
    echo "[OK] 服务重启成功"
else
    echo "[ERROR] 服务重启失败"
    systemctl status mc-rcon
    exit 1
fi
echo ""

echo "=========================================="
echo "修复完成！"
echo "=========================================="
echo ""
echo "现在访问后台应该能看到中文了"
echo "如果还是英文，请："
echo "  1. 清除浏览器缓存"
echo "  2. 在页面右上角切换语言"
echo "  3. 检查 Django 设置: LANGUAGE_CODE='zh-hans'"
echo ""
