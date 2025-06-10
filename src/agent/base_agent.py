"""
基础代理类 - 所有代理的基类
"""
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
import uuid
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class AgentStatus(Enum):
    """代理状态枚举"""
    INITIALIZED = "initialized"
    PLANNING = "planning"
    EXECUTING = "executing"
    WAITING = "waiting"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class AgentState:
    """代理状态数据结构"""
    agent_id: str
    position: Dict[str, Any] = field(default_factory=dict)  # 当前位置信息
    resources: Dict[str, float] = field(default_factory=dict)  # 资源状态（预算、时间等）
    goals: List[str] = field(default_factory=list)  # 目标列表
    preferences: Dict[str, Any] = field(default_factory=dict)  # 偏好设置
    memory: List[Dict[str, Any]] = field(default_factory=list)  # 记忆/历史信息
    status: AgentStatus = AgentStatus.INITIALIZED
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class AgentAction:
    """代理行为数据结构"""
    action_id: str
    agent_id: str
    action_type: str  # 行为类型
    parameters: Dict[str, Any] = field(default_factory=dict)  # 行为参数
    expected_outcome: str = ""  # 预期结果
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

class BaseAgent(ABC):
    """基础智能代理类"""
    
    def __init__(self, agent_id: str = None, name: str = "Agent"):
        self.agent_id = agent_id or str(uuid.uuid4())[:8]
        self.name = name
        self.state = AgentState(agent_id=self.agent_id)
        self.action_history: List[AgentAction] = []
        self.perception_history: List[Dict[str, Any]] = []
        logger.info(f"Agent {self.name} ({self.agent_id}) 已初始化")
    
    @abstractmethod
    async def perceive(self, environment_state: Dict[str, Any]) -> Dict[str, Any]:
        """感知环境状态"""
        pass
    
    @abstractmethod
    async def decide(self, perception: Dict[str, Any]) -> AgentAction:
        """基于感知信息做出决策"""
        pass
    
    @abstractmethod
    async def act(self, action: AgentAction, environment) -> Dict[str, Any]:
        """执行行为"""
        pass
    
    def update_state(self, updates: Dict[str, Any]):
        """更新代理状态"""
        for key, value in updates.items():
            if hasattr(self.state, key):
                setattr(self.state, key, value)
        self.state.timestamp = datetime.now().isoformat()
        logger.debug(f"Agent {self.agent_id} 状态已更新: {updates}")
    
    def add_memory(self, memory_item: Dict[str, Any]):
        """添加记忆"""
        memory_item['timestamp'] = datetime.now().isoformat()
        self.state.memory.append(memory_item)
        # 限制记忆数量
        if len(self.state.memory) > 50:
            self.state.memory = self.state.memory[-50:]
    
    def get_state_summary(self) -> Dict[str, Any]:
        """获取状态摘要"""
        return {
            'agent_id': self.agent_id,
            'name': self.name,
            'status': self.state.status.value,
            'position': self.state.position,
            'resources': self.state.resources,
            'goals_count': len(self.state.goals),
            'memory_count': len(self.state.memory),
            'actions_count': len(self.action_history)
        }