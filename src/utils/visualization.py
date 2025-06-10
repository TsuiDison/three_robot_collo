"""
可视化工具类
提供各种图表和可视化功能
"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class VisualizationManager:
    """可视化管理器"""
    
    def __init__(self):
        self.color_palette = [
            '#667eea', '#764ba2', '#f093fb', '#f5576c',
            '#4facfe', '#00f2fe', '#43e97b', '#38f9d7'
        ]
    
    def create_metrics_timeline(self, simulation_history: List[Dict]) -> go.Figure:
        """创建指标时间线图表"""
        try:
            if not simulation_history:
                return self._create_empty_figure("暂无仿真数据")
            
            # 提取数据
            steps = []
            satisfaction = []
            budget = []
            energy = []
            success_rate = []
            
            for step in simulation_history:
                metrics = step.get('metrics', {})
                steps.append(step.get('step_number', 0))
                satisfaction.append(metrics.get('average_satisfaction', 0))
                budget.append(metrics.get('average_budget_remaining', 0))
                energy.append(metrics.get('average_energy', 0))
                success_rate.append(metrics.get('successful_actions', 0))
            
            # 创建子图
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('平均满意度', '平均剩余预算', '平均体力', '成功行为数'),
                vertical_spacing=0.12,
                horizontal_spacing=0.1
            )
            
            # 添加数据线
            fig.add_trace(
                go.Scatter(x=steps, y=satisfaction, mode='lines+markers',
                          name='满意度', line=dict(color=self.color_palette[0])),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(x=steps, y=budget, mode='lines+markers',
                          name='预算', line=dict(color=self.color_palette[1])),
                row=1, col=2
            )
            
            fig.add_trace(
                go.Scatter(x=steps, y=energy, mode='lines+markers',
                          name='体力', line=dict(color=self.color_palette[2])),
                row=2, col=1
            )
            
            fig.add_trace(
                go.Scatter(x=steps, y=success_rate, mode='lines+markers',
                          name='成功数', line=dict(color=self.color_palette[3])),
                row=2, col=2
            )
            
            # 更新布局
            fig.update_layout(
                height=600,
                showlegend=False,
                title_text="仿真关键指标趋势",
                title_x=0.5
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"创建指标时间线失败: {e}")
            return self._create_empty_figure("创建图表失败")
    
    def create_agent_comparison_chart(self, agents_data: List[Dict]) -> go.Figure:
        """创建代理对比图表"""
        try:
            if not agents_data:
                return self._create_empty_figure("暂无代理数据")
            
            # 提取数据
            agent_ids = [agent['agent_id'] for agent in agents_data]
            satisfaction = [agent['resources']['satisfaction'] for agent in agents_data]
            budget = [agent['resources']['budget'] for agent in agents_data]
            energy = [agent['resources']['energy'] for agent in agents_data]
            
            # 创建柱状图
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name='满意度',
                x=agent_ids,
                y=satisfaction,
                marker_color=self.color_palette[0]
            ))
            
            fig.add_trace(go.Bar(
                name='预算',
                x=agent_ids,
                y=budget,
                marker_color=self.color_palette[1]
            ))
            
            fig.add_trace(go.Bar(
                name='体力',
                x=agent_ids,
                y=energy,
                marker_color=self.color_palette[2]
            ))
            
            fig.update_layout(
                barmode='group',
                title='代理状态对比',
                xaxis_title='代理ID',
                yaxis_title='数值',
                height=400
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"创建代理对比图表失败: {e}")
            return self._create_empty_figure("创建图表失败")
    
    def create_activity_distribution_pie(self, activity_data: List[Dict]) -> go.Figure:
        """创建活动分布饼图"""
        try:
            if not activity_data:
                return self._create_empty_figure("暂无活动数据")
            
            # 统计活动类型
            activity_counts = {}
            for activity in activity_data:
                activity_type = activity.get('action_type', 'unknown')
                activity_counts[activity_type] = activity_counts.get(activity_type, 0) + 1
            
            # 创建饼图
            fig = go.Figure(data=[go.Pie(
                labels=list(activity_counts.keys()),
                values=list(activity_counts.values()),
                hole=0.3,
                marker=dict(colors=self.color_palette[:len(activity_counts)])
            )])
            
            fig.update_layout(
                title="活动类型分布",
                height=400
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"创建活动分布图表失败: {e}")
            return self._create_empty_figure("创建图表失败")
    
    def create_satisfaction_heatmap(self, satisfaction_matrix: List[List[float]],
                                  x_labels: List[str], y_labels: List[str]) -> go.Figure:
        """创建满意度热力图"""
        try:
            fig = go.Figure(data=go.Heatmap(
                z=satisfaction_matrix,
                x=x_labels,
                y=y_labels,
                colorscale='Viridis',
                colorbar=dict(title="满意度")
            ))
            
            fig.update_layout(
                title="代理满意度热力图",
                xaxis_title="时间步",
                yaxis_title="代理ID",
                height=400
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"创建满意度热力图失败: {e}")
            return self._create_empty_figure("创建图表失败")
    
    def create_resource_usage_chart(self, resource_data: Dict[str, List[float]]) -> go.Figure:
        """创建资源使用图表"""
        try:
            fig = go.Figure()
            
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
            
            for i, (resource_type, values) in enumerate(resource_data.items()):
                fig.add_trace(go.Scatter(
                    y=values,
                    mode='lines+markers',
                    name=resource_type,
                    line=dict(color=colors[i % len(colors)])
                ))
            
            fig.update_layout(
                title="资源使用趋势",
                xaxis_title="时间步",
                yaxis_title="资源量",
                height=400,
                hovermode='x unified'
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"创建资源使用图表失败: {e}")
            return self._create_empty_figure("创建图表失败")
    
    def _create_empty_figure(self, message: str = "暂无数据") -> go.Figure:
        """创建空图表"""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            height=400
        )
        return fig
    
    def create_performance_dashboard(self, performance_data: Dict[str, Any]) -> go.Figure:
        """创建性能仪表板"""
        try:
            # 创建多个指标的组合图表
            fig = make_subplots(
                rows=2, cols=3,
                subplot_titles=(
                    'CPU使用率', '内存使用', '仿真速度',
                    '代理响应时间', '错误率', '吞吐量'
                ),
                specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
                       [{"type": "scatter"}, {"type": "bar"}, {"type": "scatter"}]]
            )
            
            # 添加指标仪表
            cpu_usage = performance_data.get('cpu_usage', 0)
            fig.add_trace(go.Indicator(
                mode = "gauge+number",
                value = cpu_usage,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "CPU %"},
                gauge = {'axis': {'range': [None, 100]},
                        'bar': {'color': "darkblue"},
                        'bgcolor': "white",
                        'borderwidth': 2,
                        'bordercolor': "gray"}),
                row=1, col=1)
            
            return fig
            
        except Exception as e:
            logger.error(f"创建性能仪表板失败: {e}")
            return self._create_empty_figure("创建仪表板失败")