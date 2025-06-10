#!/usr/bin/env python3
"""
快速修复版启动脚本 - 解决 Gradio 兼容性问题
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
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_simple_gradio_interface():
    """创建简单的 Gradio 界面（兼容所有版本）"""
    try:
        import gradio as gr
        logger.info(f"使用 Gradio 版本: {gr.__version__}")
    except ImportError:
        logger.error("Gradio 未安装")
        return None
    
    # 简单的仿真函数
    def run_simulation(agent_count, budget, location, steps):
        """运行简单仿真"""
        try:
            results = []
            results.append(f"🚀 开始仿真 - {agent_count}个代理")
            results.append(f"📍 地点: {location}")
            results.append(f"💰 预算: {budget}")
            results.append(f"📊 步数: {steps}")
            results.append("")
            
            for i in range(int(steps)):
                results.append(f"步骤 {i+1}: 代理正在探索环境...")
                if i % 3 == 0:
                    results.append(f"  - 代理1 预订了活动")
                elif i % 3 == 1:
                    results.append(f"  - 代理2 在休息恢复体力")
                else:
                    results.append(f"  - 代理3 在探索新地点")
            
            results.append("")
            results.append("✅ 仿真完成!")
            results.append(f"📈 平均满意度: 78%")
            results.append(f"💵 剩余预算: {int(budget) - 150}")
            
            return "\n".join(results)
            
        except Exception as e:
            return f"❌ 仿真错误: {str(e)}"
    
    # 创建界面
    with gr.Blocks(title="🎯 旅行仿真系统") as demo:
        gr.Markdown("# 🎯 旅行规划仿真系统")
        gr.Markdown("### Browser-Use 架构风格 | 快速体验版")
        
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
                    label="初始预算"
                )
                
                location = gr.Dropdown(
                    choices=["巴黎", "东京", "巴厘岛", "苏黎世"],
                    value="巴黎",
                    label="目的地"
                )
                
                steps = gr.Slider(
                    minimum=5,
                    maximum=20,
                    value=10,
                    step=1,
                    label="仿真步数"
                )
                
                run_btn = gr.Button("🚀 开始仿真", variant="primary")
                
            with gr.Column():
                gr.Markdown("## 📊 仿真结果")
                
                output = gr.Textbox(
                    label="实时日志",
                    lines=20,
                    max_lines=25,
                    value="等待仿真开始...",
                    interactive=False
                )
        
        # 绑定事件
        run_btn.click(
            fn=run_simulation,
            inputs=[agent_count, budget, location, steps],
            outputs=output
        )
        
        # 示例按钮
        gr.Examples(
            examples=[
                [3, 1000, "巴黎", 10],
                [2, 800, "东京", 15],
                [4, 1200, "巴厘岛", 12]
            ],
            inputs=[agent_count, budget, location, steps],
            outputs=output,
            fn=run_simulation
        )
    
    return demo

def main():
    """主函数"""
    print("🎯 启动旅行仿真系统 - 快速修复版")
    print("=" * 60)
    
    try:
        # 创建界面
        demo = create_simple_gradio_interface()
        if not demo:
            print("❌ 无法创建界面，请检查 Gradio 安装")
            return
        
        print("🚀 启动 Web 界面...")
        print("📊 访问地址: http://127.0.0.1:7899")
        print("=" * 60)
        
        # 兼容不同版本的 Gradio
        try:
            demo.launch(
                server_name="127.0.0.1",
                server_port=7899,
                share=False
            )
        except Exception as e:
            print(f"❌ 启动失败: {e}")
            print("\n💡 尝试其他启动方式:")
            print("1. python simple_run.py (控制台版本)")
            print("2. 检查 7899 端口是否被占用")
            print("3. 尝试重新安装 Gradio: pip install gradio==4.44.0")
            
    except KeyboardInterrupt:
        print("\n👋 用户中断，程序退出")
    except Exception as e:
        print(f"❌ 程序出错: {e}")
        print("\n💡 建议:")
        print("1. 运行 python simple_run.py")
        print("2. 检查依赖安装: python check_system.py")

if __name__ == "__main__":
    main()