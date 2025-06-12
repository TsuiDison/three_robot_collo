# -*- coding: utf-8 -*-
"""
配送任务模块
定义配送任务类和相关属性
"""


class DeliveryTask:
    """配送任务类"""
    
    def __init__(self, start_pos, goal_pos, weight=None, volume=None, time_window=None, 
                 safety=None, urgency=None, cost_limit=None, scalability=None, cargo_type=None):
        """
        初始化配送任务
        
        参数:
        start_pos: 起始位置
        goal_pos: 目标位置
        weight: 重量限制
        volume: 体积限制
        time_window: 时间窗口
        safety: 安全需求
        urgency: 紧急程度
        cost_limit: 成本限制
        scalability: 可扩展性需求
        cargo_type: 货物类型
        """
        self.start_pos = start_pos
        self.goal_pos = goal_pos
        
        # 为了兼容性，同时设置直接属性和attributes字典
        self.weight = weight if weight is not None else 1.0
        self.volume = volume
        self.time_window = time_window
        self.safety = safety
        self.urgency = urgency
        self.cost_limit = cost_limit
        self.scalability = scalability
        self.cargo_type = cargo_type
        
        self.attributes = {
            1: weight,       # 重量限制
            2: volume,       # 体积限制
            3: time_window,  # 时间窗口
            4: safety,       # 安全需求
            5: urgency,      # 紧急程度
            6: cost_limit,   # 成本限制
            7: scalability,  # 可扩展性需求
            8: cargo_type    # 货物类型
        }
    
    def get_attribute(self, attr_id, default=None):
        """获取任务属性，如果不存在则返回默认值"""
        return self.attributes.get(attr_id, default)
    
    def set_attribute(self, attr_id, value):
        """设置任务属性"""
        self.attributes[attr_id] = value
    
    def __str__(self):
        """返回任务的字符串表示"""
        return f"DeliveryTask: {self.start_pos} -> {self.goal_pos}, 属性: {self.attributes}"