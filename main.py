"""
基于 Agent-Environment 架构的旅行规划仿真系统
主程序入口
"""
import gradio as gr
import asyncio
import logging
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.webui.interface_manager import InterfaceManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """主程序入口"""
    print("=" * 60)
    print("🎯 旅行规划仿真系统 - Agent-Environment 架构")
    print("=" * 60)
    print("🏗️ 系统架构: Agent-Environment")
    print("🤖 核心特性:")
    print("   • 智能代理决策仿真")
    print("   • 动态环境交互模拟")
    print("   • 实时状态可视化")
    print("   • 多代理协作仿真")
    print("   • 完全本地部署")
    print("=" * 60)
    
    try:
        # 创建界面管理器并启动
        interface_manager = InterfaceManager()
        demo = interface_manager.create_interface()
        
        print("🚀 系统启动成功!")
        print("📱 访问地址: http://127.0.0.1:7899")
        print("=" * 60)
        
        demo.launch(
            server_name="127.0.0.1",
            server_port=7899,
            share=False,
            debug=False,
            show_error=True
        )
        
    except Exception as e:
        logger.error(f"系统启动失败: {e}")
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    main()