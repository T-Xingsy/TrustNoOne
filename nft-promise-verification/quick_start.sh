#!/bin/bash
# NFT 承诺验证 Mock 数据演示 - 快速启动脚本

set -e  # 遇到错误立即退出

echo "=========================================="
echo "🚀 NFT 承诺验证 Mock 数据演示系统"
echo "=========================================="
echo ""

# 检查 conda 环境
if ! conda info --envs | grep -q "hackason"; then
    echo "❌ Conda 环境 'hackason' 不存在"
    echo "请先创建环境: conda create -n hackason python=3.11"
    exit 1
fi

# 激活 conda 环境
echo "📦 激活 Conda 环境..."
eval "$(conda shell.bash hook)"
conda activate hackason

# 检查依赖
echo "🔍 检查依赖..."
if ! python -c "import fastapi" 2>/dev/null; then
    echo "⚠️  缺少依赖，正在安装..."
    pip install fastapi uvicorn structlog pydantic pydantic-settings
fi

# 进入项目目录
cd "$(dirname "$0")"

# 导入 Mock 数据
echo ""
echo "📥 导入 Mock 数据..."
python mock_data_loader.py --clear

# 询问用户选择
echo ""
echo "请选择演示模式:"
echo "  1. 命令行演示（交互式）"
echo "  2. 启动 API 服务器"
echo "  3. 生成所有项目报告"
echo "  4. 退出"
echo ""
read -p "请输入选项 (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🎯 启动命令行演示..."
        python demo.py
        ;;
    2)
        echo ""
        echo "🌐 启动 API 服务器..."
        echo "API 文档: http://localhost:8000/docs"
        echo "按 Ctrl+C 停止服务器"
        echo ""
        python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
        ;;
    3)
        echo ""
        echo "📊 生成所有项目报告..."
        mkdir -p reports
        python demo.py --project "Azuki" --format markdown --output reports/azuki_report.md
        python demo.py --project "Moonbirds" --format markdown --output reports/moonbirds_report.md
        python demo.py --project "PixelmonNFT" --format markdown --output reports/pixelmon_report.md
        echo ""
        echo "✅ 报告已生成到 reports/ 目录"
        ls -lh reports/
        ;;
    4)
        echo "👋 退出"
        exit 0
        ;;
    *)
        echo "❌ 无效选项"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "✅ 演示完成"
echo "=========================================="
