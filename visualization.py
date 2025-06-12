# -*- coding: utf-8 -*-
"""
可视化系统模块
负责GUI界面、地图渲染和动画更新
"""

import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle, Rectangle, Polygon
from matplotlib import rcParams
from vehicle_system import Drone
from delivery_task import DeliveryTask

# 设置默认字体以避免警告
rcParams['font.family'] = ['SimHei', 'Microsoft YaHei', 'sans-serif']


class DeliveryVisualizer:
    """可视化类"""
    
    def __init__(self, delivery_system, map, width=1200, height=800):
        self.delivery_system = delivery_system
        self.map = map
        self.root = tk.Tk()
        self.root.title("多智能体协作配送系统")
        self.root.geometry(f"{width}x{height}")
        
        # 确保中文显示正常
        self.setup_fonts()
        
        # 创建框架
        self.control_frame = ttk.Frame(self.root, padding="10")
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        self.canvas_frame = ttk.Frame(self.root)
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 反馈文本框放在右侧
        self.feedback_frame = ttk.Frame(self.root, padding="10")
        self.feedback_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=10)
        
        # 创建matplotlib图形和画布
        self.fig = Figure(figsize=(9, 7), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 初始化控件
        self._create_controls()
        self._create_feedback_area()
        
        # 动画设置
        self.animation = None
        self.path_lines = []
        self.vehicle_markers = []
        self.obstacle_patches = []
        self.terrain_image = None
        self.drone_patches = []
        self.car_patches = []
        self.robot_dog_patches = []
        self.path_traces = []  # 用于载具路径的可视化
        self.trace_lines = []  # 路径轨迹的线条
        
        # 初始化可视化
        self.initialize_visualization()
    
    def setup_fonts(self):
        """确保中文显示正常"""
        plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC", "sans-serif"]
    
    def _create_controls(self):
        """创建控制面板"""
        # 天气控制
        ttk.Label(self.control_frame, text="天气条件:").pack(anchor=tk.W, pady=5)
        self.weather_var = tk.StringVar(value="clear")
        weather_options = ["clear", "rainy", "windy", "stormy"]
        self.weather_combo = ttk.Combobox(self.control_frame, textvariable=self.weather_var, values=weather_options)
        self.weather_combo.pack(fill=tk.X, pady=5)
        self.weather_combo.bind("<<ComboboxSelected>>", self.update_weather)
        
        # 任务创建控制
        ttk.Label(self.control_frame, text="创建新任务:").pack(anchor=tk.W, pady=10)
        
        # 坐标输入
        ttk.Label(self.control_frame, text="起点 X:").pack(anchor=tk.W)
        self.start_x = tk.Entry(self.control_frame)
        self.start_x.insert(0, "10")
        self.start_x.pack(fill=tk.X, pady=2)
        
        ttk.Label(self.control_frame, text="起点 Y:").pack(anchor=tk.W)
        self.start_y = tk.Entry(self.control_frame)
        self.start_y.insert(0, "10")
        self.start_y.pack(fill=tk.X, pady=2)
        
        ttk.Label(self.control_frame, text="终点 X:").pack(anchor=tk.W)
        self.goal_x = tk.Entry(self.control_frame)
        self.goal_x.insert(0, "80")
        self.goal_x.pack(fill=tk.X, pady=2)
        
        ttk.Label(self.control_frame, text="终点 Y:").pack(anchor=tk.W)
        self.goal_y = tk.Entry(self.control_frame)
        self.goal_y.insert(0, "80")
        self.goal_y.pack(fill=tk.X, pady=2)
        
        # 任务属性输入
        ttk.Label(self.control_frame, text="重量限制:").pack(anchor=tk.W)
        self.weight = tk.Entry(self.control_frame)
        self.weight.insert(0, "2")
        self.weight.pack(fill=tk.X, pady=2)
        
        ttk.Label(self.control_frame, text="时间窗口:").pack(anchor=tk.W)
        self.time_window = tk.Entry(self.control_frame)
        self.time_window.insert(0, "30")
        self.time_window.pack(fill=tk.X, pady=2)
        
        ttk.Label(self.control_frame, text="紧急程度:").pack(anchor=tk.W)
        self.urgency = tk.Entry(self.control_frame)
        self.urgency.insert(0, "2")
        self.urgency.pack(fill=tk.X, pady=2)
        
        ttk.Label(self.control_frame, text="安全需求:").pack(anchor=tk.W)
        self.safety = tk.Entry(self.control_frame)
        self.safety.insert(0, "2")
        self.safety.pack(fill=tk.X, pady=2)
        
        ttk.Label(self.control_frame, text="成本限制:").pack(anchor=tk.W)
        self.cost_limit = tk.Entry(self.control_frame)
        self.cost_limit.insert(0, "100")
        self.cost_limit.pack(fill=tk.X, pady=2)
        
        ttk.Label(self.control_frame, text="货物类型:").pack(anchor=tk.W)
        self.cargo_type = tk.Entry(self.control_frame)
        self.cargo_type.insert(0, "normal")
        self.cargo_type.pack(fill=tk.X, pady=2)
        
        self.create_task_btn = ttk.Button(self.control_frame, text="创建任务", command=self.create_task)
        self.create_task_btn.pack(fill=tk.X, pady=10)
    
    def _create_feedback_area(self):
        """创建反馈区域"""
        ttk.Label(self.feedback_frame, text="系统反馈:").pack(anchor=tk.W, pady=10)
        self.feedback_text = scrolledtext.ScrolledText(self.feedback_frame, wrap=tk.WORD, width=35, height=25)
        self.feedback_text.pack(fill=tk.BOTH, expand=True, pady=5)
    
    def initialize_visualization(self):
        """初始化地图和载具的可视化"""
        self.ax.clear()
        self.ax.set_xlim(0, self.map.width)
        self.ax.set_ylim(0, self.map.height)
        self.ax.set_aspect('equal')
        self.ax.set_title("多智能体协作配送系统")
        
        # 创建地形图像
        terrain_colors = {
            'normal': '#90EE90',  # 浅绿色
            'steep': '#8B4513',   # 棕色
            'narrow': '#D2B48C',  # 棕褐色
            'hilly': '#556B2F',   # 深橄榄绿
            'water': '#87CEEB',   # 浅蓝色
            'road': '#808080'     # 灰色
        }
        
        terrain_image = np.zeros((self.map.height, self.map.width, 3))
        for x in range(self.map.width):
            for y in range(self.map.height):
                terrain_type = self.map.get_terrain(x, y)
                color = terrain_colors.get(terrain_type, '#FFFFFF')  # 默认为白色
                # 将十六进制颜色转换为RGB
                color = mcolors.to_rgb(color)
                terrain_image[y, x] = color
        
        self.terrain_image = self.ax.imshow(terrain_image, origin='lower', extent=[0, self.map.width, 0, self.map.height])
        
        # 绘制河流
        for river_points, width in self.map.rivers:
            river_x = [p[0] for p in river_points]
            river_y = [p[1] for p in river_points]
            self.ax.plot(river_x, river_y, 'b-', linewidth=width, alpha=0.5)
        
        # 绘制道路
        road_x = [p[0] for p in self.map.roads]
        road_y = [p[1] for p in self.map.roads]
        self.ax.scatter(road_x, road_y, color='#808080', s=10, alpha=0.5)
        
        # 绘制建筑物
        for building in self.map.buildings:
            x, y, width, height = building
            rect = Rectangle((x, y), width, height, linewidth=1, edgecolor='black', facecolor='#A9A9A9')
            self.ax.add_patch(rect)
        
        # 绘制障碍物
        for obstacle in self.map.obstacles:
            x, y, radius = obstacle
            circle = Circle((x, y), radius, linewidth=1, edgecolor='black', facecolor='#FF0000')
            self.ax.add_patch(circle)
        
        # 用独特的形状和颜色初始化载具标记
        self._initialize_vehicle_markers()
        
        # 绘制图例
        self.ax.plot([], [], 'bo', label='无人机')
        self.ax.plot([], [], 'ro', label='汽车')
        self.ax.plot([], [], 'go', label='机器狗')
        self.ax.legend(loc='upper right')
        
        self.canvas.draw()
    
    def _initialize_vehicle_markers(self):
        """初始化载具标记"""
        for i, drone in enumerate(self.delivery_system.drones):
            # 为无人机创建三角形
            drone_patch = Polygon(self._get_triangle_points(drone.current_pos[0], drone.current_pos[1]), 
                                 closed=True, edgecolor='blue', facecolor=drone.color)
            self.ax.add_patch(drone_patch)
            self.drone_patches.append(drone_patch)
        
        for i, car in enumerate(self.delivery_system.cars):
            # 为汽车创建矩形
            car_patch = Rectangle((car.current_pos[0] - 1, car.current_pos[1] - 0.7), 2, 1.4, 
                                 edgecolor='red', facecolor=car.color, angle=np.degrees(car.heading))
            self.ax.add_patch(car_patch)
            self.car_patches.append(car_patch)
        
        for i, robot_dog in enumerate(self.delivery_system.robot_dogs):
            # 为机器狗创建菱形
            robot_dog_patch = Polygon(self._get_diamond_points(robot_dog.current_pos[0], robot_dog.current_pos[1]), 
                                     closed=True, edgecolor='green', facecolor=robot_dog.color)
            self.ax.add_patch(robot_dog_patch)
            self.robot_dog_patches.append(robot_dog_patch)
    
    def _get_triangle_points(self, x, y, size=1.5):
        """生成指向无人机方向的三角形点"""
        points = [
            (x, y + size),
            (x - size/2, y - size/2),
            (x + size/2, y - size/2)
        ]
        return points
    
    def _get_diamond_points(self, x, y, size=1.0):
        """生成菱形的点"""
        points = [
            (x, y + size),
            (x + size, y),
            (x, y - size),
            (x - size, y)
        ]
        return points
    
    def update_visualization(self, frame):
        """更新动画的每一帧的可视化"""
        try:
            # 更新无人机位置和旋转
            for i, drone in enumerate(self.delivery_system.drones):
                if i < len(self.drone_patches):
                    x, y = drone.animation_state["position"]
                    rotation = drone.animation_state["rotation"]
                    
                    # 更新位置和旋转
                    triangle = self._get_triangle_points(x, y)
                    rotated_triangle = self._rotate_polygon(triangle, (x, y), rotation)
                    self.drone_patches[i].set_xy(rotated_triangle)
                    
                    # 添加高度指示器
                    if drone.animation_state.get("height"):
                        height_text = f"H: {drone.animation_state['height']:.1f}"
                        if hasattr(drone, 'height_text'):
                            drone.height_text.set_text(height_text)
                            drone.height_text.set_position((x, y + 2))
                        else:
                            drone.height_text = self.ax.text(x, y + 2, height_text, fontsize=8, 
                                                            ha='center', va='center', color='blue')
            
            # 更新汽车位置和旋转
            for i, car in enumerate(self.delivery_system.cars):
                if i < len(self.car_patches):
                    x, y = car.animation_state["position"]
                    rotation = car.animation_state["rotation"]
                    
                    # 更新位置和旋转
                    self.car_patches[i].set_xy((x - 1, y - 0.7))
                    self.car_patches[i].angle = np.degrees(rotation)
            
            # 更新机器狗位置和旋转
            for i, robot_dog in enumerate(self.delivery_system.robot_dogs):
                if i < len(self.robot_dog_patches):
                    x, y = robot_dog.animation_state["position"]
                    rotation = robot_dog.animation_state["rotation"]
                    
                    # 更新位置和旋转
                    diamond = self._get_diamond_points(x, y)
                    rotated_diamond = self._rotate_polygon(diamond, (x, y), rotation)
                    self.robot_dog_patches[i].set_xy(rotated_diamond)
            
            # 清除旧的路径轨迹
            for trace in self.path_lines:
                trace.remove()
            for trace in self.trace_lines:
                trace.remove()
                
            self.path_lines = []
            self.trace_lines = []
            
            # 绘制新路径和轨迹
            for vehicle, path, task in self.delivery_system.current_paths:
                if not path:
                    continue
                    
                # 绘制规划路径
                if isinstance(vehicle, Drone):
                    color = vehicle.color
                    path_x = [p[0] for p in path]
                    path_y = [p[1] for p in path]
                else:
                    color = vehicle.color
                    path_x = [p[0] for p in path]
                    path_y = [p[1] for p in path]
                
                path_line, = self.ax.plot(path_x, path_y, '--', linewidth=1, color=color, alpha=0.7)
                self.path_lines.append(path_line)
                
                # 绘制实际移动轨迹
                if vehicle.path_trace:
                    trace_x = [p[0] for p in vehicle.path_trace]
                    trace_y = [p[1] for p in vehicle.path_trace]
                    trace_line, = self.ax.plot(trace_x, trace_y, '-', linewidth=0.8, color=color, alpha=0.5)
                    self.trace_lines.append(trace_line)
            
            # 更新反馈文本
            self.feedback_text.delete(1.0, tk.END)
            for feedback in self.delivery_system.feedback[-15:]:  # 显示最后15条反馈
                self.feedback_text.insert(tk.END, feedback + "\n")
            self.feedback_text.see(tk.END)  # 自动滚动到末尾
            
            return self.drone_patches + self.car_patches + self.robot_dog_patches + self.path_lines + self.trace_lines
        except Exception as e:
            # 捕获动画更新过程中的异常，防止动画停止
            self.feedback_text.insert(tk.END, f"动画更新错误: {str(e)}\n")
            return []
    
    def _rotate_polygon(self, points, origin, rotation):
        """围绕点旋转多边形"""
        rotated_points = []
        for point in points:
            # 将点移动到原点
            translated_x = point[0] - origin[0]
            translated_y = point[1] - origin[1]
            
            # 旋转点
            rotated_x = translated_x * np.cos(rotation) - translated_y * np.sin(rotation)
            rotated_y = translated_x * np.sin(rotation) + translated_y * np.cos(rotation)
            
            # 移回原位置
            rotated_points.append((rotated_x + origin[0], rotated_y + origin[1]))
            
        return rotated_points
    
    def update_weather(self, event=None):
        """更新天气条件"""
        weather = self.weather_var.get()
        self.map.set_weather(weather)
        self.delivery_system.feedback.append(f"天气已更新为: {weather}")
    
    def create_task(self):
        """创建新的配送任务"""
        try:
            start_x = int(self.start_x.get())
            start_y = int(self.start_y.get())
            goal_x = int(self.goal_x.get())
            goal_y = int(self.goal_y.get())
            weight = float(self.weight.get())
            time_window = float(self.time_window.get())
            urgency = int(self.urgency.get())
            safety = int(self.safety.get())
            cost_limit = float(self.cost_limit.get())
            cargo_type = self.cargo_type.get()
            
            # 验证位置
            if not self.map.is_valid(start_x, start_y):
                self.feedback_text.insert(tk.END, f"错误: 起点 ({start_x}, {start_y}) 无效\n")
                return
            
            if not self.map.is_valid(goal_x, goal_y):
                self.feedback_text.insert(tk.END, f"错误: 终点 ({goal_x}, {goal_y}) 无效\n")
                return
            
            # 创建任务
            task = DeliveryTask(
                (start_x, start_y),
                (goal_x, goal_y),
                weight=weight,
                time_window=time_window,
                urgency=urgency,
                safety=safety,
                cost_limit=cost_limit,
                cargo_type=cargo_type
            )
            
            # 将任务添加到配送系统
            self.delivery_system.add_task(task)
            self.feedback_text.insert(tk.END, f"新任务已创建: 从 ({start_x}, {start_y}) 到 ({goal_x}, {goal_y})\n")
        except Exception as e:
            self.feedback_text.insert(tk.END, f"创建任务时出错: {str(e)}\n")
    
    def start_animation(self):
        """启动动画"""
        self.animation = FuncAnimation(self.fig, self.update_visualization, 
                                       interval=50, blit=True, cache_frame_data=False)
        self.canvas.draw()
        
        # 设置窗口关闭时的处理函数
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """处理窗口关闭事件"""
        if messagebox.askokcancel("退出", "确定要退出吗?"):
            if self.animation:
                self.animation.event_source.stop()
            self.root.destroy()