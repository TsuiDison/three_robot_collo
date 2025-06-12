# -*- coding: utf-8 -*-
"""
协作配送系统模块
实现多智能体协作配送的核心逻辑
"""

from typing import List, Dict, Tuple, Optional
import random
import math
from delivery_task import DeliveryTask
from agent_fixed import Agent, AgentState, create_random_agents


class CollaborativeDeliverySystem:
    """协作配送系统"""
    
    def __init__(self, map):
        self.map = map
        self.tasks = []
        self.completed_tasks = []
        
        # 创建随机分布的智能体
        self.agents = create_random_agents(
            map.width, map.height,
            num_dogs=2, num_vehicles=2, num_drones=2
        )
        
        print(f"智能体初始化完成:")
        for agent in self.agents:
            print(f"  {agent.agent_type} {agent.agent_id} 位置: {agent.position}")
    
    def add_task(self, task: DeliveryTask):
        """添加配送任务"""
        self.tasks.append(task)
        print(f"新任务添加: 从 {task.start_pos} 到 {task.goal_pos}")
        self._assign_best_agent(task)
    
    def _assign_best_agent(self, task: DeliveryTask) -> bool:
        """为任务分配最佳智能体（基于距离权重和空闲状态）"""
        # 获取所有空闲且能处理该任务的智能体
        available_agents = [agent for agent in self.agents if agent.can_handle_task(task)]
        
        if not available_agents:
            print(f"警告: 没有可用的智能体处理任务 {task}")
            return False
        
        # 计算每个智能体到任务取货点的距离权重
        best_agent = None
        min_weighted_distance = float('inf')
        
        for agent in available_agents:
            distance = agent.calculate_distance(task.start_pos)
            
            # 根据智能体类型和任务特性计算权重
            weight_factor = self._calculate_weight_factor(agent, task)
            weighted_distance = distance * weight_factor
            
            if weighted_distance < min_weighted_distance:
                min_weighted_distance = weighted_distance
                best_agent = agent
        
        if best_agent and best_agent.assign_task(task):
            print(f"任务分配成功: {best_agent.agent_type} {best_agent.agent_id} "
                  f"(距离: {best_agent.calculate_distance(task.start_pos):.1f})")
            return True
        
        print(f"任务分配失败")
        return False
    
    def _calculate_weight_factor(self, agent: Agent, task: DeliveryTask) -> float:
        """计算智能体处理任务的权重因子"""
        weight_factor = 1.0
        
        # 获取任务重量
        task_weight = getattr(task, 'weight', getattr(task, 'cargo_weight', 1.0))
        
        # 根据载重能力调整权重
        if task_weight > agent.max_weight * 0.8:
            weight_factor *= 1.5  # 重任务增加权重
        
        # 根据智能体类型调整权重
        if agent.agent_type == "drone":
            if hasattr(task, 'urgency') and task.urgency >= 4:
                weight_factor *= 0.7  # 无人机适合紧急任务
            if hasattr(task, 'cargo_type') and task.cargo_type == "fragile":
                weight_factor *= 1.3  # 易碎品不太适合无人机
        
        elif agent.agent_type == "unmanned_vehicle":
            if task_weight > 10:
                weight_factor *= 0.8  # 无人车适合重货
            
        elif agent.agent_type == "robot_dog":
            if hasattr(task, 'safety') and task.safety >= 3:
                weight_factor *= 0.9  # 机器狗适合安全要求高的任务
        
        return weight_factor
    
    def update_system(self):
        """更新系统状态"""
        # 更新所有智能体
        for agent in self.agents:
            agent.update()
            
            # 检查任务完成
            if (agent.state == AgentState.IDLE and 
                agent.current_task is None and 
                len([t for t in self.tasks if not hasattr(t, 'completed')]) > 0):
                # 尝试分配新任务
                pending_tasks = [t for t in self.tasks if not hasattr(t, 'completed')]
                if pending_tasks:
                    self._assign_best_agent(pending_tasks[0])
    
    def get_idle_agents(self) -> List[Agent]:
        """获取所有空闲的智能体"""
        return [agent for agent in self.agents if agent.state == AgentState.IDLE]
    
    def get_busy_agents(self) -> List[Agent]:
        """获取所有忙碌的智能体"""
        return [agent for agent in self.agents if agent.state != AgentState.IDLE]
    
    def get_system_status(self) -> Dict:
        """获取系统状态信息"""
        idle_agents = self.get_idle_agents()
        busy_agents = self.get_busy_agents()
        
        status = {
            "total_agents": len(self.agents),
            "idle_agents": len(idle_agents),
            "busy_agents": len(busy_agents),
            "pending_tasks": len([t for t in self.tasks if not hasattr(t, 'completed')]),
            "completed_tasks": len(self.completed_tasks),
            "agents_detail": []
        }
        
        for agent in self.agents:
            agent_info = {
                "id": agent.agent_id,
                "type": agent.agent_type,
                "position": agent.position,
                "state": agent.state.value,
                "energy": agent.energy,
                "current_weight": agent.current_weight
            }
            status["agents_detail"].append(agent_info)
        
        return status
    
    # 为了兼容性保留的属性
    @property
    def robot_dogs(self):
        return [agent for agent in self.agents if agent.agent_type == "robot_dog"]
    
    @property 
    def unmanned_vehicles(self):
        return [agent for agent in self.agents if agent.agent_type == "unmanned_vehicle"]
    
    @property
    def drones(self):
        return [agent for agent in self.agents if agent.agent_type == "drone"]
    
    @property
    def all_agents(self):
        return self.agents