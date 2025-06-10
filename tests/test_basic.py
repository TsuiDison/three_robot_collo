"""
测试套件 - 基本功能测试
"""
import asyncio
import unittest
from src.agent.travel_agent import TravelAgent
from src.environment.travel_environment import TravelEnvironment
from src.simulation.simulation_engine import SimulationEngine, SimulationConfig

class TestTravelAgent(unittest.TestCase):
    """旅行代理测试"""
    
    def setUp(self):
        """测试前准备"""
        self.agent = TravelAgent(name="测试代理")
        self.environment = TravelEnvironment()
    
    def test_agent_initialization(self):
        """测试代理初始化"""
        self.assertIsNotNone(self.agent.agent_id)
        self.assertEqual(self.agent.name, "测试代理")
        self.assertEqual(self.agent.state.resources['budget'], 1000.0)
        self.assertEqual(self.agent.state.resources['energy'], 100.0)
    
    async def test_agent_perception(self):
        """测试代理感知功能"""
        env_state = await self.environment.get_state_for_agent(
            self.agent.agent_id,
            self.agent.state.resources
        )
        
        perception = await self.agent.perceive(env_state)
        
        self.assertIn('available_activities', perception)
        self.assertIn('weather', perception)
        self.assertIn('analysis', perception)
    
    async def test_agent_decision(self):
        """测试代理决策功能"""
        # 模拟感知结果
        perception = {
            'available_activities': [
                {
                    'id': 'test_activity',
                    'name': '测试活动',
                    'cost': 50,
                    'energy_required': 30,
                    'satisfaction_rating': 80,
                    'type': 'cultural'
                }
            ],
            'analysis': {
                'opportunities': [
                    {
                        'type': 'activity',
                        'item': {
                            'id': 'test_activity',
                            'name': '测试活动',
                            'cost': 50,
                            'energy_required': 30,
                            'satisfaction_rating': 80,
                            'type': 'cultural'
                        },
                        'score': 0.8
                    }
                ]
            }
        }
        
        action = await self.agent.decide(perception)
        
        self.assertIsNotNone(action)
        self.assertIn(action.action_type, ['book_activity', 'rest', 'explore'])

class TestTravelEnvironment(unittest.TestCase):
    """旅行环境测试"""
    
    def setUp(self):
        """测试前准备"""
        self.environment = TravelEnvironment()
    
    def test_environment_initialization(self):
        """测试环境初始化"""
        self.assertIsNotNone(self.environment.current_location_id)
        self.assertIn(self.environment.current_location_id, self.environment.locations)
        self.assertTrue(len(self.environment.activities) > 0)
    
    def test_location_data(self):
        """测试地点数据"""
        for location_id, location in self.environment.locations.items():
            self.assertIsNotNone(location.name)
            self.assertIsNotNone(location.country)
            self.assertIsInstance(location.cost_level, (int, float))
    
    def test_activity_data(self):
        """测试活动数据"""
        for activity_id, activity in self.environment.activities.items():
            self.assertIsNotNone(activity.name)
            self.assertIsNotNone(activity.type)
            self.assertIsInstance(activity.cost, (int, float))
            self.assertIsInstance(activity.duration, int)
    
    async def test_agent_registration(self):
        """测试代理注册"""
        agent_id = "test_agent_123"
        agent_name = "测试代理"
        
        await self.environment.register_agent(agent_id, agent_name)
        
        self.assertIn(agent_id, self.environment.registered_agents)
        self.assertEqual(
            self.environment.registered_agents[agent_id]['name'],
            agent_name
        )
    
    def test_available_activities(self):
        """测试可用活动获取"""
        activities = self.environment.get_available_activities()
        self.assertIsInstance(activities, list)
        
        # 测试资源过滤
        agent_resources = {'budget': 20, 'energy': 50}
        filtered_activities = self.environment.get_available_activities(
            agent_resources=agent_resources
        )
        
        for activity in filtered_activities:
            self.assertLessEqual(activity.cost, agent_resources['budget'])
            self.assertLessEqual(activity.energy_required, agent_resources['energy'])

class TestSimulationEngine(unittest.TestCase):
    """仿真引擎测试"""
    
    def setUp(self):
        """测试前准备"""
        self.config = SimulationConfig(max_steps=5, step_interval=0.1)
        self.simulation = SimulationEngine(self.config)
        self.environment = TravelEnvironment()
        self.agent = TravelAgent(name="测试代理")
    
    def test_simulation_initialization(self):
        """测试仿真引擎初始化"""
        self.assertEqual(self.simulation.current_step, 0)
        self.assertEqual(self.simulation.config.max_steps, 5)
    
    def test_add_components(self):
        """测试添加组件"""
        self.simulation.set_environment(self.environment)
        self.simulation.add_agent(self.agent)
        
        self.assertEqual(self.simulation.environment, self.environment)
        self.assertIn(self.agent.agent_id, self.simulation.agents)
    
    async def test_simulation_execution(self):
        """测试仿真执行"""
        self.simulation.set_environment(self.environment)
        self.simulation.add_agent(self.agent)
        
        # 启动仿真
        await self.simulation.start_simulation()
        
        # 等待一小段时间让仿真运行
        await asyncio.sleep(1)
        
        # 停止仿真
        await self.simulation.stop_simulation()
        
        # 验证仿真运行了
        self.assertGreater(self.simulation.current_step, 0)
        self.assertTrue(len(self.simulation.simulation_history) > 0)

async def run_async_tests():
    """运行异步测试"""
    print("🧪 运行异步测试...")
    
    # 创建测试实例
    agent_test = TestTravelAgent()
    env_test = TestTravelEnvironment()
    sim_test = TestSimulationEngine()
    
    # 运行异步测试
    try:
        agent_test.setUp()
        await agent_test.test_agent_perception()
        await agent_test.test_agent_decision()
        print("✅ 代理异步测试通过")
        
        env_test.setUp()
        await env_test.test_agent_registration()
        print("✅ 环境异步测试通过")
        
        sim_test.setUp()
        await sim_test.test_simulation_execution()
        print("✅ 仿真引擎异步测试通过")
        
    except Exception as e:
        print(f"❌ 异步测试失败: {e}")
        raise

def main():
    """主测试函数"""
    print("🧪 旅行仿真系统测试套件")
    print("=" * 50)
    
    # 运行同步测试
    print("运行同步测试...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # 运行异步测试
    asyncio.run(run_async_tests())
    
    print("\n🎉 所有测试完成!")

if __name__ == "__main__":
    main()