"""
应用配置管理
"""
import os
import json
from typing import Dict, Any, Optional, List
from pathlib import Path

from app.core.logger import get_logger

logger = get_logger("Config")


class Settings:
    """应用设置管理器"""
    
    def __init__(self):
        self.config_file = Path("config.json")
        self.config_data: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
                logger.info(f"配置文件加载成功: {self.config_file}")
            else:
                self.config_data = self._get_default_config()
                self.save_config()
                logger.info("使用默认配置并保存到文件")
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            self.config_data = self._get_default_config()
    
    def save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
            logger.info("配置文件保存成功")
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self.config_data
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split('.')
        config = self.config_data
        
        # 创建嵌套字典结构
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "app": {
                "name": "时迹工时追踪系统",
                "version": "1.0.0",
                "debug": False,
                "host": "127.0.0.1",
                "port": 8000
            },
            "database": {
                "url": "sqlite:///time_trace.db",
                "pool_size": 10,
                "max_overflow": 20,
                "pool_timeout": 30
            },
            "work": {
                "standard_hours": 8.0,
                "max_daily_hours": 12.0,
                "overtime_threshold": 8.0,
                "min_work_duration": 0.5,
                "max_break_duration": 2.0,
                "auto_break_threshold": 30,
                "start_time": "09:00",
                "end_time": "18:00",
                "lunch_start": "12:00",
                "lunch_end": "13:00"
            },
            "event": {
                "enabled_types": [
                    "LOCK", "UNLOCK", "STARTUP", "SHUTDOWN", "SUSPEND", "RESUME"
                ],
                "min_intervals": {
                    "LOCK": 5.0,
                    "UNLOCK": 5.0,
                    "SUSPEND": 10.0,
                    "RESUME": 10.0
                }
            },
            "api": {
                "cors_origins": [
                    "http://localhost:3000",
                    "http://127.0.0.1:3000",
                    "http://localhost:8080",
                    "http://127.0.0.1:8080"
                ],
                "trusted_hosts": ["localhost", "127.0.0.1"],
                "rate_limit": {
                    "enabled": True,
                    "requests_per_minute": 100
                }
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file_enabled": True,
                "file_path": "logs/app.log",
                "file_max_size": "10MB",
                "file_backup_count": 5,
                "console_enabled": True
            }
        }
    
    def reload(self):
        """重新加载配置"""
        self.load_config()
        logger.info("配置已重新加载")
    
    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self.config_data.copy()
    
    def update(self, config_dict: Dict[str, Any]):
        """批量更新配置"""
        def deep_update(base_dict, update_dict):
            for key, value in update_dict.items():
                if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
                    deep_update(base_dict[key], value)
                else:
                    base_dict[key] = value
        
        deep_update(self.config_data, config_dict)
        self.save_config()
        logger.info("配置批量更新完成")


# 全局配置实例
settings = Settings()


# 便捷函数
def get_config(key: str, default: Any = None) -> Any:
    """获取配置值"""
    return settings.get(key, default)


def set_config(key: str, value: Any):
    """设置配置值"""
    settings.set(key, value)


def reload_config():
    """重新加载配置"""
    settings.reload()


# 环境变量支持
class EnvSettings:
    """环境变量配置"""
    
    @property
    def database_url(self) -> str:
        return os.getenv("DATABASE_URL", get_config("database.url"))
    
    @property
    def debug(self) -> bool:
        return os.getenv("DEBUG", "false").lower() == "true"
    
    @property
    def host(self) -> str:
        return os.getenv("HOST", get_config("app.host"))
    
    @property
    def port(self) -> int:
        return int(os.getenv("PORT", get_config("app.port")))
    
    @property
    def log_level(self) -> str:
        return os.getenv("LOG_LEVEL", get_config("logging.level"))


env_settings = EnvSettings()
