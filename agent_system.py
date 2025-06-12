# -*- coding: utf-8 -*-
"""
智能体系统模块
定义智能体基类和具体智能体实现
"""

import numpy as np
import threading
import time
import queue
import random
from abc import ABC, abstractmethod
from vehicle_system import Drone, Car, RobotDog
from path_planning import a_star_planning


class Agent(ABC):
    """智能体基类"""
    
    def __init__(self, agent_id, position, capabilities):
        self.agent_id = agent_id
        self.position = position
        self.capabilities = capabilities
        self.state = "idle"  # idle, moving, busy, charging
        self.current_task = None
        self.knowledge_base = {}
        self.communication_queue = queue.Queue()
        self.message_history = []
        self.performance_metrics = {
            "tasks_completed": 0,
            "total_distance": 0,
            "energy_consumed": 0,
            "success_rate": 0.0
        }
        self.is_active = True
        self.decision_thread = None
        
    @abstractmethod
    def perceive_environment(self, map_system):
        """感知环境"""
        pass
    
    @abstractmethod
    def make_decision(self, available_tasks):
        """决策制定"""
        pass
    
    @abstractmethod
    def execute_action(self, action, map_system):
        """执行动作"""
        pass
    
    @abstractmethod
    def communicate(self, message, target_agent=None):
        """与其他智能体通信"""
        pass
    
    def receive_message(self, message):
        """接收消息"""
        self.communication_queue.put(message)
        self.message_history.append(message)
    
    def process_messages(self):
        """处理接收到的消息"""
        while not self.communication_queue.empty():
            message = self.communication_queue.get()
            self.handle_message(message)
    
    @abstractmethod
    def handle_message(self, message):
        """处理具体消息"""
        pass
    
    def update_knowledge(self, key, value):
        """更新知识库"""
        self.knowledge_base[key] = value
    
    def get_knowledge(self, key, default=None):
        """获取知识"""
        return self.knowledge_base.get(key, default)
    
    def update_performance(self, metric, value):
        """更新性能指标"""
        if metric in self.performance_metrics:
            self.performance_metrics[metric] = value
    
    def start_agent(self):
        """启动智能体"""
        self.is_active = True
        self.decision_thread = threading.Thread(target=self.agent_loop, daemon=True)
        self.decision_thread.start()
    
    def stop_agent(self):
        """停止智能体"""
        self.is_active = False
    
    def agent_loop(self):
        """智能体主循环"""
        while self.is_active:
            try:
                self.process_messages()
                time.sleep(0.1)  # 防止过度占用CPU
            except Exception as e:
                print(f"Agent {self.agent_id} error in main loop: {e}")


class DroneAgent(Agent):
    """无人机智能体"""
    
    def __init__(self, agent_id, position):
        capabilities = {
            "speed": 15,
            "weight_limit": 5,
            "terrain_adaptability": 5,  # 可跨越所有地形
            "cost": 2,
            "safety": 4,
            "flight_height": (5, 20),
            "weather_resistance": 2
        }
        super().__init__(agent_id, position, capabilities)
        self.vehicle = Drone(position, position)
        self.battery_level = 100
        self.max_flight_time = 30  # 分钟
        self.current_height = 10
        
    def perceive_environment(self, map_system):
        """感知环境 - 无人机可以获得更广阔的视野"""
        perception = {
            "current_position": self.position,
            "battery_level": self.battery_level,
            "weather": map_system.weather,
            "weather_effect": map_system.weather_effect,
            "visible_obstacles": [],
            "traffic_density": self.assess_air_traffic(),
            "no_fly_zones": self.detect_no_fly_zones(map_system)
        }
        
        # 检测周围的障碍物和地形
        vision_range = 15
        for x in range(max(0, int(self.position[0] - vision_range)), 
                      min(map_system.width, int(self.position[0] + vision_range))):
            for y in range(max(0, int(self.position[1] - vision_range)), 
                          min(map_system.height, int(self.position[1] + vision_range))):
                if map_system.is_obstacle(x, y):
                    perception["visible_obstacles"].append((x, y))
        
        return perception
    
    def make_decision(self, available_tasks):
        """决策制定 - 基于任务优先级和自身状态"""
        if self.state != "idle" or self.battery_level < 20:
            return None
        
        best_task = None
        best_score = -1
        
        for task in available_tasks:
            # 计算任务适配度
            distance = np.sqrt((task.goal_pos[0] - self.position[0])**2 + 
                             (task.goal_pos[1] - self.position[1])**2)
            
            # 检查重量限制
            weight = task.get_attribute(1, 0)
            if weight > self.capabilities["weight_limit"]:
                continue
            
            # 检查时间窗口
            time_window = task.get_attribute(3, float('inf'))
            estimated_time = distance / self.capabilities["speed"]
            if estimated_time > time_window:
                continue
            
            # 计算评分
            urgency = task.get_attribute(5, 1)
            safety_req = task.get_attribute(4, 1)
            
            score = (urgency * 0.4 + 
                    (1 / (distance + 1)) * 0.3 + 
                    self.capabilities["safety"] * safety_req * 0.3)
            
            if score > best_score:
                best_score = score
                best_task = task
        
        return best_task
    
    def execute_action(self, action, map_system):
        """执行动作"""
        if action["type"] == "deliver":
            task = action["task"]
            self.current_task = task
            self.state = "moving"
            
            # 规划路径
            path = a_star_planning(self.vehicle, map_system, self.position, task.goal_pos)
            if path:
                self.vehicle.path = path
                self.vehicle.current_waypoint_index = 0
                return True
            else:
                self.state = "idle"
                return False
        
        elif action["type"] == "return_base":
            self.state = "moving"
            base_position = (10, 10, 10)  # 基地位置
            path = a_star_planning(self.vehicle, map_system, self.position, base_position)
            if path:
                self.vehicle.path = path
                self.vehicle.current_waypoint_index = 0
                return True
            return False
        
        elif action["type"] == "charge":
            self.state = "charging"
            self.battery_level = min(100, self.battery_level + 10)
            if self.battery_level >= 100:
                self.state = "idle"
            return True
        
        return False
    
    def communicate(self, message, target_agent=None):
        """与其他智能体通信"""
        communication_msg = {
            "sender": self.agent_id,
            "target": target_agent,
            "message": message,
            "timestamp": time.time(),
            "position": self.position
        }
        return communication_msg
    
    def handle_message(self, message):
        """处理消息"""
        msg_type = message.get("type", "")
        
        if msg_type == "task_request":
            # 其他智能体请求协助
            if self.state == "idle" and self.battery_level > 50:
                response = self.communicate({
                    "type": "task_response",
                    "available": True,
                    "capabilities": self.capabilities
                }, message["sender"])
                return response
        
        elif msg_type == "obstacle_warning":
            # 障碍物警告
            obstacle_pos = message.get("obstacle_position")
            self.update_knowledge(f"obstacle_{obstacle_pos}", True)
        
        elif msg_type == "weather_update":
            # 天气更新
            weather_info = message.get("weather_info")
            self.update_knowledge("weather", weather_info)
    
    def assess_air_traffic(self):
        """评估空中交通密度"""
        return random.randint(0, 5)  # 简化实现
    
    def detect_no_fly_zones(self, map_system):
        """检测禁飞区"""
        no_fly_zones = []
        # 建筑物上方可能是禁飞区
        for building in map_system.buildings:
            x, y, width, height = building
            no_fly_zones.append((x, y, width, height))
        return no_fly_zones


class CarAgent(Agent):
    """汽车智能体"""
    
    def __init__(self, agent_id, position):
        capabilities = {
            "speed": 5,
            "weight_limit": 100,
            "terrain_adaptability": 2,  # 仅限道路
            "cost": 1,
            "safety": 5,
            "fuel_efficiency": 8,
            "cargo_space": 50
        }
        super().__init__(agent_id, position, capabilities)
        self.vehicle = Car(position, position)
        self.fuel_level = 100
        self.cargo_load = 0
        
    def perceive_environment(self, map_system):
        """感知环境 - 汽车主要感知道路状况"""
        perception = {
            "current_position": self.position,
            "fuel_level": self.fuel_level,
            "cargo_load": self.cargo_load,
            "road_conditions": self.assess_road_conditions(map_system),
            "traffic_density": self.assess_traffic_density(),
            "nearby_roads": self.find_nearby_roads(map_system),
            "weather_impact": map_system.weather_effect
        }
        return perception
    
    def make_decision(self, available_tasks):
        """决策制定 - 基于载重能力和道路可达性"""
        if self.state != "idle" or self.fuel_level < 30:
            return None
        
        best_task = None
        best_score = -1
        
        for task in available_tasks:
            # 检查重量限制
            weight = task.get_attribute(1, 0)
            if weight > self.capabilities["weight_limit"]:
                continue
            
            # 检查起点和终点是否在道路上或附近
            if not self.is_accessible_by_road(task.start_pos, task.goal_pos):
                continue
            
            # 计算距离和评分
            distance = np.sqrt((task.goal_pos[0] - self.position[0])**2 + 
                             (task.goal_pos[1] - self.position[1])**2)
            
            cost_efficiency = 1 / (distance * self.capabilities["cost"] + 1)
            cargo_utilization = min(weight / self.capabilities["weight_limit"], 1.0)
            
            score = cost_efficiency * 0.5 + cargo_utilization * 0.3 + self.capabilities["safety"] * 0.2
            
            if score > best_score:
                best_score = score
                best_task = task
        
        return best_task
    
    def execute_action(self, action, map_system):
        """执行动作"""
        if action["type"] == "deliver":
            task = action["task"]
            self.current_task = task
            self.state = "moving"
            
            # 规划道路路径
            path = a_star_planning(self.vehicle, map_system, self.position, task.goal_pos)
            if path:
                self.vehicle.path = path
                self.vehicle.current_waypoint_index = 0
                self.cargo_load += task.get_attribute(1, 0)
                return True
            else:
                self.state = "idle"
                return False
        
        elif action["type"] == "refuel":
            self.state = "busy"
            self.fuel_level = min(100, self.fuel_level + 20)
            if self.fuel_level >= 100:
                self.state = "idle"
            return True
        
        return False
    
    def communicate(self, message, target_agent=None):
        """与其他智能体通信"""
        communication_msg = {
            "sender": self.agent_id,
            "target": target_agent,
            "message": message,
            "timestamp": time.time(),
            "position": self.position
        }
        return communication_msg
    
    def handle_message(self, message):
        """处理消息"""
        msg_type = message.get("type", "")
        
        if msg_type == "road_condition":
            # 道路状况更新
            road_info = message.get("road_info")
            self.update_knowledge("road_conditions", road_info)
        
        elif msg_type == "cargo_request":
            # 大件货物运输请求
            cargo_weight = message.get("weight", 0)
            if cargo_weight <= self.capabilities["weight_limit"] and self.state == "idle":
                response = self.communicate({
                    "type": "cargo_response",
                    "available": True,
                    "capacity": self.capabilities["weight_limit"] - self.cargo_load
                }, message["sender"])
                return response
    
    def assess_road_conditions(self, map_system):
        """评估道路状况"""
        conditions = {"good": 0, "moderate": 0, "poor": 0}
        # 简化实现
        weather_impact = map_system.weather_effect
        if weather_impact > 1.5:
            conditions["poor"] = 3
        elif weather_impact > 1.2:
            conditions["moderate"] = 2
        else:
            conditions["good"] = 1
        return conditions
    
    def assess_traffic_density(self):
        """评估交通密度"""
        return random.randint(1, 10)  # 简化实现
    
    def find_nearby_roads(self, map_system):
        """找到附近的道路"""
        nearby_roads = []
        search_radius = 5
        for x in range(max(0, int(self.position[0] - search_radius)), 
                      min(map_system.width, int(self.position[0] + search_radius))):
            for y in range(max(0, int(self.position[1] - search_radius)), 
                          min(map_system.height, int(self.position[1] + search_radius))):
                if map_system.is_road(x, y):
                    nearby_roads.append((x, y))
        return nearby_roads
    
    def is_accessible_by_road(self, start_pos, goal_pos):
        """检查位置是否可通过道路到达"""
        # 简化实现 - 实际应该进行更复杂的路径可达性分析
        return True


class RobotDogAgent(Agent):
    """机器狗智能体"""
    
    def __init__(self, agent_id, position):
        capabilities = {
            "speed": 7,
            "weight_limit": 20,
            "terrain_adaptability": 5,  # 全地形
            "cost": 1.5,
            "safety": 3,
            "climbing_ability": 1.0,
            "stealth": 4
        }
        super().__init__(agent_id, position, capabilities)
        self.vehicle = RobotDog(position, position)
        self.battery_level = 100
        self.stealth_mode = False
        
    def perceive_environment(self, map_system):
        """感知环境 - 机器狗有强大的地形感知能力"""
        perception = {
            "current_position": self.position,
            "battery_level": self.battery_level,
            "terrain_analysis": self.analyze_terrain(map_system),
            "obstacle_detection": self.detect_obstacles(map_system),
            "stealth_opportunities": self.assess_stealth_routes(map_system),
            "weather_impact": map_system.weather_effect
        }
        return perception
    
    def make_decision(self, available_tasks):
        """决策制定 - 基于地形适应性和隐蔽性"""
        if self.state != "idle" or self.battery_level < 25:
            return None
        
        best_task = None
        best_score = -1
        
        for task in available_tasks:
            # 检查重量限制
            weight = task.get_attribute(1, 0)
            if weight > self.capabilities["weight_limit"]:
                continue
            
            # 计算地形难度
            terrain_difficulty = self.calculate_terrain_difficulty(task.start_pos, task.goal_pos)
            
            # 机器狗适合复杂地形和隐蔽任务
            distance = np.sqrt((task.goal_pos[0] - self.position[0])**2 + 
                             (task.goal_pos[1] - self.position[1])**2)
            
            terrain_advantage = self.capabilities["terrain_adaptability"] / (terrain_difficulty + 1)
            stealth_bonus = 2 if task.get_attribute(8, "") == "stealth" else 1
            
            score = terrain_advantage * 0.4 + (1 / (distance + 1)) * 0.3 + stealth_bonus * 0.3
            
            if score > best_score:
                best_score = score
                best_task = task
        
        return best_task
    
    def execute_action(self, action, map_system):
        """执行动作"""
        if action["type"] == "deliver":
            task = action["task"]
            self.current_task = task
            self.state = "moving"
            
            # 激活隐蔽模式如果需要
            if task.get_attribute(8, "") == "stealth":
                self.stealth_mode = True
            
            # 规划路径
            path = a_star_planning(self.vehicle, map_system, self.position, task.goal_pos)
            if path:
                self.vehicle.path = path
                self.vehicle.current_waypoint_index = 0
                return True
            else:
                self.state = "idle"
                return False
        
        elif action["type"] == "recharge":
            self.state = "charging"
            self.battery_level = min(100, self.battery_level + 15)
            if self.battery_level >= 100:
                self.state = "idle"
            return True
        
        return False
    
    def communicate(self, message, target_agent=None):
        """与其他智能体通信"""
        communication_msg = {
            "sender": self.agent_id,
            "target": target_agent,
            "message": message,
            "timestamp": time.time(),
            "position": self.position,
            "stealth_mode": self.stealth_mode
        }
        return communication_msg
    
    def handle_message(self, message):
        """处理消息"""
        msg_type = message.get("type", "")
        
        if msg_type == "terrain_survey":
            # 地形勘察请求
            survey_area = message.get("area")
            terrain_data = self.survey_terrain(survey_area)
            response = self.communicate({
                "type": "terrain_data",
                "data": terrain_data
            }, message["sender"])
            return response
        
        elif msg_type == "stealth_mission":
            # 隐蔽任务请求
            if self.state == "idle":
                response = self.communicate({
                    "type": "stealth_response",
                    "available": True,
                    "stealth_rating": self.capabilities["stealth"]
                }, message["sender"])
                return response
    
    def analyze_terrain(self, map_system):
        """分析地形"""
        terrain_types = {}
        analysis_radius = 8
        
        for x in range(max(0, int(self.position[0] - analysis_radius)), 
                      min(map_system.width, int(self.position[0] + analysis_radius))):
            for y in range(max(0, int(self.position[1] - analysis_radius)), 
                          min(map_system.height, int(self.position[1] + analysis_radius))):
                terrain = map_system.get_terrain(x, y)
                terrain_types[terrain] = terrain_types.get(terrain, 0) + 1
        
        return terrain_types
    
    def detect_obstacles(self, map_system):
        """检测障碍物"""
        obstacles = []
        detection_radius = 10
        
        for obstacle in map_system.obstacles:
            x, y, radius = obstacle
            distance = np.sqrt((x - self.position[0])**2 + (y - self.position[1])**2)
            if distance <= detection_radius:
                obstacles.append({"position": (x, y), "size": radius, "distance": distance})
        
        return obstacles
    
    def assess_stealth_routes(self, map_system):
        """评估隐蔽路线"""
        stealth_routes = []
        # 寻找树林、山丘等可以提供掩护的地形
        for x in range(max(0, int(self.position[0] - 15)), 
                      min(map_system.width, int(self.position[0] + 15))):
            for y in range(max(0, int(self.position[1] - 15)), 
                          min(map_system.height, int(self.position[1] + 15))):
                terrain = map_system.get_terrain(x, y)
                if terrain in ['hilly', 'steep']:
                    stealth_routes.append((x, y))
        
        return stealth_routes
    
    def calculate_terrain_difficulty(self, start_pos, goal_pos):
        """计算地形难度"""
        # 简化实现
        return random.uniform(0.5, 2.0)
    
    def survey_terrain(self, area):
        """勘察地形"""
        # 简化实现
        return {"terrain_type": "mixed", "difficulty": 1.5, "obstacles": 3}