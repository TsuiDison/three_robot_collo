#!/usr/bin/env python3
"""
一键安装和启动脚本
自动检查环境、安装依赖并启动系统
"""
import sys
import subprocess
import os
import platform
from pathlib import Path

def print_banner():
    """显示欢迎横幅"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                   🎯 旅行规划仿真系统                            ║
║                                                                  ║
║              一键安装和启动脚本 v1.0                              ║
║                                                                  ║
║  🔧 自动环境检查                                                  ║
║  📦 智能依赖安装                                                  ║
║  🚀 快速系统启动                                                  ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)

def check_python_version():
    """检查Python版本"""
    print("🐍 检查Python版本...")
    version = sys.version_info
    
    # 检查是否在conda环境中
    conda_env = os.environ.get('CONDA_DEFAULT_ENV')
    if conda_env:
        print(f"🌿 当前conda环境: {conda_env}")
        if conda_env == "agentclass":
            print("✅ 正在agentclass环境中运行")
        else:
            print("💡 建议在agentclass环境中运行")
    else:
        print("📦 使用系统Python环境")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python版本过低: {version.major}.{version.minor}")
        print("   需要Python 3.8或更高版本")
        return False
    
    print(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
    return True

def check_pip():
    """检查pip是否可用"""
    print("📦 检查pip...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
        print("✅ pip可用")
        return True
    except subprocess.CalledProcessError:
        print("❌ pip不可用")
        return False

def get_mirror_choice():
    """选择pip镜像"""
    print("\n🌍 选择pip镜像源:")
    print("1. 默认源 (国外)")
    print("2. 清华源 (推荐)")
    print("3. 阿里源")
    print("4. 中科大源")
    
    while True:
        choice = input("请选择 (1-4) [默认:2]: ").strip()
        if not choice:
            choice = "2"
        
        mirrors = {
            "1": "",
            "2": "https://pypi.tuna.tsinghua.edu.cn/simple/",
            "3": "https://mirrors.aliyun.com/pypi/simple/",
            "4": "https://pypi.mirrors.ustc.edu.cn/simple/"
        }
        
        if choice in mirrors:
            return mirrors[choice]
        
        print("❌ 无效选择，请重新输入")

def install_package(package, mirror_url="", timeout=300):
    """安装单个包"""
    cmd = [sys.executable, "-m", "pip", "install", package, "--timeout", str(timeout)]
    
    if mirror_url:
        cmd.extend(["-i", mirror_url])
    
    try:
        print(f"📦 正在安装 {package}...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {package} 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {package} 安装失败: {e.stderr}")
        return False

def install_dependencies():
    """安装依赖"""
    print("\n📦 开始安装依赖...")
    
    # 选择镜像源
    mirror_url = get_mirror_choice()
    
    # 基础依赖（必需）
    essential_packages = [
        "gradio>=4.0.0"
    ]
    
    # 可选依赖
    optional_packages = [
        ("plotly>=5.0.0", "图表可视化"),
        ("psutil>=5.9.0", "性能监控"),
        ("python-dateutil>=2.8.0", "日期处理")
    ]
    
    print("🔧 安装基础依赖...")
    for package in essential_packages:
        if not install_package(package, mirror_url):
            print(f"❌ 基础依赖 {package} 安装失败")
            return False
    
    print("\n🎨 安装可选依赖...")
    failed_optional = []
    
    for package, description in optional_packages:
        print(f"安装 {description}...")
        if not install_package(package, mirror_url, timeout=600):
            failed_optional.append((package, description))
    
    if failed_optional:
        print("\n⚠️  以下可选依赖安装失败（不影响基本功能）:")
        for package, description in failed_optional:
            print(f"   - {package} ({description})")
    
    print("\n✅ 依赖安装完成!")
    return True

def create_directories():
    """创建必要的目录"""
    print("📁 创建目录结构...")
    
    directories = [
        "logs",
        "data", 
        "data/simulations",
        "data/exports",
        "data/backups"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"   📂 {dir_path}")
    
    print("✅ 目录结构创建完成")

def test_imports():
    """测试关键模块导入"""
    print("\n🧪 测试模块导入...")
    
    test_modules = [
        ("gradio", "Web界面框架"),
        ("plotly.graph_objects", "图表库", True),
        ("psutil", "性能监控", True),
        ("dateutil", "日期处理", True)
    ]
    
    available_features = []
    
    for module_info in test_modules:
        module_name = module_info[0]
        description = module_info[1]
        is_optional = len(module_info) > 2 and module_info[2]
        
        try:
            __import__(module_name)
            print(f"✅ {description} - 可用")
            available_features.append(module_name)
        except ImportError:
            if is_optional:
                print(f"⚠️  {description} - 不可用 (可选)")
            else:
                print(f"❌ {description} - 不可用 (必需)")
                return False, []
    
    return True, available_features

def choose_startup_mode(available_features):
    """选择启动模式"""
    print("\n🚀 选择启动模式:")
    
    modes = []
    
    if "gradio" in available_features:
        modes.append(("browser", "🌐 Web界面模式 (推荐)", "main_browser_use.py"))
        modes.append(("web", "🎮 经典Web模式", "main.py"))
    
    modes.append(("console", "💻 控制台模式 (无需依赖)", "simple_run.py"))
    
    for i, (mode_id, description, _) in enumerate(modes, 1):
        print(f"{i}. {description}")
    
    while True:
        try:
            choice = input(f"\n请选择 (1-{len(modes)}) [默认:1]: ").strip()
            if not choice:
                choice = "1"
            
            index = int(choice) - 1
            if 0 <= index < len(modes):
                return modes[index]
            else:
                print("❌ 无效选择，请重新输入")
        except ValueError:
            print("❌ 请输入数字")

def start_system(script_name):
    """启动系统"""
    print(f"\n🚀 启动系统: {script_name}")
    
    if not Path(script_name).exists():
        print(f"❌ 启动脚本不存在: {script_name}")
        return False
    
    try:
        # 使用当前Python解释器启动
        subprocess.Popen([sys.executable, script_name])
        print(f"✅ 系统启动成功!")
        
        if "main" in script_name and "browser" in script_name:
            print("🌐 Web界面地址: http://127.0.0.1:7899")
        elif "main.py" in script_name:
            print("🌐 Web界面地址: http://127.0.0.1:7899")
        
        return True
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False

def main():
    """主函数"""
    print_banner()
    
    # 检查Python版本
    if not check_python_version():
        input("按回车键退出...")
        return
    
    # 检查pip
    if not check_pip():
        print("请先安装pip")
        input("按回车键退出...")
        return
    
    # 询问是否需要安装依赖
    print("\n❓ 是否需要安装/更新依赖?")
    install_deps = input("输入 y 安装依赖，n 跳过 [y/n]: ").strip().lower()
    
    if install_deps in ['y', 'yes', '']:
        if not install_dependencies():
            print("❌ 依赖安装失败")
            fallback = input("是否尝试控制台模式? [y/n]: ").strip().lower()
            if fallback in ['y', 'yes']:
                start_system("simple_run.py")
            return
    
    # 创建目录
    create_directories()
    
    # 测试导入
    success, available_features = test_imports()
    if not success:
        print("❌ 关键模块不可用，尝试重新安装依赖")
        return
    
    # 选择启动模式
    mode_id, description, script_name = choose_startup_mode(available_features)
    
    print(f"\n🎯 选择的模式: {description}")
    
    # 启动系统
    if start_system(script_name):
        print("\n🎉 启动完成!")
        print("💡 提示: 可以直接运行 python simple_run.py 体验无依赖版本")
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 用户中断，退出安装程序")
    except Exception as e:
        print(f"\n❌ 安装程序出错: {e}")
        input("按回车键退出...")