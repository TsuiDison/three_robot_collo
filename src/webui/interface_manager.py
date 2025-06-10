"""
界面管理器 - 基于 browser-use web-ui 架构的改进版本
参考 browser-use 的组件管理和状态管理模式
"""
import gradio as gr
import logging
import asyncio
import json
import uuid
from typing import Dict, Any, List, Optional, Tuple, Callable
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from src.simulation.simulation_engine import SimulationEngine, SimulationConfig, SimulationStatus
from src.agent.travel_agent import TravelAgent
from src.environment.travel_environment import TravelEnvironment
from src.webui.components.simulation_tab import SimulationTab
from src.webui.components.monitoring_tab import MonitoringTab
from src.webui.components.agent_tab import AgentTab
from src.webui.state_manager import StateManager, SessionState

logger = logging.getLogger(__name__)

class InterfaceManager:
    """界面管理器"""
    
    def __init__(self):
        # 仿真组件
        self.simulation_engine = None
        self.environment = None
        
        # UI状态
        self.simulation_running = False
        self.update_task = None
        
        # 实时数据
        self.real_time_data = {
            'simulation_status': 'stopped',
            'current_step': 0,
            'agents_status': {},
            'environment_status': {},
            'metrics': {}
        }
        
        logger.info("InterfaceManager 初始化完成")
    
    def create_interface(self) -> gr.Blocks:
        """创建主界面"""
        with gr.Blocks(
            title="旅行规划仿真系统 - Agent-Environment 架构",
            theme=gr.themes.Soft(),
            css=self._get_custom_css()
        ) as demo:
            
            # 标题区域
            self._create_header()
            
            # 主要内容区域
            with gr.Tabs() as main_tabs:
                
                # 仿真控制台
                with gr.TabItem("🎮 仿真控制台"):
                    simulation_components = self._create_simulation_console()
                
                # 实时监控
                with gr.TabItem("📊 实时监控"):
                    monitoring_components = self._create_monitoring_dashboard()
                
                # 代理管理
                with gr.TabItem("🤖 代理管理"):
                    agent_components = self._create_agent_management()
                
                # 环境设置
                with gr.TabItem("🌍 环境设置"):
                    environment_components = self._create_environment_settings()
                
                # 数据分析
                with gr.TabItem("📈 数据分析"):
                    analysis_components = self._create_data_analysis()
            
            # 设置事件处理
            self._setup_event_handlers(
                simulation_components,
                monitoring_components,
                agent_components,
                environment_components,
                analysis_components
            )
        
        return demo
    
    def _get_custom_css(self) -> str:
        """获取自定义CSS样式"""
        return """
        .main-header {
            text-align: center;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .status-card {
            border: 2px solid #e1e5e9;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            background: #f8f9fa;
        }
        .metric-card {
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 12px;
            margin: 5px;
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .agent-card {
            border: 1px solid #28a745;
            border-radius: 8px;
            padding: 10px;
            margin: 5px 0;
            background: #f8fff9;
        }
        .environment-info {
            background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
        }
        """
    
    def _create_header(self):
        """创建页面头部"""
        gr.HTML("""
        <div class="main-header">
            <h1>🎯 旅行规划仿真系统</h1>
            <h3>基于 Agent-Environment 架构的智能仿真平台</h3>
            <p>模拟智能代理在旅行环境中的决策和交互过程</p>
        </div>
        """)
    
    def _create_simulation_console(self) -> Dict[str, gr.Component]:
        """创建仿真控制台"""
        components = {}
        
        with gr.Row():
            with gr.Column(scale=2):
                gr.Markdown("## 🎮 仿真控制")
                
                # 仿真配置
                with gr.Group():
                    gr.Markdown("### ⚙️ 仿真参数")
                    components['max_steps'] = gr.Number(
                        label="最大步数",
                        value=50,
                        minimum=1,
                        maximum=1000
                    )
                    components['step_interval'] = gr.Slider(
                        label="步骤间隔 (秒)",
                        minimum=0.1,
                        maximum=5.0,
                        value=1.0,
                        step=0.1
                    )
                    components['simulation_speed'] = gr.Slider(
                        label="仿真速度倍数",
                        minimum=0.1,
                        maximum=10.0,
                        value=1.0,
                        step=0.1
                    )
                
                # 代理配置
                with gr.Group():
                    gr.Markdown("### 🤖 代理配置")
                    components['agent_count'] = gr.Number(
                        label="代理数量",
                        value=3,
                        minimum=1,
                        maximum=10
                    )
                    components['agent_budget'] = gr.Number(
                        label="初始预算",
                        value=1000,
                        minimum=100,
                        maximum=5000
                    )
                
                # 控制按钮
                with gr.Row():
                    components['start_btn'] = gr.Button(
                        "🚀 启动仿真",
                        variant="primary",
                        size="lg"
                    )
                    components['pause_btn'] = gr.Button(
                        "⏸️ 暂停",
                        variant="secondary"
                    )
                    components['stop_btn'] = gr.Button(
                        "⏹️ 停止",
                        variant="stop"
                    )
            
            with gr.Column(scale=3):
                gr.Markdown("## 📊 仿真状态")
                
                # 状态显示
                components['status_display'] = gr.HTML(
                    '<div class="status-card">仿真未启动</div>'
                )
                
                # 实时日志
                components['log_display'] = gr.Textbox(
                    label="实时日志",
                    lines=15,
                    max_lines=20,
                    interactive=False,
                    show_copy_button=True
                )
                
                # 清空日志按钮
                components['clear_log_btn'] = gr.Button("🗑️ 清空日志")
        
        return components
    
    def _create_monitoring_dashboard(self) -> Dict[str, gr.Component]:
        """创建监控仪表板"""
        components = {}
        
        with gr.Row():
            # 指标卡片
            with gr.Column(scale=1):
                components['current_step_display'] = gr.HTML(
                    '<div class="metric-card"><h3>0</h3><p>当前步数</p></div>'
                )
            with gr.Column(scale=1):
                components['total_agents_display'] = gr.HTML(
                    '<div class="metric-card"><h3>0</h3><p>活跃代理</p></div>'
                )
            with gr.Column(scale=1):
                components['avg_satisfaction_display'] = gr.HTML(
                    '<div class="metric-card"><h3>0%</h3><p>平均满意度</p></div>'
                )
            with gr.Column(scale=1):
                components['success_rate_display'] = gr.HTML(
                    '<div class="metric-card"><h3>0%</h3><p>成功率</p></div>'
                )
        
        with gr.Row():
            with gr.Column():
                # 实时图表
                components['metrics_plot'] = gr.Plot(
                    label="指标趋势图",
                    value=self._create_empty_plot()
                )
                
                # 自动刷新控制
                with gr.Row():
                    components['auto_refresh'] = gr.Checkbox(
                        label="自动刷新",
                        value=True
                    )
                    components['refresh_interval'] = gr.Slider(
                        label="刷新间隔(秒)",
                        minimum=1,
                        maximum=10,
                        value=2,
                        step=1
                    )
                    components['manual_refresh_btn'] = gr.Button("🔄 手动刷新")
        
        with gr.Row():
            with gr.Column():
                # 代理状态表格
                components['agents_table'] = gr.Dataframe(
                    headers=["代理ID", "状态", "预算", "体力", "满意度", "位置"],
                    label="代理状态总览",
                    interactive=False
                )
            
            with gr.Column():
                # 环境状态
                components['environment_info'] = gr.HTML(
                    '<div class="environment-info">环境信息将在这里显示</div>'
                )
        
        return components
    
    def _create_agent_management(self) -> Dict[str, gr.Component]:
        """创建代理管理界面"""
        components = {}
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("## 🤖 代理详细信息")
                
                # 代理选择器
                components['agent_selector'] = gr.Dropdown(
                    label="选择代理",
                    choices=[],
                    interactive=True
                )
                
                # 代理详细信息
                components['agent_details'] = gr.JSON(
                    label="代理状态详情",
                    value={}
                )
                
                # 代理行为历史
                components['agent_history'] = gr.Dataframe(
                    headers=["时间", "行为类型", "参数", "结果"],
                    label="行为历史",
                    interactive=False
                )
            
            with gr.Column():
                gr.Markdown("## 🎯 代理控制")
                
                # 手动控制（调试用）
                with gr.Group():
                    gr.Markdown("### 手动干预 (调试模式)")
                    components['manual_action_type'] = gr.Dropdown(
                        label="行为类型",
                        choices=["book_activity", "rest", "explore"],
                        value="rest"
                    )
                    components['manual_action_params'] = gr.Textbox(
                        label="参数 (JSON格式)",
                        value='{"duration": 2}',
                        lines=3
                    )
                    components['execute_manual_action'] = gr.Button(
                        "执行手动行为",
                        variant="secondary"
                    )
                
                # 代理统计
                components['agent_statistics'] = gr.HTML(
                    '<div>代理统计信息将在这里显示</div>'
                )
        
        return components
    
    def _create_environment_settings(self) -> Dict[str, gr.Component]:
        """创建环境设置界面"""
        components = {}
        
        with gr.Column():
            gr.Markdown("## 🌍 环境配置")
            
            with gr.Row():
                with gr.Column():
                    # 地点设置
                    components['current_location'] = gr.Dropdown(
                        label="当前地点",
                        choices=["paris", "tokyo", "bali", "zurich"],
                        value="paris"
                    )
                    
                    # 天气设置
                    components['weather_condition'] = gr.Dropdown(
                        label="天气条件",
                        choices=["sunny", "cloudy", "rainy", "snowy"],
                        value="sunny"
                    )
                    
                    components['temperature'] = gr.Slider(
                        label="温度 (°C)",
                        minimum=-10,
                        maximum=40,
                        value=20
                    )
                
                with gr.Column():
                    # 环境参数
                    components['cost_multiplier'] = gr.Slider(
                        label="消费水平倍数",
                        minimum=0.5,
                        maximum=3.0,
                        value=1.0,
                        step=0.1
                    )
                    
                    components['activity_availability'] = gr.Slider(
                        label="活动可用性 (%)",
                        minimum=0,
                        maximum=100,
                        value=80
                    )
                    
                    # 应用环境设置按钮
                    components['apply_env_settings'] = gr.Button(
                        "应用环境设置",
                        variant="primary"
                    )
            
            # 环境状态预览
            components['environment_preview'] = gr.JSON(
                label="环境状态预览",
                value={}
            )
            
            # 可用活动列表
            components['available_activities'] = gr.Dataframe(
                headers=["活动名称", "类型", "费用", "耗时", "满意度"],
                label="可用活动",
                interactive=False
            )
        
        return components
    
    def _create_data_analysis(self) -> Dict[str, gr.Component]:
        """创建数据分析界面"""
        components = {}
        
        with gr.Column():
            gr.Markdown("## 📈 仿真数据分析")
            
            with gr.Row():
                with gr.Column():
                    # 分析选项
                    components['analysis_type'] = gr.Dropdown(
                        label="分析类型",
                        choices=[
                            "满意度趋势",
                            "预算使用情况",
                            "体力变化",
                            "行为分布",
                            "成功率分析"
                        ],
                        value="满意度趋势"
                    )
                    
                    components['time_range'] = gr.Slider(
                        label="时间范围 (最近N步)",
                        minimum=10,
                        maximum=100,
                        value=50
                    )
                    
                    components['generate_analysis'] = gr.Button(
                        "生成分析报告",
                        variant="primary"
                    )
                
                with gr.Column():
                    # 导出选项
                    components['export_format'] = gr.Dropdown(
                        label="导出格式",
                        choices=["JSON", "CSV"],
                        value="JSON"
                    )
                    
                    components['export_data'] = gr.Button(
                        "导出数据",
                        variant="secondary"
                    )
                    
                    components['export_status'] = gr.Textbox(
                        label="导出状态",
                        interactive=False
                    )
            
            # 分析结果
            components['analysis_plot'] = gr.Plot(
                label="分析图表",
                value=self._create_empty_plot()
            )
            
            components['analysis_summary'] = gr.Markdown(
                "分析结果将在这里显示"
            )
            
            # 详细数据表格
            components['detailed_data'] = gr.Dataframe(
                label="详细数据",
                interactive=False,
                wrap=True
            )
        
        return components
    
    def _create_empty_plot(self):
        """创建空图表"""
        import plotly.graph_objects as go
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[], y=[], mode='lines', name='数据'))
        fig.update_layout(
            title="暂无数据",
            xaxis_title="时间步",
            yaxis_title="数值",
            showlegend=True
        )
        return fig
    
    def _setup_event_handlers(self, simulation_components, monitoring_components, 
                            agent_components, environment_components, analysis_components):
        """设置事件处理器"""
        
        # 仿真控制事件
        simulation_components['start_btn'].click(
            fn=self._start_simulation,
            inputs=[
                simulation_components['max_steps'],
                simulation_components['step_interval'],
                simulation_components['simulation_speed'],
                simulation_components['agent_count'],
                simulation_components['agent_budget']
            ],
            outputs=[
                simulation_components['status_display'],
                simulation_components['log_display']
            ]
        )
        
        simulation_components['stop_btn'].click(
            fn=self._stop_simulation,
            outputs=[
                simulation_components['status_display'],
                simulation_components['log_display']
            ]
        )
        
        simulation_components['clear_log_btn'].click(
            fn=lambda: "",
            outputs=[simulation_components['log_display']]
        )
        
        # 监控刷新事件
        monitoring_components['manual_refresh_btn'].click(
            fn=self._refresh_monitoring_data,
            outputs=[
                monitoring_components['current_step_display'],
                monitoring_components['total_agents_display'],
                monitoring_components['avg_satisfaction_display'],
                monitoring_components['success_rate_display'],
                monitoring_components['metrics_plot'],
                monitoring_components['agents_table'],
                monitoring_components['environment_info']
            ]
        )
        
        # 代理管理事件
        agent_components['agent_selector'].change(
            fn=self._load_agent_details,
            inputs=[agent_components['agent_selector']],
            outputs=[
                agent_components['agent_details'],
                agent_components['agent_history'],
                agent_components['agent_statistics']
            ]
        )
        
        # 环境设置事件
        environment_components['apply_env_settings'].click(
            fn=self._apply_environment_settings,
            inputs=[
                environment_components['current_location'],
                environment_components['weather_condition'],
                environment_components['temperature'],
                environment_components['cost_multiplier'],
                environment_components['activity_availability']
            ],
            outputs=[
                environment_components['environment_preview'],
                environment_components['available_activities']
            ]
        )
        
        # 数据分析事件
        analysis_components['generate_analysis'].click(
            fn=self._generate_analysis,
            inputs=[
                analysis_components['analysis_type'],
                analysis_components['time_range']
            ],
            outputs=[
                analysis_components['analysis_plot'],
                analysis_components['analysis_summary'],
                analysis_components['detailed_data']
            ]
        )
    
    # ==================== 事件处理方法 ====================
    
    async def _start_simulation(self, max_steps, step_interval, simulation_speed, 
                               agent_count, agent_budget):
        """启动仿真"""
        try:
            # 创建仿真配置
            config = SimulationConfig(
                max_steps=int(max_steps),
                step_interval=float(step_interval),
                simulation_speed=float(simulation_speed)
            )
            
            # 初始化组件
            self.environment = TravelEnvironment()
            self.simulation_engine = SimulationEngine(config)
            self.simulation_engine.set_environment(self.environment)
            
            # 创建代理
            for i in range(int(agent_count)):
                agent = TravelAgent(name=f"旅行者{i+1}")
                agent.state.resources['budget'] = float(agent_budget)
                self.simulation_engine.add_agent(agent)
            
            # 设置回调
            self.simulation_engine.add_step_callback(self._on_simulation_step)
            self.simulation_engine.add_status_callback(self._on_status_change)
            
            # 启动仿真
            await self.simulation_engine.start_simulation()
            
            status_html = '<div class="status-card" style="background: #d4edda;">✅ 仿真已启动</div>'
            log_message = f"[{datetime.now().strftime('%H:%M:%S')}] 仿真启动成功 - {agent_count}个代理已创建\n"
            
            return status_html, log_message
            
        except Exception as e:
            error_html = f'<div class="status-card" style="background: #f8d7da;">❌ 启动失败: {str(e)}</div>'
            error_log = f"[{datetime.now().strftime('%H:%M:%S')}] 启动失败: {str(e)}\n"
            logger.error(f"启动仿真失败: {e}")
            return error_html, error_log
    
    async def _stop_simulation(self):
        """停止仿真"""
        try:
            if self.simulation_engine:
                await self.simulation_engine.stop_simulation()
            
            status_html = '<div class="status-card" style="background: #fff3cd;">⏹️ 仿真已停止</div>'
            log_message = f"[{datetime.now().strftime('%H:%M:%S')}] 仿真已停止\n"
            
            return status_html, log_message
            
        except Exception as e:
            error_html = f'<div class="status-card" style="background: #f8d7da;">❌ 停止失败: {str(e)}</div>'
            error_log = f"[{datetime.now().strftime('%H:%M:%S')}] 停止失败: {str(e)}\n"
            return error_html, error_log
    
    def _refresh_monitoring_data(self):
        """刷新监控数据"""
        try:
            if not self.simulation_engine:
                return self._get_empty_monitoring_data()
            
            # 获取仿真摘要
            summary = self.simulation_engine.get_simulation_summary()
            metrics = self.simulation_engine.get_latest_metrics()
            
            # 更新指标卡片
            current_step_html = f'<div class="metric-card"><h3>{summary["current_step"]}</h3><p>当前步数</p></div>'
            total_agents_html = f'<div class="metric-card"><h3>{summary["total_agents"]}</h3><p>活跃代理</p></div>'
            
            avg_satisfaction = metrics.get('average_satisfaction', 0)
            satisfaction_html = f'<div class="metric-card"><h3>{avg_satisfaction:.1f}%</h3><p>平均满意度</p></div>'
            
            success_rate = metrics.get('successful_actions', 0) / max(summary["total_agents"], 1) * 100
            success_html = f'<div class="metric-card"><h3>{success_rate:.1f}%</h3><p>成功率</p></div>'
            
            # 生成趋势图
            metrics_plot = self._create_metrics_plot()
            
            # 代理状态表格
            agents_table = self._create_agents_table()
            
            # 环境信息
            environment_info = self._create_environment_info()
            
            return (current_step_html, total_agents_html, satisfaction_html, 
                   success_html, metrics_plot, agents_table, environment_info)
            
        except Exception as e:
            logger.error(f"刷新监控数据失败: {e}")
            return self._get_empty_monitoring_data()
    
    def _get_empty_monitoring_data(self):
        """获取空的监控数据"""
        empty_html = '<div class="metric-card"><h3>-</h3><p>无数据</p></div>'
        empty_plot = self._create_empty_plot()
        empty_table = []
        empty_env = '<div class="environment-info">环境未初始化</div>'
        
        return (empty_html, empty_html, empty_html, empty_html, 
               empty_plot, empty_table, empty_env)
    
    def _create_metrics_plot(self):
        """创建指标趋势图"""
        try:
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots
            
            if not self.simulation_engine or not self.simulation_engine.simulation_history:
                return self._create_empty_plot()
            
            history = self.simulation_engine.simulation_history[-20:]  # 最近20步
            
            steps = [step.step_number for step in history]
            satisfaction = [step.metrics.get('average_satisfaction', 0) for step in history]
            budget = [step.metrics.get('average_budget_remaining', 0) for step in history]
            energy = [step.metrics.get('average_energy', 0) for step in history]
            
            # 创建子图
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('满意度', '剩余预算', '体力值', '成功率'),
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            # 添加数据
            fig.add_trace(
                go.Scatter(x=steps, y=satisfaction, mode='lines+markers', name='满意度'),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(x=steps, y=budget, mode='lines+markers', name='预算'),
                row=1, col=2
            )
            
            fig.add_trace(
                go.Scatter(x=steps, y=energy, mode='lines+markers', name='体力'),
                row=2, col=1
            )
            
            success_rates = [step.metrics.get('successful_actions', 0) for step in history]
            fig.add_trace(
                go.Scatter(x=steps, y=success_rates, mode='lines+markers', name='成功行为数'),
                row=2, col=2
            )
            
            fig.update_layout(height=600, showlegend=False, title_text="关键指标趋势")
            return fig
            
        except Exception as e:
            logger.error(f"创建指标图表失败: {e}")
            return self._create_empty_plot()
    
    def _create_agents_table(self):
        """创建代理状态表格"""
        try:
            if not self.simulation_engine:
                return []
            
            table_data = []
            for agent in self.simulation_engine.agents.values():
                resources = agent.state.resources
                table_data.append([
                    agent.agent_id,
                    agent.state.status.value,
                    f"{resources.get('budget', 0):.1f}",
                    f"{resources.get('energy', 0):.1f}",
                    f"{resources.get('satisfaction', 0):.1f}",
                    agent.state.position.get('location', '未知')
                ])
            
            return table_data
            
        except Exception as e:
            logger.error(f"创建代理表格失败: {e}")
            return []
    
    def _create_environment_info(self):
        """创建环境信息"""
        try:
            if not self.environment:
                return '<div class="environment-info">环境未初始化</div>'
            
            env_summary = self.environment.get_environment_summary()
            
            info_html = f'''
            <div class="environment-info">
                <h4>🌍 环境状态</h4>
                <p><strong>当前时间:</strong> {env_summary.get('current_time', 'N/A')}</p>
                <p><strong>当前地点:</strong> {env_summary.get('current_location', 'N/A')}</p>
                <p><strong>注册代理:</strong> {env_summary.get('registered_agents', 0)}</p>
                <p><strong>可用活动:</strong> {env_summary.get('total_activities', 0)}</p>
                <p><strong>天气:</strong> {env_summary.get('weather', {}).get('condition', 'N/A')}</p>
                <p><strong>时间段:</strong> {env_summary.get('time_of_day', 'N/A')}</p>
            </div>
            '''
            
            return info_html
            
        except Exception as e:
            logger.error(f"创建环境信息失败: {e}")
            return '<div class="environment-info">获取环境信息失败</div>'
    
    def _load_agent_details(self, agent_id):
        """加载代理详细信息"""
        try:
            if not self.simulation_engine or not agent_id:
                return {}, [], '<div>请先选择代理</div>'
            
            agent = self.simulation_engine.agents.get(agent_id)
            if not agent:
                return {}, [], '<div>代理不存在</div>'
            
            # 代理详细状态
            details = {
                'agent_id': agent.agent_id,
                'name': agent.name,
                'status': agent.state.status.value,
                'resources': agent.state.resources,
                'goals': agent.state.goals,
                'preferences': agent.state.preferences,
                'memory_count': len(agent.state.memory),
                'action_count': len(agent.action_history)
            }
            
            # 行为历史
            history_data = []
            for action in agent.action_history[-10:]:  # 最近10个行为
                history_data.append([
                    action.timestamp,
                    action.action_type,
                    str(action.parameters),
                    action.expected_outcome
                ])
            
            # 统计信息
            statistics_html = f'''
            <div>
                <h4>📊 代理统计</h4>
                <p><strong>总行为数:</strong> {len(agent.action_history)}</p>
                <p><strong>记忆条目:</strong> {len(agent.state.memory)}</p>
                <p><strong>当前预算:</strong> {agent.state.resources.get('budget', 0):.1f}</p>
                <p><strong>当前体力:</strong> {agent.state.resources.get('energy', 0):.1f}</p>
                <p><strong>满意度:</strong> {agent.state.resources.get('satisfaction', 0):.1f}</p>
            </div>
            '''
            
            return details, history_data, statistics_html
            
        except Exception as e:
            logger.error(f"加载代理详情失败: {e}")
            return {}, [], f'<div>加载失败: {str(e)}</div>'
    
    def _apply_environment_settings(self, location, weather, temperature, 
                                  cost_multiplier, activity_availability):
        """应用环境设置"""
        try:
            # 这里可以实现环境设置的应用逻辑
            # 目前返回模拟数据
            
            preview = {
                'location': location,
                'weather': {
                    'condition': weather,
                    'temperature': temperature
                },
                'cost_multiplier': cost_multiplier,
                'activity_availability': activity_availability
            }
            
            # 模拟活动数据
            activities_data = [
                ['卢浮宫参观', '文化', '25.0', '3h', '85'],
                ['塞纳河游船', '观光', '35.0', '2h', '78'],
                ['埃菲尔铁塔', '地标', '30.0', '2h', '90']
            ]
            
            return preview, activities_data
            
        except Exception as e:
            logger.error(f"应用环境设置失败: {e}")
            return {}, []
    
    def _generate_analysis(self, analysis_type, time_range):
        """生成分析报告"""
        try:
            # 创建示例分析
            import plotly.graph_objects as go
            
            if not self.simulation_engine or not self.simulation_engine.simulation_history:
                return self._create_empty_plot(), "暂无数据进行分析", []
            
            history = self.simulation_engine.simulation_history[-int(time_range):]
            
            if analysis_type == "满意度趋势":
                steps = [step.step_number for step in history]
                satisfaction = [step.metrics.get('average_satisfaction', 0) for step in history]
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=steps, y=satisfaction, mode='lines+markers', name='满意度'))
                fig.update_layout(title="满意度趋势分析", xaxis_title="步数", yaxis_title="满意度")
                
                summary = f"## 满意度分析报告\n\n"
                summary += f"- 平均满意度: {sum(satisfaction)/len(satisfaction):.1f}%\n"
                summary += f"- 最高满意度: {max(satisfaction):.1f}%\n"
                summary += f"- 最低满意度: {min(satisfaction):.1f}%\n"
                
                detailed_data = [[step, sat] for step, sat in zip(steps, satisfaction)]
                
                return fig, summary, detailed_data
            
            # 其他分析类型的实现...
            return self._create_empty_plot(), "分析功能开发中", []
            
        except Exception as e:
            logger.error(f"生成分析失败: {e}")
            return self._create_empty_plot(), f"分析失败: {str(e)}", []
    
    async def _on_simulation_step(self, step):
        """仿真步骤回调"""
        # 更新实时数据
        self.real_time_data['current_step'] = step.step_number
        self.real_time_data['metrics'] = step.metrics
        
        # 这里可以添加实时更新UI的逻辑
        logger.debug(f"仿真步骤 {step.step_number} 完成")
    
    async def _on_status_change(self, old_status, new_status):
        """状态变化回调"""
        self.real_time_data['simulation_status'] = new_status.value
        logger.info(f"仿真状态变化: {old_status.value} -> {new_status.value}")