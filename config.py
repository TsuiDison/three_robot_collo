"""
项目配置文件
包含所有系统级配置参数
"""

# ==================== 应用基础配置 ====================
APP_CONFIG = {
    "name": "旅行规划仿真系统",
    "version": "1.0.0",
    "description": "基于 Agent-Environment 架构的智能旅行规划仿真系统",
    "author": "Travel Simulation Team",
    "license": "MIT"
}

# ==================== 服务器配置 ====================
SERVER_CONFIG = {
    "host": "127.0.0.1",
    "port": 7899,
    "debug": False,
    "share": False,
    "show_error": True,
    "enable_queue": True,
    "max_threads": 10
}

# ==================== 仿真引擎配置 ====================
SIMULATION_CONFIG = {
    "default_max_steps": 50,
    "default_step_interval": 1.0,
    "default_simulation_speed": 1.0,
    "max_agents": 20,
    "auto_save_interval": 10,
    "enable_logging": True,
    "log_level": "INFO"
}

# ==================== 代理配置 ====================
AGENT_CONFIG = {
    "default_budget": 1000.0,
    "default_energy": 100.0,
    "default_satisfaction": 50.0,
    "max_memory_items": 50,
    "max_action_history": 100,
    
    # 决策权重
    "decision_weights": {
        "cost": 0.3,
        "satisfaction_potential": 0.4,
        "energy_required": 0.2,
        "preference_match": 0.1
    },
    
    # 偏好选项
    "available_preferences": [
        "cultural", "nature", "food", "shopping", 
        "nightlife", "history", "art", "outdoor"
    ]
}

# ==================== 环境配置 ====================
ENVIRONMENT_CONFIG = {
    "default_location": "paris",
    "simulation_start_hour": 9,  # 上午9点开始
    "weather_change_probability": 0.1,  # 10%概率天气变化
    "event_occurrence_probability": 0.3,  # 30%概率有特殊事件
    
    # 地点成本倍数
    "location_cost_multipliers": {
        "paris": 1.5,
        "tokyo": 1.3,
        "bali": 0.8,
        "zurich": 2.0
    },
    
    # 活动类型
    "activity_types": [
        "cultural", "scenic", "food", "shopping",
        "outdoor", "entertainment", "wellness", "education"
    ]
}

# ==================== UI配置 ====================
UI_CONFIG = {
    "theme": "Soft",
    "language": "zh-CN",
    "default_chart_height": 400,
    "default_table_height": 300,
    "refresh_interval": 2,  # 秒
    "max_log_lines": 100,
    "enable_auto_refresh": True,
    
    # 颜色主题
    "colors": {
        "primary": "#667eea",
        "secondary": "#764ba2", 
        "success": "#28a745",
        "warning": "#ffc107",
        "danger": "#dc3545",
        "info": "#17a2b8"
    }
}

# ==================== 数据存储配置 ====================
DATA_CONFIG = {
    "save_directory": "./data",
    "backup_directory": "./backups",
    "export_directory": "./exports",
    "log_directory": "./logs",
    
    # 文件格式
    "export_formats": ["json", "csv", "xlsx"],
    "default_export_format": "json",
    
    # 自动保存
    "enable_auto_save": True,
    "auto_save_interval": 60,  # 秒
    "max_backup_files": 10
}

# ==================== 性能配置 ====================
PERFORMANCE_CONFIG = {
    "max_concurrent_agents": 10,
    "max_simulation_steps": 1000,
    "memory_limit_mb": 512,
    "cpu_usage_limit": 80,  # 百分比
    
    # 缓存配置
    "enable_caching": True,
    "cache_size_mb": 64,
    "cache_ttl_seconds": 300
}

# ==================== 日志配置 ====================
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file_handler": {
        "enabled": True,
        "filename": "logs/simulation.log",
        "max_bytes": 10 * 1024 * 1024,  # 10MB
        "backup_count": 5
    },
    "console_handler": {
        "enabled": True
    }
}

# ==================== 安全配置 ====================
SECURITY_CONFIG = {
    "enable_cors": True,
    "allowed_origins": ["http://localhost:*", "http://127.0.0.1:*"],
    "max_request_size_mb": 10,
    "rate_limit_per_minute": 60,
    "enable_csrf_protection": False  # Gradio内部处理
}

# ==================== 开发配置 ====================
DEVELOPMENT_CONFIG = {
    "debug_mode": False,
    "enable_hot_reload": False,
    "show_gradio_api": True,
    "enable_profiling": False,
    "mock_data": False
}

# ==================== 获取配置的辅助函数 ====================
def get_config(config_name: str):
    """获取指定的配置"""
    config_map = {
        "app": APP_CONFIG,
        "server": SERVER_CONFIG,
        "simulation": SIMULATION_CONFIG,
        "agent": AGENT_CONFIG,
        "environment": ENVIRONMENT_CONFIG,
        "ui": UI_CONFIG,
        "data": DATA_CONFIG,
        "performance": PERFORMANCE_CONFIG,
        "logging": LOGGING_CONFIG,
        "security": SECURITY_CONFIG,
        "development": DEVELOPMENT_CONFIG
    }
    return config_map.get(config_name, {})

def get_all_configs():
    """获取所有配置"""
    return {
        "app": APP_CONFIG,
        "server": SERVER_CONFIG,
        "simulation": SIMULATION_CONFIG,
        "agent": AGENT_CONFIG,
        "environment": ENVIRONMENT_CONFIG,
        "ui": UI_CONFIG,
        "data": DATA_CONFIG,
        "performance": PERFORMANCE_CONFIG,
        "logging": LOGGING_CONFIG,
        "security": SECURITY_CONFIG,
        "development": DEVELOPMENT_CONFIG
    }