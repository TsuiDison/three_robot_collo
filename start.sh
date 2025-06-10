#!/bin/bash

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                   🎯 旅行规划仿真系统                            ║"
echo "║                                                                  ║"
echo "║                  Linux/Mac 一键启动脚本                           ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo

# 切换到脚本所在目录
cd "$(dirname "$0")"

# 检查Python
echo "🐍 检查Python环境..."

# 检查是否在agentclass环境中
if [ -n "$CONDA_DEFAULT_ENV" ]; then
    if [ "$CONDA_DEFAULT_ENV" = "agentclass" ]; then
        echo "✅ 已在agentclass环境中"
        # 跳转到程序运行部分
    else
        echo "当前环境: $CONDA_DEFAULT_ENV"
        echo "尝试切换到agentclass环境..."
        
        # 尝试激活agentclass环境
        echo "🔄 激活agentclass环境..."
        if command -v conda &> /dev/null; then
            source $(conda info --base)/etc/profile.d/conda.sh
            conda activate agentclass 2>/dev/null
            if [ $? -eq 0 ]; then
                echo "✅ agentclass环境已激活"
            else
                echo "❌ 无法激活agentclass环境"
                echo
                echo "💡 请先创建agentclass环境:"
                echo "   conda create -n agentclass python=3.9 -y"
                echo "   conda activate agentclass"
                echo
                echo "或者使用现有Python环境..."
            fi
        else
            echo "❌ 未找到conda命令"
        fi
    fi
else
    echo "未检测到conda环境，尝试使用系统Python..."
fi

# 检查Python是否可用
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "❌ Python未安装"
        echo "请先安装Python 3.8或更高版本"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "📍 当前Python环境:"
$PYTHON_CMD --version
echo "✅ Python环境正常"

echo
echo "🚀 启动安装程序..."
$PYTHON_CMD install_and_run.py

echo
echo "按任意键退出..."
read -n 1