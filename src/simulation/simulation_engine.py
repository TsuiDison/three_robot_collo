"""
仿真引擎 - 控制Agent-Environment交互的核心引擎
"""
import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json

from src.agent.travel_agent import TravelAgent
from src.environment.travel_environment import TravelEnvironment

logger = logging.getLogger(__name__)

class SimulationStatus(Enum):
    """仿真状态枚举"""
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class SimulationConfig:
    """仿真配置"""
    max_steps: int = 100
    step_interval: float = 1.0  # 秒
    auto_save_interval: int = 10  # 步数
    enable_logging: bool = True
    simulation_speed: float = 1.0

@dataclass
class SimulationStep:
    """仿真步骤数据"""
    step_number: int
    timestamp: str
    environment_state: Dict[str, Any]
    agent_states: Dict[str, Dict[str, Any]]
    actions: List[Dict[str, Any]]
    results: List[Dict[str, Any]]
    metrics: Dict[str, float] = field(default_factory=dict)

class SimulationEngine:
    """仿真引擎核心类"""
    
    def __init__(self, config: SimulationConfig = None):
        self.config = config or SimulationConfig()
        self.status = SimulationStatus.STOPPED
        
        # 核心组件
        self.environment: Optional[TravelEnvironment] = None
        self.agents: Dict[str, TravelAgent] = {}
        
        # 仿真状态
        self.current_step = 0
        self.start_time = None
        self.simulation_history: List[SimulationStep] = []
        
        # 事件回调
        self.step_callbacks: List[Callable] = []
        self.status_callbacks: List[Callable] = []
        
        # 异步任务
        self.simulation_task = None
        self.stop_event = asyncio.Event()
        
        logger.info("SimulationEngine 初始化完成")
    
    def set_environment(self, environment: TravelEnvironment):
        """设置环境"""
        self.environment = environment
        logger.info("环境已设置")
    
    def add_agent(self, agent: TravelAgent):
        """添加代理"""
        self.agents[agent.agent_id] = agent
        logger.info(f"代理 {agent.agent_id} 已添加")
    
    def remove_agent(self, agent_id: str):
        """移除代理"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            logger.info(f"代理 {agent_id} 已移除")
    
    def add_step_callback(self, callback: Callable):
        """添加步骤回调函数"""
        self.step_callbacks.append(callback)
    
    def add_status_callback(self, callback: Callable):
        """添加状态回调函数"""
        self.status_callbacks.append(callback)
    
    async def start_simulation(self):
        """启动仿真"""
        if self.status == SimulationStatus.RUNNING:
            logger.warning("仿真已在运行中")
            return
        
        if not self.environment:
            raise ValueError("未设置环境")
        
        if not self.agents:
            raise ValueError("未添加代理")
        
        # 重置状态
        self.current_step = 0
        self.start_time = datetime.now()
        self.stop_event.clear()
        self.simulation_history.clear()
        
        # 注册代理到环境
        for agent in self.agents.values():
            await self.environment.register_agent(agent.agent_id, agent.name)
        
        # 更新状态
        await self._update_status(SimulationStatus.RUNNING)
        
        # 启动仿真循环
        self.simulation_task = asyncio.create_task(self._simulation_loop())
        
        logger.info("仿真已启动")
    
    async def stop_simulation(self):
        """停止仿真"""
        if self.status != SimulationStatus.RUNNING:
            return
        
        self.stop_event.set()
        
        if self.simulation_task:
            await self.simulation_task
        
        # 注销代理
        for agent in self.agents.values():
            await self.environment.unregister_agent(agent.agent_id)
        
        await self._update_status(SimulationStatus.STOPPED)
        logger.info("仿真已停止")
    
    async def pause_simulation(self):
        """暂停仿真"""
        if self.status == SimulationStatus.RUNNING:
            await self._update_status(SimulationStatus.PAUSED)
            logger.info("仿真已暂停")
    
    async def resume_simulation(self):
        """恢复仿真"""
        if self.status == SimulationStatus.PAUSED:
            await self._update_status(SimulationStatus.RUNNING)
            logger.info("仿真已恢复")
    
    async def _simulation_loop(self):
        """仿真主循环"""
        try:
            while (self.current_step < self.config.max_steps and 
                   not self.stop_event.is_set()):
                
                # 检查暂停状态
                while self.status == SimulationStatus.PAUSED:
                    await asyncio.sleep(0.1)
                    if self.stop_event.is_set():
                        return
                
                # 执行仿真步骤
                await self._execute_simulation_step()
                
                # 等待下一步
                await asyncio.sleep(self.config.step_interval / self.config.simulation_speed)
            
            # 仿真完成
            await self._update_status(SimulationStatus.COMPLETED)
            logger.info("仿真已完成")
            
        except Exception as e:
            logger.error(f"仿真循环出错: {e}")
            await self._update_status(SimulationStatus.ERROR)
    
    async def _execute_simulation_step(self):
        """执行单个仿真步骤"""
        step_start_time = datetime.now()
        
        # 更新环境
        await self.environment.update_environment()
        
        # 收集当前状态
        environment_state = self.environment.get_environment_summary()
        agent_states = {}
        actions = []
        results = []
        
        # 并行处理所有代理
        agent_tasks = []
        for agent in self.agents.values():
            task = self._process_agent_step(agent)
            agent_tasks.append(task)
        
        # 等待所有代理完成
        agent_results = await asyncio.gather(*agent_tasks, return_exceptions=True)
        
        # 处理结果
        for i, (agent_id, agent) in enumerate(self.agents.items()):
            agent_states[agent_id] = agent.get_state_summary()
            
            if i < len(agent_results) and not isinstance(agent_results[i], Exception):
                action, result = agent_results[i]
                actions.append({
                    'agent_id': agent_id,
                    'action': action.__dict__ if action else None
                })
                results.append({
                    'agent_id': agent_id,
                    'result': result
                })
        
        # 计算指标
        metrics = self._calculate_step_metrics(agent_states, actions, results)
        
        # 创建步骤记录
        step = SimulationStep(
            step_number=self.current_step,
            timestamp=step_start_time.isoformat(),
            environment_state=environment_state,
            agent_states=agent_states,
            actions=actions,
            results=results,
            metrics=metrics
        )
        
        # 保存步骤
        self.simulation_history.append(step)
        
        # 调用回调函数
        for callback in self.step_callbacks:
            try:
                await callback(step)
            except Exception as e:
                logger.error(f"步骤回调出错: {e}")
        
        # 自动保存
        if self.current_step % self.config.auto_save_interval == 0:
            await self._auto_save()
        
        self.current_step += 1
        logger.debug(f"步骤 {self.current_step} 完成")
    
    async def _process_agent_step(self, agent: TravelAgent):
        """处理单个代理的步骤"""
        try:
            # 获取环境状态
            env_state = await self.environment.get_state_for_agent(
                agent.agent_id, 
                agent.state.resources
            )
            
            # 代理感知
            perception = await agent.perceive(env_state)
            
            # 代理决策
            action = await agent.decide(perception)
            
            # 代理执行
            result = await agent.act(action, self.environment)
            
            return action, result
            
        except Exception as e:
            logger.error(f"处理代理 {agent.agent_id} 步骤时出错: {e}")
            return None, {'success': False, 'error': str(e)}
    
    def _calculate_step_metrics(self, agent_states: Dict, actions: List, results: List) -> Dict[str, float]:
        """计算步骤指标"""
        metrics = {
            'total_agents': len(agent_states),
            'successful_actions': sum(1 for r in results if r.get('result', {}).get('success', False)),
            'average_satisfaction': 0.0,
            'average_budget_remaining': 0.0,
            'average_energy': 0.0
        }
        
        if agent_states:
            satisfactions = []
            budgets = []
            energies = []
            
            for state in agent_states.values():
                resources = state.get('resources', {})
                satisfactions.append(resources.get('satisfaction', 0))
                budgets.append(resources.get('budget', 0))
                energies.append(resources.get('energy', 0))
            
            if satisfactions:
                metrics['average_satisfaction'] = sum(satisfactions) / len(satisfactions)
            if budgets:
                metrics['average_budget_remaining'] = sum(budgets) / len(budgets)
            if energies:
                metrics['average_energy'] = sum(energies) / len(energies)
        
        return metrics
    
    async def _update_status(self, new_status: SimulationStatus):
        """更新仿真状态"""
        old_status = self.status
        self.status = new_status
        
        # 调用状态回调
        for callback in self.status_callbacks:
            try:
                await callback(old_status, new_status)
            except Exception as e:
                logger.error(f"状态回调出错: {e}")
    
    async def _auto_save(self):
        """自动保存"""
        try:
            # 这里可以实现保存到文件的逻辑
            pass
        except Exception as e:
            logger.error(f"自动保存失败: {e}")
    
    def get_simulation_summary(self) -> Dict[str, Any]:
        """获取仿真摘要"""
        duration = None
        if self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()
        
        return {
            'status': self.status.value,
            'current_step': self.current_step,
            'max_steps': self.config.max_steps,
            'progress': self.current_step / self.config.max_steps if self.config.max_steps > 0 else 0,
            'duration_seconds': duration,
            'total_agents': len(self.agents),
            'history_length': len(self.simulation_history),
            'start_time': self.start_time.isoformat() if self.start_time else None
        }
    
    def get_latest_metrics(self) -> Dict[str, float]:
        """获取最新指标"""
        if self.simulation_history:
            return self.simulation_history[-1].metrics
        return {}
    
    def export_simulation_data(self) -> Dict[str, Any]:
        """导出仿真数据"""
        return {
            'config': {
                'max_steps': self.config.max_steps,
                'step_interval': self.config.step_interval,
                'simulation_speed': self.config.simulation_speed
            },
            'summary': self.get_simulation_summary(),
            'history': [
                {
                    'step': step.step_number,
                    'timestamp': step.timestamp,
                    'metrics': step.metrics,
                    'agent_count': len(step.agent_states),
                    'action_count': len(step.actions)
                }
                for step in self.simulation_history
            ]
        }