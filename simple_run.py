"""
简化版主程序 - 无需复杂依赖的轻量级版本
"""
import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any, List

# 模拟智能代理
class SimpleAgent:
    def __init__(self, name: str):
        self.name = name
        self.budget = 1000
        self.energy = 100
        self.satisfaction = 50
        self.location = "巴黎"
        self.activities_done = []
    
    def make_decision(self, available_activities):
        """简单决策算法"""
        if self.energy < 30:
            return "rest"
        
        if available_activities and self.budget > 50:
            # 选择第一个负担得起的活动
            for activity in available_activities:
                if activity['cost'] <= self.budget:
                    return f"book_{activity['name']}"
        
        return "explore"
    
    def execute_action(self, action):
        """执行行为"""
        if action == "rest":
            self.energy = min(100, self.energy + 30)
            return f"{self.name} 休息了一下，体力恢复到 {self.energy}"
        
        elif action.startswith("book_"):
            activity_name = action.replace("book_", "")
            cost = 80  # 模拟成本
            self.budget -= cost
            self.energy -= 20
            self.satisfaction += 15
            self.activities_done.append(activity_name)
            return f"{self.name} 预订了 {activity_name}，花费 {cost} 元"
        
        else:  # explore
            self.energy -= 10
            self.satisfaction += 5
            return f"{self.name} 探索了周围环境"

# 模拟环境
class SimpleEnvironment:
    def __init__(self):
        self.current_time = datetime.now()
        self.weather = "晴朗"
        self.activities = [
            {"name": "卢浮宫参观", "cost": 25, "type": "文化"},
            {"name": "塞纳河游船", "cost": 35, "type": "观光"},
            {"name": "埃菲尔铁塔", "cost": 30, "type": "地标"}
        ]
    
    def get_available_activities(self):
        return self.activities
    
    def update_environment(self):
        """更新环境状态"""
        import random
        weather_options = ["晴朗", "多云", "小雨"]
        self.weather = random.choice(weather_options)

# 仿真控制器
class SimpleSimulation:
    def __init__(self):
        self.agents = []
        self.environment = SimpleEnvironment()
        self.step_count = 0
        self.running = False
        self.history = []
    
    def add_agent(self, agent):
        self.agents.append(agent)
    
    async def run_simulation(self, max_steps=20):
        """运行仿真"""
        self.running = True
        print(f"🚀 开始仿真，最大步数: {max_steps}")
        
        for step in range(max_steps):
            if not self.running:
                break
            
            self.step_count = step + 1
            print(f"\n--- 步骤 {self.step_count} ---")
            
            # 更新环境
            self.environment.update_environment()
            print(f"环境状态: {self.environment.weather}")
            
            # 代理决策和执行
            step_results = []
            available_activities = self.environment.get_available_activities()
            
            for agent in self.agents:
                decision = agent.make_decision(available_activities)
                result = agent.execute_action(decision)
                step_results.append(result)
                print(f"  {result}")
                print(f"  状态: 预算={agent.budget}, 体力={agent.energy}, 满意度={agent.satisfaction}")
            
            # 记录历史
            self.history.append({
                'step': self.step_count,
                'time': datetime.now().isoformat(),
                'weather': self.environment.weather,
                'results': step_results,
                'agent_states': [
                    {
                        'name': agent.name,
                        'budget': agent.budget,
                        'energy': agent.energy,
                        'satisfaction': agent.satisfaction
                    }
                    for agent in self.agents
                ]
            })
            
            # 等待
            await asyncio.sleep(0.5)
        
        print(f"\n🎉 仿真完成，共执行 {self.step_count} 步")
        self._print_summary()
    
    def stop_simulation(self):
        """停止仿真"""
        self.running = False
        print("⏹️ 仿真已停止")
    
    def _print_summary(self):
        """打印仿真摘要"""
        print("\n📊 仿真摘要:")
        print("=" * 40)
        
        for agent in self.agents:
            print(f"\n👤 {agent.name}:")
            print(f"  最终预算: {agent.budget}")
            print(f"  最终体力: {agent.energy}")
            print(f"  最终满意度: {agent.satisfaction}")
            print(f"  完成活动: {len(agent.activities_done)}")
            if agent.activities_done:
                print(f"  活动列表: {', '.join(agent.activities_done)}")

def create_console_interface():
    """创建控制台界面"""
    print("🎯 旅行规划仿真系统 - 控制台版本")
    print("=" * 60)
    print("这是一个简化版本，无需复杂依赖即可运行")
    print("=" * 60)
    
    # 创建仿真
    simulation = SimpleSimulation()
    
    # 创建代理
    agent1 = SimpleAgent("文化探索者")
    agent2 = SimpleAgent("休闲旅行者")
    
    simulation.add_agent(agent1)
    simulation.add_agent(agent2)
    
    print(f"✅ 已创建 {len(simulation.agents)} 个代理")
    
    return simulation

async def main():
    """主函数"""
    try:
        # 创建界面
        simulation = create_console_interface()
        
        # 用户选择
        print("\n请选择操作:")
        print("1. 运行标准仿真 (20步)")
        print("2. 运行快速仿真 (10步)")
        print("3. 运行详细仿真 (30步)")
        print("4. 退出")
        
        while True:
            choice = input("\n请输入选择 (1-4): ").strip()
            
            if choice == "1":
                await simulation.run_simulation(20)
                break
            elif choice == "2":
                await simulation.run_simulation(10)
                break
            elif choice == "3":
                await simulation.run_simulation(30)
                break
            elif choice == "4":
                print("👋 再见!")
                break
            else:
                print("❌ 无效选择，请重新输入")
    
    except KeyboardInterrupt:
        print("\n👋 用户中断，程序退出")
    except Exception as e:
        print(f"\n❌ 程序出错: {e}")

if __name__ == "__main__":
    asyncio.run(main())