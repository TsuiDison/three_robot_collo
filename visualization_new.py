# -*- coding: utf-8 -*-
"""
可视化模块
显示多智能体协作配送系统的实时状态
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from matplotlib.patches import Circle
from agent_fixed import AgentState
import threading
import time


class DeliveryVisualizer:
    """配送系统可视化器"""
    
    def __init__(self, delivery_system, map):
        self.delivery_system = delivery_system
        self.map = map
        
        # 设置图形
        self.fig, self.ax = plt.subplots(figsize=(12, 10))
        self.ax.set_xlim(0, map.width)
        self.ax.set_ylim(0, map.height)
        self.ax.set_title('多智能体协作配送系统仿真', fontsize=16)
        self.ax.set_xlabel('X坐标')
        self.ax.set_ylabel('Y坐标')
        
        # 智能体颜色映射
        self.agent_colors = {
            'robot_dog': 'brown',
            'unmanned_vehicle': 'blue', 
            'drone': 'red'
        }
        
        # 状态颜色映射
        self.state_colors = {
            AgentState.IDLE: 'green',
            AgentState.MOVING_TO_PICKUP: 'orange',
            AgentState.PICKING_UP: 'yellow',
            AgentState.MOVING_TO_DELIVERY: 'purple',
            AgentState.DELIVERING: 'pink',
            AgentState.RETURNING: 'gray'
        }
        
        # 初始化绘图元素
        self.agent_plots = {}
        self.task_plots = []
        self.info_text = None
        
        # 启动系统更新线程
        self.running = True
        self.update_thread = threading.Thread(target=self._update_system)
        self.update_thread.daemon = True
        self.update_thread.start()
    
    def _update_system(self):
        """后台更新系统状态"""
        while self.running:
            self.delivery_system.update_system()
            #time.sleep(0.01)  # 100ms更新一次
    
    def animate(self, frame):
        """动画更新函数"""
        self.ax.clear()
        self.ax.set_xlim(0, self.map.width)
        self.ax.set_ylim(0, self.map.height)
        self.ax.set_title('多智能体协作配送系统仿真', fontsize=16)
        self.ax.set_xlabel('X坐标')
        self.ax.set_ylabel('Y坐标')
        
        # 绘制地图网格
        self.ax.grid(True, alpha=0.3)
        
        # 绘制智能体
        for agent in self.delivery_system.agents:
            x, y = agent.position
            
            # 根据智能体类型选择标记
            if agent.agent_type == 'robot_dog':
                marker = 's'  # 方形
                size = 100
            elif agent.agent_type == 'unmanned_vehicle':
                marker = '^'  # 三角形
                size = 150
            elif agent.agent_type == 'drone':
                marker = 'o'  # 圆形
                size = 80
            
            # 根据状态选择颜色
            color = self.state_colors.get(agent.state, 'black')
            
            # 绘制智能体
            self.ax.scatter(x, y, c=color, marker=marker, s=size, 
                           edgecolors='black', linewidth=1, alpha=0.8)
            
            # 添加智能体标签
            self.ax.annotate(f'{agent.agent_id}\n{agent.state.value}', 
                           (x, y), xytext=(5, 5), textcoords='offset points',
                           fontsize=8, ha='left')
            
            # 绘制目标位置连线
            if agent.target_position:
                target_x, target_y = agent.target_position
                self.ax.plot([x, target_x], [y, target_y], 
                           color=color, linestyle='--', alpha=0.6)
                self.ax.scatter(target_x, target_y, c='red', marker='x', s=50)
          # 绘制任务位置
        for i, task in enumerate(self.delivery_system.tasks):
            if not hasattr(task, 'completed'):
                # 取货点
                pickup_x, pickup_y = task.start_pos
                self.ax.scatter(pickup_x, pickup_y, c='green', marker='D', 
                               s=60, label='取货点' if i == 0 else "")
                
                # 配送点
                delivery_x, delivery_y = task.goal_pos
                self.ax.scatter(delivery_x, delivery_y, c='red', marker='*', 
                               s=80, label='配送点' if i == 0 else "")
                
                # 连线
                self.ax.plot([pickup_x, delivery_x], [pickup_y, delivery_y], 
                           'k--', alpha=0.3)
        
        # 添加图例
        legend_elements = []
        for agent_type, color in self.agent_colors.items():
            if agent_type == 'robot_dog':
                marker = 's'
            elif agent_type == 'unmanned_vehicle':
                marker = '^'
            else:
                marker = 'o'
            legend_elements.append(plt.scatter([], [], c=color, marker=marker, 
                                             label=agent_type, s=100))
        
        self.ax.legend(handles=legend_elements, loc='upper right')
        
        # 显示系统状态信息
        status = self.delivery_system.get_system_status()
        info_text = f"""系统状态:
总智能体: {status['total_agents']}
空闲: {status['idle_agents']}
忙碌: {status['busy_agents']}
待处理任务: {status['pending_tasks']}
已完成: {status['completed_tasks']}"""
        
        self.ax.text(0.02, 0.98, info_text, transform=self.ax.transAxes,
                    verticalalignment='top', bbox=dict(boxstyle='round', 
                    facecolor='wheat', alpha=0.8))
    
    def start_animation(self):
        """启动动画"""
        ani = animation.FuncAnimation(self.fig, self.animate, interval=500, 
                                     cache_frame_data=False)
        plt.show()
        self.running = False