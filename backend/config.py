"""
配置管理模块
"""
import os
from pathlib import Path
from typing import Optional
from pydantic import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基本信息
    app_name: str = "时迹 (TimeTrace)"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Web服务配置
    host: str = "127.0.0.1"
    port: int = 5000
    reload: bool = False
    
    # 数据库配置
    database_url: Optional[str] = None
    
    # 日志配置
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # 工时配置
    standard_work_hours: int = 8  # 标准工作时长(小时)
    lunch_break_start: str = "12:00"  # 午休开始时间
    lunch_break_end: str = "13:00"    # 午休结束时间
    
    # 提醒配置
    enable_work_reminder: bool = False
    enable_overtime_reminder: bool = False
    overtime_threshold: int = 9  # 加班提醒阈值(小时)
    
    # 系统配置
    auto_startup: bool = True
    minimize_to_tray: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_app_data_dir() -> Path:
    """获取应用数据目录"""
    if os.name == 'nt':  # Windows
        data_dir = Path(os.environ.get('APPDATA', '')) / 'TimeTrace'
    elif os.name == 'posix':
        if os.uname().sysname == 'Darwin':  # macOS
            data_dir = Path.home() / 'Library' / 'Application Support' / 'TimeTrace'
        else:  # Linux
            data_dir = Path.home() / '.local' / 'share' / 'TimeTrace'
    else:
        data_dir = Path.home() / '.timetrack'
    
    # 确保目录存在
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_database_path() -> str:
    """获取数据库文件路径"""
    return str(get_app_data_dir() / 'timetrack.db')


def get_log_file_path() -> str:
    """获取日志文件路径"""
    return str(get_app_data_dir() / 'timetrack.log')


# 全局配置实例
settings = Settings()

# 设置默认路径
if not settings.database_url:
    settings.database_url = f"sqlite:///{get_database_path()}"

if not settings.log_file:
    settings.log_file = get_log_file_path()
