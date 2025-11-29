#!/bin/bash
# 临时修复脚本 - 直接在服务器上运行

echo "=== 修复 .env 文件中的加密密钥 ==="

cd /opt/mc_rcon || exit 1

# 备份当前的 .env
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

# 读取当前密钥（去除所有空白字符）
CURRENT_KEY=$(grep '^RCON_ENCRYPTION_KEY=' .env | cut -d'=' -f2 | tr -d '[:space:]')

echo "当前密钥长度: ${#CURRENT_KEY}"

if [ ${#CURRENT_KEY} -eq 44 ]; then
    echo "✅ 密钥长度正确，无需修复"
    exit 0
fi

if [ ${#CURRENT_KEY} -eq 43 ] || [ ${#CURRENT_KEY} -eq 45 ]; then
    echo "⚠️  密钥长度不正确: ${#CURRENT_KEY} 字符"
    echo "重新生成密钥..."
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 重新生成密钥
    python generate_key.py --auto-yes
    
    # 读取新密钥
    NEW_KEY=$(grep '^RCON_ENCRYPTION_KEY=' .env | cut -d'=' -f2 | tr -d '[:space:]')
    
    echo "新密钥长度: ${#NEW_KEY}"
    
    if [ ${#NEW_KEY} -eq 44 ]; then
        echo "✅ 密钥生成成功"
        
        # 验证密钥
        python -c "
from servers.utils.key_validator import KeyValidator
key = '$NEW_KEY'
is_valid, error = KeyValidator.validate_key(key)
if is_valid:
    print('✅ 密钥验证通过')
else:
    print('❌ 密钥验证失败')
    print(error)
    exit(1)
"
        
        if [ $? -eq 0 ]; then
            echo "✅ 修复完成！现在可以继续安装"
            echo "运行: python create_superuser_no_email.py"
        fi
    else
        echo "❌ 密钥生成失败，长度仍然不正确"
        exit 1
    fi
else
    echo "❌ 密钥长度异常: ${#CURRENT_KEY}"
    exit 1
fi
