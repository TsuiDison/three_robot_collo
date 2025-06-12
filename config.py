# -*- coding: utf-8 -*-
"""
配置模块
系统配置参数和常量定义
"""

# 地图配置
MAP_CONFIG = {
    'width': 100,
    'height': 100,
    'min_rivers': 1,
    'max_rivers': 3,
    'min_buildings': 15,
    'max_buildings': 30,
    'min_obstacles': 20,
    'max_obstacles': 40
}

# 载具配置
VEHICLE_CONFIG = {
    'drone': {
        'count': 3,
        'speed': 15,
        'weight_limit': 5,
        'max_height': 20,
        'min_height': 5,
        'vertical_speed': 1.0
    },
    'car': {
        'count': 2,
        'speed': 5,
        'weight_limit': 100,
        'turning_radius': 2.0
    },
    'robot_dog': {
        'count': 2,
        'speed': 7,
        'weight_limit': 20,
        'max_climb_height': 1.0
    }
}

# 天气效果配置
WEATHER_EFFECTS = {
    'clear': 1.0,
    'rainy': 1.3,
    'windy': 1.5,
    'stormy': 2.0
}

TERRAIN_TYPES = {
    'normal': 0,
    'steep': 1,
    'narrow': 2,
    'hilly': 3,
    'water': 4,
    'road': 5,
    'building': 6 # 新增：为建筑分配一个ID
}

# --- 地形颜色配置 (增加 building) ---
TERRAIN_COLORS = {
    'normal': '#76B947',
    'hilly': '#B8A073',
    'steep': '#8B4513',
    'water': '#5D9CEC',
    'road': '#6E6E6E',
    'building': '#BDBDBD', # 使用与之前相同的浅灰色
    'unknown': '#1C1C1C'
}


# --- 新增：其他可视化颜色配置 ---
VISUALIZATION_COLORS = {
    'warehouse': '#FFD700',  # 金色
    'relay_station': '#00FFFF', # 青色
    'building': '#BDBDBD',   # 浅灰色建筑
    'obstacle': '#FF6347',    # 番茄红障碍物，醒目
    'agent_path': '#FFFF00'   # 亮黄色路径
}

# 可视化配置
VISUALIZATION_CONFIG = {
    'window_width': 1200,
    'window_height': 800,
    'animation_interval': 50,
    'path_alpha': 0.7,
    'trace_alpha': 0.5
}

# 任务属性ID映射
TASK_ATTRIBUTES = {
    'weight': 1,
    'volume': 2,
    'time_window': 3,
    'safety': 4,
    'urgency': 5,
    'cost_limit': 6,
    'scalability': 7,
    'cargo_type': 8
}