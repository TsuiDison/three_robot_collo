# main.py
# -*- coding: utf-8 -*-

import yaml
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from map_system import Map
from delivery_task import DeliveryTask
from multi_agent_coordination import MultiAgentCoordinationSystem
from visualization import DeliveryVisualizer

def load_tasks_from_yaml(filepath: str) -> list[DeliveryTask]:
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            tasks_data = yaml.safe_load(file)
            if not tasks_data: return []
            return [ DeliveryTask( task_id=item['id'], goal_pos=tuple(item['goal_pos']), weight=item.get('weight', 1.0), urgency=item.get('urgency', 1) ) for item in tasks_data ]
    except Exception as e:
        print(f"加载或解析YAML文件时出错: {e}")
        return []

def main():
    print("正在初始化仿真环境...")
    real_map = Map()
    print("真实地图创建完成。")
    coord_system = MultiAgentCoordinationSystem(real_map)
    print("协调系统初始化完成。")

    tasks = load_tasks_from_yaml('tasks.yaml')
    if tasks:
        print(f"成功加载 {len(tasks)} 个任务到队列。")
        for task in tasks:
            coord_system.add_task(task)
    
    # 启动后台世界引擎
    coord_system.start()
    print("协调系统已启动，后台引擎开始运转...")

    visualizer = DeliveryVisualizer(coord_system)
    visualizer.start_animation()
    
    # --- FuncAnimation 现在使用 blit=False ---
    # 更新函数现在只负责画图，不负责更新世界状态
    ani = animation.FuncAnimation(
        visualizer.fig, 
        visualizer._update_frame, # 直接调用可视化的帧更新函数
        init_func=visualizer._init_animation,
        interval=50, # 尝试以接近 30 FPS 的速度渲染
        blit=True,
        cache_frame_data=False
    )
    plt.show()

    print("可视化窗口已关闭...")
    coord_system.stop()
    print("仿真已结束。")

if __name__ == "__main__":
    main()