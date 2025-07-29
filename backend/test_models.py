#!/usr/bin/env python3
"""
测试模型定义
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


class BaseTimestampModel(BaseModel):
    """带时间戳的基础模型"""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class TimeRecordBase(BaseModel):
    """工时记录基础模型"""
    date: date
    clock_in: Optional[datetime] = None
    clock_out: Optional[datetime] = None
    duration: int = 0
    break_duration: int = 0
    overtime_duration: int = 0
    status: RecordStatus = RecordStatus.NORMAL
    notes: Optional[str] = None


class TimeRecordCreate(TimeRecordBase):
    """创建工时记录模型"""
    pass


class TimeRecord(TimeRecordBase, BaseTimestampModel):
    """工时记录完整模型"""
    id: int


if __name__ == "__main__":
    print("测试模型定义...")
    
    # 测试创建记录
    record_data = TimeRecordCreate(
        date=date.today(),
        clock_in=datetime.now(),
        clock_out=datetime.now(),
        duration=480,
        status=RecordStatus.NORMAL
    )
    
    print(f"创建记录成功: {record_data}")
    print("模型定义正常")
