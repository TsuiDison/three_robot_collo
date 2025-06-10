"""
旅行环境类 - 模拟旅行环境的动态变化
"""
import logging
import random
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class Location:
    """地点数据结构"""
    id: str
    name: str
    country: str
    description: str
    coordinates: Dict[str, float] = field(default_factory=dict)
    climate: str = "temperate"
    cost_level: float = 1.0  # 消费水平倍数

@dataclass
class Activity:
    """活动数据结构"""
    id: str
    name: str
    type: str
    description: str
    location_id: str
    cost: float
    duration: int  # 小时
    energy_required: int
    satisfaction_rating: int
    requirements: List[str] = field(default_factory=list)
    max_participants: int = 10
    current_participants: int = 0

@dataclass
class Weather:
    """天气数据结构"""
    condition: str  # sunny, cloudy, rainy, etc.
    temperature: float
    humidity: float
    wind_speed: float

class TravelEnvironment:
    """旅行环境类"""
    
    def __init__(self):
        self.current_time = datetime.now()
        self.simulation_speed = 1  # 仿真速度倍数
        
        # 初始化地点
        self.locations = self._init_locations()
        self.current_location_id = "paris"
        
        # 初始化活动
        self.activities = self._init_activities()
        
        # 环境状态
        self.environment_state = {
            'timestamp': self.current_time.isoformat(),
            'current_location': self.current_location_id,
            'weather': self._generate_weather(),
            'time_of_day': self._get_time_of_day(),
            'available_activities': [],
            'available_accommodations': [],
            'local_events': [],
            'transportation_options': []
        }
        
        # 代理注册表
        self.registered_agents = {}
        self.agent_locations = {}
        
        # 事件历史
        self.event_history = []
        
        logger.info("TravelEnvironment 初始化完成")
    
    def _init_locations(self) -> Dict[str, Location]:
        """初始化地点数据"""
        locations = {
            "paris": Location(
                id="paris",
                name="巴黎",
                country="法国",
                description="浪漫之都，艺术与文化的殿堂",
                coordinates={"lat": 48.8566, "lng": 2.3522},
                climate="temperate",
                cost_level=1.5
            ),
            "tokyo": Location(
                id="tokyo",
                name="东京",
                country="日本",
                description="现代与传统完美融合的国际大都市",
                coordinates={"lat": 35.6762, "lng": 139.6503},
                climate="temperate",
                cost_level=1.3
            ),
            "bali": Location(
                id="bali",
                name="巴厘岛",
                country="印度尼西亚",
                description="热带天堂，海滩与文化的完美结合",
                coordinates={"lat": -8.3405, "lng": 115.0920},
                climate="tropical",
                cost_level=0.8
            ),
            "zurich": Location(
                id="zurich",
                name="苏黎世",
                country="瑞士",
                description="阿尔卑斯山脚下的金融之都",
                coordinates={"lat": 47.3769, "lng": 8.5417},
                climate="alpine",
                cost_level=2.0
            )
        }
        return locations
    
    def _init_activities(self) -> Dict[str, Activity]:
        """初始化活动数据"""
        activities = {}
        
        # 巴黎活动
        activities.update({
            "louvre_tour": Activity(
                id="louvre_tour",
                name="卢浮宫参观",
                type="cultural",
                description="参观世界著名的卢浮宫博物馆",
                location_id="paris",
                cost=25.0,
                duration=3,
                energy_required=40,
                satisfaction_rating=85
            ),
            "seine_cruise": Activity(
                id="seine_cruise",
                name="塞纳河游船",
                type="scenic",
                description="乘船游览塞纳河，欣赏巴黎美景",
                location_id="paris",
                cost=35.0,
                duration=2,
                energy_required=20,
                satisfaction_rating=78
            ),
            "eiffel_tower": Activity(
                id="eiffel_tower",
                name="埃菲尔铁塔登塔",
                type="landmark",
                description="登上埃菲尔铁塔，俯瞰巴黎全景",
                location_id="paris",
                cost=30.0,
                duration=2,
                energy_required=35,
                satisfaction_rating=90
            )
        })
        
        # 东京活动
        activities.update({
            "temple_visit": Activity(
                id="temple_visit",
                name="浅草寺参拜",
                type="cultural",
                description="参观历史悠久的浅草寺",
                location_id="tokyo",
                cost=0.0,
                duration=2,
                energy_required=25,
                satisfaction_rating=75
            ),
            "sushi_experience": Activity(
                id="sushi_experience",
                name="寿司制作体验",
                type="food",
                description="学习制作正宗日式寿司",
                location_id="tokyo",
                cost=80.0,
                duration=3,
                energy_required=30,
                satisfaction_rating=88
            ),
            "shibuya_crossing": Activity(
                id="shibuya_crossing",
                name="涩谷十字路口体验",
                type="urban",
                description="体验世界最繁忙的十字路口",
                location_id="tokyo",
                cost=0.0,
                duration=1,
                energy_required=15,
                satisfaction_rating=70
            )
        })
        
        # 巴厘岛活动
        activities.update({
            "beach_relaxation": Activity(
                id="beach_relaxation",
                name="海滩休闲",
                type="nature",
                description="在美丽的海滩上放松身心",
                location_id="bali",
                cost=0.0,
                duration=4,
                energy_required=10,
                satisfaction_rating=80
            ),
            "temple_tour": Activity(
                id="temple_tour",
                name="寺庙巡礼",
                type="cultural",
                description="参观巴厘岛传统寺庙",
                location_id="bali",
                cost=15.0,
                duration=3,
                energy_required=35,
                satisfaction_rating=82
            ),
            "spa_treatment": Activity(
                id="spa_treatment",
                name="传统SPA体验",
                type="wellness",
                description="享受巴厘岛传统SPA护理",
                location_id="bali",
                cost=50.0,
                duration=2,
                energy_required=-20,  # 负值表示恢复体力
                satisfaction_rating=85
            )
        })
        
        return activities
    
    def _generate_weather(self) -> Weather:
        """生成随机天气"""
        conditions = ["sunny", "cloudy", "partly_cloudy", "rainy"]
        location = self.locations.get(self.current_location_id)
        
        if location and location.climate == "tropical":
            # 热带气候
            condition = random.choice(["sunny", "cloudy", "rainy"])
            temperature = random.uniform(25, 32)
            humidity = random.uniform(60, 90)
        elif location and location.climate == "alpine":
            # 高山气候
            condition = random.choice(["sunny", "cloudy", "snowy"])
            temperature = random.uniform(-5, 15)
            humidity = random.uniform(40, 70)
        else:
            # 温带气候
            condition = random.choice(conditions)
            temperature = random.uniform(10, 25)
            humidity = random.uniform(40, 80)
        
        return Weather(
            condition=condition,
            temperature=temperature,
            humidity=humidity,
            wind_speed=random.uniform(0, 20)
        )
    
    def _get_time_of_day(self) -> str:
        """获取一天中的时间段"""
        hour = self.current_time.hour
        if 6 <= hour < 12:
            return "morning"
        elif 12 <= hour < 18:
            return "afternoon"
        elif 18 <= hour < 22:
            return "evening"
        else:
            return "night"
    
    def get_available_activities(self, time_of_day: str = None, agent_resources: Dict[str, Any] = None) -> List[Activity]:
        """获取可用活动列表"""
        available = []
        location_activities = [act for act in self.activities.values() 
                             if act.location_id == self.current_location_id]
        
        for activity in location_activities:
            # 检查时间限制
            if time_of_day == "night" and activity.type in ["cultural", "scenic"]:
                continue
            
            # 检查参与人数限制
            if activity.current_participants >= activity.max_participants:
                continue
            
            # 检查代理资源（如果提供）
            if agent_resources:
                if activity.cost > agent_resources.get('budget', 0):
                    continue
                if activity.energy_required > agent_resources.get('energy', 0):
                    continue
            
            available.append(activity)
        
        return available
    
    async def register_agent(self, agent_id: str, agent_name: str = ""):
        """注册代理到环境"""
        self.registered_agents[agent_id] = {
            'name': agent_name,
            'registered_at': datetime.now().isoformat(),
            'actions_count': 0
        }
        self.agent_locations[agent_id] = self.current_location_id
        logger.info(f"代理 {agent_id} 已注册到环境")
    
    async def unregister_agent(self, agent_id: str):
        """从环境注销代理"""
        if agent_id in self.registered_agents:
            del self.registered_agents[agent_id]
        if agent_id in self.agent_locations:
            del self.agent_locations[agent_id]
        logger.info(f"代理 {agent_id} 已从环境注销")
    
    async def get_state_for_agent(self, agent_id: str, agent_resources: Dict[str, Any] = None) -> Dict[str, Any]:
        """获取特定代理的环境状态"""
        time_of_day = self._get_time_of_day()
        available_activities = self.get_available_activities(time_of_day, agent_resources)
        
        state = {
            'timestamp': self.current_time.isoformat(),
            'current_location': self.current_location_id,
            'location_info': self.locations.get(self.current_location_id).__dict__,
            'weather': self.environment_state['weather'].__dict__,
            'time_of_day': time_of_day,
            'available_activities': [act.__dict__ for act in available_activities],
            'available_accommodations': self._get_available_accommodations(),
            'local_events': self._get_local_events(),
            'transportation_options': self._get_transportation_options()
        }
        
        return state
    
    def _get_available_accommodations(self) -> List[Dict[str, Any]]:
        """获取可用住宿"""
        location = self.locations.get(self.current_location_id)
        if not location:
            return []
        
        base_cost = 50 * location.cost_level
        
        accommodations = [
            {
                'id': 'luxury_hotel',
                'name': '豪华酒店',
                'type': 'hotel',
                'cost_per_night': base_cost * 3,
                'comfort_level': 5,
                'amenities': ['spa', 'pool', 'restaurant', 'concierge']
            },
            {
                'id': 'boutique_hotel',
                'name': '精品酒店',
                'type': 'hotel',
                'cost_per_night': base_cost * 2,
                'comfort_level': 4,
                'amenities': ['restaurant', 'wifi', 'room_service']
            },
            {
                'id': 'budget_hotel',
                'name': '经济酒店',
                'type': 'hotel',
                'cost_per_night': base_cost,
                'comfort_level': 3,
                'amenities': ['wifi', 'breakfast']
            },
            {
                'id': 'hostel',
                'name': '青年旅社',
                'type': 'hostel',
                'cost_per_night': base_cost * 0.3,
                'comfort_level': 2,
                'amenities': ['wifi', 'kitchen']
            }
        ]
        
        return accommodations
    
    def _get_local_events(self) -> List[Dict[str, Any]]:
        """获取当地活动"""
        events = []
        
        # 随机生成一些当地活动
        if random.random() < 0.3:  # 30% 概率有特殊活动
            event_types = ['festival', 'concert', 'exhibition', 'market']
            event_type = random.choice(event_types)
            
            events.append({
                'id': f"event_{len(self.event_history)}",
                'name': f"当地{event_type}",
                'type': event_type,
                'description': f"正在进行的{event_type}活动",
                'start_time': self.current_time.isoformat(),
                'duration': random.randint(2, 8),
                'cost': random.uniform(10, 50) if event_type != 'market' else 0
            })
        
        return events
    
    def _get_transportation_options(self) -> List[Dict[str, Any]]:
        """获取交通选项"""
        location = self.locations.get(self.current_location_id)
        if not location:
            return []
        
        options = [
            {
                'type': 'walking',
                'name': '步行',
                'cost_per_km': 0,
                'speed_kmh': 5,
                'comfort': 2,
                'availability': 'always'
            },
            {
                'type': 'public_transport',
                'name': '公共交通',
                'cost_per_km': 1.5 * location.cost_level,
                'speed_kmh': 20,
                'comfort': 3,
                'availability': 'day_time'
            },
            {
                'type': 'taxi',
                'name': '出租车',
                'cost_per_km': 5 * location.cost_level,
                'speed_kmh': 30,
                'comfort': 4,
                'availability': 'always'
            }
        ]
        
        return options
    
    async def process_agent_action(self, agent_id: str, action) -> Dict[str, Any]:
        """处理代理行为对环境的影响"""
        if agent_id not in self.registered_agents:
            return {'success': False, 'message': '代理未注册'}
        
        # 更新代理行为计数
        self.registered_agents[agent_id]['actions_count'] += 1
        
        # 处理不同类型的行为
        result = {'success': True, 'environmental_effects': []}
        
        if action.action_type == 'book_activity':
            activity_id = action.parameters.get('activity', {}).get('id')
            if activity_id in self.activities:
                # 增加活动参与人数
                self.activities[activity_id].current_participants += 1
                result['environmental_effects'].append(
                    f"活动 {activity_id} 参与人数增加"
                )
        
        # 记录环境事件
        self.event_history.append({
            'timestamp': datetime.now().isoformat(),
            'type': 'agent_action',
            'agent_id': agent_id,
            'action': action.action_type,
            'result': result
        })
        
        return result
    
    async def update_environment(self):
        """更新环境状态"""
        # 推进时间
        self.current_time += timedelta(hours=1 * self.simulation_speed)
        
        # 更新天气
        if random.random() < 0.1:  # 10% 概率天气变化
            self.environment_state['weather'] = self._generate_weather()
        
        # 更新时间段
        self.environment_state['time_of_day'] = self._get_time_of_day()
        self.environment_state['timestamp'] = self.current_time.isoformat()
        
        # 重置活动参与人数（每天重置）
        if self.current_time.hour == 0:
            for activity in self.activities.values():
                activity.current_participants = 0
        
        logger.debug(f"环境状态已更新: {self.current_time}")
    
    def get_environment_summary(self) -> Dict[str, Any]:
        """获取环境状态摘要"""
        return {
            'current_time': self.current_time.isoformat(),
            'current_location': self.current_location_id,
            'registered_agents': len(self.registered_agents),
            'total_activities': len(self.activities),
            'total_locations': len(self.locations),
            'weather': self.environment_state['weather'].__dict__ if hasattr(self.environment_state['weather'], '__dict__') else self.environment_state['weather'],
            'time_of_day': self.environment_state['time_of_day'],
            'events_count': len(self.event_history)
        }