@echo off
chcp 65001 >nul
echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║               🌿 AgentClass 环境配置工具                          ║
echo ║                                                                  ║
echo ║          自动创建和配置conda虚拟环境                               ║
echo ║                                                                  ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

echo 🔍 检查conda环境...
conda --version >nul 2>&1
if errorlevel 1 (
    echo ❌ conda未安装
    echo 请先安装Anaconda或Miniconda
    echo 下载地址: https://www.anaconda.com/products/distribution
    pause
    exit /b 1
)

echo ✅ conda已安装

echo.
echo 🌿 检查agentclass环境...
conda info --envs | findstr "agentclass" >nul
if errorlevel 1 (
    echo ❌ agentclass环境不存在
    echo.
    set /p choice="是否创建agentclass环境? [y/n]: "
    if /i "%choice%"=="y" (
        echo 📦 创建agentclass环境...
        conda create -n agentclass python=3.9 -y
        if errorlevel 1 (
            echo ❌ 环境创建失败
            pause
            exit /b 1
        )
        echo ✅ agentclass环境创建成功
    ) else (
        echo 取消创建环境
        pause
        exit /b 0
    )
) else (
    echo ✅ agentclass环境已存在
)

echo.
echo 🔄 激活agentclass环境...
call conda activate agentclass
if errorlevel 1 (
    echo ❌ 环境激活失败
    pause
    exit /b 1
)

echo ✅ 环境激活成功
echo 📍 当前环境: %CONDA_DEFAULT_ENV%

echo.
echo 📦 安装依赖包...
pip install gradio plotly psutil python-dateutil
if errorlevel 1 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)

echo ✅ 依赖安装完成

echo.
echo 🎉 agentclass环境配置完成！
echo.
echo 💡 使用说明:
echo    1. 运行 conda activate agentclass
echo    2. 运行 start.bat 启动系统
echo.

pause