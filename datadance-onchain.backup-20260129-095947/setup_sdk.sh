#!/bin/bash
# BSN-DDC SDK 配置向导
# 帮助用户快速配置环境变量

echo "🚀 BSN-DDC SDK 配置向导"
echo "======================================"
echo ""

# 检查 .env 文件是否存在
if [ -f ".env" ]; then
    echo "⚠️  .env 文件已存在"
    read -p "是否覆盖现有配置? (y/N): " overwrite
    if [ "$overwrite" != "y" ] && [ "$overwrite" != "Y" ]; then
        echo "❌ 配置已取消"
        exit 0
    fi
fi

echo ""
echo "请输入 BSN-DDC 配置信息:"
echo "（可以从 https://ddc.bsnbase.com 控制台获取）"
echo ""

# 获取 Gateway URL
echo "1️⃣  Gateway URL"
echo "   测试环境示例: https://opbningxia.bsngate.com:18602/api/taianchain/v1"
echo "   生产环境示例: https://opbningxia.bsngate.com:17602/api/taianchain/v1"
read -p "   请输入: " gateway_url

# 获取 API Key
echo ""
echo "2️⃣  API Key"
echo "   格式: 32位字符串"
read -p "   请输入: " api_key

# 选择链类型
echo ""
echo "3️⃣  链类型"
echo "   1) taianchain  - 泰安链 (FISCO BCOS)"
echo "   2) wuhanchain  - 武汉链 (Ethereum)"
echo "   3) wenchangchain - 文昌链 (IRITA)"
echo "   4) zhongyichain - 中移链 (EOS)"
read -p "   请选择 (1-4, 默认 1): " chain_choice

case $chain_choice in
    2) chain="wuhanchain" ;;
    3) chain="wenchangchain" ;;
    4) chain="zhongyichain" ;;
    *) chain="taianchain" ;;
esac

# 获取用户地址（可选）
echo ""
echo "4️⃣  用户地址 (可选)"
read -p "   请输入 (按回车跳过): " user_address

# 调试模式
echo ""
echo "5️⃣  调试模式"
read -p "   是否启用? (y/N): " debug_choice

if [ "$debug_choice" = "y" ] || [ "$debug_choice" = "Y" ]; then
    debug="true"
else
    debug="false"
fi

# 生成 .env 文件
echo ""
echo "📝 生成配置文件..."

cat > .env << EOF
# BSN-DDC SDK 配置
# 生成时间: $(date)

# 网关地址
BSN_DDC_GATEWAY_URL=$gateway_url

# API 密钥
BSN_DDC_API_KEY=$api_key

# 链类型
BSN_DDC_CHAIN=$chain

EOF

# 添加可选配置
if [ -n "$user_address" ]; then
    echo "# 用户地址" >> .env
    echo "BSN_DDC_USER_ADDRESS=$user_address" >> .env
    echo "" >> .env
fi

# 添加调试配置
echo "# 调试模式" >> .env
echo "DEBUG=$debug" >> .env

echo "✅ 配置文件已生成: .env"
echo ""

# 验证配置
echo "🔍 验证配置..."
echo ""

# 激活 conda 环境并测试
if command -v conda &> /dev/null; then
    echo "激活 conda 环境: hackason"
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate hackason 2>/dev/null

    if [ $? -eq 0 ]; then
        echo "✓ conda 环境已激活"
        echo ""
        echo "运行测试..."
        python scripts/bsn_ddc_client_real.py
    else
        echo "⚠️  无法激活 conda 环境 'hackason'"
        echo "   请手动运行: conda activate hackason && python scripts/bsn_ddc_client_real.py"
    fi
else
    echo "⚠️  未检测到 conda"
    echo "   请手动运行: python scripts/bsn_ddc_client_real.py"
fi

echo ""
echo "======================================"
echo "✨ 配置完成！"
echo ""
echo "下一步:"
echo "  1. 查看配置: cat .env"
echo "  2. 测试 SDK: conda activate hackason && python scripts/bsn_ddc_client_real.py"
echo "  3. 阅读文档: docs/REAL_SDK_IMPLEMENTATION.md"
echo ""
