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
from log_entry import LogEntry
import json

class MultiAgentCoordinationSystem:
    def __init__(self, real_map_system):
        self.real_map = real_map_system
        self.knowledge_map = SharedKnowledgeMap(real_map_system.width, real_map_system.height)
        self.agents = {}
        self.main_task_queue = queue.PriorityQueue() # 更换为优先队列
        self.relay_task_pool = []
        self.warehouse_pos = tuple(map(int, self.real_map.warehouse["center"]))
        self.relay_station_pos = tuple(map(int, self.real_map.relay_station["center"]))
        self.RELAY_PROCESSING_TIME = 2.0
        self.RELAY_WAIT_PENALTY = -3.5  # 中转站等待时间惩罚
        self.is_running = False
        self.completed_task_count = 0
        self.task_counter = 0
        # --- 3. 初始化日志系统 ---
        self.delivery_log: List[LogEntry] = []
        self.log_lock = threading.Lock() # 保证日志写入的线程安全
        
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
        
        print("正在保存配送日志...")
        self.save_log_to_json()
        print("日志已保存到 delivery_log.json。")

    def save_log_to_json(self, filename="delivery_log.json"):
        """将所有日志条目写入一个JSON文件。"""
        log_data = [entry.to_dict() for entry in self.delivery_log]
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"保存日志文件时出错: {e}")

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

    def add_task(self, task: DeliveryTask):
    # 优先级数字越小越优先，所以用负的紧急度
    # 我们还加入 time.time() 作为第二排序标准，确保相同紧急度的任务按先来后到排序
        priority = -task.urgency
        self.task_counter += 1
        entry = (priority, self.task_counter, task) 
        self.main_task_queue.put(entry)
    def get_completed_task_count(self): return self.completed_task_count
    
    def report_task_completion(self, task: DeliveryTask):
        with self.log_lock:
            # 从后往前找，因为最近分配的任务最可能先完成
            for entry in reversed(self.delivery_log):
                if entry.task_id == task.task_id and entry.status == "assigned":
                    entry.mark_as_completed()
                    break
        
        if "_leg1" in task.task_id:
            print(f"[协调器] 任务 {task.task_id} 的第一段已抵达中转站，不计入最终完成数。")
            return
    
        print(f"[协调器] 收到 {task.task_id} 的完成报告。")
        self.completed_task_count += 1

    def plan_path_for_agent(self, agent, start, end, return_cost=False):
        """
        规划路径并返回路径、与目标的最终距离和成本。
        """
        # --- 核心修改 3: 处理新的返回值 ---
        path, final_distance = a_star_planning(agent.capabilities, self.knowledge_map, start, end)

        # 增加一个送达距离阈值，超过这个距离认为任务不可达
        DELIVERY_RADIUS_THRESHOLD = 5.0

        if path and final_distance <= DELIVERY_RADIUS_THRESHOLD:
            if not return_cost:
                return path # 只返回路径
            
            # 计算成本时，也可以把final_distance考虑进去
            cost = (len(path) / agent.capabilities['speed']) + (final_distance * 0.1) # 距离惩罚
            return path, cost
        
        # 如果路径不存在或最终距离太远
        if not return_cost:
            return None
        return None, float('inf')
        # --- 修改结束 ---

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
                    log_entry = LogEntry(task, best_agent.agent_id, "relay_leg2")
                    log_entry.set_path(best_full_path)
                    with self.log_lock:
                        self.delivery_log.append(log_entry)
                    # --- 修改结束 ---
                    print(f"[中继分配] {best_agent.agent_id} 从当前位置出发，接取已处理好的任务 {task.task_id}")
                    self.relay_task_pool.remove(task)
                    idle_agents.remove(best_agent)

    def _find_best_option_for_relay(self, idle_agents, task):
        best_agent, best_full_path, min_full_cost = None, None, float('inf')
        for agent in idle_agents:
            if task.weight <= agent.capabilities["weight_limit"]:
                # --- 调用已修改的 plan_path_for_agent ---
                # 它现在内部处理了送达距离检查
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
        
        # 从优先队列中查看最高优先级的任务，但不取出
        _, _, task = self.main_task_queue.queue[0] 

        decision = self._decide_delivery_strategy(task)
        if not decision:
            # 如果暂时无法处理，我们不把它放回队尾了
            # 因为优先队列的机制会让它下次依然被优先考虑
            # 可以在这里加一个日志，表示暂时无法处理最高优先级的任务
            # print(f"[决策] 暂时无法为最高优先级任务 {task.task_id} (Urgency: {task.urgency}) 找到方案。")
            return

        # 决策成功，正式取出任务
        _, _, task = self.main_task_queue.get()
        
        # (后续逻辑保持不变)
        strategy, agent, path = decision['strategy'], decision['agent'], decision['path']

        if strategy == "direct":
            task.start_pos = self.warehouse_pos
            if agent.assign_task(task, path):
                log_entry = LogEntry(task, agent.agent_id, "direct")
                log_entry.set_path(path)
                with self.log_lock:
                    self.delivery_log.append(log_entry)

        elif strategy == "relay":
            print(f"[决策] 任务 {task.task_id} 采用中转策略，第一程由 {agent.agent_id} 负责")
            leg1_task = DeliveryTask(
                goal_pos=self.relay_station_pos, weight=task.weight, 
                task_id=f"{task.task_id}_leg1", start_pos=self.warehouse_pos,
                color=task.color,
                urgency=task.urgency, # 传递紧急度
                original_task_id=task.task_id # 传递原始ID
            )
            if agent.assign_task(leg1_task, path):
                log_entry = LogEntry(leg1_task, agent.agent_id, "relay_leg1")
                log_entry.set_path(path)
                with self.log_lock:
                    self.delivery_log.append(log_entry)
            
            leg2_task = DeliveryTask(
                goal_pos=task.original_goal, weight=task.weight, 
                task_id=f"{task.task_id}_leg2", start_pos=self.relay_station_pos, 
                is_relay_leg=True, color=task.color,
                urgency=task.urgency, # 传递紧急度
                original_task_id=task.task_id # 传递原始ID
            )
            self.relay_task_pool.append(leg2_task)
            print(f"[中继任务] {leg2_task.task_id} 已在中转站等待接力。")

    def _decide_delivery_strategy(self, task: DeliveryTask) -> Optional[dict]:
        idle_agents = [agent for agent in self.agents.values() if agent.state == "idle"]
        if not idle_agents: return None
        
        # --- 核心修改 4: 引入紧急度作为成本调整因子 ---
        # urgency 范围通常是 1-5。我们不希望它直接作为除数，影响太大。
        # 我们可以设计一个平滑的权重函数。例如: urgency_weight = 1 + (urgency / 5)
        # 这样权重范围是 [1.2, 2.0]。紧急度越高，权重越高，计算成本越低。
        # 或者更简单：urgency_weight = task.urgency，如果紧急度范围合适的话。
        # 我们这里用一个简单的线性映射，避免为0
        urgency_weight = 1 + task.urgency 
        # --- 修改结束 ---

        # --- 直接配送策略评估 ---
        best_direct_agent, best_direct_path, min_direct_cost = None, None, float('inf')
        for agent in idle_agents:
            if task.weight <= agent.capabilities["weight_limit"]:
                path_to_warehouse, cost_to_warehouse = self.plan_path_for_agent(agent, agent.position, self.warehouse_pos, return_cost=True)
                if not path_to_warehouse: continue
                path_to_goal, cost_to_goal = self.plan_path_for_agent(agent, self.warehouse_pos, task.original_goal, return_cost=True)
                if not path_to_goal: continue
                
                # --- 核心修改 5: 应用紧急度权重 ---
                total_cost = (cost_to_warehouse + cost_to_goal) / urgency_weight
                # --- 修改结束 ---

                if total_cost < min_direct_cost:
                    min_direct_cost = total_cost
                    best_direct_agent = agent
                    # 注意：返回的路径不应该受权重影响，所以要重新组合
                    best_direct_path = path_to_warehouse + path_to_goal[1:]

        # --- 中转策略评估 ---
        best_leg1_agent, best_leg1_path, min_leg1_cost = None, None, float('inf')
        for agent in idle_agents:
            if task.weight <= agent.capabilities["weight_limit"]:
                path_to_warehouse, cost_to_warehouse = self.plan_path_for_agent(agent, agent.position, self.warehouse_pos, return_cost=True)
                if not path_to_warehouse: continue
                path_to_relay, cost_to_relay = self.plan_path_for_agent(agent, self.warehouse_pos, self.relay_station_pos, return_cost=True)
                if not path_to_relay: continue
                
                # --- 核心修改 6: 应用紧急度权重 ---
                total_cost = (cost_to_warehouse + cost_to_relay) / urgency_weight
                # --- 修改结束 ---

                if total_cost < min_leg1_cost:
                    min_leg1_cost = total_cost
                    best_leg1_agent = agent
                    best_leg1_path = path_to_warehouse + path_to_relay[1:]
        
        _, _, min_leg2_cost_raw = self._find_best_option_from_point(self.agents.values(), self.relay_station_pos, task.original_goal, task.weight)
        
        # --- 核心修改 7: 应用紧急度权重 ---
        min_leg2_cost = min_leg2_cost_raw / urgency_weight if min_leg2_cost_raw != float('inf') else float('inf')
        # --- 修改结束 ---
        
        total_relay_cost = float('inf')
        if min_leg1_cost != float('inf') and min_leg2_cost != float('inf'):
            # --- 核心修改 8: RELAY_WAIT_PENALTY 也应该受紧急度影响 ---
            # 高紧急任务不应受同样多的等待惩罚
            adjusted_penalty = self.RELAY_WAIT_PENALTY / (urgency_weight / 2) # 惩罚被紧急度削弱
            total_relay_cost = min_leg1_cost + min_leg2_cost + adjusted_penalty
            # --- 修改结束 ---
            
        # --- 最终决策 (逻辑不变，但比较的值已经变了) ---
        can_do_direct = best_direct_agent is not None
        can_do_relay = best_leg1_agent is not None

        if can_do_direct and (not can_do_relay or min_direct_cost <= total_relay_cost):
            # 返回原始路径，而不是加权后的成本
            return {"strategy": "direct", "agent": best_direct_agent, "path": best_direct_path}
        elif can_do_relay:
            # 返回原始路径
            return {"strategy": "relay", "agent": best_leg1_agent, "path": best_leg1_path}
        
        return None

    def _find_best_option_from_point(self, agents_to_consider, start, end, weight):
        best_agent, best_path, min_cost = None, None, float('inf')
        for agent in agents_to_consider:
            if weight <= agent.capabilities["weight_limit"]:
                # --- 调用已修改的 plan_path_for_agent ---
                path, cost = self.plan_path_for_agent(agent, start, end, return_cost=True)
                if path and cost < min_cost:
                    # 注意：这里我们不需要路径，只需要成本，所以best_path可以是None
                    min_cost = cost
        # 这个函数主要用于估算成本，所以返回 (None, None, min_cost) 是可以接受的
        return None, None, min_cost