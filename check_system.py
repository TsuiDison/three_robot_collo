"""
快速检查工具 - 验证系统是否可以正常运行
"""
import sys
import subprocess
import importlib

def check_system():
    """检查系统状态"""
    print("🔍 系统状态检查")
    print("=" * 50)
    
    # Python版本检查
    version = sys.version_info
    print(f"Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python版本过低，需要3.8+")
        return False
    else:
        print("✅ Python版本符合要求")
    
    # 依赖检查
    dependencies = {
        'gradio': '必需 - Web界面框架',
        'plotly': '可选 - 图表可视化',
        'psutil': '可选 - 性能监控',
        'dateutil': '可选 - 日期处理'
    }
    
    print("\n📦 依赖检查:")
    available = []
    missing = []
    
    for dep, desc in dependencies.items():
        try:
            importlib.import_module(dep)
            print(f"✅ {dep} - {desc}")
            available.append(dep)
        except ImportError:
            print(f"❌ {dep} - {desc}")
            missing.append(dep)
    
    # 给出建议
    print(f"\n📊 检查结果:")
    print(f"可用模块: {len(available)}/{len(dependencies)}")
    
    if 'gradio' in available:
        print("✅ 可以运行Web界面版本")
        print("推荐命令: python main_browser_use.py")
    else:
        print("⚠️  只能运行控制台版本")
        print("推荐命令: python simple_run.py")
        
        if 'gradio' in missing:
            print("\n💡 要启用Web界面，请运行:")
            print("   pip install gradio")
    
    if missing:
        print(f"\n🔧 安装缺失依赖:")
        print("   pip install " + " ".join(missing))
        print("   或使用国内镜像:")
        print("   pip install " + " ".join(missing) + " -i https://pypi.tuna.tsinghua.edu.cn/simple/")
    
    return True

def quick_test():
    """快速功能测试"""
    print("\n🧪 快速功能测试:")
    
    try:
        # 测试代理创建
        from src.agent.travel_agent import TravelAgent
        agent = TravelAgent("测试代理")
        print("✅ 代理模块正常")
        
        # 测试环境创建
        from src.environment.travel_environment import TravelEnvironment
        env = TravelEnvironment()
        print("✅ 环境模块正常")
        
        # 测试仿真引擎
        from src.simulation.simulation_engine import SimulationEngine, SimulationConfig
        config = SimulationConfig(max_steps=1)
        sim = SimulationEngine(config)
        print("✅ 仿真引擎正常")
        
        print("\n🎉 核心功能测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ 功能测试失败: {e}")
        return False

def main():
    """主检查流程"""
    print("🎯 旅行仿真系统 - 系统检查工具")
    print("=" * 60)
    
    if not check_system():
        print("\n❌ 系统检查失败")
        return
    
    if not quick_test():
        print("\n❌ 功能测试失败")
        return
    
    print("\n✅ 系统检查完成，一切正常!")
    print("\n🚀 启动建议:")
    print("1. 双击 start.bat (Windows) 或运行 ./start.sh (Linux/Mac)")
    print("2. 或运行 python install_and_run.py")
    print("3. 或直接运行 python simple_run.py (控制台版本)")

if __name__ == "__main__":
    main()