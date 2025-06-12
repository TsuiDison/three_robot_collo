# path_planning.py
# -*- coding: utf-8 -*-
"""
路径规划模块
实现A*算法在不完整的知识地图上进行路径规划 (鲁棒版)
"""
import math
from queue import PriorityQueue

def a_star_planning(agent_capabilities, knowledge_map, start_pos, goal_pos):
    rules = agent_capabilities["terrain_rules"]
    start_node = tuple(map(int, start_pos))
    goal_node = tuple(map(int, goal_pos))

    # --- 核心修复 1：处理起点不在路上的情况 ---
    # 如果是 road_only 智能体，但起点不在路上，则先找到最近的道路点作为实际起点
    if rules["road_only"] and not knowledge_map.is_road(start_node[0], start_node[1]):
        nearest_road_start = find_nearest_road(knowledge_map, start_node)
        if not nearest_road_start: return None # 如果附近完全没有路
        start_node = nearest_road_start

    open_set = PriorityQueue()
    open_set.put((0, start_node))
    came_from = {}
    g_score = {start_node: 0}
    f_score = {start_node: heuristic(start_node, goal_node)}
    
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    
    # --- 核心修复 2：放宽到达条件 ---
    # 如果目标本身不在路上，我们需要找到离目标最近的路点
    closest_node_to_goal = start_node
    min_dist_to_goal = heuristic(start_node, goal_node)

    while not open_set.empty():
        _, current = open_set.get()
        
        # 更新离目标最近的可达节点
        current_dist_to_goal = heuristic(current, goal_node)
        if current_dist_to_goal < min_dist_to_goal:
            min_dist_to_goal = current_dist_to_goal
            closest_node_to_goal = current

        # 如果直接到达目标，完美
        if current == goal_node:
            return reconstruct_path(came_from, current)

        for dx, dy in directions:
            # ... (邻居检查和成本计算逻辑保持不变)
            neighbor = (current[0] + dx, current[1] + dy)
            if not (0 <= neighbor[0] < knowledge_map.width and 0 <= neighbor[1] < knowledge_map.height): continue
            terrain = knowledge_map.get_terrain(neighbor[0], neighbor[1]); is_on_road = knowledge_map.is_road(neighbor[0], neighbor[1])
            if rules["road_only"] and not is_on_road: continue
            if not rules["can_cross_water"] and terrain == 'water': continue
            terrain_penalty = 0
            if terrain == 'hilly': terrain_penalty = 2
            elif terrain == 'steep': terrain_penalty = 5
            if terrain_penalty > rules["climb_height"]: continue
            unknown_penalty = 0
            if terrain == 'unknown':
                unknown_penalty = 10 
                if rules["road_only"]: unknown_penalty = 50
            move_cost = 0.8 if is_on_road else 1.0; final_cost = move_cost + terrain_penalty + unknown_penalty
            tentative_g_score = g_score[current] + final_cost
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current; g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal_node); open_set.put((f_score[neighbor], neighbor))
    
    # 如果 open_set 空了都没能到达 goal_node (可能 goal 不可达)
    # 就返回到达过的、离目标最近的节点的路径
    #print(f"警告: 无法直接到达 {goal_node}。规划到最近点 {closest_node_to_goal}。")
    return reconstruct_path(came_from, closest_node_to_goal)

def find_nearest_road(knowledge_map, start_node):
    """一个简单的广度优先搜索，从一个点开始找到最近的道路格子"""
    q = [(start_node, 0)]
    visited = {start_node}
    while q:
        (x, y), dist = q.pop(0)
        if knowledge_map.is_road(x, y):
            return (x, y)
        if dist > 10: # 搜索半径限制
            return None
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) not in visited and 0 <= nx < knowledge_map.width and 0 <= ny < knowledge_map.height:
                visited.add((nx, ny))
                q.append(((nx, ny), dist + 1))
    return None

def reconstruct_path(came_from, current):
    # (此函数保持不变)
    path = [current]
    while current in came_from:
        current = came_from[current]; path.append(current)
    path.reverse(); return path

def heuristic(a, b):
    # (此函数保持不变)
    return abs(a[0] - b[0]) + abs(a[1] - b[1])