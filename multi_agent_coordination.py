# multi_agent_coordination.py
# -*- coding: utf-8 -*-

import threading
import time
import queue
import math
import numpy as np
from typing import Optional
from delivery_task import DeliveryTask
from config import VEHICLE_CONFIG
from knowledge_base import SharedKnowledgeMap
from path_planning import a_star_planning

class MultiAgentCoordinationSystem:
    def __init__(self, real_map_system):
        self.real_map = real_map_system
        self.knowledge_map = SharedKnowledgeMap(real_map_system.width, real_map_system.height)
        self.agents = {}
        self.main_task_queue = queue.Queue()
        self.relay_task_pool = []
        self.warehouse_pos = tuple(map(int, self.real_map.warehouse["center"]))
        self.relay_station_pos = tuple(map(int, self.real_map.relay_station["center"]))
        self.RELAY_PROCESSING_TIME = 2.0
        self.RELAY_WAIT_PENALTY = 10.0
        self.is_running = False
        self.completed_task_count = 0
        
        print("预加载已知地图信息...")
        self._preload_known_map_info()
        self._initialize_agents()

    def _initialize_agents(self):
        from agent import DroneAgent, CarAgent, RobotDogAgent
        agent_configs = { 'drone': (DroneAgent, VEHICLE_CONFIG['drone']['count']), 'car': (CarAgent, VEHICLE_CONFIG['car']['count']), 'robot_dog': (RobotDogAgent, VEHICLE_CONFIG['robot_dog']['count']) }
        for agent_type, (agent_class, count) in agent_configs.items():
            for i in range(count):
                agent_id = f"{agent_type}_{i+1}"
                agent = agent_class(agent_id, self.warehouse_pos, self)
                self.agents[agent_id] = agent

    def _preload_known_map_info(self):
        map_fragment = {}
        road_id = self.real_map.terrain_types['road']
        road_indices = np.argwhere(self.real_map.terrain == road_id)
        for y, x in road_indices: map_fragment[(x, y)] = road_id
        areas_to_scan = [self.warehouse_pos, self.relay_station_pos]; scan_radius = 15
        for center_x, center_y in areas_to_scan:
            for dx in range(-scan_radius, scan_radius + 1):
                for dy in range(-scan_radius, scan_radius + 1):
                    if dx**2 + dy**2 <= scan_radius**2:
                        x, y = center_x + dx, center_y + dy
                        if 0 <= x < self.real_map.width and 0 <= y < self.real_map.height:
                             map_fragment[(x, y)] = self.real_map.terrain[x, y]
        self.knowledge_map.bulk_update(map_fragment)

    def report_map_fragment(self, map_fragment: dict): self.knowledge_map.bulk_update(map_fragment)
    def start(self):
        """启动协调器的后台世界引擎线程"""
        self.is_running = True
        self.coordination_thread = threading.Thread(target=self._coordination_loop, daemon=True)
        self.coordination_thread.start()
        print("后台世界引擎已启动。")

    def stop(self):
        """停止引擎"""
        self.is_running = False
        if self.coordination_thread and self.coordination_thread.is_alive():
            self.coordination_thread.join()

    def _coordination_loop(self):
        """世界引擎主循环，以固定的高频率更新所有对象状态"""
        LOGIC_UPDATE_INTERVAL = 0.02  # 每 20ms 更新一次逻辑 (50 FPS)
        last_task_dispatch_time = 0
        TASK_DISPATCH_INTERVAL = 1.0

        while self.is_running:
            frame_start_time = time.time()
            # 更新所有智能体
            for agent in self.agents.values():
                agent.update()
            # 分配任务 (低频)
            current_time = time.time()
            if current_time - last_task_dispatch_time > TASK_DISPATCH_INTERVAL:
                self._dispatch_relay_tasks()
                self._process_main_queue()
                last_task_dispatch_time = current_time
            # 稳定帧率
            elapsed_time = time.time() - frame_start_time
            sleep_time = LOGIC_UPDATE_INTERVAL - elapsed_time
            if sleep_time > 0:
                time.sleep(sleep_time)
    
    # def update_world(self):
    #     if not self.is_running: return
    #     for agent in self.agents.values(): agent.update()
    #     self._dispatch_relay_tasks()
    #     self._process_main_queue()

    def add_task(self, task: DeliveryTask): self.main_task_queue.put(task)
    def get_completed_task_count(self): return self.completed_task_count
    
    def report_task_completion(self, task: DeliveryTask):
        print(f"[协调器] 收到 {task.task_id} 的完成报告。")
        self.completed_task_count += 1

    def plan_path_for_agent(self, agent, start, end, return_cost=False):
        path = a_star_planning(agent.capabilities, self.knowledge_map, start, end)
        if not return_cost: return path
        if path: cost = len(path) / agent.capabilities['speed']; return path, cost
        return None, float('inf')

    def _dispatch_relay_tasks(self):
        if not self.relay_task_pool: return
        idle_agents = [agent for agent in self.agents.values() if agent.state == "idle"]
        if not idle_agents: return
        current_time = time.time()
        
        for task in self.relay_task_pool[:]:
            if task.arrival_time is None:
                task.arrival_time = current_time
                continue
            if current_time - task.arrival_time < self.RELAY_PROCESSING_TIME:
                continue

            best_agent, best_full_path, _ = self._find_best_option_for_relay(idle_agents, task)
            
            if best_agent and best_full_path:
                if best_agent.assign_task(task, best_full_path):
                    print(f"[中继分配] {best_agent.agent_id} 从当前位置出发，接取已处理好的任务 {task.task_id}")
                    self.relay_task_pool.remove(task)
                    idle_agents.remove(best_agent)

    def _find_best_option_for_relay(self, idle_agents, task):
        best_agent, best_full_path, min_full_cost = None, None, float('inf')
        for agent in idle_agents:
            if task.weight <= agent.capabilities["weight_limit"]:
                path1, cost1 = self.plan_path_for_agent(agent, agent.position, self.relay_station_pos, return_cost=True)
                if not path1: continue
                path2, cost2 = self.plan_path_for_agent(agent, self.relay_station_pos, task.goal_pos, return_cost=True)
                if not path2: continue
                total_cost = cost1 + cost2
                if total_cost < min_full_cost:
                    min_full_cost, best_agent, best_full_path = total_cost, agent, path1 + path2[1:]
        return best_agent, best_full_path, min_full_cost

    def _process_main_queue(self):
        if self.main_task_queue.empty(): return
        task = self.main_task_queue.queue[0]
        decision = self._decide_delivery_strategy(task)
        if not decision:
            task_to_requeue = self.main_task_queue.get(); self.main_task_queue.put(task_to_requeue)
            return

        task = self.main_task_queue.get()
        strategy, agent, path = decision['strategy'], decision['agent'], decision['path']

        if strategy == "direct":
            task.start_pos = self.warehouse_pos
            agent.assign_task(task, path)
        elif strategy == "relay":
            print(f"[决策] 任务 {task.task_id} 采用中转策略，第一程由 {agent.agent_id} 负责")
            # --- 核心修改：传递颜色 ---
            leg1_task = DeliveryTask(
                goal_pos=self.relay_station_pos, weight=task.weight, 
                task_id=f"{task.task_id}_leg1", start_pos=self.warehouse_pos,
                color=task.color 
            )
            agent.assign_task(leg1_task, path)
            
            leg2_task = DeliveryTask(
                goal_pos=task.original_goal, weight=task.weight, 
                task_id=f"{task.task_id}_leg2", start_pos=self.relay_station_pos, 
                is_relay_leg=True,
                color=task.color
            )
            self.relay_task_pool.append(leg2_task)
            print(f"[中继任务] {leg2_task.task_id} 已在中转站等待接力。")

    def _decide_delivery_strategy(self, task: DeliveryTask) -> Optional[dict]:
        idle_agents = [agent for agent in self.agents.values() if agent.state == "idle"]
        if not idle_agents: return None
        
        best_direct_agent, best_direct_path, min_direct_cost = None, None, float('inf')
        for agent in idle_agents:
            if task.weight <= agent.capabilities["weight_limit"]:
                path_to_warehouse, cost_to_warehouse = self.plan_path_for_agent(agent, agent.position, self.warehouse_pos, return_cost=True)
                if not path_to_warehouse: continue
                path_to_goal, cost_to_goal = self.plan_path_for_agent(agent, self.warehouse_pos, task.original_goal, return_cost=True)
                if not path_to_goal: continue
                total_cost = cost_to_warehouse + cost_to_goal
                if total_cost < min_direct_cost:
                    min_direct_cost, best_direct_agent, best_direct_path = total_cost, agent, path_to_warehouse + path_to_goal[1:]
        
        best_leg1_agent, best_leg1_path, min_leg1_cost = None, None, float('inf')
        for agent in idle_agents:
            if task.weight <= agent.capabilities["weight_limit"]:
                path_to_warehouse, cost_to_warehouse = self.plan_path_for_agent(agent, agent.position, self.warehouse_pos, return_cost=True)
                if not path_to_warehouse: continue
                path_to_relay, cost_to_relay = self.plan_path_for_agent(agent, self.warehouse_pos, self.relay_station_pos, return_cost=True)
                if not path_to_relay: continue
                total_cost = cost_to_warehouse + cost_to_relay
                if total_cost < min_leg1_cost:
                    min_leg1_cost, best_leg1_agent, best_leg1_path = total_cost, agent, path_to_warehouse + path_to_relay[1:]
        
        _, _, min_leg2_cost = self._find_best_option_from_point(self.agents.values(), self.relay_station_pos, task.original_goal, task.weight)
        
        total_relay_cost = float('inf')
        if min_leg1_cost != float('inf') and min_leg2_cost != float('inf'):
            total_relay_cost = min_leg1_cost + min_leg2_cost + self.RELAY_WAIT_PENALTY
            
        can_do_direct = best_direct_agent is not None
        can_do_relay = best_leg1_agent is not None

        if can_do_direct and (not can_do_relay or min_direct_cost <= total_relay_cost):
            return {"strategy": "direct", "agent": best_direct_agent, "path": best_direct_path}
        elif can_do_relay:
            return {"strategy": "relay", "agent": best_leg1_agent, "path": best_leg1_path}
        
        return None

    def _find_best_option_from_point(self, agents_to_consider, start, end, weight):
        best_agent, best_path, min_cost = None, None, float('inf')
        for agent in agents_to_consider:
            if weight <= agent.capabilities["weight_limit"]:
                path, cost = self.plan_path_for_agent(agent, start, end, return_cost=True)
                if path and cost < min_cost:
                    min_cost = cost
        return best_agent, best_path, min_cost