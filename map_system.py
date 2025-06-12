# map_system.py
# -*- coding: utf-8 -*-
"""
地图系统模块 (最终演示版)
创建一个既有宏观地貌（大河、大山、大湖）又包含随机细节的复杂地图。
"""

import numpy as np
import random
import noise
from path_planning import a_star_planning
from config import TERRAIN_TYPES, MAP_CONFIG

class Map:
    def __init__(self, width=MAP_CONFIG['width'], height=MAP_CONFIG['height']):
        self.width = width
        self.height = height
        self.obstacles = []
        self.buildings = []
        self.warehouse = None
        self.relay_station = None
        self.terrain = np.full((width, height), TERRAIN_TYPES['normal'], dtype=int)
        self.terrain_types = TERRAIN_TYPES
        
        print("正在生成最终演示版地图...")
        self._generate_final_demo_map()
        print("最终演示版地图生成完毕。")

    def _generate_final_demo_map(self):
        """混合生成策略，确保关键地貌存在"""
        # 1. 手动雕刻宏观地貌：山脉、河流、湖泊
        self._carve_macro_features()
        
        # 2. 放置关键建筑
        self._generate_warehouse()
        self._generate_relay_station()
        
        # 3. 使用A*规划并建造智能主干道
        self._generate_smart_roads()
        
        # 4. 在道路附近生成城市建筑集群
        self._generate_building_clusters()
        
        # 5. 生成随机障碍物
        self._generate_obstacles()

    def _carve_macro_features(self):
        """手动定义并用噪声填充宏观地貌"""
        print("雕刻宏观地貌：大山、大河、大湖...")
        seed = random.randint(0, 100)
        
        # --- 1. 创建右上角的雄伟山脉 ---
        mountain_rect = (60, 60, 40, 40) # x, y, w, h
        self._fill_area_with_noisy_terrain(mountain_rect, 
                                           [self.terrain_types['hilly'], self.terrain_types['steep']],
                                           scale=30.0, seed=seed)

        # --- 2. 创建左上角的大湖 ---
        lake_rect = (10, 60, 40, 30)
        self._fill_area_with_noisy_terrain(lake_rect, 
                                           [self.terrain_types['water'], self.terrain_types['normal']], # 用平原做湖岸
                                           scale=20.0, seed=seed+1)

        # --- 3. 开凿一条贯穿南北的大河 ---
        river_x = 62
        for y in range(self.height):
            # 用噪声给河道增加一点随机宽度
            wobble = int(noise.pnoise1(y / 15.0, base=seed+2) * 3)
            river_width = random.randint(2, 4) + wobble
            for i in range(river_width):
                if 0 <= river_x + i < self.width:
                    self.terrain[river_x + i, y] = self.terrain_types['water']

    def _fill_area_with_noisy_terrain(self, rect, terrain_ids, scale, seed):
        """一个辅助函数，用噪声在指定矩形区域内填充地形"""
        x_start, y_start, w, h = rect
        octaves = 4; persistence = 0.5; lacunarity = 2.0
        
        for x in range(x_start, x_start + w):
            for y in range(y_start, y_start + h):
                if 0 <= x < self.width and 0 <= y < self.height:
                    noise_value = noise.pnoise2(x / scale, y / scale, octaves=octaves,
                                                persistence=persistence, lacunarity=lacunarity, base=seed)
                    # 根据噪声值选择地形
                    # 将 -1 到 1 的噪声映射到 terrain_ids 的索引
                    t_index = int((noise_value + 1) / 2 * len(terrain_ids))
                    t_index = min(t_index, len(terrain_ids) - 1) # 确保索引不越界
                    self.terrain[x, y] = terrain_ids[t_index]

    def _generate_warehouse(self):
        w, h, x, y = 10, 10, 5, 5
        self.warehouse = { "rect": (x, y, w, h), "center": (x + w / 2, y + h / 2), "color": "#FFD700" }

    def _generate_relay_station(self):
        w, h = 8, 8; x, y = self.width // 2 - w // 2, self.height // 2 - h // 2
        self.relay_station = { "rect": (x, y, w, h), "center": (x + w / 2, y + h / 2), "color": "#00FFFF" }

    def _generate_smart_roads(self):
        print("使用A*规划智能道路骨架...")
        road_planner_caps = {"terrain_rules": {"road_only": False, "can_cross_water": False, "can_climb": True, "climb_height": 10}}
        city_nodes = [tuple(map(int, self.warehouse["center"])), tuple(map(int, self.relay_station["center"])),
                      (self.width - 15, self.height - 15), (self.width - 15, 15), (15, self.height - 15)]
        
        # 强制在河流上建造一座桥
        bridge_y = 45
        for x in range(60, 70): self.terrain[x, bridge_y] = self.terrain_types['road']
        city_nodes.append((65, bridge_y)) # 将桥的中心也作为一个关键节点

        for i in range(len(city_nodes)):
            for j in range(i + 1, len(city_nodes)):
                path = a_star_planning(road_planner_caps, self, city_nodes[i], city_nodes[j])
                if path:
                    for x, y in path:
                        if self.terrain[x, y] != self.terrain_types['water']:
                            self.terrain[x, y] = self.terrain_types['road']
        
        for facility in [self.warehouse, self.relay_station]:
            rect = facility['rect']
            for i in range(rect[0], rect[0] + rect[2]):
                for j in range(rect[1], rect[1] + rect[3]):
                    self.terrain[i,j] = self.terrain_types['road']

    def _generate_building_clusters(self):
        print("生成建筑集群...")
        num_clusters = 30
        road_coords = np.argwhere(self.terrain == self.terrain_types['road'])
        if len(road_coords) == 0: return
        self.buildings = []
        for _ in range(num_clusters):
            center_y, center_x = random.choice(road_coords)
            if self.terrain[center_x, center_y] != self.terrain_types['road']: continue
            num_buildings = random.randint(5, 15); cluster_radius = 15
            for _ in range(num_buildings):
                dx, dy = random.randint(-cluster_radius, cluster_radius), random.randint(-cluster_radius, cluster_radius)
                bx, by = center_x + dx, center_y + dy; w, h = random.randint(2, 4), random.randint(2, 4)
                if 0 <= bx < self.width - w and 0 <= by < self.height - h:
                    is_overlapping = any(bx < obx + obw and bx + w > obx and by < oby + obh and by + h > oby for obx, oby, obw, obh in self.buildings)
                    is_on_road = np.any(self.terrain[bx:bx+w, by:by+h] == self.terrain_types['road'])
                    if not is_overlapping and not is_on_road:
                        self.buildings.append((bx, by, w, h))
                        self.terrain[bx:bx+w, by:by+h] = self.terrain_types['building']
    
    def _generate_obstacles(self):
        for _ in range(random.randint(MAP_CONFIG['min_obstacles'], MAP_CONFIG['max_obstacles'])):
            x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
            if self.terrain[x, y] == self.terrain_types['normal']:
                self.obstacles.append((x, y, random.uniform(0.5, 2.0)))
    
    # --- 查询方法保持不变 ---
    def is_road(self, x, y):
        x_int, y_int = int(round(x)), int(round(y))
        if 0 <= x_int < self.width and 0 <= y_int < self.height:
            return self.terrain[x_int, y_int] == self.terrain_types['road']
        return False

    def get_terrain(self, x, y):
        x_int, y_int = int(round(x)), int(round(y))
        if 0 <= x_int < self.width and 0 <= y_int < self.height:
            terrain_type_id = self.terrain[x_int, y_int]
            for name, tid in self.terrain_types.items():
                if tid == terrain_type_id:
                    return name
        return 'normal'