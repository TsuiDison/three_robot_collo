"""
环境管理工具 - 自动创建和配置agentclass环境
"""
import subprocess
import sys
import os

def create_agentclass_env():
    """创建agentclass conda环境"""
    print("🌿 创建agentclass环境...")
    
    try:
        # 检查conda是否可用
        subprocess.run(["conda", "--version"], check=True, capture_output=True)
        print("✅ conda可用")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ conda不可用，请先安装Anaconda或Miniconda")
        return False
    
    try:
        # 创建环境
        print("📦 创建agentclass环境 (Python 3.9)...")
        subprocess.run([
            "conda", "create", "-n", "agentclass", 
            "python=3.9", "-y"
        ], check=True)
        
        print("✅ agentclass环境创建成功")
        
        # 给出后续指导
        print("\n💡 环境创建完成！请执行以下步骤:")
        if os.name == 'nt':  # Windows
            print("   conda activate agentclass")
            print("   start.bat")
        else:  # Linux/Mac
            print("   conda activate agentclass")
            print("   ./start.sh")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 环境创建失败: {e}")
        return False

def check_agentclass_env():
    """检查agentclass环境是否存在"""
    try:
        result = subprocess.run([
            "conda", "info", "--envs"
        ], capture_output=True, text=True, check=True)
        
        if "agentclass" in result.stdout:
            print("✅ agentclass环境已存在")
            return True
        else:
            print("❌ agentclass环境不存在")
            return False
            
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_in_agentclass():
    """在agentclass环境中安装依赖"""
    print("📦 在agentclass环境中安装依赖...")
    
    # 获取agentclass环境的Python路径
    try:
        result = subprocess.run([
            "conda", "run", "-n", "agentclass", 
            "python", "-c", "import sys; print(sys.executable)"
        ], capture_output=True, text=True, check=True)
        
        python_path = result.stdout.strip()
        print(f"📍 agentclass Python路径: {python_path}")
        
        # 使用agentclass环境的pip安装
        packages = ["gradio", "plotly", "psutil", "python-dateutil"]
        
        for package in packages:
            print(f"📦 安装 {package}...")
            subprocess.run([
                "conda", "run", "-n", "agentclass",
                "pip", "install", package
            ], check=True)
        
        print("✅ 依赖安装完成")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 安装失败: {e}")
        return False

def main():
    """主函数"""
    print("🌿 Conda环境管理工具")
    print("=" * 50)
    
    if not check_agentclass_env():
        choice = input("agentclass环境不存在，是否创建? [y/n]: ").strip().lower()
        if choice in ['y', 'yes']:
            if create_agentclass_env():
                print("✅ 环境创建成功")
            else:
                print("❌ 环境创建失败")
        return
    
    choice = input("是否在agentclass环境中安装依赖? [y/n]: ").strip().lower()
    if choice in ['y', 'yes']:
        install_in_agentclass()

if __name__ == "__main__":
    main()