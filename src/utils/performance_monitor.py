"""
性能监控工具
监控系统性能和资源使用情况
"""
import psutil
import time
import threading
from typing import Dict, Any, Callable, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """性能指标数据结构"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_sent_mb: float
    network_recv_mb: float
    active_threads: int
    simulation_fps: float = 0.0

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, monitor_interval: float = 1.0):
        self.monitor_interval = monitor_interval
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        # 性能数据存储
        self.metrics_history: list[PerformanceMetrics] = []
        self.max_history_size = 1000
        
        # 回调函数
        self.callbacks: list[Callable[[PerformanceMetrics], None]] = []
        
        # 基准数据
        self.baseline_metrics: Optional[PerformanceMetrics] = None
        
        # 仿真性能追踪
        self.simulation_start_time = None
        self.simulation_step_count = 0
        
        # 初始化基准值
        self._initialize_baseline()
    
    def _initialize_baseline(self):
        """初始化基准性能数据"""
        try:
            self.baseline_metrics = self._collect_current_metrics()
            logger.info("性能监控基准已建立")
        except Exception as e:
            logger.error(f"建立性能基准失败: {e}")
    
    def add_callback(self, callback: Callable[[PerformanceMetrics], None]):
        """添加性能数据回调函数"""
        self.callbacks.append(callback)
    
    def start_monitoring(self):
        """开始性能监控"""
        if self.is_monitoring:
            logger.warning("性能监控已在运行")
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("性能监控已启动")
    
    def stop_monitoring(self):
        """停止性能监控"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        logger.info("性能监控已停止")
    
    def _monitor_loop(self):
        """监控主循环"""
        while self.is_monitoring:
            try:
                metrics = self._collect_current_metrics()
                
                # 保存到历史记录
                self.metrics_history.append(metrics)
                
                # 限制历史记录大小
                if len(self.metrics_history) > self.max_history_size:
                    self.metrics_history = self.metrics_history[-self.max_history_size:]
                
                # 调用回调函数
                for callback in self.callbacks:
                    try:
                        callback(metrics)
                    except Exception as e:
                        logger.error(f"性能监控回调错误: {e}")
                
                time.sleep(self.monitor_interval)
                
            except Exception as e:
                logger.error(f"性能监控循环错误: {e}")
                time.sleep(self.monitor_interval)
    
    def _collect_current_metrics(self) -> PerformanceMetrics:
        """收集当前性能指标"""
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=None)
        
        # 内存使用情况
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used_mb = memory.used / (1024 * 1024)
        
        # 磁盘IO
        disk_io = psutil.disk_io_counters()
        disk_io_read_mb = disk_io.read_bytes / (1024 * 1024) if disk_io else 0
        disk_io_write_mb = disk_io.write_bytes / (1024 * 1024) if disk_io else 0
        
        # 网络IO
        network_io = psutil.net_io_counters()
        network_sent_mb = network_io.bytes_sent / (1024 * 1024) if network_io else 0
        network_recv_mb = network_io.bytes_recv / (1024 * 1024) if network_io else 0
        
        # 活跃线程数
        active_threads = threading.active_count()
        
        # 计算仿真FPS
        simulation_fps = self._calculate_simulation_fps()
        
        return PerformanceMetrics(
            timestamp=datetime.now().isoformat(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_used_mb=memory_used_mb,
            disk_io_read_mb=disk_io_read_mb,
            disk_io_write_mb=disk_io_write_mb,
            network_sent_mb=network_sent_mb,
            network_recv_mb=network_recv_mb,
            active_threads=active_threads,
            simulation_fps=simulation_fps
        )
    
    def _calculate_simulation_fps(self) -> float:
        """计算仿真FPS（每秒步数）"""
        if not self.simulation_start_time or self.simulation_step_count == 0:
            return 0.0
        
        elapsed_time = time.time() - self.simulation_start_time
        if elapsed_time > 0:
            return self.simulation_step_count / elapsed_time
        return 0.0
    
    def start_simulation_tracking(self):
        """开始仿真性能追踪"""
        self.simulation_start_time = time.time()
        self.simulation_step_count = 0
        logger.debug("仿真性能追踪已开始")
    
    def record_simulation_step(self):
        """记录仿真步骤"""
        self.simulation_step_count += 1
    
    def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """获取当前性能指标"""
        if self.metrics_history:
            return self.metrics_history[-1]
        return None
    
    def get_average_metrics(self, window_size: int = 10) -> Optional[PerformanceMetrics]:
        """获取平均性能指标"""
        if len(self.metrics_history) < window_size:
            window_size = len(self.metrics_history)
        
        if window_size == 0:
            return None
        
        recent_metrics = self.metrics_history[-window_size:]
        
        # 计算平均值
        avg_cpu = sum(m.cpu_percent for m in recent_metrics) / window_size
        avg_memory_percent = sum(m.memory_percent for m in recent_metrics) / window_size
        avg_memory_used = sum(m.memory_used_mb for m in recent_metrics) / window_size
        avg_simulation_fps = sum(m.simulation_fps for m in recent_metrics) / window_size
        
        return PerformanceMetrics(
            timestamp=datetime.now().isoformat(),
            cpu_percent=avg_cpu,
            memory_percent=avg_memory_percent,
            memory_used_mb=avg_memory_used,
            disk_io_read_mb=0,  # 累计值不适合平均
            disk_io_write_mb=0,
            network_sent_mb=0,
            network_recv_mb=0,
            active_threads=recent_metrics[-1].active_threads,
            simulation_fps=avg_simulation_fps
        )
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        if not self.metrics_history:
            return {}
        
        current = self.metrics_history[-1]
        baseline = self.baseline_metrics
        
        summary = {
            "current_metrics": {
                "cpu_percent": current.cpu_percent,
                "memory_percent": current.memory_percent,
                "memory_used_mb": current.memory_used_mb,
                "active_threads": current.active_threads,
                "simulation_fps": current.simulation_fps
            },
            "monitoring_duration_minutes": len(self.metrics_history) * self.monitor_interval / 60,
            "data_points": len(self.metrics_history)
        }
        
        if baseline:
            summary["performance_change"] = {
                "cpu_change": current.cpu_percent - baseline.cpu_percent,
                "memory_change": current.memory_percent - baseline.memory_percent,
                "threads_change": current.active_threads - baseline.active_threads
            }
        
        # 计算峰值
        if len(self.metrics_history) > 1:
            summary["peak_metrics"] = {
                "max_cpu": max(m.cpu_percent for m in self.metrics_history),
                "max_memory": max(m.memory_percent for m in self.metrics_history),
                "max_fps": max(m.simulation_fps for m in self.metrics_history)
            }
        
        return summary
    
    def detect_performance_issues(self) -> list[str]:
        """检测性能问题"""
        issues = []
        
        if not self.metrics_history:
            return issues
        
        current = self.metrics_history[-1]
        
        # CPU使用率过高
        if current.cpu_percent > 90:
            issues.append(f"CPU使用率过高: {current.cpu_percent:.1f}%")
        
        # 内存使用率过高
        if current.memory_percent > 90:
            issues.append(f"内存使用率过高: {current.memory_percent:.1f}%")
        
        # 仿真FPS过低
        if current.simulation_fps > 0 and current.simulation_fps < 0.5:
            issues.append(f"仿真性能低: {current.simulation_fps:.2f} FPS")
        
        # 线程数过多
        if current.active_threads > 50:
            issues.append(f"活跃线程过多: {current.active_threads}")
        
        return issues
    
    def export_metrics_data(self) -> list[Dict[str, Any]]:
        """导出性能数据"""
        return [
            {
                "timestamp": m.timestamp,
                "cpu_percent": m.cpu_percent,
                "memory_percent": m.memory_percent,
                "memory_used_mb": m.memory_used_mb,
                "active_threads": m.active_threads,
                "simulation_fps": m.simulation_fps
            }
            for m in self.metrics_history
        ]

# 全局性能监控实例
performance_monitor = PerformanceMonitor()

def start_performance_monitoring():
    """启动性能监控"""
    performance_monitor.start_monitoring()

def stop_performance_monitoring():
    """停止性能监控"""
    performance_monitor.stop_monitoring()

def get_performance_data() -> Dict[str, Any]:
    """获取性能数据"""
    return performance_monitor.get_performance_summary()