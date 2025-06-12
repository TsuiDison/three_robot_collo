# -*- coding: utf-8 -*-
"""
主程序模块
启动多智能体协作配送系统 - 简化版本
"""

import threading
from map_system import Map
from agent import create_random_agents
from delivery_task import DeliveryTask


class SimpleDeliverySystem:
    """简化的配送系统"""
    
    def __init__(self, map_instance):
        self.map = map_instance
        self.agents = create_random_agents(map_instance.width, map_instance.height, 
                                         num_dogs=2, num_vehicles=2, num_drones=2)
        self.tasks = []
        self.feedback = []
        
        self.feedback.append(f"系统初始化完成，共有 {len(self.agents)} 个智能体")
        
    def add_task(self, task):
        """添加任务"""
        self.tasks.append(task)
        self.feedback.append(f"新任务添加: 从 {task.start_pos} 到 {task.goal_pos}")
        
        # 简单的任务分配：分配给第一个空闲的智能体
        for agent in self.agents:
            if agent.can_handle_task(task):
                if agent.assign_task(task):
                    self.feedback.append(f"任务已分配给 {agent.agent_id}")
                    break
        else:
            self.feedback.append("暂无可用智能体处理此任务")
    
    def update_system(self):
        """更新系统状态"""
        for agent in self.agents:
            agent.update()
    
    def get_system_status(self):
        """获取系统状态"""
        idle_count = sum(1 for agent in self.agents if agent.state.value == "idle")
        busy_count = len(self.agents) - idle_count
        
        return {
            'total_agents': len(self.agents),
            'idle_agents': idle_count,
            'busy_agents': busy_count,
            'pending_tasks': len([t for t in self.tasks if not hasattr(t, 'completed')]),
            'completed_tasks': len([t for t in self.tasks if hasattr(t, 'completed')])
        }


def main():
    """运行仿真的主函数"""
    # 创建地图
    map_instance = Map(width=100, height=100)
    
    # 创建简化配送系统
    delivery_system = SimpleDeliverySystem(map_instance)
    
    # 添加示例任务
    sample_task = DeliveryTask(
        (10, 10), (90, 90),
        weight=2, time_window=100, urgency=3, safety=2
    )
    delivery_system.add_task(sample_task)
    
    print("简化配送系统已启动")
    print(f"地图大小: {map_instance.width}x{map_instance.height}")
    print(f"智能体数量: {len(delivery_system.agents)}")
    
    # 运行几次更新循环来测试系统
    for i in range(10):
        delivery_system.update_system()
        status = delivery_system.get_system_status()
        print(f"步骤 {i+1}: 空闲智能体 {status['idle_agents']}, 忙碌智能体 {status['busy_agents']}")
        
        # 输出反馈信息
        if delivery_system.feedback:
            print("系统反馈:")
            for feedback in delivery_system.feedback:
                print(f"  - {feedback}")
            delivery_system.feedback = []  # 清空已显示的反馈
    print("\n简化版本测试完成！")
    print("注意：这是最简版本，缺少可视化和高级功能")
    print("后续将逐步添加探索系统、共享地图知识库等功能")


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()