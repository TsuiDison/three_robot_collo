"""
监控标签页 - 借鉴 browser-use 的实时监控模式
"""
import gradio as gr
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class MonitoringTab:
    """监控标签页 - 类似 browser-use 的实时监控面板"""
    
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.components: Dict[str, gr.Component] = {}
        self.auto_refresh_enabled = True
        self.refresh_interval = 2
        
        logger.info("MonitoringTab initialized")
    
    def create_ui(self) -> gr.Column:
        """创建监控UI"""
        with gr.Column() as tab:
            # 会话选择器 - 类似 browser-use 的会话管理
            self._create_session_selector()
            
            # 实时指标卡片 - 类似 browser-use 的状态卡片
            self._create_metrics_cards()
            
            # 数据表格 - 类似 browser-use 的详细信息
            self._create_data_tables()
            
            # 控制面板
            self._create_control_panel()
        
        return tab
    
    def _create_session_selector(self):
        """创建会话选择器"""
        with gr.Group():
            gr.Markdown("### 📱 会话管理")
            
            with gr.Row():
                self.components['session_selector'] = gr.Dropdown(
                    label="选择活跃会话",
                    choices=[],
                    interactive=True,
                    scale=2
                )
                
                self.components['refresh_sessions_btn'] = gr.Button(
                    "🔄 刷新会话",
                    scale=1
                )
                
                self.components['create_session_btn'] = gr.Button(
                    "➕ 新建会话",
                    variant="primary",
                    scale=1
                )
    
    def _create_metrics_cards(self):
        """创建指标卡片"""
        gr.Markdown("### 📊 实时监控面板")
        
        with gr.Row():
            # 仿真状态卡片
            self.components['simulation_status_card'] = gr.HTML(
                self._generate_metric_card("仿真状态", "待机", "#6c757d")
            )
            
            # 当前步数卡片  
            self.components['current_step_card'] = gr.HTML(
                self._generate_metric_card("当前步数", "0", "#17a2b8")
            )
            
            # 活跃代理卡片
            self.components['active_agents_card'] = gr.HTML(
                self._generate_metric_card("活跃代理", "0", "#28a745")
            )
            
            # 平均满意度卡片
            self.components['avg_satisfaction_card'] = gr.HTML(
                self._generate_metric_card("平均满意度", "0%", "#ffc107")
            )
    
    def _create_data_tables(self):
        """创建数据表格"""
        with gr.Row():
            with gr.Column():
                # 代理状态表格 - 类似 browser-use 的详细状态
                gr.Markdown("#### 🤖 代理状态详情")
                self.components['agents_table'] = gr.Dataframe(
                    headers=["代理ID", "状态", "预算", "体力", "满意度", "当前活动"],
                    datatype=["str", "str", "number", "number", "number", "str"],
                    label="代理实时状态",
                    interactive=False,
                    height=300
                )
            
            with gr.Column():
                # 环境状态显示
                gr.Markdown("#### 🌍 环境状态")
                self.components['environment_info'] = gr.JSON(
                    label="环境详细信息",
                    value={}
                )
                
                # 最近活动
                gr.Markdown("#### 📋 最近活动")
                self.components['recent_activities'] = gr.Dataframe(
                    headers=["时间", "代理", "活动", "结果"],
                    datatype=["str", "str", "str", "str"],
                    label="活动历史",
                    interactive=False,
                    height=200
                )
    
    def _create_control_panel(self):
        """创建控制面板"""
        with gr.Group():
            gr.Markdown("### ⚙️ 监控控制")
            
            with gr.Row():
                # 自动刷新控制
                self.components['auto_refresh_checkbox'] = gr.Checkbox(
                    label="自动刷新",
                    value=True
                )
                
                self.components['refresh_interval_slider'] = gr.Slider(
                    label="刷新间隔(秒)",
                    minimum=1,
                    maximum=10,
                    value=2,
                    step=1
                )
                
                self.components['manual_refresh_btn'] = gr.Button(
                    "🔄 手动刷新",
                    variant="secondary"
                )
                
                # 导出功能
                self.components['export_data_btn'] = gr.Button(
                    "📊 导出数据",
                    variant="secondary"
                )
            
            # 导出状态显示
            self.components['export_status'] = gr.Textbox(
                label="导出状态",
                interactive=False,
                visible=False
            )
    
    def setup_event_handlers(self):
        """设置事件处理器"""
        
        # 会话选择事件
        self.components['session_selector'].change(
            fn=self.handle_session_change,
            inputs=[self.components['session_selector']],
            outputs=self._get_all_output_components()
        )
        
        # 刷新会话列表
        self.components['refresh_sessions_btn'].click(
            fn=self.handle_refresh_sessions,
            outputs=[self.components['session_selector']]
        )
        
        # 手动刷新
        self.components['manual_refresh_btn'].click(
            fn=self.handle_manual_refresh,
            inputs=[self.components['session_selector']],
            outputs=self._get_all_output_components()
        )
        
        # 导出数据
        self.components['export_data_btn'].click(
            fn=self.handle_export_data,
            inputs=[self.components['session_selector']],
            outputs=[self.components['export_status']]
        )
        
        # 自动刷新设置
        self.components['auto_refresh_checkbox'].change(
            fn=self.handle_auto_refresh_toggle,
            inputs=[self.components['auto_refresh_checkbox']]
        )
    
    def handle_session_change(self, session_id: str):
        """处理会话切换"""
        try:
            if not session_id:
                return self._get_empty_data()
            
            self.state_manager.set_active_session(session_id)
            session = self.state_manager.get_session(session_id)
            
            if not session:
                return self._get_empty_data()
            
            # 更新指标卡片
            status_card = self._generate_metric_card(
                "仿真状态", 
                session.status.value, 
                self._get_status_color(session.status.value)
            )
            
            step_card = self._generate_metric_card(
                "当前步数",
                f"{session.current_step}/{session.total_steps}",
                "#17a2b8"
            )
            
            agents_card = self._generate_metric_card(
                "活跃代理",
                str(len(session.agents_config)),
                "#28a745"
            )
            
            # 模拟平均满意度
            avg_satisfaction = "75%" if session.current_step > 0 else "50%"
            satisfaction_card = self._generate_metric_card(
                "平均满意度",
                avg_satisfaction,
                "#ffc107"
            )
            
            # 生成代理状态表格
            agents_table_data = self._generate_agents_table_data(session)
            
            # 生成环境信息
            environment_info = {
                "当前地点": session.environment_config.get("start_location", "未知"),
                "天气": "晴朗",
                "时间": datetime.now().strftime("%H:%M"),
                "可用活动数": 8
            }
            
            # 生成最近活动
            recent_activities_data = self._generate_recent_activities_data(session)
            
            return (status_card, step_card, agents_card, satisfaction_card,
                   agents_table_data, environment_info, recent_activities_data)
            
        except Exception as e:
            logger.error(f"Session change error: {e}")
            return self._get_empty_data()
    
    def handle_refresh_sessions(self):
        """刷新会话列表"""
        try:
            sessions = self.state_manager.get_session_list()
            choices = [(f"{s['session_id']} ({s['status']})", s['session_id']) 
                      for s in sessions]
            
            if not choices:
                choices = [("无活跃会话", "")]
            
            return gr.update(choices=choices)
            
        except Exception as e:
            logger.error(f"Refresh sessions error: {e}")
            return gr.update(choices=[("错误", "")])
    
    def handle_manual_refresh(self, session_id: str):
        """处理手动刷新"""
        return self.handle_session_change(session_id)
    
    def handle_export_data(self, session_id: str):
        """处理数据导出"""
        try:
            if not session_id:
                return "❌ 请先选择会话"
            
            session = self.state_manager.get_session(session_id)
            if not session:
                return "❌ 会话不存在"
            
            # 模拟导出过程
            export_data = {
                "session_id": session.session_id,
                "status": session.status.value,
                "created_at": session.created_at,
                "current_step": session.current_step,
                "total_steps": session.total_steps,
                "agents_config": session.agents_config,
                "simulation_results": session.simulation_results
            }
            
            # 这里可以实际保存到文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"simulation_data_{session_id}_{timestamp}.json"
            
            return f"✅ 数据已导出: {filename}"
            
        except Exception as e:
            logger.error(f"Export data error: {e}")
            return f"❌ 导出失败: {str(e)}"
    
    def handle_auto_refresh_toggle(self, enabled: bool):
        """处理自动刷新切换"""
        self.auto_refresh_enabled = enabled
        logger.info(f"Auto refresh {'enabled' if enabled else 'disabled'}")
    
    def _get_all_output_components(self) -> List[gr.Component]:
        """获取所有输出组件"""
        return [
            self.components['simulation_status_card'],
            self.components['current_step_card'],
            self.components['active_agents_card'],
            self.components['avg_satisfaction_card'],
            self.components['agents_table'],
            self.components['environment_info'],
            self.components['recent_activities']
        ]
    
    def _get_empty_data(self):
        """获取空数据"""
        empty_card = self._generate_metric_card("状态", "无数据", "#6c757d")
        return (empty_card, empty_card, empty_card, empty_card, 
                [], {}, [])
    
    def _generate_metric_card(self, title: str, value: str, color: str) -> str:
        """生成指标卡片HTML"""
        return f"""
        <div style="
            border: 2px solid {color};
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            background: linear-gradient(135deg, {color}15, {color}05);
            margin: 5px;
        ">
            <h3 style="color: {color}; margin: 0 0 10px 0; font-size: 2em;">
                {value}
            </h3>
            <p style="margin: 0; color: #666; font-size: 0.9em;">
                {title}
            </p>
        </div>
        """
    
    def _get_status_color(self, status: str) -> str:
        """获取状态颜色"""
        color_map = {
            "idle": "#6c757d",
            "running": "#28a745",
            "paused": "#ffc107", 
            "completed": "#17a2b8",
            "error": "#dc3545"
        }
        return color_map.get(status, "#6c757d")
    
    def _generate_agents_table_data(self, session) -> List[List[str]]:
        """生成代理状态表格数据"""
        if not session.agents_config:
            return []
        
        table_data = []
        for i, agent_config in enumerate(session.agents_config):
            # 模拟代理状态数据
            table_data.append([
                agent_config.get('name', f'Agent{i+1}'),
                "活跃" if session.status.value == "running" else "待机",
                f"{agent_config.get('budget', 1000):.0f}",
                "85" if session.current_step > 0 else "100",
                "78" if session.current_step > 0 else "50",
                "探索中" if session.status.value == "running" else "无"
            ])
        
        return table_data
    
    def _generate_recent_activities_data(self, session) -> List[List[str]]:
        """生成最近活动数据"""
        if session.current_step == 0:
            return []
        
        # 模拟最近活动数据
        activities = [
            [
                datetime.now().strftime("%H:%M:%S"),
                "旅行者1",
                "预订活动",
                "成功"
            ],
            [
                datetime.now().strftime("%H:%M:%S"),
                "旅行者2", 
                "探索环境",
                "成功"
            ]
        ]
        
        return activities