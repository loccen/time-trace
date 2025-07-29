"""
系统事件模型
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from .base import EventType, EventSource, BaseTimestampModel


class SystemEventBase(BaseModel):
    """系统事件基础模型"""
    event_type: EventType = Field(..., description="事件类型")
    event_time: datetime = Field(..., description="事件时间")
    event_source: EventSource = Field(default=EventSource.SYSTEM, description="事件来源")
    details: Optional[str] = Field(None, description="事件详情")
    processed: bool = Field(default=False, description="是否已处理")


class SystemEventCreate(SystemEventBase):
    """创建系统事件模型"""
    pass


class SystemEvent(SystemEventBase, BaseTimestampModel):
    """系统事件完整模型"""
    id: int = Field(..., description="事件ID")


class SystemEventQuery(BaseModel):
    """系统事件查询参数"""
    event_type: Optional[EventType] = Field(None, description="事件类型")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    processed: Optional[bool] = Field(None, description="是否已处理")
    page: int = Field(default=1, ge=1, description="页码")
    size: int = Field(default=50, ge=1, le=200, description="每页大小")


class EventStatistics(BaseModel):
    """事件统计模型"""
    total_events: int = Field(default=0, description="总事件数")
    event_counts: dict = Field(default={}, description="各类型事件计数")
    uptime_seconds: float = Field(default=0, description="运行时间(秒)")
    events_per_hour: float = Field(default=0, description="每小时事件数")
    recent_events: list = Field(default=[], description="最近事件")
