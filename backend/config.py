"""
配置管理模块
"""
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import time


class Settings(BaseModel):
    """应用配置类"""
    
    # 应用基本信息
    app_name: str = Field(default="时迹 (TimeTrace)", description="应用名称")
    app_version: str = Field(default="1.0.0", description="应用版本")
    debug: bool = Field(default=False, description="调试模式")

    # Web服务配置
    host: str = Field(default="127.0.0.1", description="Web服务主机地址")
    port: int = Field(default=5000, ge=1024, le=65535, description="Web服务端口")
    reload: bool = Field(default=False, description="热重载模式")

    # 数据库配置
    database_url: Optional[str] = Field(default=None, description="数据库连接URL")

    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_file: Optional[str] = Field(default=None, description="日志文件路径")

    # 工时配置
    standard_work_hours: int = Field(default=8, ge=1, le=24, description="标准工作时长(小时)")
    lunch_break_start: str = Field(default="12:00", description="午休开始时间")
    lunch_break_end: str = Field(default="13:00", description="午休结束时间")

    # 提醒配置
    enable_work_reminder: bool = Field(default=False, description="启用上下班提醒")
    enable_overtime_reminder: bool = Field(default=False, description="启用加班提醒")
    overtime_threshold: int = Field(default=9, ge=1, le=24, description="加班提醒阈值(小时)")

    # 系统配置
    auto_startup: bool = Field(default=True, description="开机自启动")
    minimize_to_tray: bool = Field(default=True, description="最小化到系统托盘")

    @validator('log_level')
    def validate_log_level(cls, v):
        """验证日志级别"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'日志级别必须是以下之一: {valid_levels}')
        return v.upper()

    @validator('lunch_break_start', 'lunch_break_end')
    def validate_time_format(cls, v):
        """验证时间格式"""
        try:
            time.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError('时间格式必须是 HH:MM')

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        validate_assignment = True


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


def get_config_file_path() -> str:
    """获取配置文件路径"""
    return str(get_app_data_dir() / 'config.json')


class ConfigManager:
    """配置管理器"""

    def __init__(self):
        self._settings = None
        self._config_file = get_config_file_path()

    @property
    def settings(self) -> Settings:
        """获取配置实例"""
        if self._settings is None:
            self._settings = self.load_config()
        return self._settings

    def load_config(self) -> Settings:
        """从文件加载配置"""
        try:
            config_path = Path(self._config_file)
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                settings = Settings(**config_data)
            else:
                # 使用默认配置
                settings = Settings()
                # 首次创建时保存默认配置
                self.save_config(settings)
        except Exception as e:
            print(f"加载配置文件失败，使用默认配置: {e}")
            settings = Settings()

        # 设置默认路径
        if not settings.database_url:
            settings.database_url = f"sqlite:///{get_database_path()}"

        if not settings.log_file:
            settings.log_file = get_log_file_path()

        return settings

    def save_config(self, settings: Settings = None) -> bool:
        """保存配置到文件"""
        try:
            if settings is None:
                settings = self._settings

            if settings is None:
                return False

            config_path = Path(self._config_file)
            config_path.parent.mkdir(parents=True, exist_ok=True)

            # 转换为字典，排除敏感信息
            config_data = settings.dict()

            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False

    def update_config(self, **kwargs) -> bool:
        """更新配置"""
        try:
            current_config = self.settings.dict()
            current_config.update(kwargs)

            # 验证新配置
            new_settings = Settings(**current_config)

            # 保存新配置
            if self.save_config(new_settings):
                self._settings = new_settings
                return True
            return False
        except Exception as e:
            print(f"更新配置失败: {e}")
            return False

    def reset_config(self) -> bool:
        """重置为默认配置"""
        try:
            default_settings = Settings()
            if self.save_config(default_settings):
                self._settings = default_settings
                return True
            return False
        except Exception as e:
            print(f"重置配置失败: {e}")
            return False

    def backup_config(self, backup_path: str = None) -> bool:
        """备份配置文件"""
        try:
            if backup_path is None:
                timestamp = Path(self._config_file).stem
                backup_path = str(get_app_data_dir() / f'config_backup_{timestamp}.json')

            config_path = Path(self._config_file)
            if config_path.exists():
                import shutil
                shutil.copy2(config_path, backup_path)
                return True
            return False
        except Exception as e:
            print(f"备份配置失败: {e}")
            return False

    def restore_config(self, backup_path: str) -> bool:
        """从备份恢复配置"""
        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                return False

            with open(backup_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            # 验证配置
            settings = Settings(**config_data)

            # 保存恢复的配置
            if self.save_config(settings):
                self._settings = settings
                return True
            return False
        except Exception as e:
            print(f"恢复配置失败: {e}")
            return False


# 全局配置管理器实例
config_manager = ConfigManager()

# 全局配置实例（向后兼容）
settings = config_manager.settings
