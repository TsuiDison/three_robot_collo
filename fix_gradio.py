"""
Gradio 版本检查和修复工具
"""
import subprocess
import sys

def check_gradio_version():
    """检查 Gradio 版本"""
    try:
        import gradio as gr
        version = gr.__version__
        print(f"当前 Gradio 版本: {version}")
        
        # 检查版本兼容性
        major_version = int(version.split('.')[0])
        if major_version >= 4:
            print("✅ Gradio 4.x 版本 - 需要移除 enable_queue 参数")
            return "v4"
        else:
            print("✅ Gradio 3.x 版本 - 支持 enable_queue 参数")
            return "v3"
            
    except ImportError:
        print("❌ Gradio 未安装")
        return None

def fix_gradio_compatibility():
    """修复 Gradio 兼容性"""
    version = check_gradio_version()
    
    if version is None:
        print("请先安装 Gradio: pip install gradio")
        return False
    
    if version == "v4":
        print("🔧 检测到 Gradio 4.x，应用兼容性修复...")
        
        # 建议降级到稳定版本
        print("💡 建议使用稳定版本:")
        choice = input("是否安装 Gradio 4.44.0 (稳定版)? [y/n]: ").strip().lower()
        
        if choice in ['y', 'yes']:
            try:
                print("📦 安装 Gradio 4.44.0...")
                subprocess.run([
                    sys.executable, "-m", "pip", "install", 
                    "gradio==4.44.0", "--upgrade"
                ], check=True)
                print("✅ Gradio 安装完成")
                return True
            except subprocess.CalledProcessError:
                print("❌ 安装失败")
                return False
    
    return True

def main():
    """主函数"""
    print("🔧 Gradio 兼容性检查工具")
    print("=" * 40)
    
    if fix_gradio_compatibility():
        print("\n✅ 兼容性检查完成")
        print("🚀 现在可以启动系统了:")
        print("   python quick_start.py")
    else:
        print("\n❌ 修复失败")
        print("💡 建议使用控制台版本:")
        print("   python simple_run.py")

if __name__ == "__main__":
    main()