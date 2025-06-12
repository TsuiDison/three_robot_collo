# -*- coding: utf-8 -*-
"""
主程序模块
启动多智能体协作配送系统
"""

import threading
from map_system import Map
from collaborative_system import CollaborativeDeliverySystem
from visualization import DeliveryVisualizer
from delivery_task import DeliveryTask


def main():
    """运行仿真的主函数"""
    # 创建地图
    map = Map(width=100, height=100)
    
    # 创建配送系统
    delivery_system = CollaborativeDeliverySystem(map)
    
    # 添加示例任务以开始
    sample_task = DeliveryTask(
        (10, 10), (90, 90),
        weight=2, time_window=100, urgency=3, safety=2
    )
    delivery_system.add_task(sample_task)
    
    # 启动任务分配线程
    task_assignment_thread = threading.Thread(target=delivery_system.assign_tasks, daemon=True)
    task_assignment_thread.start()
    
    # 创建并启动可视化
    visualizer = DeliveryVisualizer(delivery_system, map)
    visualizer.start_animation()


if __name__ == "__main__":
    main()