# -*- coding: utf-8 -*-
"""
协作配送系统模块
负责载具选择、任务分配和配送执行
"""

import numpy as np
import threading
import queue
import time
import traceback
from vehicle_system import Drone, Car, RobotDog
from path_planning import a_star_planning


class CollaborativeDeliverySystem:
    """增强的协作配送系统类"""
    
    def __init__(self, map):
        self.map = map
        self.drones = [Drone((10, 10), (0, 0)) for _ in range(3)]
        self.cars = [Car((20, 20), (0, 0)) for _ in range(2)]
        self.robot_dogs = [RobotDog((30, 30), (0, 0)) for _ in range(2)]
        self.tasks = []
        self.task_queue = queue.Queue()
        self.lock = threading.Lock()
        self.current_paths = []  # 存储当前路径
        self.feedback = []       # 存储规划反馈
        self.paths_updated = False  # 路径更新标志
        self.vehicles_in_use = []  # 跟踪当前正在使用的载具
    
    def add_task(self, task):
        """将配送任务添加到队列"""
        self.task_queue.put(task)
        self.feedback.append(f"新任务已添加: 从 {task.start_pos} 到 {task.goal_pos}")
        self.paths_updated = True
    
    def vehicle_selector(self, task):
        """为给定任务选择最合适的载具"""
        # 定义载具类型及其能力
        vehicle_types = {
            "drone": {"speed": 15, "weight_limit": 5, "terrain_adaptability": 3, "cost": 2, "safety": 4},
            "car": {"speed": 5, "weight_limit": 100, "terrain_adaptability": 2, "cost": 1, "safety": 5},
            "robot_dog": {"speed": 7, "weight_limit": 20, "terrain_adaptability": 5, "cost": 1.5, "safety": 3}
        }
        
        # 基于任务需求为每种载具类型评分
        scores = {}
        
        # 获取任务需求，使用默认值
        weight = task.attributes.get(1, 0)
        urgency = task.attributes.get(5, 1)
        safety = task.attributes.get(4, 1)  # 如果未提供，默认为1
        cost_limit = task.attributes.get(6, float('inf'))  # 默认为无穷大
        cargo_type = task.attributes.get(8, "")
        
        # 检查起点和终点之间的地形
        start_terrain = self.map.get_terrain(task.start_pos[0], task.start_pos[1])
        goal_terrain = self.map.get_terrain(task.goal_pos[0], task.goal_pos[1])
        
        # 天气影响
        weather_effect = self.map.weather_effect
        
        for vehicle_type, capabilities in vehicle_types.items():
            # 检查载具是否能处理重量
            if weight > capabilities["weight_limit"]:
                scores[vehicle_type] = -1
                continue
            
            # 计算距离
            distance = np.sqrt((task.goal_pos[0] - task.start_pos[0])**2 + 
                              (task.goal_pos[1] - task.start_pos[1])**2)
            
            # 计算估计时间
            estimated_time = distance / capabilities["speed"] * weather_effect
            
            # 时间窗口考虑
            time_window = task.attributes.get(3, float('inf'))
            if time_window is None:
                time_window = float('inf')  # 默认设为无穷大
            
            if estimated_time > time_window:
                scores[vehicle_type] = -1
                continue
            
            # 地形适应性分数
            terrain_score = 0
            if start_terrain == 'water' and vehicle_type != 'drone':
                terrain_score = -1
            elif goal_terrain == 'water' and vehicle_type != 'drone':
                terrain_score = -1
            else:
                # 地形适应性越好分数越高
                terrain_score = capabilities["terrain_adaptability"]
            
            if terrain_score == -1:
                scores[vehicle_type] = -1
                continue
            
            # 紧急程度分数
            urgency_score = (1 / estimated_time) * urgency
            
            # 安全分数
            safety = safety if safety is not None else 1
            safety_score = capabilities["safety"] * safety
            
            # 成本分数 - 确保cost_limit有效
            cost_limit = cost_limit if cost_limit is not None else float('inf')
            estimated_cost = distance * capabilities["cost"] * weather_effect
            if estimated_cost > cost_limit:
                scores[vehicle_type] = -1
                continue
            cost_score = 1 / estimated_cost
            
            # 货物类型考虑
            if cargo_type == "fragile" and vehicle_type != "car":
                scores[vehicle_type] -= 5
            
            # 用权重组合分数
            total_score = (urgency_score * 0.4) + (safety_score * 0.3) + (cost_score * 0.3)
            
            scores[vehicle_type] = total_score
        
        # 找到分数最高的载具类型
        best_vehicle_type = max(scores, key=scores.get)
        if scores[best_vehicle_type] < 0:
            self.feedback.append(f"警告: 没有合适的交通工具可用于从 {task.start_pos} 到 {task.goal_pos} 的任务")
            return None
        
        # 选择最佳类型的第一个可用载具
        if best_vehicle_type == "drone":
            for drone in self.drones:
                if drone not in self.vehicles_in_use:
                    return drone
        elif best_vehicle_type == "car":
            for car in self.cars:
                if car not in self.vehicles_in_use:
                    return car
        elif best_vehicle_type == "robot_dog":
            for robot_dog in self.robot_dogs:
                if robot_dog not in self.vehicles_in_use:
                    return robot_dog
        
        self.feedback.append(f"警告: 所有 {best_vehicle_type} 都在使用中，任务从 {task.start_pos} 到 {task.goal_pos} 将等待")
        return None

    def assign_tasks(self):
        """将任务分配给可用载具"""
        while True:
            try:
                task = self.task_queue.get(block=False)
            except queue.Empty:
                time.sleep(1)  # 检查前等待一下
                continue
            
            # 为任务选择最佳载具
            vehicle = self.vehicle_selector(task)
            
            if vehicle:
                # 将起始位置设置为载具的当前位置
                task.start_pos = vehicle.current_pos
                
                # 标记载具为使用中
                self.vehicles_in_use.append(vehicle)
                
                # 规划路径
                path = a_star_planning(vehicle, self.map, task.start_pos, task.goal_pos)
                
                if path:
                    self.current_paths.append((vehicle, path, task))
                    self.feedback.append(f"任务分配成功: 从 {task.start_pos} 到 {task.goal_pos}, 使用 {type(vehicle).__name__}")
                    self.paths_updated = True
                    
                    # 启动线程执行配送
                    threading.Thread(target=self.execute_delivery, args=(vehicle, path, task), daemon=True).start()
                else:
                    self.feedback.append(f"错误: 无法为从 {task.start_pos} 到 {task.goal_pos} 的任务找到路径")
                    # 将任务放回队列
                    self.task_queue.put(task)
                    
                    # 释放载具
                    if vehicle in self.vehicles_in_use:
                        self.vehicles_in_use.remove(vehicle)
            else:
                # 没有可用载具，将任务放回队列
                self.task_queue.put(task)
                time.sleep(5)  # 重试前等待更长时间
    
    def execute_delivery(self, vehicle, path, task):
        """使用给定载具和路径执行配送任务"""
        try:
            self.feedback.append(f"{type(vehicle).__name__} 开始执行任务: 从 {task.start_pos} 到 {task.goal_pos}")
            
            # 沿路径移动
            while vehicle.current_waypoint_index < len(vehicle.path):
                if not vehicle.path:
                    break
                    
                if vehicle.current_waypoint_index < len(vehicle.path):
                    target_pos = vehicle.path[vehicle.current_waypoint_index]
                    vehicle.move_towards(target_pos, self.map)
                
                # 为可视化放慢速度
                time.sleep(0.01)
            
            # 配送完成
            self.feedback.append(f"任务完成: 从 {task.start_pos} 到 {task.goal_pos}, 使用 {type(vehicle).__name__}")
            
            # 返回基地 (简化)
            self.feedback.append(f"{type(vehicle).__name__} 正在返回基地")
            return_path = a_star_planning(vehicle, self.map, vehicle.current_pos, vehicle.start_pos)
            if return_path:
                # 沿返回路径移动
                while vehicle.current_waypoint_index < len(vehicle.path):
                    if vehicle.current_waypoint_index < len(vehicle.path):
                        target_pos = vehicle.path[vehicle.current_waypoint_index]
                        vehicle.move_towards(target_pos, self.map)
                    
                    # 为可视化放慢速度
                    time.sleep(0.01)
                
                self.feedback.append(f"{type(vehicle).__name__} 已返回基地")
            else:
                self.feedback.append(f"警告: {type(vehicle).__name__} 无法返回基地")
        except Exception as e:
            self.feedback.append(f"错误: 执行任务时发生异常: {str(e)}")
            # 打印详细的异常堆栈信息，帮助调试
            self.feedback.append(traceback.format_exc())
        finally:
            # 释放载具
            if vehicle in self.vehicles_in_use:
                self.vehicles_in_use.remove(vehicle)
            
            # 从当前路径中移除路径
            if (vehicle, path, task) in self.current_paths:
                self.current_paths.remove((vehicle, path, task))
            
            self.paths_updated = True