# -*- coding: utf-8 -*-
"""
路径规划模块
实现A*算法用于载具路径规划
"""

import math
import numpy as np
from queue import PriorityQueue


def a_star_planning(vehicle, map, start_pos, goal_pos):
    """
    使用A*算法为给定的交通工具规划路径
    
    参数:
    vehicle: 交通工具对象
    map: 地图对象
    start_pos: 起点坐标
    goal_pos: 终点坐标
    
    返回:
    规划好的路径点列表
    """
    from vehicle_system import Drone, RobotDog
    
    # 确保无人机的起点和终点包含高度信息
    if isinstance(vehicle, Drone):
        # 添加默认高度(如果未提供)
        if len(start_pos) == 2:
            start_pos = (*start_pos, vehicle.min_height)
        if len(goal_pos) == 2:
            goal_pos = (*goal_pos, vehicle.min_height)
    
    # A*算法实现
    open_set = PriorityQueue()
    open_set.put((0, start_pos))
    came_from = {}
    g_score = {start_pos: 0}
    f_score = {start_pos: heuristic(start_pos, goal_pos)}
    
    # 定义相邻节点的移动方向
    if isinstance(vehicle, Drone):
        # 无人机可以在三维空间中移动
        directions = [
            (1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0),
            (0, 0, 1), (0, 0, -1),  # 垂直移动
            (1, 1, 0), (1, -1, 0), (-1, 1, 0), (-1, -1, 0),  # 对角线移动
            (1, 0, 1), (1, 0, -1), (-1, 0, 1), (-1, 0, -1),  # 水平和垂直组合
            (0, 1, 1), (0, 1, -1), (0, -1, 1), (0, -1, -1)   # 水平和垂直组合
        ]
    else:
        # 地面交通工具只能在二维平面上移动
        directions = [
            (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (1, -1), (-1, 1), (-1, -1)  # 对角线移动
        ]
    
    while not open_set.empty():
        _, current = open_set.get()
        
        # 到达目标点
        if distance(current, goal_pos) < 1.5:
            path = reconstruct_path(came_from, current)
            # 对路径进行插值以获得平滑的运动轨迹
            vehicle.path = path
            vehicle.path = vehicle.interpolate_path()
            vehicle.current_waypoint_index = 0
            return vehicle.path
        
        # 获取相邻节点
        for dx, *dyz in directions:  # 处理二维或三维移动
            if isinstance(vehicle, Drone):
                dy, dz = dyz
                neighbor = (current[0] + dx, current[1] + dy, current[2] + dz)
                
                # 检查高度约束
                if neighbor[2] < vehicle.min_height or neighbor[2] > vehicle.max_height:
                    continue
            else:
                dy = dyz[0] if dyz else 0
                neighbor = (current[0] + dx, current[1] + dy)
            
            # 检查是否在地图范围内
            if not (0 <= neighbor[0] < map.width and 0 <= neighbor[1] < map.height):
                continue
            
            # 检查障碍物(考虑交通工具的类型)
            if isinstance(vehicle, Drone):
                # 无人机只需要避开建筑物和障碍物
                if map.is_obstacle(neighbor[0], neighbor[1]):
                    continue
            else:
                # 地面交通工具需要考虑地形和障碍物
                terrain = map.get_terrain(neighbor[0], neighbor[1])
                if terrain == 'water' or map.is_obstacle(neighbor[0], neighbor[1]):
                    continue
                if terrain == 'steep' and not isinstance(vehicle, RobotDog):
                    continue  # 只有机器狗可以在陡峭地形上移动
            
            # 考虑天气影响
            weather_effect = map.weather_effect
            
            # 计算移动成本
            if isinstance(vehicle, Drone):
                # 无人机在不同天气下的移动成本
                move_cost = 1.0 * weather_effect
                if map.get_terrain(neighbor[0], neighbor[1]) == 'water':
                    move_cost *= 1.2  # 水面上方飞行略微困难
            else:
                # 地面交通工具在不同地形上的移动成本
                terrain = map.get_terrain(neighbor[0], neighbor[1])
                if terrain == 'normal':
                    move_cost = 1.0 * weather_effect
                elif terrain == 'road':
                    move_cost = 0.8 * weather_effect  # 道路上移动更快
                elif terrain == 'steep':
                    move_cost = 2.0 * weather_effect  # 陡峭地形移动更慢
                elif terrain == 'narrow':
                    move_cost = 1.5 * weather_effect  # 狭窄地形移动更慢
                elif terrain == 'hilly':
                    move_cost = 1.8 * weather_effect  # 丘陵地形移动更慢
                else:  # water
                    move_cost = float('inf')  # 地面交通工具不能在水上行驶
            
            # 计算新的g值
            tentative_g_score = g_score[current] + move_cost
            
            # 如果新路径更好，则记录它
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal_pos)
                open_set.put((f_score[neighbor], neighbor))
    
    # 如果无法找到路径
    return None


def reconstruct_path(came_from, current):
    """从A*算法的结果中重构路径"""
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path


def heuristic(a, b):
    """计算两点之间的启发式估计值(曼哈顿距离)"""
    if len(a) == 3 and len(b) == 3:
        return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])
    else:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])


def distance(a, b):
    """计算两点之间的欧几里得距离"""
    if len(a) == 3 and len(b) == 3:
        return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2 + (a[2] - b[2])**2)
    else:
        return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)