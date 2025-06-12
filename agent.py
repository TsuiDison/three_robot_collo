# -*- coding: utf-8 -*-
"""
智能体模块
定义机器狗、无人车、无人机三种智能体
"""

import random
import math
from enum import Enum
from typing import List, Tuple, Optional
from delivery_task import DeliveryTask


class AgentState(Enum):
    """智能体状态枚举"""
    IDLE = "idle"          # 空闲
    MOVING_TO_PICKUP = "moving_to_pickup"    # 前往取货点
    PICKING_UP = "picking_up"                # 取货中
    MOVING_TO_DELIVERY = "moving_to_delivery"  # 前往配送点
    DELIVERING = "delivering"                # 配送中
    RETURNING = "returning"                  # 返回基地


class Agent:
    """智能体基类"""
    
    def __init__(self, agent_id: str, agent_type: str, position: Tuple[int, int], 
                 max_weight: float, max_speed: float, energy_consumption: float):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.position = position
        self.max_weight = max_weight
        self.max_speed = max_speed
        self.energy_consumption = energy_consumption
        self.current_weight = 0.0
        self.energy = 100.0
        self.state = AgentState.IDLE
        self.current_task = None
        self.task_queue = []        self.target_position = None
        
    def can_handle_task(self, task: DeliveryTask) -> bool:
        """检查是否能处理指定任务"""
        # 检查任务是否有weight属性，如果没有则使用默认值
        task_weight = getattr(task, 'weight', getattr(task, 'cargo_weight', 1.0))
        return (self.state == AgentState.IDLE and 
                task_weight <= self.max_weight and
                self.energy > 20)  # 保留足够能量
    
    def assign_task(self, task: DeliveryTask):
        """分配任务给智能体"""
        if self.can_handle_task(task):
            self.current_task = task
            self.state = AgentState.MOVING_TO_PICKUP
            self.target_position = task.start_pos
            return True
        return False
    
    def calculate_distance(self, position: Tuple[int, int]) -> float:
        """计算到指定位置的距离"""
        return math.sqrt((self.position[0] - position[0])**2 + 
                        (self.position[1] - position[1])**2)
    
    def move_towards_target(self):
        """向目标位置移动"""
        if self.target_position is None:
            return
            
        dx = self.target_position[0] - self.position[0]
        dy = self.target_position[1] - self.position[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance <= self.max_speed:
            # 到达目标位置
            self.position = self.target_position
            self._handle_arrival()
        else:
            # 按速度移动
            move_x = (dx / distance) * self.max_speed
            move_y = (dy / distance) * self.max_speed
            self.position = (self.position[0] + move_x, self.position[1] + move_y)
        
        # 消耗能量
        self.energy -= self.energy_consumption
    def _handle_arrival(self):
        """处理到达目标位置的逻辑"""
        if self.state == AgentState.MOVING_TO_PICKUP:
            self.state = AgentState.PICKING_UP
            self.current_weight += self.current_task.weight
            # 设置配送目标
            self.target_position = self.current_task.goal_pos
            self.state = AgentState.MOVING_TO_DELIVERY
        elif self.state == AgentState.MOVING_TO_DELIVERY:
            self.state = AgentState.DELIVERING
            self.current_weight -= self.current_task.weight
            # 任务完成
            self.current_task = None
            self.state = AgentState.IDLE
            self.target_position = None
    
    def update(self):
        """更新智能体状态"""
        if self.state in [AgentState.MOVING_TO_PICKUP, AgentState.MOVING_TO_DELIVERY]:
            self.move_towards_target()


class RobotDog(Agent):
    """机器狗智能体"""
    
    def __init__(self, agent_id: str, position: Tuple[int, int]):
        super().__init__(
            agent_id=agent_id,
            agent_type="robot_dog",
            position=position,
            max_weight=5.0,      # 最大载重5kg
            max_speed=3.0,       # 速度3单位/步
            energy_consumption=0.8  # 能耗
        )
        self.terrain_adaptability = 0.9  # 地形适应性


class UnmannedVehicle(Agent):
    """无人车智能体"""
    
    def __init__(self, agent_id: str, position: Tuple[int, int]):
        super().__init__(
            agent_id=agent_id,
            agent_type="unmanned_vehicle",
            position=position,
            max_weight=50.0,     # 最大载重50kg
            max_speed=5.0,       # 速度5单位/步
            energy_consumption=1.2  # 能耗
        )
        self.road_preference = True  # 偏好道路行驶


class Drone(Agent):
    """无人机智能体"""
    
    def __init__(self, agent_id: str, position: Tuple[int, int]):
        super().__init__(
            agent_id=agent_id,
            agent_type="drone",
            position=position,
            max_weight=2.0,      # 最大载重2kg
            max_speed=8.0,       # 速度8单位/步（飞行速度快）
            energy_consumption=2.0  # 能耗高
        )
        self.flight_altitude = 50  # 飞行高度


def create_random_agents(map_width: int, map_height: int, 
                        num_dogs: int = 2, num_vehicles: int = 2, num_drones: int = 2) -> List[Agent]:
    """在地图上随机创建智能体"""
    agents = []
    
    # 创建机器狗
    for i in range(num_dogs):
        position = (random.randint(0, map_width-1), random.randint(0, map_height-1))
        agents.append(RobotDog(f"dog_{i+1}", position))
    
    # 创建无人车
    for i in range(num_vehicles):
        position = (random.randint(0, map_width-1), random.randint(0, map_height-1))
        agents.append(UnmannedVehicle(f"vehicle_{i+1}", position))
    
    # 创建无人机
    for i in range(num_drones):
        position = (random.randint(0, map_width-1), random.randint(0, map_height-1))
        agents.append(Drone(f"drone_{i+1}", position))
    
    return agents