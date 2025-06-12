# -*- coding: utf-8 -*-
"""
多智能体协调系统模块
负责智能体之间的协调、任务分配和通信管理
"""

import threading
import time
import queue
import numpy as np
from agent_system import DroneAgent, CarAgent, RobotDogAgent
from delivery_task import DeliveryTask


class MultiAgentCoordinationSystem:
    """多智能体协调系统"""
    
    def __init__(self, map_system):
        self.map_system = map_system
        self.agents = {}
        self.tasks = queue.Queue()
        self.completed_tasks = []
        self.active_tasks = {}
        self.communication_hub = queue.Queue()
        self.system_knowledge = {}
        self.coordination_thread = None
        self.is_running = False
        self.feedback = []
        self.performance_metrics = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "success_rate": 0.0,
            "average_completion_time": 0.0,
            "total_distance": 0.0,
            "energy_efficiency": 0.0
        }
        
        # 初始化智能体
        self._initialize_agents()
        
    def _initialize_agents(self):
        """初始化智能体群体"""
        # 创建无人机智能体
        for i in range(3):
            drone_id = f"drone_{i+1}"
            position = (10 + i*5, 10 + i*5)
            drone_agent = DroneAgent(drone_id, position)
            self.agents[drone_id] = drone_agent
            drone_agent.start_agent()
            
        # 创建汽车智能体
        for i in range(2):
            car_id = f"car_{i+1}"
            position = (20 + i*10, 20 + i*10)
            car_agent = CarAgent(car_id, position)
            self.agents[car_id] = car_agent
            car_agent.start_agent()
            
        # 创建机器狗智能体
        for i in range(2):
            dog_id = f"robot_dog_{i+1}"
            position = (30 + i*10, 30 + i*10)
            dog_agent = RobotDogAgent(dog_id, position)
            self.agents[dog_id] = dog_agent
            dog_agent.start_agent()
            
        self.feedback.append(f"已初始化 {len(self.agents)} 个智能体")
    
    def start_coordination(self):
        """启动协调系统"""
        self.is_running = True
        self.coordination_thread = threading.Thread(target=self._coordination_loop, daemon=True)
        self.coordination_thread.start()
        self.feedback.append("多智能体协调系统已启动")
    
    def stop_coordination(self):
        """停止协调系统"""
        self.is_running = False
        for agent in self.agents.values():
            agent.stop_agent()
        self.feedback.append("多智能体协调系统已停止")
    
    def add_task(self, task):
        """添加新任务"""
        self.tasks.put(task)
        self.performance_metrics["total_tasks"] += 1
        self.feedback.append(f"新任务已添加: 从 {task.start_pos} 到 {task.goal_pos}")
    
    def _coordination_loop(self):
        """协调主循环"""
        while self.is_running:
            try:
                # 处理通信消息
                self._process_communication()
                
                # 任务分配
                self._allocate_tasks()
                
                # 监控任务执行
                self._monitor_tasks()
                
                # 更新系统知识
                self._update_system_knowledge()
                
                # 性能评估
                self._evaluate_performance()
                
                time.sleep(0.5)  # 协调周期
                
            except Exception as e:
                self.feedback.append(f"协调系统错误: {str(e)}")
    
    def _process_communication(self):
        """处理智能体间通信"""
        while not self.communication_hub.empty():
            try:
                message = self.communication_hub.get(timeout=0.1)
                self._route_message(message)
            except queue.Empty:
                break
    
    def _route_message(self, message):
        """路由消息到目标智能体"""
        target = message.get("target")
        if target and target in self.agents:
            self.agents[target].receive_message(message)
        elif target is None:
            # 广播消息
            for agent in self.agents.values():
                agent.receive_message(message)
    
    def _allocate_tasks(self):
        """智能任务分配算法"""
        if self.tasks.empty():
            return
            
        available_tasks = []
        while not self.tasks.empty():
            try:
                task = self.tasks.get(timeout=0.1)
                available_tasks.append(task)
            except queue.Empty:
                break
        
        if not available_tasks:
            return
            
        # 多轮竞标机制
        for task in available_tasks:
            best_agent = self._auction_based_allocation(task)
            
            if best_agent:
                # 分配任务
                action = {"type": "deliver", "task": task}
                success = best_agent.execute_action(action, self.map_system)
                
                if success:
                    self.active_tasks[task] = {
                        "agent": best_agent,
                        "start_time": time.time(),
                        "task": task
                    }
                    self.feedback.append(f"任务已分配给 {best_agent.agent_id}: {task.start_pos} -> {task.goal_pos}")
                else:
                    # 重新排队
                    self.tasks.put(task)
                    self.feedback.append(f"任务分配失败，重新排队: {task.start_pos} -> {task.goal_pos}")
            else:
                # 没有可用智能体，重新排队
                self.tasks.put(task)
    
    def _auction_based_allocation(self, task):
        """基于拍卖的任务分配"""
        bids = {}
        
        # 收集智能体竞标
        for agent_id, agent in self.agents.items():
            if agent.state == "idle":
                # 让智能体感知环境并做决策
                perception = agent.perceive_environment(self.map_system)
                decision_task = agent.make_decision([task])
                
                if decision_task:
                    # 计算竞标价值
                    bid_value = self._calculate_bid_value(agent, task)
                    bids[agent_id] = {"agent": agent, "bid": bid_value}
        
        if not bids:
            return None
            
        # 选择最佳竞标者
        best_agent_id = max(bids.keys(), key=lambda x: bids[x]["bid"])
        return bids[best_agent_id]["agent"]
    
    def _calculate_bid_value(self, agent, task):
        """计算智能体对任务的竞标价值"""
        # 距离因子
        distance = np.sqrt((task.goal_pos[0] - agent.position[0])**2 + 
                          (task.goal_pos[1] - agent.position[1])**2)
        distance_score = 1 / (distance + 1)
        
        # 能力匹配度
        task_weight = task.get_attribute(1, 0)
        weight_score = 1.0 if task_weight <= agent.capabilities["weight_limit"] else 0.0
        
        # 地形适应性
        terrain_score = agent.capabilities.get("terrain_adaptability", 1) / 5.0
        
        # 当前负载和状态
        load_score = 1.0
        if hasattr(agent, 'battery_level'):
            load_score = agent.battery_level / 100.0
        elif hasattr(agent, 'fuel_level'):
            load_score = agent.fuel_level / 100.0
        
        # 紧急程度匹配
        urgency = task.get_attribute(5, 1)
        urgency_score = urgency / 5.0
        
        # 综合评分
        total_score = (distance_score * 0.3 + 
                      weight_score * 0.25 + 
                      terrain_score * 0.2 + 
                      load_score * 0.15 + 
                      urgency_score * 0.1)
        
        return total_score
    
    def _monitor_tasks(self):
        """监控任务执行状态"""
        completed_tasks = []
        
        for task, task_info in self.active_tasks.items():
            agent = task_info["agent"]
            
            # 检查任务是否完成
            if self._is_task_completed(agent, task):
                completion_time = time.time() - task_info["start_time"]
                self.completed_tasks.append({
                    "task": task,
                    "agent": agent.agent_id,
                    "completion_time": completion_time
                })
                
                completed_tasks.append(task)
                agent.state = "idle"
                agent.current_task = None
                agent.update_performance("tasks_completed", 
                                       agent.performance_metrics["tasks_completed"] + 1)
                
                self.feedback.append(f"任务完成: {agent.agent_id} 完成了从 {task.start_pos} 到 {task.goal_pos} 的配送")
            
            # 检查超时任务
            elif time.time() - task_info["start_time"] > 300:  # 5分钟超时
                completed_tasks.append(task)
                agent.state = "idle"
                agent.current_task = None
                self.feedback.append(f"任务超时: {agent.agent_id} 任务超时")
        
        # 移除已完成的任务
        for task in completed_tasks:
            if task in self.active_tasks:
                del self.active_tasks[task]
    
    def _is_task_completed(self, agent, task):
        """检查任务是否完成"""
        # 检查智能体是否到达目标位置
        distance_to_goal = np.sqrt((agent.position[0] - task.goal_pos[0])**2 + 
                                  (agent.position[1] - task.goal_pos[1])**2)
        return distance_to_goal < 2.0
    
    def _update_system_knowledge(self):
        """更新系统级知识库"""
        # 聚合智能体的环境感知信息
        system_perception = {
            "weather": self.map_system.weather,
            "active_agents": len([a for a in self.agents.values() if a.state != "idle"]),
            "total_agents": len(self.agents),
            "pending_tasks": self.tasks.qsize(),
            "active_tasks": len(self.active_tasks)
        }
        
        self.system_knowledge.update(system_perception)
        
        # 共享关键信息给所有智能体
        if self.map_system.weather != self.system_knowledge.get("last_weather"):
            weather_msg = {
                "type": "weather_update",
                "weather_info": {
                    "weather": self.map_system.weather,
                    "effect": self.map_system.weather_effect
                },
                "sender": "coordination_system",
                "target": None  # 广播
            }
            self.communication_hub.put(weather_msg)
            self.system_knowledge["last_weather"] = self.map_system.weather
    
    def _evaluate_performance(self):
        """评估系统性能"""
        if self.completed_tasks:
            total_completed = len(self.completed_tasks)
            total_tasks = self.performance_metrics["total_tasks"]
            
            self.performance_metrics["completed_tasks"] = total_completed
            self.performance_metrics["success_rate"] = total_completed / total_tasks if total_tasks > 0 else 0.0
            
            # 计算平均完成时间
            completion_times = [task["completion_time"] for task in self.completed_tasks]
            self.performance_metrics["average_completion_time"] = np.mean(completion_times)
            
            # 计算总距离和能效
            total_distance = sum(agent.performance_metrics.get("total_distance", 0) 
                               for agent in self.agents.values())
            self.performance_metrics["total_distance"] = total_distance
    
    def get_system_status(self):
        """获取系统状态"""
        agent_status = {}
        for agent_id, agent in self.agents.items():
            agent_status[agent_id] = {
                "state": agent.state,
                "position": agent.position,
                "current_task": agent.current_task.goal_pos if agent.current_task else None,
                "performance": agent.performance_metrics
            }
        
        return {
            "agents": agent_status,
            "pending_tasks": self.tasks.qsize(),
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "performance": self.performance_metrics,
            "system_knowledge": self.system_knowledge
        }
    
    def send_broadcast_message(self, message):
        """发送广播消息"""
        broadcast_msg = {
            "sender": "coordination_system",
            "target": None,
            "message": message,
            "timestamp": time.time()
        }
        self.communication_hub.put(broadcast_msg)
    
    def request_agent_collaboration(self, task, primary_agent_id):
        """请求智能体协作"""
        collaboration_msg = {
            "type": "collaboration_request",
            "task": task,
            "primary_agent": primary_agent_id,
            "sender": "coordination_system"
        }
        
        for agent_id, agent in self.agents.items():
            if agent_id != primary_agent_id and agent.state == "idle":
                collaboration_msg["target"] = agent_id
                self.communication_hub.put(collaboration_msg)
    
    def get_agent_recommendations(self, task):
        """获取智能体推荐"""
        recommendations = []
        
        for agent_id, agent in self.agents.items():
            if agent.state == "idle":
                bid_value = self._calculate_bid_value(agent, task)
                recommendations.append({
                    "agent_id": agent_id,
                    "agent_type": type(agent).__name__,
                    "suitability_score": bid_value,
                    "capabilities": agent.capabilities,
                    "current_state": agent.state
                })
        
        # 按适合度排序
        recommendations.sort(key=lambda x: x["suitability_score"], reverse=True)
        return recommendations