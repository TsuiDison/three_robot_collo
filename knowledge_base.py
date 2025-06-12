# knowledge_base.py
# -*- coding: utf-8 -*-
"""
定义共享知识地图模块
"""
import numpy as np
from config import TERRAIN_TYPES, TERRAIN_COLORS

class SharedKnowledgeMap:
    """
    一个所有智能体共享的、动态更新的地图知识库。
    """
    # --- 使用这个新的 __init__ 方法 ---
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # -1 代表未知地形
        self.terrain_types = TERRAIN_TYPES.copy()
        self.terrain_types['unknown'] = -1
        self.terrain = np.full((width, height), self.terrain_types['unknown'], dtype=int)
        
        # --- 核心修复：将颜色值归一化到 0-1 范围 ---
        self.color_map = {}
        # 迭代 config 中定义的颜色
        for name, color_hex in TERRAIN_COLORS.items():
            if name in self.terrain_types:
                terrain_id = self.terrain_types[name]
                # 将 #RRGGBB 转换为 (R/255, G/255, B/255) 的浮点数元组
                rgb_int = tuple(int(color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                self.color_map[terrain_id] = tuple(v / 255.0 for v in rgb_int)
        
        # 专门处理 'unknown' 颜色的归一化
        unknown_color_hex = TERRAIN_COLORS.get('unknown', '#141414') # 提供一个默认值
        rgb_int_unknown = tuple(int(unknown_color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        self.color_map[self.terrain_types['unknown']] = tuple(v / 255.0 for v in rgb_int_unknown)
        # --- 修改结束 ---

    def bulk_update(self, map_fragment: dict):
        """用一个地图碎片批量更新知识库"""
        for (x, y), terrain_id in map_fragment.items():
            if 0 <= x < self.width and 0 <= y < self.height:
                if self.terrain[x, y] == self.terrain_types['unknown']:
                    self.terrain[x, y] = terrain_id

    def get_terrain(self, x, y):
        """从知识库中获取地形名称"""
        x_int, y_int = int(round(x)), int(round(y))
        if 0 <= x_int < self.width and 0 <= y_int < self.height:
            terrain_type_id = self.terrain[x_int, y_int]
            for name, tid in self.terrain_types.items():
                if tid == terrain_type_id:
                    return name
        return 'unknown'

    def is_road(self, x, y):
        """从知识库中判断是否是道路"""
        x_int, y_int = int(round(x)), int(round(y))
        if 0 <= x_int < self.width and 0 <= y_int < self.height:
            return self.terrain[x_int, y_int] == self.terrain_types['road']
        return False