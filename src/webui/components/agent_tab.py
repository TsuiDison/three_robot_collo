"""
代理管理标签页 - 借鉴 browser-use 的详细信息管理模式
"""
import gradio as gr
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class AgentTab:
    """代理管理标签页 - 类似 browser-use 的浏览器管理"""
    
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.components: Dict[str, gr.Component] = {}
        self.selected_agent_id: Optional[str] = None
        
        logger.info("AgentTab initialized")
    
    def create_ui(self) -> gr.Column:
        """创建代理管理UI"""
        with gr.Column() as tab:
            # 代理选择器 - 类似 browser-use 的浏览器选择
            self._create_agent_selector()
            
            # 代理详细信息 - 类似 browser-use 的浏览器详情
            self._create_agent_details()
            
            # 代理控制面板 - 类似 browser-use 的控制操作
            self._create_agent_controls()
            
            # 代理性能分析 - 类似 browser-use 的性能监控
            self._create_agent_analytics()
        
        return tab
    
    def _create_agent_selector(self):
        """创建代理选择器"""
        with gr.Group():
            gr.Markdown("### 🤖 代理选择与概览")
            
            with gr.Row():
                self.components['agent_selector'] = gr.Dropdown(
                    label="选择代理",
                    choices=[],
                    interactive=True,
                    scale=2
                )
                
                self.components['refresh_agents_btn'] = gr.Button(
                    "🔄 刷新代理列表",
                    scale=1
                )
            
            # 代理概览卡片
            self.components['agent_overview'] = gr.HTML(
                self._generate_agent_overview_card()
            )
    
    def _create_agent_details(self):
        """创建代理详细信息"""
        with gr.Row():
            with gr.Column(scale=2):
                gr.Markdown("#### 📊 代理状态详情")
                
                # 基本信息
                self.components['agent_basic_info'] = gr.JSON(
                    label="基本信息",
                    value={}
                )
                
                # 资源状态
                with gr.Group():
                    gr.Markdown("##### 💰 资源状态")
                    
                    with gr.Row():
                        self.components['budget_display'] = gr.HTML(
                            self._generate_resource_gauge("预算", 0, 1000, "#28a745")
                        )
                        
                        self.components['energy_display'] = gr.HTML(
                            self._generate_resource_gauge("体力", 0, 100, "#17a2b8")
                        )
                        
                        self.components['satisfaction_display'] = gr.HTML(
                            self._generate_resource_gauge("满意度", 0, 100, "#ffc107")
                        )
            
            with gr.Column(scale=1):
                gr.Markdown("#### 🎯 代理配置")
                
                # 偏好设置
                self.components['agent_preferences'] = gr.JSON(
                    label="偏好设置",
                    value={}
                )
                
                # 目标设置
                self.components['agent_goals'] = gr.JSON(
                    label="目标列表",
                    value={}
                )
    
    def _create_agent_controls(self):
        """创建代理控制面板"""
        with gr.Group():
            gr.Markdown("### 🎮 代理控制面板")
            
            with gr.Row():
                # 手动操作 - 类似 browser-use 的手动控制
                with gr.Column():
                    gr.Markdown("#### 🕹️ 手动操作")
                    
                    self.components['manual_action_type'] = gr.Dropdown(
                        label="操作类型",
                        choices=[
                            ("预订活动", "book_activity"),
                            ("休息恢复", "rest"),
                            ("环境探索", "explore"),
                            ("移动位置", "move"),
                            ("购买物品", "purchase")
                        ],
                        value="rest"
                    )
                    
                    self.components['action_parameters'] = gr.Textbox(
                        label="操作参数 (JSON格式)",
                        value='{"duration": 2, "reason": "手动操作"}',
                        lines=3
                    )
                    
                    self.components['execute_action_btn'] = gr.Button(
                        "🚀 执行操作",
                        variant="primary"
                    )
                
                # 自动化设置
                with gr.Column():
                    gr.Markdown("#### 🤖 自动化设置")
                    
                    self.components['auto_mode_checkbox'] = gr.Checkbox(
                        label="启用自动模式",
                        value=True
                    )
                    
                    self.components['decision_speed_slider'] = gr.Slider(
                        label="决策速度",
                        minimum=0.1,
                        maximum=5.0,
                        value=1.0,
                        step=0.1
                    )
                    
                    self.components['risk_tolerance_slider'] = gr.Slider(
                        label="风险容忍度",
                        minimum=0.0,
                        maximum=1.0,
                        value=0.5,
                        step=0.1
                    )
            
            # 操作结果显示
            self.components['action_result'] = gr.Textbox(
                label="操作结果",
                interactive=False,
                lines=3
            )
    
    def _create_agent_analytics(self):
        """创建代理性能分析"""
        with gr.Group():
            gr.Markdown("### 📈 代理性能分析")
            
            with gr.Row():
                # 行为历史
                with gr.Column():
                    gr.Markdown("#### 📋 行为历史")
                    
                    self.components['action_history_table'] = gr.Dataframe(
                        headers=["时间", "操作类型", "参数", "结果", "满意度变化"],
                        datatype=["str", "str", "str", "str", "number"],
                        label="最近20条行为记录",
                        interactive=False,
                        height=300
                    )
                
                # 统计信息
                with gr.Column():
                    gr.Markdown("#### 📊 统计信息")
                    
                    self.components['agent_statistics'] = gr.HTML(
                        self._generate_statistics_display()
                    )
                    
                    # 性能指标
                    self.components['performance_metrics'] = gr.JSON(
                        label="性能指标",
                        value={}
                    )
            
            # 决策分析
            with gr.Row():
                gr.Markdown("#### 🧠 决策分析")
                
                self.components['decision_analysis'] = gr.Textbox(
                    label="最新决策分析",
                    interactive=False,
                    lines=4,
                    value="等待代理做出决策..."
                )
    
    def setup_event_handlers(self):
        """设置事件处理器"""
        
        # 代理选择事件
        self.components['agent_selector'].change(
            fn=self.handle_agent_selection,
            inputs=[self.components['agent_selector']],
            outputs=self._get_agent_detail_outputs()
        )
        
        # 刷新代理列表
        self.components['refresh_agents_btn'].click(
            fn=self.handle_refresh_agents,
            outputs=[self.components['agent_selector']]
        )
        
        # 执行手动操作
        self.components['execute_action_btn'].click(
            fn=self.handle_execute_action,
            inputs=[
                self.components['agent_selector'],
                self.components['manual_action_type'],
                self.components['action_parameters']
            ],
            outputs=[
                self.components['action_result'],
                self.components['budget_display'],
                self.components['energy_display'],
                self.components['satisfaction_display']
            ]
        )
        
        # 自动模式切换
        self.components['auto_mode_checkbox'].change(
            fn=self.handle_auto_mode_toggle,
            inputs=[
                self.components['agent_selector'],
                self.components['auto_mode_checkbox']
            ]
        )
    
    def handle_agent_selection(self, agent_id: str):
        """处理代理选择"""
        try:
            if not agent_id:
                return self._get_empty_agent_data()
            
            self.selected_agent_id = agent_id
            session = self.state_manager.get_session()
            
            if not session:
                return self._get_empty_agent_data()
            
            # 查找选中的代理配置
            agent_config = None
            for config in session.agents_config:
                if config.get('name') == agent_id:
                    agent_config = config
                    break
            
            if not agent_config:
                return self._get_empty_agent_data()
            
            # 生成代理详细信息
            basic_info = {
                "代理ID": agent_config.get('name', 'Unknown'),
                "类型": "旅行代理",
                "状态": "活跃" if session.status.value == "running" else "待机",
                "创建时间": session.created_at,
                "当前位置": agent_config.get('location', '未知')
            }
            
            # 模拟资源状态
            current_budget = agent_config.get('budget', 1000)
            current_energy = 85 if session.current_step > 0 else 100
            current_satisfaction = 75 if session.current_step > 0 else 50
            
            budget_gauge = self._generate_resource_gauge("预算", current_budget, 1000, "#28a745")
            energy_gauge = self._generate_resource_gauge("体力", current_energy, 100, "#17a2b8")
            satisfaction_gauge = self._generate_resource_gauge("满意度", current_satisfaction, 100, "#ffc107")
            
            # 偏好设置
            preferences = {
                "活动类型": ["文化", "自然", "美食"],
                "预算等级": "中等",
                "冒险度": 0.5,
                "社交偏好": "独立旅行"
            }
            
            # 目标列表
            goals = {
                "主要目标": "最大化旅行满意度",
                "次要目标": ["控制预算", "保持健康", "体验文化"],
                "完成度": "60%"
            }
            
            # 行为历史
            action_history = self._generate_action_history_data(session.current_step)
            
            # 统计信息
            statistics_html = self._generate_statistics_display({
                "总操作数": session.current_step * 2,
                "成功率": "92%",
                "平均满意度": f"{current_satisfaction}%",
                "预算使用率": f"{((1000 - current_budget) / 1000) * 100:.1f}%"
            })
            
            # 性能指标
            performance_metrics = {
                "决策时间": "0.23秒",
                "成功操作": session.current_step * 2 - 1,
                "失败操作": 1,
                "效率评分": "A+"
            }
            
            # 决策分析
            decision_analysis = self._generate_decision_analysis(agent_config, session)
            
            return (basic_info, budget_gauge, energy_gauge, satisfaction_gauge,
                   preferences, goals, action_history, statistics_html,
                   performance_metrics, decision_analysis)
            
        except Exception as e:
            logger.error(f"Agent selection error: {e}")
            return self._get_empty_agent_data()
    
    def handle_refresh_agents(self):
        """刷新代理列表"""
        try:
            session = self.state_manager.get_session()
            if not session or not session.agents_config:
                return gr.update(choices=[("无代理", "")])
            
            choices = [(config.get('name', f'Agent{i+1}'), config.get('name', f'Agent{i+1}'))
                      for i, config in enumerate(session.agents_config)]
            
            return gr.update(choices=choices)
            
        except Exception as e:
            logger.error(f"Refresh agents error: {e}")
            return gr.update(choices=[("错误", "")])
    
    def handle_execute_action(self, agent_id: str, action_type: str, parameters_json: str):
        """处理手动操作执行"""
        try:
            if not agent_id:
                return "❌ 请先选择代理", "", "", ""
            
            # 解析参数
            try:
                parameters = json.loads(parameters_json)
            except json.JSONDecodeError:
                return "❌ 参数格式错误，请使用有效的JSON格式", "", "", ""
            
            # 模拟操作执行
            session = self.state_manager.get_session()
            if not session:
                return "❌ 无活跃会话", "", "", ""
            
            # 执行操作并更新状态
            result_message = f"✅ 操作执行成功\n"
            result_message += f"代理: {agent_id}\n"
            result_message += f"操作: {action_type}\n"
            result_message += f"参数: {parameters}\n"
            result_message += f"时间: {datetime.now().strftime('%H:%M:%S')}"
            
            # 模拟资源变化
            if action_type == "rest":
                new_energy = min(100, 85 + parameters.get('duration', 2) * 10)
                new_budget = 950  # 休息可能有小额花费
                new_satisfaction = 78
            elif action_type == "book_activity":
                new_energy = max(0, 85 - 25)
                new_budget = 950 - 50  # 活动费用
                new_satisfaction = 85
            else:
                new_energy = 80
                new_budget = 945
                new_satisfaction = 76
            
            # 更新资源显示
            budget_gauge = self._generate_resource_gauge("预算", new_budget, 1000, "#28a745")
            energy_gauge = self._generate_resource_gauge("体力", new_energy, 100, "#17a2b8") 
            satisfaction_gauge = self._generate_resource_gauge("满意度", new_satisfaction, 100, "#ffc107")
            
            return result_message, budget_gauge, energy_gauge, satisfaction_gauge
            
        except Exception as e:
            error_msg = f"❌ 操作执行失败: {str(e)}"
            return error_msg, "", "", ""
    
    def handle_auto_mode_toggle(self, agent_id: str, enabled: bool):
        """处理自动模式切换"""
        try:
            if not agent_id:
                return
            
            mode = "启用" if enabled else "禁用"
            logger.info(f"Agent {agent_id} auto mode {mode}")
            
            # 这里可以实际更新代理的自动模式设置
            
        except Exception as e:
            logger.error(f"Auto mode toggle error: {e}")
    
    def _get_agent_detail_outputs(self) -> List[gr.Component]:
        """获取代理详情输出组件"""
        return [
            self.components['agent_basic_info'],
            self.components['budget_display'],
            self.components['energy_display'],
            self.components['satisfaction_display'],
            self.components['agent_preferences'],
            self.components['agent_goals'],
            self.components['action_history_table'],
            self.components['agent_statistics'],
            self.components['performance_metrics'],
            self.components['decision_analysis']
        ]
    
    def _get_empty_agent_data(self):
        """获取空代理数据"""
        empty_gauge = self._generate_resource_gauge("无数据", 0, 100, "#6c757d")
        empty_stats = self._generate_statistics_display()
        
        return ({}, empty_gauge, empty_gauge, empty_gauge, 
                {}, {}, [], empty_stats, {}, "请选择代理查看详细信息")
    
    def _generate_agent_overview_card(self) -> str:
        """生成代理概览卡片"""
        return """
        <div style="
            border: 2px solid #17a2b8;
            border-radius: 10px;
            padding: 20px;
            background: linear-gradient(135deg, #17a2b815, #17a2b805);
            margin: 10px 0;
        ">
            <h3 style="color: #17a2b8; margin: 0 0 10px 0;">
                🤖 代理概览
            </h3>
            <p style="margin: 0; color: #333;">
                选择代理查看详细信息和控制选项
            </p>
        </div>
        """
    
    def _generate_resource_gauge(self, name: str, current: float, max_val: float, color: str) -> str:
        """生成资源仪表盘HTML"""
        percentage = (current / max_val) * 100 if max_val > 0 else 0
        
        return f"""
        <div style="
            border: 2px solid {color};
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            background: linear-gradient(135deg, {color}15, {color}05);
            margin: 5px;
        ">
            <h4 style="color: {color}; margin: 0 0 10px 0;">
                {name}
            </h4>
            <div style="
                width: 80px;
                height: 80px;
                border-radius: 50%;
                background: conic-gradient({color} {percentage * 3.6}deg, #e9ecef 0deg);
                margin: 0 auto 10px auto;
                display: flex;
                align-items: center;
                justify-content: center;
                position: relative;
            ">
                <div style="
                    width: 60px;
                    height: 60px;
                    border-radius: 50%;
                    background: white;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: bold;
                    color: {color};
                ">
                    {current:.0f}
                </div>
            </div>
            <small style="color: #666;">
                {percentage:.1f}%
            </small>
        </div>
        """
    
    def _generate_statistics_display(self, stats: Dict[str, Any] = None) -> str:
        """生成统计信息显示"""
        if not stats:
            stats = {"暂无数据": "请选择代理"}
        
        stats_html = """
        <div style="
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 15px;
            background: #f8f9fa;
        ">
            <h4 style="margin: 0 0 15px 0;">📊 代理统计</h4>
        """
        
        for key, value in stats.items():
            stats_html += f"""
            <div style="
                display: flex;
                justify-content: space-between;
                margin-bottom: 8px;
                padding: 5px 0;
                border-bottom: 1px solid #e9ecef;
            ">
                <strong>{key}:</strong>
                <span>{value}</span>
            </div>
            """
        
        stats_html += "</div>"
        return stats_html
    
    def _generate_action_history_data(self, current_step: int) -> List[List[str]]:
        """生成行为历史数据"""
        if current_step == 0:
            return []
        
        # 模拟行为历史
        actions = []
        for i in range(min(current_step, 10)):
            actions.append([
                datetime.now().strftime("%H:%M:%S"),
                "book_activity" if i % 2 == 0 else "explore",
                '{"activity": "卢浮宫参观"}' if i % 2 == 0 else '{"duration": 1}',
                "成功",
                "+15" if i % 2 == 0 else "+5"
            ])
        
        return actions
    
    def _generate_decision_analysis(self, agent_config: Dict[str, Any], session) -> str:
        """生成决策分析"""
        if session.current_step == 0:
            return "代理尚未开始决策过程"
        
        analysis = f"""
最新决策分析 (步骤 {session.current_step}):

🎯 决策目标: 在预算约束下最大化满意度
💰 当前预算: {agent_config.get('budget', 1000):.0f} 元
⚡ 决策因素:
  - 成本考虑: 30%
  - 满意度潜力: 40% 
  - 体力需求: 20%
  - 偏好匹配: 10%

🤔 决策过程:
1. 感知到 3 个可用活动选项
2. 评估各选项的成本效益比
3. 选择满意度评分最高的活动
4. 成功执行预订操作

📈 决策效果: 满意度 +15, 预算 -50, 体力 -20
        """
        
        return analysis