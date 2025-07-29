"""
基础模型和枚举定义
"""
from datetime import datetime, date
from datetime import time as time_type
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field


class RecordStatus(str, Enum):
    """工时记录状态枚举"""
    NORMAL = "normal"
    ABNORMAL = "abnormal"
    MANUAL = "manual"
    INCOMPLETE = "incomplete"


class EventType(str, Enum):
    """系统事件类型枚举"""
    LOCK = "lock"
    UNLOCK = "unlock"
    SHUTDOWN = "shutdown"
    STARTUP = "startup"
    SUSPEND = "suspend"
    RESUME = "resume"


class EventSource(str, Enum):
    """事件来源枚举"""
    SYSTEM = "system"
    MANUAL = "manual"
    AUTO = "auto"


class WorkMode(str, Enum):
    """工作模式枚举"""
    STANDARD = "standard"  # 标准工作模式
    FLEXIBLE = "flexible"  # 弹性工作模式
    SHIFT = "shift"        # 轮班工作模式
    REMOTE = "remote"      # 远程工作模式


class BreakType(str, Enum):
    """休息类型枚举"""
    LUNCH = "lunch"        # 午休
    SHORT = "short"        # 短暂休息
    LONG = "long"          # 长时间休息
    MEETING = "meeting"    # 会议间隙
    SYSTEM = "system"      # 系统锁屏


class BaseTimestampModel(BaseModel):
    """带时间戳的基础模型"""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class BaseResponseModel(BaseModel):
    """基础响应模型"""
    success: bool
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)
