# agent.py
# -*- coding: utf-8 -*-

import math
from typing import Tuple, Optional
from delivery_task import DeliveryTask
from vehicle import Drone, Car, RobotDog

class Agent:
    def __init__(self, agent_id: str, position: Tuple[int, int], capabilities: dict, coord_system_ref):
        self.agent_id = agent_id
        self.start_position = position
        self.position = position
        self.capabilities = capabilities
        self.state = "idle"
        self.current_task: Optional[DeliveryTask] = None
        self.vehicle = None
        self.exploration_radius = 5
        self.coord_system = coord_system_ref

    # --- 核心修改：移除线程相关方法，添加 update() ---
    def update(self):
        """由协调器调用的主更新方法，取代了 _agent_loop"""
        # 1. 如果在移动，就前进一步
        if self.state in ["delivering", "returning"]:
            self.follow_path()
        
        # 2. 然后，在当前新位置进行探索
        self.explore_surroundings()

    def follow_path(self):
        # ...
        # --- 核心修改：循环移动，直到到达路点 ---
        # 为了在一个 update() 调用中移动完 agent.speed 的距离
        # 我们需要在这里加一个循环
        
        # 计算本次 update 调用中，这个 agent 总共应该移动多远
        # time.sleep(0.1) 对应 100ms, interval=100 也是 100ms
        # 所以每次更新，移动的距离就是 speed * 0.1
        distance_to_move_this_frame = self.capabilities['speed'] * 0.1

        moved_distance = 0
        while moved_distance < distance_to_move_this_frame:
            if self.vehicle.current_waypoint_index >= len(self.vehicle.path):
                # 路径提前走完，退出循环
                # 状态切换的逻辑移到循环外
                break 

            next_waypoint = self.vehicle.path[self.vehicle.current_waypoint_index]
            
            # --- 调用修改后的 move_towards ---
            self.vehicle.move_towards(next_waypoint)
            self.position = self.vehicle.current_pos
            
            # 累加移动距离
            # step_distance 在 vehicle.py 中是 0.5
            moved_distance += 0.5 
            
            dist_to_waypoint = math.hypot(self.position[0] - next_waypoint[0], self.position[1] - next_waypoint[1])
            if dist_to_waypoint < 0.5: # 如果离路点非常近
                self.vehicle.current_waypoint_index += 1

        if self.vehicle.current_waypoint_index >= len(self.vehicle.path):
            if self.state == "delivering":
                print(f"[{self.agent_id}] 送货至 {self.position} 完成。")
                # --- 核心修改：向协调器上报任务完成 ---
                self.coord_system.report_task_completion(self.current_task)
                self.decide_and_start_return_trip()
            elif self.state == "returning":
                print(f"[{self.agent_id}] 已返回待命点 {self.position}。进入空闲状态。")
                if self.current_task: self.current_task.completed = True
                self.state = "idle"; self.current_task = None; self.vehicle = None
            return

        next_waypoint = self.vehicle.path[self.vehicle.current_waypoint_index]
        self.vehicle.move_towards(next_waypoint)
        self.position = self.vehicle.current_pos
        
        dist_to_waypoint = math.hypot(self.position[0] - next_waypoint[0], self.position[1] - next_waypoint[1])
        if dist_to_waypoint < self.vehicle.speed:
            self.vehicle.current_waypoint_index += 1

    def decide_and_start_return_trip(self):
        warehouse_pos = self.coord_system.warehouse_pos
        relay_pos = self.coord_system.relay_station_pos
        
        path_to_warehouse, cost_to_warehouse = self.coord_system.plan_path_for_agent(self, self.position, warehouse_pos, return_cost=True)
        path_to_relay, cost_to_relay = self.coord_system.plan_path_for_agent(self, self.position, relay_pos, return_cost=True)

        go_to_relay = False
        if self.capabilities['type'] == 'car':
            if cost_to_relay < cost_to_warehouse * 0.7: go_to_relay = True
        else:
            if cost_to_relay < cost_to_warehouse: go_to_relay = True
        
        return_target, return_path = (relay_pos, path_to_relay) if go_to_relay else (warehouse_pos, path_to_warehouse)
        
        if return_path:
            self.state = "returning"
            self.vehicle.path = return_path; self.vehicle.current_waypoint_index = 0
            self.vehicle.goal_pos = return_target
        else:
            self.state = "idle"; self.vehicle = None

    def assign_task(self, task: DeliveryTask, path: list) -> bool:
        if self.state == "idle":
            self.current_task = task
            if self.capabilities['type'] == 'drone': self.vehicle = Drone(self.position, task.goal_pos, max_speed=self.capabilities['speed'])
            elif self.capabilities['type'] == 'car': self.vehicle = Car(self.position, task.goal_pos, max_speed=self.capabilities['speed'])
            else: self.vehicle = RobotDog(self.position, task.goal_pos, max_speed=self.capabilities['speed'])
            self.vehicle.path = path; self.vehicle.current_waypoint_index = 0
            self.state = "delivering"
            return True
        return False

    def explore_surroundings(self):
        map_fragment = {}
        real_map = self.coord_system.real_map
        center_x, center_y = int(self.position[0]), int(self.position[1])
        for dx in range(-self.exploration_radius, self.exploration_radius + 1):
            for dy in range(-self.exploration_radius, self.exploration_radius + 1):
                if dx**2 + dy**2 <= self.exploration_radius**2:
                    x, y = center_x + dx, center_y + dy
                    if 0 <= x < real_map.width and 0 <= y < real_map.height:
                        map_fragment[(x, y)] = real_map.terrain[x, y]
        if map_fragment: self.coord_system.report_map_fragment(map_fragment)

# --- Agent 子类定义保持不变，但 __init__ 不再需要启动线程 ---
class DroneAgent(Agent):
    def __init__(self, agent_id: str, position: Tuple[int, int], coord_system_ref):
        capabilities = { "type": "drone", "speed": 15.0, "weight_limit": 10.0, "terrain_rules": { "road_only": False, "can_climb": True, "climb_height": 100, "can_cross_water": True } }
        super().__init__(agent_id, position, capabilities, coord_system_ref)
class CarAgent(Agent):
    def __init__(self, agent_id: str, position: Tuple[int, int], coord_system_ref):
        capabilities = { "type": "car", "speed": 5.0, "weight_limit": 50.0, "terrain_rules": { "road_only": True, "can_climb": False, "climb_height": 0, "can_cross_water": False } }
        super().__init__(agent_id, position, capabilities, coord_system_ref)
class RobotDogAgent(Agent):
    def __init__(self, agent_id: str, position: Tuple[int, int], coord_system_ref):
        capabilities = { "type": "robot_dog", "speed": 1.0, "weight_limit": 30.0, "terrain_rules": { "road_only": False, "can_climb": True, "climb_height": 5, "can_cross_water": False } }
        super().__init__(agent_id, position, capabilities, coord_system_ref)