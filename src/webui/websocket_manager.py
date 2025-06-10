"""
WebSocket 通信管理器 - 借鉴 browser-use 的实时通信架构
"""
import logging
import json
import asyncio
from typing import Dict, Any, Set, Callable, Optional
from datetime import datetime
import uuid
import threading

logger = logging.getLogger(__name__)

class WebSocketManager:
    """WebSocket 管理器 - 类似 browser-use 的实时通信"""
    
    def __init__(self):
        # 连接管理
        self.connections: Dict[str, Dict[str, Any]] = {}
        self.message_handlers: Dict[str, Callable] = {}
        
        # 事件监听器
        self.event_listeners: Dict[str, Set[str]] = {}
        
        # 消息队列
        self.message_queue = asyncio.Queue()
        self.is_processing = False
        
        # 统计信息
        self.stats = {
            'total_connections': 0,
            'active_connections': 0,
            'messages_sent': 0,
            'messages_received': 0
        }
        
        logger.info("WebSocketManager initialized")
    
    def register_connection(self, connection_id: str = None) -> str:
        """注册新连接"""
        if connection_id is None:
            connection_id = str(uuid.uuid4())[:8]
        
        self.connections[connection_id] = {
            'id': connection_id,
            'connected_at': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat(),
            'subscriptions': set(),
            'session_data': {}
        }
        
        self.stats['total_connections'] += 1
        self.stats['active_connections'] += 1
        
        logger.info(f"WebSocket connection registered: {connection_id}")
        return connection_id
    
    def unregister_connection(self, connection_id: str):
        """注销连接"""
        if connection_id in self.connections:
            del self.connections[connection_id]
            self.stats['active_connections'] -= 1
            logger.info(f"WebSocket connection unregistered: {connection_id}")
    
    def subscribe_to_event(self, connection_id: str, event_type: str):
        """订阅事件"""
        if connection_id not in self.connections:
            return False
        
        if event_type not in self.event_listeners:
            self.event_listeners[event_type] = set()
        
        self.event_listeners[event_type].add(connection_id)
        self.connections[connection_id]['subscriptions'].add(event_type)
        
        logger.debug(f"Connection {connection_id} subscribed to {event_type}")
        return True
    
    def unsubscribe_from_event(self, connection_id: str, event_type: str):
        """取消订阅事件"""
        if event_type in self.event_listeners:
            self.event_listeners[event_type].discard(connection_id)
        
        if connection_id in self.connections:
            self.connections[connection_id]['subscriptions'].discard(event_type)
        
        logger.debug(f"Connection {connection_id} unsubscribed from {event_type}")
    
    async def broadcast_event(self, event_type: str, data: Any):
        """广播事件"""
        if event_type not in self.event_listeners:
            return
        
        message = {
            'type': 'event',
            'event_type': event_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        
        subscribers = self.event_listeners[event_type].copy()
        for connection_id in subscribers:
            await self.send_message(connection_id, message)
        
        logger.debug(f"Broadcasted {event_type} to {len(subscribers)} connections")
    
    async def send_message(self, connection_id: str, message: Dict[str, Any]):
        """发送消息到指定连接"""
        if connection_id not in self.connections:
            return False
        
        # 模拟消息发送（实际应用中这里会通过 WebSocket 发送）
        self.stats['messages_sent'] += 1
        
        # 更新连接活动时间
        self.connections[connection_id]['last_activity'] = datetime.now().isoformat()
        
        # 加入消息队列处理
        await self.message_queue.put({
            'connection_id': connection_id,
            'message': message
        })
        
        logger.debug(f"Message queued for {connection_id}: {message.get('type', 'unknown')}")
        return True
    
    async def send_to_all(self, message: Dict[str, Any]):
        """发送消息到所有连接"""
        tasks = []
        for connection_id in self.connections.keys():
            tasks.append(self.send_message(connection_id, message))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def register_message_handler(self, message_type: str, handler: Callable):
        """注册消息处理器"""
        self.message_handlers[message_type] = handler
        logger.info(f"Message handler registered for: {message_type}")
    
    async def handle_incoming_message(self, connection_id: str, message: Dict[str, Any]):
        """处理接收到的消息"""
        if connection_id not in self.connections:
            return
        
        self.stats['messages_received'] += 1
        message_type = message.get('type', 'unknown')
        
        # 更新连接活动时间
        self.connections[connection_id]['last_activity'] = datetime.now().isoformat()
        
        # 调用对应的处理器
        if message_type in self.message_handlers:
            try:
                await self.message_handlers[message_type](connection_id, message)
            except Exception as e:
                logger.error(f"Message handler error for {message_type}: {e}")
        else:
            logger.warning(f"No handler for message type: {message_type}")
    
    async def start_message_processor(self):
        """启动消息处理器"""
        if self.is_processing:
            return
        
        self.is_processing = True
        logger.info("WebSocket message processor started")
        
        while self.is_processing:
            try:
                # 等待消息
                queue_item = await asyncio.wait_for(
                    self.message_queue.get(), 
                    timeout=1.0
                )
                
                # 处理消息（这里模拟实际的 WebSocket 发送）
                connection_id = queue_item['connection_id']
                message = queue_item['message']
                
                # 实际应用中这里会通过 WebSocket 发送消息
                logger.debug(f"Processing message for {connection_id}")
                
            except asyncio.TimeoutError:
                # 超时是正常的，继续循环
                continue
            except Exception as e:
                logger.error(f"Message processor error: {e}")
    
    def stop_message_processor(self):
        """停止消息处理器"""
        self.is_processing = False
        logger.info("WebSocket message processor stopped")
    
    def get_connection_info(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """获取连接信息"""
        return self.connections.get(connection_id)
    
    def get_all_connections(self) -> Dict[str, Dict[str, Any]]:
        """获取所有连接信息"""
        return self.connections.copy()
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            **self.stats,
            'event_types': list(self.event_listeners.keys()),
            'handler_types': list(self.message_handlers.keys())
        }
    
    def cleanup_inactive_connections(self, timeout_minutes: int = 30):
        """清理不活跃的连接"""
        current_time = datetime.now()
        inactive_connections = []
        
        for connection_id, conn_info in self.connections.items():
            try:
                last_activity = datetime.fromisoformat(conn_info['last_activity'])
                if (current_time - last_activity).total_seconds() > timeout_minutes * 60:
                    inactive_connections.append(connection_id)
            except:
                # 如果时间解析失败，也标记为不活跃
                inactive_connections.append(connection_id)
        
        for connection_id in inactive_connections:
            self.unregister_connection(connection_id)
        
        if inactive_connections:
            logger.info(f"Cleaned up {len(inactive_connections)} inactive connections")

# 全局 WebSocket 管理器实例
websocket_manager = WebSocketManager()

# 便捷函数
async def broadcast_simulation_update(data: Dict[str, Any]):
    """广播仿真更新"""
    await websocket_manager.broadcast_event('simulation_update', data)

async def broadcast_agent_status(agent_data: Dict[str, Any]):
    """广播代理状态"""
    await websocket_manager.broadcast_event('agent_status', agent_data)

async def broadcast_environment_change(env_data: Dict[str, Any]):
    """广播环境变化"""
    await websocket_manager.broadcast_event('environment_change', env_data)

def setup_websocket_handlers():
    """设置 WebSocket 消息处理器"""
    async def handle_simulation_control(connection_id: str, message: Dict[str, Any]):
        """处理仿真控制消息"""
        command = message.get('command')
        parameters = message.get('parameters', {})
        
        logger.info(f"Simulation control from {connection_id}: {command}")
        
        # 这里可以调用实际的仿真控制逻辑
        response = {
            'type': 'simulation_response',
            'command': command,
            'status': 'success',
            'message': f'Command {command} executed'
        }
        
        await websocket_manager.send_message(connection_id, response)
    
    async def handle_agent_command(connection_id: str, message: Dict[str, Any]):
        """处理代理命令消息"""
        agent_id = message.get('agent_id')
        command = message.get('command')
        
        logger.info(f"Agent command from {connection_id}: {agent_id} -> {command}")
        
        # 这里可以调用实际的代理控制逻辑
        response = {
            'type': 'agent_response',
            'agent_id': agent_id,
            'command': command,
            'status': 'success'
        }
        
        await websocket_manager.send_message(connection_id, response)
    
    # 注册处理器
    websocket_manager.register_message_handler('simulation_control', handle_simulation_control)
    websocket_manager.register_message_handler('agent_command', handle_agent_command)
    
    logger.info("WebSocket handlers setup complete")