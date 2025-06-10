"""
主程序入口 - 基于 browser-use 架构的启动程序
"""
import asyncio
import logging
import sys
from pathlib import Path

# 设置项目根目录路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/travel_simulation.log', mode='a', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

def check_dependencies():
    """检查依赖并提供降级选项"""
    missing_deps = []
    available_features = {
        'gradio': False,
        'plotly': False,
        'performance_monitoring': False
    }
    
    try:
        import gradio as gr
        available_features['gradio'] = True
        logger.info("✅ Gradio available - Web UI enabled")
    except ImportError:
        missing_deps.append('gradio')
        logger.warning("❌ Gradio not available - Web UI disabled")
    
    try:
        import plotly.graph_objects as go
        available_features['plotly'] = True
        logger.info("✅ Plotly available - Advanced charts enabled")
    except ImportError:
        missing_deps.append('plotly')
        logger.warning("❌ Plotly not available - Basic charts only")
    
    try:
        import psutil
        available_features['performance_monitoring'] = True
        logger.info("✅ Psutil available - Performance monitoring enabled")
    except ImportError:
        missing_deps.append('psutil')
        logger.warning("❌ Psutil not available - Performance monitoring disabled")
    
    return available_features, missing_deps

def create_interface_manager():
    """创建界面管理器"""
    try:
        from src.webui.interface_manager import InterfaceManager
        return InterfaceManager()
    except Exception as e:
        logger.error(f"Failed to create InterfaceManager: {e}")
        return None

async def launch_web_interface():
    """启动 Web 界面 - browser-use 风格"""
    logger.info("🚀 启动旅行仿真系统 - Browser-Use 架构")
    
    # 检查依赖
    features, missing = check_dependencies()
    
    if not features['gradio']:
        logger.error("Gradio is required for web interface")
        print("请安装 Gradio: pip install gradio")
        return False
    
    try:
        # 创建界面管理器
        interface_manager = create_interface_manager()
        if not interface_manager:
            raise Exception("Failed to create interface manager")
        
        # 创建主界面
        demo = interface_manager.create_interface()
          # 启动界面 - 修复 Gradio 版本兼容性
        try:
            demo.launch(
                server_name="127.0.0.1",
                server_port=7899,
                share=False,
                debug=False,
                show_error=True
            )
        except TypeError as e:
            if "unexpected keyword argument" in str(e):
                # 兼容旧版本 Gradio
                demo.launch(
                    server_name="127.0.0.1",
                    server_port=7899,
                    share=False
                )
            else:
                raise
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to launch web interface: {e}")
        return False

def launch_console_interface():
    """启动控制台界面"""
    logger.info("🎯 启动控制台模式")
    
    try:
        from simple_run import main
        asyncio.run(main())
        return True
    except Exception as e:
        logger.error(f"Failed to launch console interface: {e}")
        return False

def show_startup_banner():
    """显示启动横幅"""
    banner = """
    ╔══════════════════════════════════════════════════════════════════╗
    ║                   🎯 旅行规划仿真系统                            ║
    ║                                                                  ║
    ║           基于 Agent-Environment 架构 | Browser-Use 风格          ║
    ║                                                                  ║
    ║  🤖 智能代理决策仿真                                              ║
    ║  🌍 动态环境模拟                                                  ║
    ║  📊 实时监控与分析                                                ║
    ║  🎮 交互式 Web 界面                                               ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def main():
    """主函数"""
    show_startup_banner()
    
    # 创建必要的目录
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    Path("exports").mkdir(exist_ok=True)
    
    # 检查依赖
    features, missing = check_dependencies()
    
    # 选择启动模式
    if features['gradio']:
        print("🌐 启动 Web 界面模式...")
        print(f"📊 访问地址: http://127.0.0.1:7899")
        print("=" * 60)
        
        try:
            asyncio.run(launch_web_interface())
        except KeyboardInterrupt:
            print("\n👋 用户中断，程序退出")
        except Exception as e:
            print(f"\n❌ Web 界面启动失败: {e}")
            print("🔄 尝试启动控制台模式...")
            launch_console_interface()
    else:
        print("💻 启动控制台模式...")
        print("=" * 60)
        launch_console_interface()

if __name__ == "__main__":
    main()