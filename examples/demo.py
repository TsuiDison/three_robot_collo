"""
示例和演示脚本
展示如何使用旅行仿真系统的各个组件
"""
import asyncio
import logging
from typing import List
from src.agent.travel_agent import TravelAgent
from src.environment.travel_environment import TravelEnvironment
from src.simulation.simulation_engine import SimulationEngine, SimulationConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def basic_simulation_example():
    """基础仿真示例"""
    print("🎯 基础仿真示例")
    print("=" * 50)
    
    # 创建环境
    environment = TravelEnvironment()
    print(f"✅ 环境已创建: {environment.current_location_id}")
    
    # 创建代理
    agent1 = TravelAgent(name="文化爱好者")
    agent1.state.preferences['activity_types'] = ['cultural', 'art', 'history']
    agent1.state.resources['budget'] = 800
    
    agent2 = TravelAgent(name="自然探索者")
    agent2.state.preferences['activity_types'] = ['nature', 'outdoor']
    agent2.state.resources['budget'] = 1200
    
    print(f"✅ 代理已创建: {agent1.name}, {agent2.name}")
    
    # 创建仿真引擎
    config = SimulationConfig(max_steps=10, step_interval=0.5)
    simulation = SimulationEngine(config)
    simulation.set_environment(environment)
    simulation.add_agent(agent1)
    simulation.add_agent(agent2)
    
    # 添加回调函数
    async def step_callback(step):
        print(f"步骤 {step.step_number}: {len(step.actions)} 个行为被执行")
        for action in step.actions:
            agent_id = action['agent_id']
            action_type = action['action']['action_type'] if action['action'] else 'None'
            print(f"  - {agent_id}: {action_type}")
    
    simulation.add_step_callback(step_callback)
    
    # 运行仿真
    print("🚀 开始仿真...")
    await simulation.start_simulation()
    
    # 等待仿真完成
    while simulation.status.value in ['running', 'paused']:
        await asyncio.sleep(1)
    
    # 输出结果
    summary = simulation.get_simulation_summary()
    print(f"\n📊 仿真完成!")
    print(f"总步数: {summary['current_step']}")
    print(f"仿真时长: {summary['duration_seconds']:.1f}秒")
    
    # 显示代理最终状态
    for agent in simulation.agents.values():
        resources = agent.state.resources
        print(f"\n👤 {agent.name} 最终状态:")
        print(f"  预算: {resources['budget']:.1f}")
        print(f"  体力: {resources['energy']:.1f}")
        print(f"  满意度: {resources['satisfaction']:.1f}")
        print(f"  执行行为: {len(agent.action_history)} 次")

async def multi_agent_interaction_example():
    """多代理交互示例"""
    print("\n🤖 多代理交互示例")
    print("=" * 50)
    
    # 创建环境
    environment = TravelEnvironment()
    
    # 创建多个不同类型的代理
    agents = [
        TravelAgent(name="经济型旅行者"),
        TravelAgent(name="豪华型旅行者"),
        TravelAgent(name="冒险型旅行者"),
        TravelAgent(name="文化型旅行者")
    ]
    
    # 设置不同的特征
    agents[0].state.resources['budget'] = 500  # 经济型
    agents[0].state.preferences['budget_level'] = 'low'
    
    agents[1].state.resources['budget'] = 2000  # 豪华型
    agents[1].state.preferences['budget_level'] = 'high'
    
    agents[2].state.preferences['adventure_level'] = 0.9  # 冒险型
    agents[2].state.preferences['activity_types'] = ['outdoor', 'adventure']
    
    agents[3].state.preferences['activity_types'] = ['cultural', 'art', 'history']  # 文化型
    
    # 创建仿真
    config = SimulationConfig(max_steps=15, step_interval=0.3)
    simulation = SimulationEngine(config)
    simulation.set_environment(environment)
    
    for agent in agents:
        simulation.add_agent(agent)
    
    print(f"✅ 创建了 {len(agents)} 个不同类型的代理")
    
    # 记录交互数据
    interaction_data = []
    
    async def interaction_callback(step):
        step_data = {
            'step': step.step_number,
            'agents': {},
            'environment': step.environment_state
        }
        
        for agent_id, agent_state in step.agent_states.items():
            step_data['agents'][agent_id] = {
                'satisfaction': agent_state['resources']['satisfaction'],
                'budget': agent_state['resources']['budget'],
                'energy': agent_state['resources']['energy']
            }
        
        interaction_data.append(step_data)
        
        # 显示进度
        if step.step_number % 5 == 0:
            avg_satisfaction = step.metrics.get('average_satisfaction', 0)
            print(f"步骤 {step.step_number}: 平均满意度 {avg_satisfaction:.1f}%")
    
    simulation.add_step_callback(interaction_callback)
    
    # 运行仿真
    print("🚀 开始多代理仿真...")
    await simulation.start_simulation()
    
    # 等待完成
    while simulation.status.value in ['running', 'paused']:
        await asyncio.sleep(0.5)
    
    # 分析结果
    print(f"\n📈 交互分析结果:")
    
    # 计算每个代理的表现
    for agent in agents:
        initial_satisfaction = 50.0  # 初始满意度
        final_satisfaction = agent.state.resources['satisfaction']
        improvement = final_satisfaction - initial_satisfaction
        
        print(f"\n👤 {agent.name}:")
        print(f"  满意度提升: {improvement:+.1f}%")
        print(f"  预算使用: {1000 - agent.state.resources['budget']:.1f}")
        print(f"  行为总数: {len(agent.action_history)}")
        
        # 分析行为偏好
        action_types = [action.action_type for action in agent.action_history]
        if action_types:
            most_common = max(set(action_types), key=action_types.count)
            print(f"  偏好行为: {most_common}")

async def environment_dynamics_example():
    """环境动态变化示例"""
    print("\n🌍 环境动态变化示例")
    print("=" * 50)
    
    # 创建环境并设置监控
    environment = TravelEnvironment()
    
    # 创建一个代理观察环境变化
    observer_agent = TravelAgent(name="环境观察者")
    
    print("🔍 观察环境变化...")
    
    # 模拟环境变化
    for step in range(10):
        # 更新环境
        await environment.update_environment()
        
        # 获取环境状态
        env_state = await environment.get_state_for_agent(
            observer_agent.agent_id,
            observer_agent.state.resources
        )
        
        # 显示环境信息
        print(f"\n⏰ 步骤 {step + 1}:")
        print(f"  时间: {env_state['time_of_day']}")
        print(f"  天气: {env_state['weather']['condition']}")
        print(f"  温度: {env_state['weather']['temperature']:.1f}°C")
        print(f"  可用活动: {len(env_state['available_activities'])}")
        
        # 显示一些可用活动
        activities = env_state['available_activities'][:3]
        for activity in activities:
            print(f"    - {activity['name']} (费用: {activity['cost']})")
        
        await asyncio.sleep(0.5)
    
    print("\n✅ 环境观察完成")

def create_custom_agent_example():
    """自定义代理示例"""
    print("\n🛠️ 自定义代理示例")
    print("=" * 50)
    
    class EcoTravelAgent(TravelAgent):
        """环保旅行代理 - 优先选择环保活动"""
        
        def _score_activity(self, activity):
            # 调用父类方法获得基础分数
            base_score = super()._score_activity(activity)
            
            # 环保加分
            eco_friendly_types = ['nature', 'walking', 'cycling', 'outdoor']
            if activity.get('type') in eco_friendly_types:
                base_score += 0.2
            
            # 高碳排放活动减分
            high_carbon_types = ['flight', 'cruise', 'car_rental']
            if activity.get('type') in high_carbon_types:
                base_score -= 0.3
            
            return min(max(base_score, 0), 1.0)
    
    # 创建环保代理
    eco_agent = EcoTravelAgent(name="环保旅行者")
    eco_agent.state.goals.append('minimize_carbon_footprint')
    eco_agent.state.preferences['activity_types'] = ['nature', 'outdoor', 'walking']
    
    print(f"✅ 创建自定义代理: {eco_agent.name}")
    print(f"目标: {eco_agent.state.goals}")
    print(f"偏好: {eco_agent.state.preferences['activity_types']}")
    
    return eco_agent

async def main():
    """主演示函数"""
    print("🎯 旅行仿真系统演示")
    print("=" * 60)
    
    try:
        # 运行各个示例
        await basic_simulation_example()
        await multi_agent_interaction_example()
        await environment_dynamics_example()
        create_custom_agent_example()
        
        print("\n🎉 所有演示完成!")
        print("💡 提示: 运行 'python main.py' 启动完整的 Web 界面")
        
    except KeyboardInterrupt:
        print("\n👋 演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        logger.error(f"演示错误: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())