# mainvi.py
# -*- coding: utf-8 -*-

import yaml
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os
from datetime import datetime
import numpy as np
from map_system import Map
from delivery_task import DeliveryTask
from multi_agent_coordination import MultiAgentCoordinationSystem
from visualization import DeliveryVisualizer

# 创建输出目录
OUTPUT_DIR = 'visualization_snapshots'
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def load_tasks_from_yaml(filepath: str) -> list[DeliveryTask]:
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            tasks_data = yaml.safe_load(file)
            if not tasks_data: return []
            return [ DeliveryTask( task_id=item['id'], goal_pos=tuple(item['goal_pos']), weight=item.get('weight', 1.0), urgency=item.get('urgency', 1) ) for item in tasks_data ]
    except Exception as e:
        print(f"加载或解析YAML文件时出错: {e}")
        return []

def main_with_snapshots():
    print("正在初始化仿真环境...")
    real_map = Map()
    print("真实地图创建完成。")
    coord_system = MultiAgentCoordinationSystem(real_map)
    print("协调系统初始化完成。")

    tasks = load_tasks_from_yaml('tasks.yaml')
    if not tasks:
        print("未找到任务，创建默认测试任务...")
        tasks = [
            DeliveryTask(goal_pos=(80, 80), weight=15.0, urgency=5, task_id="test_task_1"),
            DeliveryTask(goal_pos=(20, 70), weight=25.0, urgency=4, task_id="test_task_2"),
            DeliveryTask(goal_pos=(60, 30), weight=5.0, urgency=3, task_id="test_task_3"),
            DeliveryTask(goal_pos=(40, 50), weight=10.0, urgency=2, task_id="test_task_4")
        ]
    
    print(f"成功加载 {len(tasks)} 个任务到队列。")
    for task in tasks:
        coord_system.add_task(task)
    
    # 启动后台世界引擎
    coord_system.start()
    print("协调系统已启动，后台引擎开始运转...")

    # 创建可视化器
    visualizer = DeliveryVisualizer(coord_system)
    
    # 准备图形和画布
    fig = visualizer.fig
    
    # 保存当前时间作为时间戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 初始化动画
    visualizer._setup_ax_and_legend()
    artists = visualizer._init_animation()
    
    # 设置总帧数和快照点
    max_frames = 300  # 最多运行300帧
    snapshot_frames = np.linspace(0, max_frames-1, 6, dtype=int)
    frames_taken = set()  # 记录已经截图的帧
    
    # 定义自定义更新函数，在特定帧保存快照
    def update_with_snapshot(frame):
        # 更新可视化
        artists = visualizer._update_frame(frame)
        
        # 如果是需要截图的帧且还没有截过图
        if frame in snapshot_frames and frame not in frames_taken:
            snapshot_num = np.where(snapshot_frames == frame)[0][0] + 1
            
            # 保存快照
            output_path = os.path.join(OUTPUT_DIR, f"snapshot_{snapshot_num}_frame_{frame}_{timestamp}.png")
            fig.savefig(output_path, dpi=300, bbox_inches='tight')
            frames_taken.add(frame)
            
            # 输出完成信息
            completed = coord_system.get_completed_task_count()
            total = len(tasks)
            completion_rate = f"{completed/total*100:.1f}%" if total > 0 else "0.0%"
            active = sum(1 for agent in coord_system.agents.values() if agent.state != "idle")
            print(f"✅ 已保存快照 {snapshot_num}/6 (帧 {frame}): 完成率 {completion_rate}, 活跃智能体 {active}")
            
            # 检查是否完成所有快照
            if len(frames_taken) == len(snapshot_frames):
                print("已完成所有6张快照的截取!")
        
        return artists
    
    # 创建动画
    ani = animation.FuncAnimation(
        fig,
        update_with_snapshot,
        interval=50,
        frames=max_frames,
        blit=True,
        cache_frame_data=False
    )
    
    # 显示动画并等待交互
    print("开始捕捉快照，请等待...")
    plt.show()
    
    # 输出摘要
    print("\n📸 快照摘要:")
    print("---------------------------------------------")
    print("序号  帧号   完成率    文件名")
    print("---------------------------------------------")
    for i, frame in enumerate(sorted(frames_taken)):
        snapshot_num = np.where(snapshot_frames == frame)[0][0] + 1
        filename = f"snapshot_{snapshot_num}_frame_{frame}_{timestamp}.png"
        completed = coord_system.get_completed_task_count()
        total = len(tasks)
        completion_rate = f"{completed/total*100:.1f}%" if total > 0 else "0.0%"
        print(f"{snapshot_num:2d}    {frame:3d}   {completion_rate:6s}   {filename}")
    print("---------------------------------------------")
    
    print("可视化窗口已关闭...")
    coord_system.stop()
    print("仿真已结束。")
    print(f"所有快照已保存到 '{OUTPUT_DIR}' 目录")

if __name__ == "__main__":
    print("========== 多智能体协作配送系统可视化快照程序 ==========")
    print("将截取系统运行全过程的6个等分时刻的状态图")
    main_with_snapshots()
    print("程序执行完毕!")