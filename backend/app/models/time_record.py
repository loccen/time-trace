"""
工时记录模型
"""
from datetime import datetime, date
from datetime import time as time_type
from typing import Optional, List
from pydantic import BaseModel, Field

from .base import RecordStatus, BaseTimestampModel


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
    
    def calculate_duration(self):
        """计算工作时长"""
        if self.clock_in and self.clock_out:
            # 计算总时长（分钟）
            total_minutes = int((self.clock_out - self.clock_in).total_seconds() / 60)
            
            # 实际工作时长 = 总时长 - 休息时长
            work_duration = max(0, total_minutes - self.break_duration)
            self.duration = work_duration
            
            # 计算加班时长（超过8小时的部分）
            standard_minutes = 8 * 60  # 8小时
            if work_duration > standard_minutes:
                self.overtime_duration = work_duration - standard_minutes
            else:
                self.overtime_duration = 0


class TimeRecordCreate(TimeRecordBase):
    """创建工时记录模型"""
    pass


class TimeRecordUpdate(BaseModel):
    """更新工时记录模型"""
    clock_in: Optional[datetime] = None
    clock_out: Optional[datetime] = None
    break_duration: Optional[int] = Field(None, ge=0)
    status: Optional[RecordStatus] = None
    notes: Optional[str] = None


class TimeRecord(TimeRecordBase, BaseTimestampModel):
    """工时记录完整模型"""
    id: int


class TimeRecordQuery(BaseModel):
    """工时记录查询参数"""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[RecordStatus] = None
    page: int = 1
    size: int = 20
    order_by: str = "date"
    order_desc: bool = True


class DailyStats(BaseModel):
    """日统计模型"""
    date: date
    work_hours: float = 0
    overtime_hours: float = 0
    break_hours: float = 0
    clock_in_time: Optional[time_type] = None
    clock_out_time: Optional[time_type] = None
    status: Optional[RecordStatus] = None


class WeeklyStats(BaseModel):
    """周统计模型"""
    week_start: date
    week_end: date
    total_work_hours: float = 0
    total_overtime_hours: float = 0
    work_days: int = 0
    avg_daily_hours: float = 0
    daily_records: List[DailyStats] = []


class MonthlyStats(BaseModel):
    """月统计模型"""
    year: int
    month: int
    work_days_in_month: int
    actual_work_days: int
    attendance_rate: float
    total_work_hours: float
    total_overtime_hours: float
    avg_daily_hours: float
    expected_hours: float
    hours_variance: float


class WorkSessionInfo(BaseModel):
    """工作会话信息"""
    active: bool
    session_start: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    current_time: Optional[datetime] = None
    session_duration_minutes: int = 0
    work_duration_minutes: int = 0
    break_duration_minutes: int = 0
    work_hours: float = 0
    is_on_break: bool = False
    current_break: Optional[dict] = None
    work_mode: str = "standard"
    break_count: int = 0
