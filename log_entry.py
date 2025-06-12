# log_entry.py
# -*- coding: utf-8 -*-

import time
from typing import List, Tuple, Optional

class LogEntry:
    """
    用于记录单个任务或任务分段配送信息的结构化日志条目。
    """
    def __init__(self, task, agent_id: str, strategy: str):
        self.task_id: str = task.task_id
        self.original_task_id: str = getattr(task, 'original_task_id', task.task_id)
        self.agent_id: str = agent_id
        self.strategy: str = strategy # "direct", "relay_leg1", "relay_leg2"
        
        self.start_pos: Tuple[int, int] = task.start_pos
        self.goal_pos: Tuple[int, int] = task.goal_pos
        self.weight: float = task.weight
        self.urgency: int = task.urgency
        
        self.assigned_time: float = time.time()
        self.completion_time: Optional[float] = None
        self.duration: Optional[float] = None
        
        self.path_planned: Optional[List[Tuple[int, int]]] = None
        self.path_length: Optional[int] = None
        self.status: str = "assigned" # "assigned", "completed", "failed"

    def set_path(self, path: List[Tuple[int, int]]):
        self.path_planned = path
        self.path_length = len(path) if path else 0

    def mark_as_completed(self):
        self.status = "completed"
        self.completion_time = time.time()
        self.duration = self.completion_time - self.assigned_time

    def mark_as_failed(self, reason: str = "Unknown"):
        self.status = "failed"
        self.completion_time = time.time()
        self.duration = self.completion_time - self.assigned_time
        # 添加一个失败原因的字段
        self.failure_reason = reason
        
    def to_dict(self) -> dict:
        """将日志条目转换为可被JSON序列化的字典。"""
        return {
            "taskId": self.task_id,
            "originalTaskId": self.original_task_id,
            "agentId": self.agent_id,
            "strategy": self.strategy,
            "status": self.status,
            "startTime": self.assigned_time,
            "completionTime": self.completion_time,
            "duration": self.duration,
            "startPosition": self.start_pos,
            "goalPosition": self.goal_pos,
            "taskWeight": self.weight,
            "taskUrgency": self.urgency,
            "pathLength": self.path_length,
            "failureReason": getattr(self, 'failure_reason', None)
        }