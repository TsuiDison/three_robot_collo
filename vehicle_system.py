# -*- coding: utf-8 -*-
"""
载具系统模块
定义各种载具类型及其移动行为
"""

import numpy as np
import math
import random


class Vehicle:
    """载具基类，具有更真实的移动行为"""
    
    def __init__(self, start_pos, goal_pos):
        self.start_pos = start_pos
        self.goal_pos = goal_pos
        self.current_pos = start_pos  # 维持浮点位置以实现平滑移动
        self.speed = 1.0  # 基础速度 (每步的网格单位)
        self.heading = 0  # 移动方向 (弧度)
        self.path = []    # 当前要遵循的路径
        self.current_waypoint_index = 0  # 路径中的当前路径点索引
        self.animation_state = {"position": start_pos, "rotation": 0}  # 用于动画
        self.id = id(self)  # 载具的唯一标识符
        self.path_trace = []  # 位置轨迹用于路径可视化
        self.color = "#{:06x}".format(random.randint(0, 0xFFFFFF))  # 每个载具的随机颜色
        self.max_turn_rate = math.pi / 8  # 每步的最大转向速率 (弧度)
        self.current_speed = 0  # 当前速度
        self.max_speed = 1.0  # 最大速度
    
    def heuristic(self, current_pos, goal_pos):
        """A*的启发函数 (欧几里得距离)"""
        return np.sqrt((current_pos[0] - goal_pos[0])**2 + (current_pos[1] - goal_pos[1])**2)
    
    def move_towards(self, target_pos, map):
        """朝目标位置平滑移动"""
        if not target_pos:
            return self.current_pos

        # 检查是否是无人机且目标位置包含高度
        is_drone = isinstance(self, Drone)
        requires_height = is_drone and len(target_pos) == 3

        if requires_height and len(self.current_pos) == 2:
            # 将当前位置升级为三维坐标
            self.current_pos = (*self.current_pos, self.min_height)

        # 解包目标位置
        if requires_height:
            target_x, target_y, target_z = target_pos
        else:
            target_x, target_y = target_pos

        # 当前位置可能是二元组或三元组
        current_x, current_y = self.current_pos[0], self.current_pos[1]

        # 计算方向向量
        dx = target_x - current_x
        dy = target_y - current_y
        distance = np.sqrt(dx*dx + dy*dy)

        # 检查是否到达路点
        if distance < self.speed * 0.5:
            self.current_waypoint_index += 1
            if self.current_waypoint_index < len(self.path):
                next_waypoint = self.path[self.current_waypoint_index]
                return self.move_towards(next_waypoint, map)
            return self.current_pos

        # 仅在有前进方向时移动
        if distance > 0:
            # 计算单位向量
            ux = dx / distance
            uy = dy / distance

            # 应用速度
            step = min(self.speed, distance)
            new_x = current_x + ux * step
            new_y = current_y + uy * step

            # 无人机高度处理（带安全保护）
            if requires_height:
                current_z = self.current_pos[2] if len(self.current_pos) == 3 else self.min_height
                z_dir = target_z - current_z
                z_distance = abs(z_dir)

                if z_distance > 0:
                    z_step = min(self.vertical_speed, z_distance) * np.sign(z_dir)
                    new_z = current_z + z_step
                    self.current_pos = (new_x, new_y, new_z)
                    self.animation_state["position"] = (new_x, new_y)
                    self.animation_state["height"] = new_z
                else:
                    self.current_pos = (new_x, new_y, current_z)
            else:
                # 非无人机情况
                self.current_pos = (new_x, new_y)
                self.animation_state["position"] = (new_x, new_y)

            # 更新航向
            self.heading = np.arctan2(uy, ux)
            self.animation_state["rotation"] = self.heading

            # 添加到路径轨迹
            self.path_trace.append(self.current_pos)

        return self.current_pos
    
    def interpolate_path(self):
        """在路径点之间插值以实现更平滑的移动"""
        if len(self.path) < 2:
            return self.path
            
        new_path = []
        for i in range(len(self.path) - 1):
            p1 = self.path[i]
            p2 = self.path[i+1]
            
            # 确定点之间的距离
            if len(p1) == 3:  # 无人机路径
                x1, y1, z1 = p1
                x2, y2, z2 = p2
                distance = np.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)
            else:
                x1, y1 = p1
                x2, y2 = p2
                distance = np.sqrt((x2-x1)**2 + (y2-y1)**2)
            
            # 插值的步数
            num_steps = max(2, int(distance / 0.5))  # 每0.5单位插值一次
            
            for step in range(num_steps):
                t = step / (num_steps - 1)
                if len(p1) == 3:  # 无人机路径
                    new_x = x1 + t*(x2-x1)
                    new_y = y1 + t*(y2-y1)
                    new_z = z1 + t*(z2-z1)
                    new_path.append((new_x, new_y, new_z))
                else:
                    new_x = x1 + t*(x2-x1)
                    new_y = y1 + t*(y2-y1)
                    new_path.append((new_x, new_y))
        
        return new_path


class Drone(Vehicle):
    """具有更真实飞行行为的增强无人机类"""
    
    def __init__(self, start_pos, goal_pos, max_height=20, min_height=5, max_speed=15):
        super().__init__(start_pos, goal_pos)
        self.max_height = max_height
        self.min_height = min_height
        self.max_speed = max_speed
        self.current_height = min_height
        self.speed = max_speed * 0.8  # 巡航速度
        self.vertical_speed = 1.0     # 上升/下降速度
        self.wind_effect = 1.0        # 风对移动的影响
        self.hovering = False         # 悬停状态
        
        # 动画特定属性
        self.animation_state["height"] = self.current_height
        self.animation_state["hovering"] = self.hovering
    
    def get_neighbors(self, current_pos):
        """获取A*规划的可能邻居位置"""
        x, y, z = current_pos
        neighbors = []
        
        # 水平移动
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                new_x = x + dx
                new_y = y + dy
                
                # 垂直移动
                for dz in [-1, 0, 1]:
                    new_z = z + dz
                    if self.min_height <= new_z <= self.max_height:
                        neighbors.append((new_x, new_y, new_z))
        
        return neighbors
    
    def cost(self, current_pos, next_pos):
        """计算考虑距离和高度变化的移动成本"""
        x1, y1, z1 = current_pos
        x2, y2, z2 = next_pos
        
        # 水平距离
        distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        
        # 高度变化成本
        height_change = abs(z2 - z1)
        
        # 风影响 (基于高度模拟)
        wind_factor = 1.0 + (z2 / self.max_height) * 0.5
        
        return distance * wind_factor + height_change * 2
    
    def height_penalty(self, z):
        """过高或过低的惩罚"""
        return 0.5 * (z - self.max_height)**2 if z > self.max_height else 0
    
    def takeoff(self):
        """起飞行为"""
        if self.current_height < self.max_height * 0.7:
            self.current_height += self.vertical_speed
            self.animation_state["height"] = self.current_height
            return True
        return False
    
    def land(self):
        """着陆行为"""
        if self.current_height > self.min_height:
            self.current_height -= self.vertical_speed
            self.animation_state["height"] = self.current_height
            return True
        return False
    
    def hover(self, duration=1):
        """在原地悬停一段时间"""
        self.hovering = True
        self.animation_state["hovering"] = self.hovering
        # 这里应该使用异步方式而不是阻塞
        self.hovering = False
        self.animation_state["hovering"] = self.hovering


class Car(Vehicle):
    """具有真实驾驶行为的增强汽车类"""
    
    def __init__(self, start_pos, goal_pos, max_speed=5):
        super().__init__(start_pos, goal_pos)
        self.max_speed = max_speed
        self.speed = max_speed * 0.7  # 巡航速度
        self.turning_radius = 2.0    # 最小转弯半径
        self.obey_traffic_rules = True  # 是否遵守交通规则
        self.stopped_at_intersection = False  # 在交叉口停车
        self.animation_state["turn_signal"] = "off"  # 左、右或关闭


class RobotDog(Vehicle):
    """具有真实移动的增强机器狗类"""
    
    def __init__(self, start_pos, goal_pos, max_speed=7):
        super().__init__(start_pos, goal_pos)
        self.max_speed = max_speed
        self.speed = max_speed * 0.6  # 巡航速度
        self.can_climb = True         # 可以攀爬小障碍物
        self.max_climb_height = 1.0   # 最大可攀爬高度
        self.battery_level = 100      # 电池电量 (0-100)
        self.animation_state["battery"] = self.battery_level