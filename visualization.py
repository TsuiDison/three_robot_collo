# visualization.py
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle, Circle, Patch
import numpy as np
import matplotlib.markers
from config import VISUALIZATION_COLORS, TERRAIN_COLORS

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

class DeliveryVisualizer:
    def __init__(self, coordination_system):
        self.coord_system = coordination_system
        self.knowledge_map = coordination_system.knowledge_map
        self.real_map = coordination_system.real_map
        self.fig, self.ax = plt.subplots(figsize=(16, 10))
        
        # Artist 池
        self.agent_artists = {}
        self.pending_task_pool = []
        self.relay_task_pool_artists = []
        self.MAX_TASKS_TO_DISPLAY = 30
        
        self.info_panel_text = None
        self.map_image_artist = None
        
    def _init_animation(self):
        """
        初始化动画。只创建 Artists，不做任何其他事情。
        这是 blit=True 模式的关键。
        """
        print("Initializing animation artists...")
        
        # 1. 初始化地图图像 Artist
        self.map_image_artist = self.ax.imshow(
            np.zeros((1, 1, 3), dtype=np.uint8), # 初始给一个1x1的空图像
            origin='lower', 
            extent=[0, self.knowledge_map.width, 0, self.knowledge_map.height],
            interpolation='nearest', 
            animated=True
        )

        # 2. 初始化智能体 Artists
        for agent_id in self.coord_system.agents.keys():
            scatter = self.ax.scatter([], [], s=120, edgecolors='white', zorder=10, animated=True)
            text = self.ax.text(0, 0, "", fontsize=8, color='white', backgroundcolor=(0,0,0,0.5), animated=True)
            path, = self.ax.plot([], [], color=VISUALIZATION_COLORS['agent_path'], linestyle=':', linewidth=1.5, alpha=0.8, animated=True)
            target_marker = self.ax.scatter([], [], marker='x', s=150, zorder=9, linewidth=3, animated=True)
            self.agent_artists[agent_id] = {'scatter': scatter, 'text': text, 'path': path, 'target': target_marker}
            
        # 3. 初始化任务标记 Artists 池
        for _ in range(self.MAX_TASKS_TO_DISPLAY):
            self.pending_task_pool.append(self.ax.scatter([], [], marker='P', s=150, edgecolors='white', zorder=6, linewidth=1.5, animated=True))
            scatter_r = self.ax.scatter([], [], marker='s', s=80, edgecolors='black', zorder=7, animated=True)
            text_r = self.ax.text(0, 0, "", fontsize=7, color='cyan', ha='left', va='center', zorder=7, animated=True)
            self.relay_task_pool_artists.append((scatter_r, text_r))

        # 4. 初始化信息面板 Artist
        self.info_panel_text = self.ax.text(0.01, 0.98, "", transform=self.ax.transAxes, fontsize=10, 
                                            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8), animated=True)
        
        # 5. 将所有动态 Artists 收集到一个列表中并返回
        all_artists = [self.map_image_artist, self.info_panel_text]
        for artists_dict in self.agent_artists.values(): all_artists.extend(artists_dict.values())
        all_artists.extend(self.pending_task_pool)
        for artist_tuple in self.relay_task_pool_artists: all_artists.extend(artist_tuple)
        
        print(f"Animation initialized with {len(all_artists)} artists.")
        return all_artists

    def _update_frame(self, frame):
        """动画的每一帧更新函数，只更新数据，不创建或删除 Artists"""
        
        # 1. 更新知识地图 (已修复和优化)
        # 使用 float32 类型以匹配归一化的颜色值，更高效
        image_data = np.zeros((self.knowledge_map.height, self.knowledge_map.width, 3), dtype=np.float32)
        for terrain_id, color_tuple in self.knowledge_map.color_map.items():
            # 关键修复：将 (width, height) 的掩码转置为 (height, width)
            mask = (self.knowledge_map.terrain == terrain_id).T
            # 直接使用归一化的颜色元组，无需再次转换
            image_data[mask] = color_tuple
        self.map_image_artist.set_data(image_data)

        # 2. 更新智能体
        state_info = {"idle": ('green', 'o'), "delivering": ('orange', '>'), "returning": ('cyan', '<')}
        for agent_id, agent in self.coord_system.agents.items():
            artists = self.agent_artists[agent_id]
            artists['scatter'].set_offsets(agent.position)
            artists['text'].set_position((agent.position[0] + 1.5, agent.position[1] + 1.5))
            color, marker = state_info.get(agent.state, ('white', 'x'))
            artists['scatter'].set_color(color)
            marker_style = matplotlib.markers.MarkerStyle(marker)
            artists['scatter'].set_paths([marker_style.get_path().transformed(marker_style.get_transform())])
            artists['text'].set_text(f"{agent.agent_id}\n{agent.state}")
            
            if agent.state in ["delivering", "returning"] and agent.vehicle and agent.vehicle.path:
                path_arr = np.array(agent.vehicle.path)
                target_pos = path_arr[-1]
                target_color = agent.current_task.color if agent.state == "delivering" and agent.current_task else VISUALIZATION_COLORS['agent_path']
                artists['path'].set_data(path_arr[:, 0], path_arr[:, 1]); artists['path'].set_color(target_color); artists['path'].set_visible(True)
                artists['target'].set_offsets(target_pos); artists['target'].set_color(target_color); artists['target'].set_visible(True)
            else:
                artists['path'].set_visible(False); artists['target'].set_visible(False)
        
        # 3. 更新任务标记 (使用池)
        with self.coord_system.main_task_queue.mutex:
            tasks_to_show_tuples = list(self.coord_system.main_task_queue.queue)
            # 我们只需要第三个元素，也就是 DeliveryTask 对象
            tasks_to_show = [task_tuple[2] for task_tuple in tasks_to_show_tuples]
        for i, artist in enumerate(self.pending_task_pool):
            if i < len(tasks_to_show):
                artist.set_offsets(tasks_to_show[i].original_goal); artist.set_color(tasks_to_show[i].color); artist.set_visible(True)
            else:
                artist.set_visible(False)
        tasks_to_show_r = self.coord_system.relay_task_pool
        for i, (scatter, text) in enumerate(self.relay_task_pool_artists):
            if i < len(tasks_to_show_r):
                pos = (self.coord_system.relay_station_pos[0], self.coord_system.relay_station_pos[1] - i * 2.5)
                scatter.set_offsets(pos); scatter.set_facecolor(tasks_to_show_r[i].color); scatter.set_visible(True)
                text.set_position((pos[0] + 2, pos[1])); text.set_text(tasks_to_show_r[i].task_id); text.set_color(tasks_to_show_r[i].color); text.set_visible(True)
            else:
                scatter.set_visible(False); text.set_visible(False)

        # 4. 更新信息面板
        states = [agent.state for agent in self.coord_system.agents.values()]
        info_text = (f"系统状态\n" f"总智能体: {len(self.coord_system.agents)} (空闲: {states.count('idle')})\n" f"配送中: {states.count('delivering')}\n" f"返回中: {states.count('returning')}\n" f"主线待处理: {self.coord_system.main_task_queue.qsize()}\n" f"中转站待接力: {len(self.coord_system.relay_task_pool)}\n" f"已完成任务: {self.coord_system.get_completed_task_count()}")
        self.info_panel_text.set_text(info_text)
        
        # 返回所有动态 Artists
        all_artists = [self.map_image_artist, self.info_panel_text]
        for artists_dict in self.agent_artists.values(): all_artists.extend(artists_dict.values())
        all_artists.extend(self.pending_task_pool)
        for artist_tuple in self.relay_task_pool_artists: all_artists.extend(artist_tuple)
            
        return all_artists

    def start_animation(self):
        """启动高性能动画"""
        # 静态背景和图例在动画开始前就绘制好
        self._setup_ax_and_legend()
        
        ani = animation.FuncAnimation(
            self.fig, 
            self._update_frame, 
            init_func=self._init_animation,
            interval=100,
            blit=True,
            cache_frame_data=False
        )
        plt.show()
        self.coord_system.stop()

    def _setup_ax_and_legend(self):
        """
        一次性设置坐标轴、静态背景和分组化的详细图例。
        """
        # --- 坐标轴和静态背景设置 (保持不变) ---
        self.ax.set_title('多智能体协作配送系统 (最终演示版)', fontsize=16)
        self.ax.set_xlabel('X 坐标'); self.ax.set_ylabel('Y 坐标')
        self.ax.set_xlim(0, self.real_map.width); self.ax.set_ylim(0, self.real_map.height)
        unknown_color_hex = TERRAIN_COLORS.get('unknown', '#141414')
        self.ax.set_facecolor(unknown_color_hex); self.ax.grid(True, linestyle='--', color='gray', alpha=0.2)
        
        # 绘制仓库和中转站
        for name, facility in [("W", self.real_map.warehouse), ("R", self.real_map.relay_station)]:
            rect_data = facility["rect"]; color = facility["color"]
            self.ax.add_patch(Rectangle((rect_data[0], rect_data[1]), rect_data[2], rect_data[3], facecolor=color, edgecolor='white', zorder=5))
            center = facility["center"]; self.ax.text(center[0], center[1], name, color='black', ha='center', va='center', fontsize=12, weight='bold')
        
        # 绘制建筑和障碍物
        for x, y, w, h in self.real_map.buildings: self.ax.add_patch(Rectangle((x, y), w, h, facecolor=VISUALIZATION_COLORS['building'], edgecolor='black', zorder=4))
        for x, y, r in self.real_map.obstacles: self.ax.add_patch(Circle((x, y), r, facecolor=VISUALIZATION_COLORS['obstacle'], alpha=0.8, zorder=4))
        
        # --- 创建分组图例 ---

        # 图例组1: 地图与地形
        map_legend_elements = [
            # 从 TERRAIN_COLORS 动态生成地形图例
            Patch(facecolor=c, label=n.capitalize()) for n, c in TERRAIN_COLORS.items() if n != 'unknown'
        ]
        map_legend_elements.extend([
            # 手动添加地图上的静态设施
            Patch(facecolor=self.real_map.warehouse['color'], label='仓库 (W)'),
            Patch(facecolor=self.real_map.relay_station['color'], label='中转站 (R)'),
            Patch(facecolor=VISUALIZATION_COLORS['building'], label='建筑'),
            Patch(facecolor=VISUALIZATION_COLORS['obstacle'], alpha=0.8, label='障碍物')
        ])
        # 创建第一个图例并设置位置
        map_legend = self.ax.legend(
            handles=map_legend_elements, 
            loc='upper left', 
            bbox_to_anchor=(1.01, 1), # 放置在绘图区域的右侧外部
            fontsize='small', 
            title="地图图例"
        )
        # 将第一个图例添加到 a`x` 中，这样它就不会被下一个 legend 调用覆盖
        self.ax.add_artist(map_legend)

        # 图例组2: 智能体与任务
        agent_task_legend_elements = [
            # 智能体状态 (使用 Line2D 创建带标记的图例项，linestyle='None'表示不画线)
            plt.Line2D([0], [0], marker='o', color='w', label='空闲 (Idle)', 
                       markerfacecolor='green', markersize=10, linestyle='None'),
            plt.Line2D([0], [0], marker='>', color='w', label='配送中 (Delivering)', 
                       markerfacecolor='orange', markersize=10, linestyle='None'),
            plt.Line2D([0], [0], marker='<', color='w', label='返回中 (Returning)', 
                       markerfacecolor='cyan', markersize=10, linestyle='None'),
            # 智能体路径和目标
            plt.Line2D([], [], color=VISUALIZATION_COLORS['agent_path'], linestyle=':', 
                       linewidth=2, label='智能体路径'),
            plt.Line2D([0], [0], marker='x', color='yellow', label='当前目标点', 
                       markersize=10, mew=3, linestyle='None'),
            # 任务标记
            plt.Line2D([0], [0], marker='P', color='w', label='待处理任务', 
                       markerfacecolor='magenta', markersize=12, linestyle='None'),
            plt.Line2D([0], [0], marker='s', color='w', label='待接力任务', 
                       markerfacecolor='cyan', markeredgecolor='black', markersize=10, linestyle='None')
        ]
        # 创建第二个图例，并放置在第一个图例的下方
        self.ax.legend(
            handles=agent_task_legend_elements, 
            loc='upper left', 
            bbox_to_anchor=(1.01, 0.65), # 调整y坐标，使其位于第一个图例下方
            fontsize='small', 
            title="智能体与任务"
        )

        # 调整布局，为右侧的图例留出空间
        self.fig.tight_layout(rect=[0, 0, 0.85, 1])