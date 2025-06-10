"""
仿真控制标签页 - 借鉴 browser-use 的任务控制模式
"""
import gradio as gr
import logging
from typing import Dict, Any, List, Optional, Tuple, Callable
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

class SimulationTab:
    """仿真控制标签页 - 类似 browser-use 的浏览器控制"""
    
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.components: Dict[str, gr.Component] = {}
        self.callbacks: Dict[str, Callable] = {}
        
        # 任务状态
        self.current_task_id: Optional[str] = None
        self.simulation_engine = None
        
        logger.info("SimulationTab initialized")
    
    def create_ui(self) -> gr.Column:
        """创建仿真控制UI"""
        with gr.Column() as tab:
            # 任务配置区域 - 类似 browser-use 的任务输入
            self._create_task_config_section()
            
            # 控制按钮区域 - 类似 browser-use 的控制面板
            self._create_control_section()
            
            # 状态显示区域 - 类似 browser-use 的状态显示
            self._create_status_section()
            
            # 日志区域 - 类似 browser-use 的操作日志
            self._create_log_section()
        
        return tab
    
    def _create_task_config_section(self):
        """创建任务配置区域"""
        with gr.Group():
            gr.Markdown("### 🎯 仿真任务配置")
            
            with gr.Row():
                with gr.Column(scale=2):
                    # 任务描述 - 类似 browser-use 的任务输入
                    self.components['task_description'] = gr.Textbox(
                        label="仿真任务描述",
                        placeholder="例如：模拟3个旅行者在巴黎进行为期7天的旅行规划",
                        lines=3,
                        value="模拟智能代理在旅行环境中的决策过程"
                    )
                    
                    # 任务参数
                    with gr.Row():
                        self.components['max_steps'] = gr.Number(
                            label="最大步数",
                            value=30,
                            minimum=1,
                            maximum=200
                        )
                        self.components['step_interval'] = gr.Slider(
                            label="步骤间隔(秒)",
                            minimum=0.1,
                            maximum=5.0,
                            value=1.0,
                            step=0.1
                        )
                
                with gr.Column(scale=1):
                    # 代理配置
                    self.components['agent_count'] = gr.Number(
                        label="代理数量",
                        value=3,
                        minimum=1,
                        maximum=10
                    )
                    self.components['agent_budget'] = gr.Number(
                        label="初始预算",
                        value=1000,
                        minimum=100,
                        maximum=5000
                    )
                    
                    # 环境配置
                    self.components['location'] = gr.Dropdown(
                        label="起始地点",
                        choices=["paris", "tokyo", "bali", "zurich"],
                        value="paris"
                    )
    
    def _create_control_section(self):
        """创建控制按钮区域"""
        with gr.Row():
            # 主控制按钮 - 类似 browser-use 的操作按钮
            self.components['start_btn'] = gr.Button(
                "🚀 开始仿真任务",
                variant="primary",
                size="lg",
                scale=2
            )
            
            self.components['pause_btn'] = gr.Button(
                "⏸️ 暂停",
                variant="secondary",
                interactive=False
            )
            
            self.components['stop_btn'] = gr.Button(
                "⏹️ 停止",
                variant="stop",
                interactive=False
            )
            
            self.components['reset_btn'] = gr.Button(
                "🔄 重置",
                variant="secondary"
            )
    
    def _create_status_section(self):
        """创建状态显示区域"""
        with gr.Row():
            with gr.Column(scale=2):
                # 任务状态卡片 - 类似 browser-use 的状态卡片
                self.components['status_card'] = gr.HTML(
                    self._generate_status_card("待机", "系统已就绪，等待任务启动")
                )
                
                # 进度条
                self.components['progress_bar'] = gr.HTML(
                    self._generate_progress_bar(0, 100)
                )
            
            with gr.Column(scale=1):
                # 实时指标 - 类似 browser-use 的实时数据
                self.components['metrics_display'] = gr.HTML(
                    self._generate_metrics_display({})
                )
    
    def _create_log_section(self):
        """创建日志区域"""
        with gr.Group():
            gr.Markdown("### 📋 仿真日志")
            
            with gr.Row():
                # 日志显示 - 类似 browser-use 的操作日志
                self.components['log_display'] = gr.Textbox(
                    label="实时日志",
                    lines=12,
                    max_lines=20,
                    interactive=False,
                    show_copy_button=True,
                    value="[系统] 仿真系统已初始化，等待任务配置..."
                )
                
                with gr.Column(scale=1):
                    # 日志控制
                    self.components['log_level'] = gr.Dropdown(
                        label="日志级别",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                        value="INFO"
                    )
                    
                    self.components['clear_log_btn'] = gr.Button(
                        "🗑️ 清空日志",
                        size="sm"
                    )
                    
                    self.components['export_log_btn'] = gr.Button(
                        "📄 导出日志",
                        size="sm"
                    )
    
    def setup_event_handlers(self):
        """设置事件处理器 - 类似 browser-use 的事件绑定"""
        
        # 开始仿真事件
        self.components['start_btn'].click(
            fn=self.handle_start_simulation,
            inputs=[
                self.components['task_description'],
                self.components['max_steps'],
                self.components['step_interval'],
                self.components['agent_count'],
                self.components['agent_budget'],
                self.components['location']
            ],
            outputs=[
                self.components['status_card'],
                self.components['log_display'],
                self.components['start_btn'],
                self.components['pause_btn'],
                self.components['stop_btn']
            ]
        )
        
        # 停止仿真事件
        self.components['stop_btn'].click(
            fn=self.handle_stop_simulation,
            outputs=[
                self.components['status_card'],
                self.components['log_display'],
                self.components['start_btn'],
                self.components['pause_btn'],
                self.components['stop_btn']
            ]
        )
        
        # 清空日志事件
        self.components['clear_log_btn'].click(
            fn=lambda: "",
            outputs=[self.components['log_display']]
        )
        
        # 重置事件
        self.components['reset_btn'].click(
            fn=self.handle_reset_simulation,
            outputs=[
                self.components['status_card'],
                self.components['progress_bar'],
                self.components['metrics_display'],
                self.components['log_display']
            ]
        )
    
    def handle_start_simulation(self, task_desc, max_steps, step_interval, 
                              agent_count, agent_budget, location):
        """处理开始仿真事件 - 类似 browser-use 的任务启动"""
        try:
            # 创建会话
            session_id = self.state_manager.create_session()
            
            # 更新会话配置
            self.state_manager.update_session(session_id, {
                'simulation_config': {
                    'task_description': task_desc,
                    'max_steps': int(max_steps),
                    'step_interval': float(step_interval)
                },
                'agents_config': [
                    {
                        'name': f'旅行者{i+1}',
                        'budget': float(agent_budget),
                        'location': location
                    }
                    for i in range(int(agent_count))
                ],
                'environment_config': {
                    'start_location': location
                },
                'status': 'running',
                'total_steps': int(max_steps)
            })
            
            # 更新UI状态
            status_card = self._generate_status_card(
                "运行中", 
                f"任务已启动 - {task_desc}"
            )
            
            log_message = f"[{datetime.now().strftime('%H:%M:%S')}] 仿真任务已启动\n"
            log_message += f"[INFO] 任务描述: {task_desc}\n"
            log_message += f"[INFO] 配置: {agent_count}个代理, {max_steps}步, 起始地点: {location}\n"
            
            # 更新按钮状态
            start_btn_update = gr.update(interactive=False, value="🔄 运行中...")
            pause_btn_update = gr.update(interactive=True)
            stop_btn_update = gr.update(interactive=True)
            
            logger.info(f"Simulation started with session {session_id}")
            
            return (status_card, log_message, 
                   start_btn_update, pause_btn_update, stop_btn_update)
            
        except Exception as e:
            error_card = self._generate_status_card("错误", f"启动失败: {str(e)}")
            error_log = f"[{datetime.now().strftime('%H:%M:%S')}] 启动失败: {str(e)}\n"
            
            return (error_card, error_log, 
                   gr.update(interactive=True), 
                   gr.update(interactive=False), 
                   gr.update(interactive=False))
    
    def handle_stop_simulation(self):
        """处理停止仿真事件"""
        try:
            session = self.state_manager.get_session()
            if session:
                self.state_manager.update_session(session.session_id, {
                    'status': 'completed'
                })
            
            status_card = self._generate_status_card("已停止", "仿真任务已停止")
            log_message = f"[{datetime.now().strftime('%H:%M:%S')}] 仿真任务已停止\n"
            
            # 重置按钮状态
            start_btn_update = gr.update(interactive=True, value="🚀 开始仿真任务")
            pause_btn_update = gr.update(interactive=False)
            stop_btn_update = gr.update(interactive=False)
            
            return (status_card, log_message,
                   start_btn_update, pause_btn_update, stop_btn_update)
            
        except Exception as e:
            error_card = self._generate_status_card("错误", f"停止失败: {str(e)}")
            error_log = f"[{datetime.now().strftime('%H:%M:%S')}] 停止失败: {str(e)}\n"
            return (error_card, error_log, 
                   gr.update(), gr.update(), gr.update())
    
    def handle_reset_simulation(self):
        """处理重置仿真事件"""
        try:
            # 清理状态
            session = self.state_manager.get_session()
            if session:
                self.state_manager.delete_session(session.session_id)
            
            # 重置UI
            status_card = self._generate_status_card("待机", "系统已重置，等待新任务")
            progress_bar = self._generate_progress_bar(0, 100)
            metrics_display = self._generate_metrics_display({})
            log_message = f"[{datetime.now().strftime('%H:%M:%S')}] 系统已重置\n"
            
            return (status_card, progress_bar, metrics_display, log_message)
            
        except Exception as e:
            error_card = self._generate_status_card("错误", f"重置失败: {str(e)}")
            return (error_card, "", "", f"重置失败: {str(e)}\n")
    
    # UI生成辅助方法 - 类似 browser-use 的状态生成
    def _generate_status_card(self, status: str, message: str) -> str:
        """生成状态卡片HTML"""
        color_map = {
            "待机": "#6c757d",
            "运行中": "#28a745", 
            "已停止": "#ffc107",
            "错误": "#dc3545",
            "完成": "#17a2b8"
        }
        
        color = color_map.get(status, "#6c757d")
        
        return f"""
        <div style="
            border: 2px solid {color};
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            background: linear-gradient(135deg, {color}15, {color}05);
        ">
            <h3 style="color: {color}; margin: 0 0 10px 0;">
                🎯 任务状态: {status}
            </h3>
            <p style="margin: 0; color: #333;">
                {message}
            </p>
            <small style="color: #666;">
                更新时间: {datetime.now().strftime('%H:%M:%S')}
            </small>
        </div>
        """
    
    def _generate_progress_bar(self, current: int, total: int) -> str:
        """生成进度条HTML"""
        progress = (current / max(total, 1)) * 100
        
        return f"""
        <div style="margin: 10px 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span>进度: {current}/{total}</span>
                <span>{progress:.1f}%</span>
            </div>
            <div style="
                width: 100%;
                height: 10px;
                background-color: #e9ecef;
                border-radius: 5px;
                overflow: hidden;
            ">
                <div style="
                    width: {progress}%;
                    height: 100%;
                    background: linear-gradient(90deg, #667eea, #764ba2);
                    transition: width 0.3s ease;
                "></div>
            </div>
        </div>
        """
    
    def _generate_metrics_display(self, metrics: Dict[str, Any]) -> str:
        """生成指标显示HTML"""
        if not metrics:
            return """
            <div style="
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
                background: #f8f9fa;
            ">
                <h4>📊 实时指标</h4>
                <p>等待仿真开始...</p>
            </div>
            """
        
        metrics_html = """
        <div style="
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 15px;
            background: #f8f9fa;
        ">
            <h4>📊 实时指标</h4>
        """
        
        for key, value in metrics.items():
            metrics_html += f"<p><strong>{key}:</strong> {value}</p>"
        
        metrics_html += "</div>"
        return metrics_html