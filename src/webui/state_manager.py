"""
状态管理器 - 借鉴 browser-use 的状态管理模式
"""
import logging
import uuid
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import threading
import asyncio

logger = logging.getLogger(__name__)

class SessionStatus(Enum):
    """会话状态枚举"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class SessionState:
    """会话状态 - 类似 browser-use 的浏览器会话"""
    session_id: str
    status: SessionStatus = SessionStatus.IDLE
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # 仿真相关状态
    simulation_config: Dict[str, Any] = field(default_factory=dict)
    agents_config: List[Dict[str, Any]] = field(default_factory=list)
    environment_config: Dict[str, Any] = field(default_factory=dict)
    
    # 运行时状态
    current_step: int = 0
    total_steps: int = 0
    simulation_results: List[Dict[str, Any]] = field(default_factory=list)
    
    # 性能指标
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    
    # 用户设置
    user_preferences: Dict[str, Any] = field(default_factory=dict)

class StateManager:
    """状态管理器 - 参考 browser-use 的状态管理架构"""
    
    def __init__(self):
        self.sessions: Dict[str, SessionState] = {}
        self.active_session_id: Optional[str] = None
        
        # 状态变化回调
        self.state_change_callbacks: List[Callable] = []
        
        # 线程安全锁
        self._lock = threading.Lock()
        
        logger.info("StateManager initialized")
    
    def create_session(self, session_id: str = None) -> str:
        """创建新会话"""
        if session_id is None:
            session_id = str(uuid.uuid4())[:8]
        
        with self._lock:
            session = SessionState(session_id=session_id)
            self.sessions[session_id] = session
            self.active_session_id = session_id
            
            logger.info(f"Created new session: {session_id}")
            self._notify_state_change("session_created", session_id)
            
            return session_id
    
    def get_session(self, session_id: str = None) -> Optional[SessionState]:
        """获取会话状态"""
        session_id = session_id or self.active_session_id
        if session_id is None:
            return None
        
        with self._lock:
            return self.sessions.get(session_id)
    
    def update_session(self, session_id: str, updates: Dict[str, Any]):
        """更新会话状态"""
        with self._lock:
            session = self.sessions.get(session_id)
            if session:
                for key, value in updates.items():
                    if hasattr(session, key):
                        setattr(session, key, value)
                session.last_updated = datetime.now().isoformat()
                
                self._notify_state_change("session_updated", session_id, updates)
                logger.debug(f"Session {session_id} updated: {list(updates.keys())}")
    
    def delete_session(self, session_id: str):
        """删除会话"""
        with self._lock:
            if session_id in self.sessions:
                del self.sessions[session_id]
                if self.active_session_id == session_id:
                    self.active_session_id = None
                
                self._notify_state_change("session_deleted", session_id)
                logger.info(f"Session {session_id} deleted")
    
    def set_active_session(self, session_id: str):
        """设置活跃会话"""
        with self._lock:
            if session_id in self.sessions:
                self.active_session_id = session_id
                self._notify_state_change("session_activated", session_id)
                logger.info(f"Active session set to: {session_id}")
    
    def get_session_list(self) -> List[Dict[str, Any]]:
        """获取会话列表"""
        with self._lock:
            return [
                {
                    "session_id": session.session_id,
                    "status": session.status.value,
                    "created_at": session.created_at,
                    "current_step": session.current_step,
                    "total_steps": session.total_steps
                }
                for session in self.sessions.values()
            ]
    
    def add_state_change_callback(self, callback: Callable):
        """添加状态变化回调"""
        self.state_change_callbacks.append(callback)
    
    def _notify_state_change(self, event_type: str, session_id: str, data: Any = None):
        """通知状态变化"""
        for callback in self.state_change_callbacks:
            try:
                callback(event_type, session_id, data)
            except Exception as e:
                logger.error(f"State change callback error: {e}")
    
    def get_session_metrics(self, session_id: str = None) -> Dict[str, Any]:
        """获取会话指标"""
        session = self.get_session(session_id)
        if not session:
            return {}
        
        return {
            "session_id": session.session_id,
            "status": session.status.value,
            "progress": session.current_step / max(session.total_steps, 1),
            "runtime_seconds": self._calculate_runtime(session),
            "agents_count": len(session.agents_config),
            "results_count": len(session.simulation_results)
        }
    
    def _calculate_runtime(self, session: SessionState) -> float:
        """计算运行时间"""
        try:
            created = datetime.fromisoformat(session.created_at)
            updated = datetime.fromisoformat(session.last_updated)
            return (updated - created).total_seconds()
        except:
            return 0.0
    
    def cleanup_old_sessions(self, max_sessions: int = 10):
        """清理旧会话"""
        with self._lock:
            if len(self.sessions) <= max_sessions:
                return
            
            # 按创建时间排序，保留最新的会话
            sorted_sessions = sorted(
                self.sessions.items(),
                key=lambda x: x[1].created_at,
                reverse=True
            )
            
            sessions_to_keep = dict(sorted_sessions[:max_sessions])
            sessions_to_delete = [
                session_id for session_id in self.sessions
                if session_id not in sessions_to_keep
            ]
            
            for session_id in sessions_to_delete:
                self.delete_session(session_id)
            
            logger.info(f"Cleaned up {len(sessions_to_delete)} old sessions")

# 全局状态管理器实例
global_state_manager = StateManager()