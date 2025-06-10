"""
数据管理工具类
负责数据的加载、保存、导出等操作
"""
import json
import csv
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class DataManager:
    """数据管理器"""
    
    def __init__(self, base_path: str = "./data"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        
        # 创建子目录
        self.simulation_path = self.base_path / "simulations"
        self.exports_path = self.base_path / "exports"
        self.backups_path = self.base_path / "backups"
        
        for path in [self.simulation_path, self.exports_path, self.backups_path]:
            path.mkdir(exist_ok=True)
    
    def save_simulation_data(self, simulation_id: str, data: Dict[str, Any]) -> bool:
        """保存仿真数据"""
        try:
            file_path = self.simulation_path / f"{simulation_id}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"仿真数据已保存: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存仿真数据失败: {e}")
            return False
    
    def load_simulation_data(self, simulation_id: str) -> Optional[Dict[str, Any]]:
        """加载仿真数据"""
        try:
            file_path = self.simulation_path / f"{simulation_id}.json"
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"仿真数据已加载: {file_path}")
            return data
            
        except Exception as e:
            logger.error(f"加载仿真数据失败: {e}")
            return None
    
    def export_to_json(self, data: Dict[str, Any], filename: str) -> str:
        """导出为JSON格式"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = self.exports_path / f"{filename}_{timestamp}.json"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"数据已导出为JSON: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"导出JSON失败: {e}")
            return ""
    
    def export_to_csv(self, data: List[Dict[str, Any]], filename: str) -> str:
        """导出为CSV格式"""
        try:
            if not data:
                return ""
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = self.exports_path / f"{filename}_{timestamp}.csv"
            
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            
            logger.info(f"数据已导出为CSV: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"导出CSV失败: {e}")
            return ""
    
    def create_backup(self, data: Dict[str, Any], backup_name: str) -> bool:
        """创建数据备份"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = self.backups_path / f"{backup_name}_{timestamp}.json"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
            # 清理旧备份（保留最新10个）
            self._cleanup_old_backups(backup_name)
            
            logger.info(f"备份已创建: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"创建备份失败: {e}")
            return False
    
    def _cleanup_old_backups(self, backup_name: str, keep_count: int = 10):
        """清理旧备份文件"""
        try:
            pattern = f"{backup_name}_*.json"
            backup_files = list(self.backups_path.glob(pattern))
            
            if len(backup_files) > keep_count:
                # 按修改时间排序，删除最旧的文件
                backup_files.sort(key=lambda x: x.stat().st_mtime)
                for old_file in backup_files[:-keep_count]:
                    old_file.unlink()
                    logger.debug(f"删除旧备份: {old_file}")
                    
        except Exception as e:
            logger.error(f"清理备份失败: {e}")
    
    def get_simulation_list(self) -> List[str]:
        """获取仿真列表"""
        try:
            json_files = list(self.simulation_path.glob("*.json"))
            return [f.stem for f in json_files]
        except Exception as e:
            logger.error(f"获取仿真列表失败: {e}")
            return []
    
    def delete_simulation(self, simulation_id: str) -> bool:
        """删除仿真数据"""
        try:
            file_path = self.simulation_path / f"{simulation_id}.json"
            if file_path.exists():
                file_path.unlink()
                logger.info(f"仿真数据已删除: {simulation_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"删除仿真数据失败: {e}")
            return False