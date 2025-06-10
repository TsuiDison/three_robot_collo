#!/usr/bin/env python3
"""
旅行规划仿真系统 - 修复版启动程序
解决 Gradio 版本兼容性问题
"""
import sys
import os
import logging
from pathlib import Path

# 添加 src 目录到 Python 路径
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# 配置日志
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

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
        logger.info(f"✅ Gradio available - version {gr.__version__}")
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

def create_simple_interface():
    """创建简化的 Gradio 界面"""
    import gradio as gr
    
    # 简单的仿真函数
    def run_simulation(agent_count, budget, destination, max_steps):
        """运行简单仿真"""
        try:
            # 导入核心模块
            from src.agent.travel_agent import TravelAgent
            from src.environment.travel_environment import TravelEnvironment
            
            # 初始化环境
            environment = TravelEnvironment()
            environment.reset({"location": destination.lower()})
            
            # 创建代理
            agents = []
            for i in range(int(agent_count)):
                agent = TravelAgent(name=f"旅行者{i+1}")
                agent.state.resources['budget'] = float(budget)
                agents.append(agent)
            
            # 运行仿真
            results = [f"🚀 启动仿真 - {agent_count}个代理在{destination}"]
            results.append(f"💰 初始预算: {budget} 元")
            results.append(f"📊 最大步数: {max_steps}")
            results.append("")
            
            for step in range(int(max_steps)):
                results.append(f"=== 步骤 {step+1} ===")
                
                for agent in agents:
                    # 代理感知环境
                    perception = agent.perceive(environment.get_state())
                    
                    # 代理决策
                    action = agent.decide(perception)
                    
                    # 执行动作
                    result = environment.execute_action(action)
                    
                    results.append(f"  {agent.name}: {result.get('description', '进行活动')}")
                
                # 更新环境
                environment.step()
                results.append("")
            
            results.append("✅ 仿真完成!")
            
            # 计算统计信息
            avg_satisfaction = sum(agent.state.resources.get('satisfaction', 50) for agent in agents) / len(agents)
            avg_budget_remaining = sum(agent.state.resources.get('budget', budget) for agent in agents) / len(agents)
            
            results.append(f"📈 平均满意度: {avg_satisfaction:.1f}%")
            results.append(f"💵 平均剩余预算: {avg_budget_remaining:.1f} 元")
            
            return "\n".join(results)
            
        except Exception as e:
            return f"❌ 仿真错误: {str(e)}\n\n请检查系统配置或尝试控制台版本: python simple_run.py"
    
    # 创建界面 - 使用兼容的参数
    with gr.Blocks(title="🎯 旅行仿真系统 - 修复版") as demo:
        gr.Markdown("# 🎯 旅行规划仿真系统")
        gr.Markdown("### Agent-Environment 架构 | Gradio 兼容版")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("## ⚙️ 仿真配置")
                
                agent_count = gr.Slider(
                    minimum=1,
                    maximum=5,
                    value=3,
                    step=1,
                    label="代理数量"
                )
                
                budget = gr.Number(
                    value=1000,
                    label="初始预算 (元)"
                )
                
                destination = gr.Dropdown(
                    choices=["巴黎", "东京", "巴厘岛", "苏黎世"],
                    value="巴黎",
                    label="目的地"
                )
                
                max_steps = gr.Slider(
                    minimum=5,
                    maximum=20,
                    value=10,
                    step=1,
                    label="仿真步数"
                )
                
                run_btn = gr.Button("🚀 开始仿真", variant="primary")
                
                gr.Markdown("### 📚 使用说明")
                gr.Markdown("""
                1. 选择代理数量和预算
                2. 选择旅行目的地
                3. 设置仿真步数
                4. 点击开始仿真
                
                **💡 提示**: 如果遇到问题，可以尝试控制台版本: `python simple_run.py`
                """)
            
            with gr.Column():
                gr.Markdown("## 📊 仿真结果")
                
                output = gr.Textbox(
                    label="仿真日志",
                    lines=25,
                    max_lines=30,
                    value="等待仿真开始...\n\n配置参数后点击「开始仿真」按钮",
                    interactive=False
                )
        
        # 绑定事件
        run_btn.click(
            fn=run_simulation,
            inputs=[agent_count, budget, destination, max_steps],
            outputs=output
        )
        
        # 添加示例
        gr.Examples(
            examples=[
                [3, 1000, "巴黎", 10],
                [2, 800, "东京", 15],
                [4, 1200, "巴厘岛", 8],
                [1, 600, "苏黎世", 12]
            ],
            inputs=[agent_count, budget, destination, max_steps],
            outputs=output,
            fn=run_simulation
        )
    
    return demo

def launch_web_interface():
    """启动 Web 界面"""
    logger.info("🚀 启动旅行仿真系统 - 修复版")
    
    # 检查依赖
    features, missing = check_dependencies()
    
    if not features['gradio']:
        logger.error("Gradio is required for web interface")
        print("❌ Gradio 未安装")
        print("请运行: pip install gradio")
        print("或使用控制台版本: python simple_run.py")
        return False
    
    try:
        # 创建界面
        demo = create_simple_interface()
        
        print("🌐 启动 Web 界面...")
        print("📊 访问地址: http://127.0.0.1:7899")
        print("=" * 60)
        
        # 兼容不同版本的 Gradio 启动参数
        launch_kwargs = {
            "server_name": "127.0.0.1",
            "server_port": 7899,
            "share": False
        }
        
        # 尝试添加可选参数
        import gradio as gr
        try:
            demo.launch(**launch_kwargs, show_error=True)
        except TypeError:
            # 如果有不支持的参数，使用基础参数
            demo.launch(**launch_kwargs)
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to launch web interface: {e}")
        print(f"❌ Web界面启动失败: {e}")
        print("\n💡 建议:")
        print("1. 检查端口7899是否被占用")
        print("2. 尝试控制台版本: python simple_run.py")
        print("3. 检查Gradio版本: pip install gradio==4.44.0")
        return False

def launch_console_interface():
    """启动控制台界面"""
    logger.info("🎯 启动控制台模式")
    
    try:
        from simple_run import main
        main()
        return True
    except Exception as e:
        logger.error(f"Failed to launch console interface: {e}")
        print(f"❌ 控制台启动失败: {e}")
        return False

def show_startup_banner():
    """显示启动横幅"""
    banner = """
    ╔══════════════════════════════════════════════════════════════════╗
    ║                   🎯 旅行规划仿真系统                            ║
    ║                                                                  ║
    ║            修复版 - 解决 Gradio 兼容性问题                        ║
    ║                                                                  ║
    ║  🤖 智能代理决策仿真                                              ║
    ║  🌍 动态环境模拟                                                  ║
    ║  📊 实时监控与分析                                                ║
    ║  🔧 兼容多版本 Gradio                                             ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def main():
    """主函数"""
    show_startup_banner()
    
    # 创建必要的目录
    for dir_name in ["logs", "data", "exports"]:
        Path(dir_name).mkdir(exist_ok=True)
    
    # 检查依赖
    features, missing = check_dependencies()
    
    # 选择启动模式
    if features['gradio']:
        print("🌐 启动 Web 界面模式...")
        print("📊 访问地址: http://127.0.0.1:7899")
        print("=" * 60)
        
        try:
            launch_web_interface()
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