# path_planning.py
# -*- coding: utf-8 -*-
"""
路径规划模块
实现A*算法在不完整的知识地图上进行路径规划 (鲁棒版)
返回路径和最终点与原始目标的距离
"""
import math
from queue import PriorityQueue

def a_star_planning(agent_capabilities, knowledge_map, start_pos, goal_pos):
    """
    A* 路径规划函数。
    返回一个元组 (path, final_distance)，其中：
    - path: 节点列表，如果无法规划则为 None。
    - final_distance: 路径终点与原始目标点的距离。
    """
    rules = agent_capabilities["terrain_rules"]
    start_node = tuple(map(int, start_pos))
    
    # --- 核心修改 1: 保存原始目标点 ---
    original_goal_node = tuple(map(int, goal_pos))
    goal_node = original_goal_node # 先将寻路目标设为原始目标
    # --- 修改结束 ---

    # 为 road_only 智能体特殊处理起点和终点
    if rules.get("road_only", False):
        if not knowledge_map.is_road(start_node[0], start_node[1]):
            nearest_road_start = find_nearest_road(knowledge_map, start_node)
            if not nearest_road_start:
                return None, float('inf') # 规划失败
            start_node = nearest_road_start

        if not knowledge_map.is_road(goal_node[0], goal_node[1]):
            nearest_road_goal = find_nearest_road(knowledge_map, goal_node)
            if not nearest_road_goal:
                return None, float('inf') # 规划失败
            goal_node = nearest_road_goal # 更新寻路目标为最近的公路点

    open_set = PriorityQueue()
    open_set.put((0, start_node))
    came_from = {}
    g_score = {start_node: 0}
    f_score = {start_node: heuristic(start_node, goal_node)}
    
    directions = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0),
                  (1, 1, 1.4), (1, -1, 1.4), (-1, 1, 1.4), (-1, -1, 1.4)]
    
    closest_node_to_goal = start_node
    # 注意：这里的 min_dist_to_goal 依然是和寻路目标 goal_node 比较
    min_dist_to_goal = heuristic(start_node, goal_node) 

    path_found = False
    while not open_set.empty():
        _, current = open_set.get()
        
        current_dist_to_goal = heuristic(current, goal_node)
        if current_dist_to_goal < min_dist_to_goal:
            min_dist_to_goal = current_dist_to_goal
            closest_node_to_goal = current

        if current == goal_node:
            path_found = True
            break # 找到精确路径，跳出循环

        # (循环内部逻辑保持不变)
        for dx, dy, move_cost in directions:
            neighbor = (current[0] + dx, current[1] + dy)
            if not (0 <= neighbor[0] < knowledge_map.width and 0 <= neighbor[1] < knowledge_map.height):
                continue
            terrain = knowledge_map.get_terrain(neighbor[0], neighbor[1])
            is_passable = True
            terrain_penalty = 0
            if rules.get("road_only", False) and not knowledge_map.is_road(neighbor[0], neighbor[1]): is_passable = False
            if terrain == 'water' and not rules.get("can_cross_water", False): is_passable = False
            if terrain == 'hilly': terrain_penalty = 2
            elif terrain == 'steep': terrain_penalty = 5
            if terrain_penalty > rules.get("climb_height", 0): is_passable = False
            if not is_passable: continue
            unknown_penalty = 0
            if terrain == 'unknown':
                unknown_penalty = 10 
                if rules.get("road_only", False): unknown_penalty = 50
            final_move_cost = move_cost * 0.8 if knowledge_map.is_road(neighbor[0], neighbor[1]) else move_cost
            tentative_g_score = g_score[current] + final_move_cost + terrain_penalty + unknown_penalty
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal_node)
                open_set.put((f_score[neighbor], neighbor))
    
    # --- 核心修改 2: 统一处理返回逻辑 ---
    final_node = None
    if path_found:
        final_node = goal_node # 如果找到了精确目标
    elif not rules.get("road_only", False):
        final_node = closest_node_to_goal # 对于非road_only, 回退到最近点
    
    if final_node:
        path = reconstruct_path(came_from, final_node)
        # 计算路径终点与原始目标的距离
        final_distance = heuristic(path[-1], original_goal_node)
        return path, final_distance
    else:
        # 对于 road_only 且找不到精确路径，或任何其他失败情况
        return None, float('inf')
    # --- 修改结束 ---

def find_nearest_road(knowledge_map, start_node):
    q = [(start_node, 0)]
    visited = {start_node}
    search_radius_limit = 20 
    while q:
        (x, y), dist = q.pop(0)
        if knowledge_map.is_road(x, y):
            return (x, y)
        if dist > search_radius_limit:
            continue
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) not in visited and 0 <= nx < knowledge_map.width and 0 <= ny < knowledge_map.height:
                visited.add((nx, ny))
                q.append(((nx, ny), dist + 1))
    return None

def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path

def heuristic(a, b):
    # 使用欧几里得距离的平方，或者实际的欧几里得距离，对于物理距离更准确
    return math.hypot(a[0] - b[0], a[1] - b[1])