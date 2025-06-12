# vehicle.py
# -*- coding: utf-8 -*-
"""
载具系统模块
定义各种载具类型及其移动行为
"""

import math
import random

class Vehicle:
    """载具基类"""

    def __init__(self, start_pos: tuple, goal_pos: tuple, max_speed: float):
        self.start_pos = start_pos
        self.goal_pos = goal_pos
        self.max_speed = max_speed
        self.speed = max_speed # 当前速度可以动态变化，但先初始化为最大速度

        self.current_pos = tuple(map(float, start_pos))
        self.path = []
        self.path_trace = [start_pos]
        self.color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
        
        # 创建 animation_state 字典，以避免 AttributeError
        self.animation_state = {"position": self.current_pos, "rotation": 0}

    def move_towards(self, target_pos, map_instance=None):
        """朝目标位置平滑移动，每次移动一小步"""
        if not target_pos: return

        target_x, target_y = target_pos
        current_x, current_y = self.current_pos

        dx = target_x - current_x
        dy = target_y - current_y
        distance = math.hypot(dx, dy)

        # --- 核心修改：亚像素移动 ---
        # 定义每一步的移动距离，而不是用速度
        step_distance = 0.5 # 每次只移动0.5个像素，动画会非常平滑
        
        if distance < step_distance:
            self.current_pos = tuple(map(float, target_pos))
        else:
            ux = dx / distance
            uy = dy / distance
            # 乘以固定的步长，而不是 speed
            new_x = current_x + ux * step_distance
            new_y = current_y + uy * step_distance
            self.current_pos = (new_x, new_y)
        
        self.path_trace.append(self.current_pos)


class Drone(Vehicle):
    """无人机载具"""
    def __init__(self, start_pos: tuple, goal_pos: tuple, max_speed: float):
        # 必须先调用父类的 __init__ 方法！
        super().__init__(start_pos, goal_pos, max_speed)
        
        # --- 新增/修复属性 ---
        self.min_height = 5
        self.max_height = 20
        self.current_height = self.min_height
        self.animation_state["height"] = self.current_height


class Car(Vehicle):
    """无人车载具"""
    def __init__(self, start_pos: tuple, goal_pos: tuple, max_speed: float):
        super().__init__(start_pos, goal_pos, max_speed)
        # Car 特有的属性
        self.animation_state["turn_signal"] = "off"


class RobotDog(Vehicle):
    """机器狗载具"""
    def __init__(self, start_pos: tuple, goal_pos: tuple, max_speed: float):
        super().__init__(start_pos, goal_pos, max_speed)
        # RobotDog 特有的属性
        self.battery_level = 100.0
        self.animation_state["battery"] = self.battery_level