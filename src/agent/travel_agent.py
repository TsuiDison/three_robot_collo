"""
旅行智能代理 - 专门用于旅行规划的智能代理
"""
import logging
import random
from typing import Dict, Any, List, Optional
from src.agent.base_agent import BaseAgent, AgentAction, AgentStatus
import asyncio

logger = logging.getLogger(__name__)

class TravelAgent(BaseAgent):
    """旅行智能代理"""
    
    def __init__(self, agent_id: str = None, name: str = "TravelAgent"):
        super().__init__(agent_id, name)
        
        # 初始化旅行相关属性
        self.state.resources = {
            'budget': 1000.0,  # 预算
            'time_remaining': 7,  # 剩余天数
            'energy': 100.0,  # 体力值
            'satisfaction': 50.0  # 满意度
        }
        
        self.state.preferences = {
            'activity_types': ['cultural', 'nature', 'food'],
            'budget_level': 'medium',
            'comfort_level': 'standard',
            'adventure_level': 0.5
        }
        
        self.state.goals = [
            'maximize_satisfaction',
            'stay_within_budget',
            'visit_attractions',
            'experience_culture'
        ]
        
        # 决策权重
        self.decision_weights = {
            'cost': 0.3,
            'satisfaction_potential': 0.4,
            'energy_required': 0.2,
            'preference_match': 0.1
        }
        
        logger.info(f"TravelAgent {self.agent_id} 初始化完成")
    
    async def perceive(self, environment_state: Dict[str, Any]) -> Dict[str, Any]:
        """感知环境状态"""
        perception = {
            'timestamp': environment_state.get('timestamp'),
            'current_location': environment_state.get('current_location'),
            'available_activities': environment_state.get('available_activities', []),
            'available_accommodations': environment_state.get('available_accommodations', []),
            'weather': environment_state.get('weather', {}),
            'local_events': environment_state.get('local_events', []),
            'transportation_options': environment_state.get('transportation_options', []),
            'time_of_day': environment_state.get('time_of_day', 'morning')
        }
        
        # 分析感知信息
        perception['analysis'] = self._analyze_perception(perception)
        
        # 保存感知历史
        self.perception_history.append(perception)
        if len(self.perception_history) > 20:
            self.perception_history = self.perception_history[-20:]
        
        logger.debug(f"Agent {self.agent_id} 感知到 {len(perception['available_activities'])} 个活动选项")
        return perception
    
    def _analyze_perception(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """分析感知信息"""
        analysis = {
            'opportunities': [],
            'threats': [],
            'resource_status': self._assess_resources(),
            'preference_matches': []
        }
        
        # 分析可用活动
        for activity in perception.get('available_activities', []):
            score = self._score_activity(activity)
            if score > 0.6:
                analysis['opportunities'].append({
                    'type': 'activity',
                    'item': activity,
                    'score': score
                })
        
        # 分析资源状况
        if self.state.resources['budget'] < 100:
            analysis['threats'].append('low_budget')
        if self.state.resources['energy'] < 30:
            analysis['threats'].append('low_energy')
        
        return analysis
    
    def _score_activity(self, activity: Dict[str, Any]) -> float:
        """对活动进行评分"""
        score = 0.0
        
        # 成本评分
        cost = activity.get('cost', 0)
        if cost <= self.state.resources['budget'] * 0.2:
            score += self.decision_weights['cost']
        elif cost <= self.state.resources['budget'] * 0.5:
            score += self.decision_weights['cost'] * 0.5
        
        # 满意度潜力评分
        satisfaction_potential = activity.get('satisfaction_rating', 50)
        score += (satisfaction_potential / 100) * self.decision_weights['satisfaction_potential']
        
        # 体力需求评分
        energy_required = activity.get('energy_required', 30)
        if energy_required <= self.state.resources['energy']:
            score += self.decision_weights['energy_required']
        
        # 偏好匹配评分
        activity_type = activity.get('type', '')
        if activity_type in self.state.preferences['activity_types']:
            score += self.decision_weights['preference_match']
        
        return min(score, 1.0)
    
    async def decide(self, perception: Dict[str, Any]) -> AgentAction:
        """基于感知信息做出决策"""
        self.state.status = AgentStatus.PLANNING
        
        # 分析当前情况
        analysis = perception.get('analysis', {})
        opportunities = analysis.get('opportunities', [])
        
        # 选择最佳行动
        if opportunities:
            # 选择评分最高的机会
            best_opportunity = max(opportunities, key=lambda x: x['score'])
            action_type = 'book_activity'
            parameters = {
                'activity': best_opportunity['item'],
                'reason': f"选择评分最高的活动 (score: {best_opportunity['score']:.2f})"
            }
        else:
            # 没有好的机会，选择休息或移动
            if self.state.resources['energy'] < 50:
                action_type = 'rest'
                parameters = {'duration': 2, 'reason': '体力不足，需要休息'}
            else:
                action_type = 'explore'
                parameters = {'reason': '没有合适的活动，选择探索'}
        
        action = AgentAction(
            action_id=f"action_{len(self.action_history)}",
            agent_id=self.agent_id,
            action_type=action_type,
            parameters=parameters,
            expected_outcome=f"执行 {action_type} 行动"
        )
        
        logger.info(f"Agent {self.agent_id} 决策: {action_type}")
        return action
    
    async def act(self, action: AgentAction, environment) -> Dict[str, Any]:
        """执行行为"""
        self.state.status = AgentStatus.EXECUTING
        
        try:
            # 执行具体行动
            if action.action_type == 'book_activity':
                result = await self._execute_book_activity(action, environment)
            elif action.action_type == 'rest':
                result = await self._execute_rest(action)
            elif action.action_type == 'explore':
                result = await self._execute_explore(action, environment)
            else:
                result = {'success': False, 'message': f'未知行动类型: {action.action_type}'}
            
            # 记录行动历史
            self.action_history.append(action)
            
            # 添加记忆
            self.add_memory({
                'type': 'action_result',
                'action': action.action_type,
                'result': result,
                'parameters': action.parameters
            })
            
            self.state.status = AgentStatus.WAITING
            logger.info(f"Agent {self.agent_id} 执行完成: {action.action_type}")
            
            return result
            
        except Exception as e:
            self.state.status = AgentStatus.ERROR
            error_result = {'success': False, 'message': f'执行错误: {str(e)}'}
            logger.error(f"Agent {self.agent_id} 执行失败: {e}")
            return error_result
    
    async def _execute_book_activity(self, action: AgentAction, environment) -> Dict[str, Any]:
        """执行预订活动"""
        activity = action.parameters.get('activity', {})
        cost = activity.get('cost', 0)
        energy_required = activity.get('energy_required', 30)
        satisfaction_gain = activity.get('satisfaction_rating', 50)
        
        # 检查资源是否足够
        if cost > self.state.resources['budget']:
            return {'success': False, 'message': '预算不足'}
        
        if energy_required > self.state.resources['energy']:
            return {'success': False, 'message': '体力不足'}
        
        # 扣除资源
        self.state.resources['budget'] -= cost
        self.state.resources['energy'] -= energy_required
        self.state.resources['satisfaction'] += satisfaction_gain * 0.1
        
        # 确保满意度不超过100
        self.state.resources['satisfaction'] = min(self.state.resources['satisfaction'], 100)
        
        # 通知环境
        if environment:
            await environment.process_agent_action(self.agent_id, action)
        
        return {
            'success': True,
            'message': f"成功预订活动: {activity.get('name', 'Unknown')}",
            'cost': cost,
            'satisfaction_gain': satisfaction_gain * 0.1
        }
    
    async def _execute_rest(self, action: AgentAction) -> Dict[str, Any]:
        """执行休息"""
        duration = action.parameters.get('duration', 2)
        energy_gain = duration * 20  # 每小时恢复20体力
        
        self.state.resources['energy'] += energy_gain
        self.state.resources['energy'] = min(self.state.resources['energy'], 100)
        
        return {
            'success': True,
            'message': f"休息 {duration} 小时，恢复 {energy_gain} 体力",
            'energy_gain': energy_gain
        }
    
    async def _execute_explore(self, action: AgentAction, environment) -> Dict[str, Any]:
        """执行探索"""
        energy_cost = 15
        satisfaction_gain = random.uniform(5, 15)  # 随机获得满意度
        
        self.state.resources['energy'] -= energy_cost
        self.state.resources['satisfaction'] += satisfaction_gain
        self.state.resources['satisfaction'] = min(self.state.resources['satisfaction'], 100)
        
        # 可能发现新的活动或信息
        discovery = random.choice([
            '发现了一个隐藏的咖啡店',
            '遇到了当地友好的居民',
            '找到了一个美丽的观景点',
            '发现了当地特色小吃'
        ])
        
        return {
            'success': True,
            'message': f"探索完成: {discovery}",
            'energy_cost': energy_cost,
            'satisfaction_gain': satisfaction_gain,
            'discovery': discovery
        }
    
    def _assess_resources(self) -> Dict[str, str]:
        """评估资源状况"""
        assessment = {}
        
        # 评估预算
        if self.state.resources['budget'] > 500:
            assessment['budget'] = 'sufficient'
        elif self.state.resources['budget'] > 200:
            assessment['budget'] = 'moderate'
        else:
            assessment['budget'] = 'low'
        
        # 评估体力
        if self.state.resources['energy'] > 70:
            assessment['energy'] = 'high'
        elif self.state.resources['energy'] > 30:
            assessment['energy'] = 'moderate'
        else:
            assessment['energy'] = 'low'
        
        # 评估满意度
        if self.state.resources['satisfaction'] > 70:
            assessment['satisfaction'] = 'high'
        elif self.state.resources['satisfaction'] > 40:
            assessment['satisfaction'] = 'moderate'
        else:
            assessment['satisfaction'] = 'low'
        
        return assessment