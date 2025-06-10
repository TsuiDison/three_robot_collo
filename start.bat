@echo off
chcp 65001 >nul
echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                   🎯 旅行规划仿真系统                            ║
echo ║                                                                  ║
echo ║                  Windows 一键启动脚本                             ║
echo ║                                                                  ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

echo 🐍 检查Python环境...

REM 检查是否在agentclass环境中
if defined CONDA_DEFAULT_ENV (
    if "%CONDA_DEFAULT_ENV%"=="agentclass" (
        echo ✅ 已在agentclass环境中
        goto :run_program
    ) else (
        echo 当前环境: %CONDA_DEFAULT_ENV%
        echo 尝试切换到agentclass环境...
    )
) else (
    echo 未检测到conda环境
)

REM 尝试激活agentclass环境
echo 🔄 激活agentclass环境...
call conda activate agentclass 2>nul
if errorlevel 1 (
    echo ❌ 无法激活agentclass环境
    echo.
    echo 💡 请先创建agentclass环境:
    echo    conda create -n agentclass python=3.9 -y
    echo    conda activate agentclass
    echo.
    echo 或者使用现有Python环境:
    python --version >nul 2>&1
    if errorlevel 1 (
        echo ❌ Python未安装或未添加到PATH
        echo 请先安装Python 3.8或更高版本
        echo 下载地址: https://www.python.org/downloads/
        pause
        exit /b 1
    ) else (
        echo ✅ 使用系统Python环境
        goto :run_program
    )
) else (
    echo ✅ agentclass环境已激活
)

:run_program
echo.
echo 📍 当前Python环境:
python --version
echo.
echo 🚀 启动安装程序...
python install_and_run.py

pause