# -*- coding: utf-8 -*-
"""
地图系统模块
负责生成和管理仿真环境中的地形、道路、建筑物等元素
"""

import numpy as np
import random


class Map:
    """增强型地图类，具有更真实的地形特征"""
    
    def __init__(self, width=100, height=100):
        self.width = width
        self.height = height
        self.obstacles = []  # 物理障碍物
        self.rivers = []     # 河流障碍物
        self.roads = []      # 道路网络
        self.buildings = []  # 建筑物障碍物
        self.terrain = np.zeros((width, height))  # 地形类型: 0=normal, 1=steep, 2=narrow, 3=hilly
        self.terrain_types = {'normal': 0, 'steep': 1, 'narrow': 2, 'hilly': 3, 'water': 4, 'road': 5}
        self.weather = "clear"  # 当前天气条件
        self.weather_effect = 1.0  # 基于天气的影响乘数
        
        # 生成更真实的地形
        self._generate_terrain()
        self._generate_rivers()
        self._generate_roads()
        self._generate_buildings()
        self._generate_obstacles()
    
    def _generate_terrain(self):
        """使用简单的中点位移算法生成地形"""
        # 初始化为平坦地形
        noise = np.zeros((self.width, self.height))
        
        # 添加一些随机噪声
        for i in range(self.width):
            for j in range(self.height):
                noise[i, j] = np.random.normal(0, 0.3)
        
        # 模拟地形特征
        for i in range(2, 5):
            scale = 2 ** i
            for x in range(0, self.width, scale):
                for y in range(0, self.height, scale):
                    if x + scale < self.width and y + scale < self.height:
                        # 中点位移
                        mid_x = x + scale // 2
                        mid_y = y + scale // 2
                        
                        # 计算角点平均值加上一些随机性
                        avg = (noise[x, y] + noise[x+scale, y] + noise[x, y+scale] + noise[x+scale, y+scale]) / 4
                        noise[mid_x, mid_y] = avg + np.random.normal(0, 0.2)
                        
                        # 位移边缘中点
                        if mid_x - scale // 2 >= 0:
                            noise[mid_x - scale // 2, mid_y] = (noise[x, y] + noise[x, y+scale]) / 2 + np.random.normal(0, 0.1)
                        if mid_x + scale // 2 < self.width:
                            noise[mid_x + scale // 2, mid_y] = (noise[x+scale, y] + noise[x+scale, y+scale]) / 2 + np.random.normal(0, 0.1)
                        if mid_y - scale // 2 >= 0:
                            noise[mid_x, mid_y - scale // 2] = (noise[x, y] + noise[x+scale, y]) / 2 + np.random.normal(0, 0.1)
                        if mid_y + scale // 2 < self.height:
                            noise[mid_x, mid_y + scale // 2] = (noise[x, y+scale] + noise[x+scale, y+scale]) / 2 + np.random.normal(0, 0.1)
        
        # 将噪声标准化到[0, 1]
        noise_min = np.min(noise)
        noise_max = np.max(noise)
        if noise_max - noise_min > 0:
            noise = (noise - noise_min) / (noise_max - noise_min)
        
        # 基于噪声值分配地形类型
        for x in range(self.width):
            for y in range(self.height):
                if noise[x, y] < 0.2:
                    self.terrain[x, y] = self.terrain_types['water']
                elif noise[x, y] < 0.3:
                    self.terrain[x, y] = self.terrain_types['road']
                elif noise[x, y] < 0.4:
                    self.terrain[x, y] = self.terrain_types['normal']
                elif noise[x, y] < 0.7:
                    self.terrain[x, y] = self.terrain_types['hilly']
                elif noise[x, y] < 0.9:
                    self.terrain[x, y] = self.terrain_types['steep']
                else:
                    self.terrain[x, y] = self.terrain_types['narrow']
    
    def _generate_rivers(self):
        """生成河流障碍物"""
        num_rivers = random.randint(1, 3)
        for _ in range(num_rivers):
            width = random.randint(3, 8)
            start_x = random.randint(5, self.width - 5)
            start_y = random.randint(5, self.height - 5)
            
            river_points = [(start_x, start_y)]
            current_x, current_y = start_x, start_y
            
            # 生成具有一些随机性的河流路径
            for _ in range(random.randint(20, 40)):
                dx = random.randint(-2, 2)
                dy = random.choice([-3, -2, -1, 1, 2, 3])  # 偏向一个方向流动
                
                # 确保河流保持在边界内
                new_x = max(0, min(self.width - 1, current_x + dx))
                new_y = max(0, min(self.height - 1, current_y + dy))
                
                river_points.append((new_x, new_y))
                current_x, current_y = new_x, new_y
            
            # 将河流添加到障碍物和地形中
            self.rivers.append((river_points, width))
            for x, y in river_points:
                for dx in range(-width//2, width//2 + 1):
                    for dy in range(-width//2, width//2 + 1):
                        if dx*dx + dy*dy <= (width//2)**2:
                            nx = x + dx
                            ny = y + dy
                            if 0 <= nx < self.width and 0 <= ny < self.height:
                                self.terrain[nx, ny] = self.terrain_types['water']
    
    def _generate_roads(self):
        """生成道路网络"""
        # 主要水平道路
        num_horizontal = random.randint(3, 6)
        for i in range(num_horizontal):
            y = random.randint(10, self.height - 10)
            start_x = 0
            end_x = self.width - 1
            width = 3
            
            for x in range(start_x, end_x + 1):
                for dx in range(-width//2, width//2 + 1):
                    nx = x + dx
                    if 0 <= nx < self.width:
                        self.terrain[nx, y] = self.terrain_types['road']
                        if dx == 0:  # 道路中心
                            self.roads.append((nx, y))
        
        # 主要垂直道路
        num_vertical = random.randint(3, 6)
        for i in range(num_vertical):
            x = random.randint(10, self.width - 10)
            start_y = 0
            end_y = self.height - 1
            width = 3
            
            for y in range(start_y, end_y + 1):
                for dy in range(-width//2, width//2 + 1):
                    ny = y + dy
                    if 0 <= ny < self.height:
                        self.terrain[x, ny] = self.terrain_types['road']
                        if dy == 0:  # 道路中心
                            self.roads.append((x, ny))
    
    def _generate_buildings(self):
        """生成建筑物障碍物"""
        num_buildings = random.randint(15, 30)
        for _ in range(num_buildings):
            x = random.randint(5, self.width - 15)
            y = random.randint(5, self.height - 15)
            width = random.randint(3, 8)
            height = random.randint(3, 8)
            
            # 确保建筑物不与道路重叠
            overlap = False
            for bx in range(x, x + width):
                for by in range(y, y + height):
                    if self.terrain[bx, by] == self.terrain_types['road']:
                        overlap = True
                        break
                if overlap:
                    break
            
            if not overlap:
                self.buildings.append((x, y, width, height))
                for bx in range(x, x + width):
                    for by in range(y, y + height):
                        self.obstacles.append((bx, by, 0.5))  # 点障碍物的小半径
    
    def _generate_obstacles(self):
        """生成额外的随机障碍物"""
        num_obstacles = random.randint(20, 40)
        for _ in range(num_obstacles):
            x = random.randint(5, self.width - 5)
            y = random.randint(5, self.height - 5)
            radius = random.uniform(1, 5)
            
            # 确保障碍物不与道路或建筑物重叠
            if self.terrain[x, y] == self.terrain_types['road']:
                continue
            
            overlap = False
            for (bx, by, bw, bh) in self.buildings:
                if x >= bx and x < bx + bw and y >= by and y < by + bh:
                    overlap = True
                    break
            
            if not overlap:
                self.obstacles.append((x, y, radius))
    
    def set_weather(self, weather):
        """设置天气条件并更新天气影响"""
        self.weather = weather
        if weather == "clear":
            self.weather_effect = 1.0
        elif weather == "rainy":
            self.weather_effect = 1.3
        elif weather == "windy":
            self.weather_effect = 1.5
        elif weather == "stormy":
            self.weather_effect = 2.0
    
    def is_obstacle(self, x, y):
        """检查位置是否在障碍物内"""
        # 接受浮点位置，舍入到最近的整数
        x_int = int(round(x))
        y_int = int(round(y))
        for obs in self.obstacles:
            if np.sqrt((x_int - obs[0])**2 + (y_int - obs[1])**2) <= obs[2]:
                return True
        return False
    
    def is_road(self, x, y):
        """检查位置是否在道路上"""
        # 接受浮点位置，舍入到最近的整数
        x_int = int(round(x))
        y_int = int(round(y))
        return self.terrain[x_int, y_int] == self.terrain_types['road']
    
    def get_terrain(self, x, y):
        """获取位置的地形类型"""
        # 接受浮点位置，舍入到最近的整数
        x_int = int(round(x))
        y_int = int(round(y))
        terrain_type = self.terrain[x_int, y_int]
        for key, value in self.terrain_types.items():
            if value == terrain_type:
                return key
        return 'normal'
    
    def is_valid(self, x, y, vehicle_type=None):
        """检查位置对给定载具类型是否有效"""
        # 接受浮点位置，舍入到最近的整数
        x_int = int(round(x))
        y_int = int(round(y))
        
        if not (0 <= x_int < self.width and 0 <= y_int < self.height):
            return False
        
        # 检查障碍物
        if self.is_obstacle(x_int, y_int):
            return False
        
        # 载具特定约束
        if vehicle_type == "car" and not self.is_road(x_int, y_int):
            return False
        
        # 水域对除无人机外的所有载具都无效
        if self.get_terrain(x_int, y_int) == 'water' and vehicle_type != "drone":
            return False
        
        return True