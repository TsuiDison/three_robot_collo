# delivery_task.py
# -*- coding: utf-8 -*-
"""
配送任务模块
定义了配送任务的数据结构，支持中转流程。
"""

from typing import Tuple, Optional
import random

class DeliveryTask:
    """
    配送任务类，支持简单任务和分段的中转任务。
    """
    def __init__(self, goal_pos: Tuple[int, int], weight: float,
                 urgency: int = 1, task_id: str = None, 
                 start_pos: Optional[Tuple[int, int]] = None, 
                 is_relay_leg: bool = False,
                 color: Optional[str] = None): # 新增 color 参数
        
        self.task_id = task_id if task_id else f"task_{id(self)}"
        self.original_goal = goal_pos  # 记录客户的最终位置
        self.weight = weight
        self.urgency = urgency
        
        # 任务路径点
        self.start_pos = start_pos  # 对于接力任务，起点是中转站
        self.goal_pos = goal_pos    # 当前这一程的目标点

        # 状态
        self.is_relay_leg = is_relay_leg # 标记这是否是一个接力任务
        self.completed = False
        if color:
            self.color = color
        else:
            # 随机生成一个明亮的、鲜艳的颜色
            self.color = "#{:06x}".format(random.randint(0x808080, 0xFFFFFF))
        # --- 修改结束 ---

        # --- 新增属性，用于中转站处理延迟 ---
        self.arrival_time = None # 记录任务到达中转站的时间
        
    def __repr__(self):
        """为任务提供一个清晰的字符串表示"""
        if self.is_relay_leg:
            return f"RelayTask(id={self.task_id}, from={self.start_pos} to={self.goal_pos})"
        elif self.start_pos:
             return f"DirectTask(id={self.task_id}, from={self.start_pos} to={self.goal_pos})"
        return f"MainTask(id={self.task_id}, to={self.original_goal})"  