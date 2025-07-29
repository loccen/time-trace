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
    date: date = Field(..., description="日期")
    clock_in: Optional[datetime] = Field(None, description="上班时间")
    clock_out: Optional[datetime] = Field(None, description="下班时间")
    duration: int = Field(default=0, ge=0, description="工作时长(分钟)")
    break_duration: int = Field(default=0, ge=0, description="休息时长(分钟)")
    overtime_duration: int = Field(default=0, ge=0, description="加班时长(分钟)")
    status: RecordStatus = Field(default=RecordStatus.NORMAL, description="状态")
    notes: Optional[str] = Field(None, description="备注")
    
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
    id: int = Field(..., description="记录ID")


class TimeRecordQuery(BaseModel):
    """工时记录查询参数"""
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")
    status: Optional[RecordStatus] = Field(None, description="状态筛选")
    page: int = Field(default=1, ge=1, description="页码")
    size: int = Field(default=20, ge=1, le=100, description="每页大小")
    order_by: str = Field(default="date", description="排序字段")
    order_desc: bool = Field(default=True, description="是否降序")


class DailyStats(BaseModel):
    """日统计模型"""
    date: date = Field(..., description="日期")
    work_hours: float = Field(default=0, ge=0, description="工作小时数")
    overtime_hours: float = Field(default=0, ge=0, description="加班小时数")
    break_hours: float = Field(default=0, ge=0, description="休息小时数")
    clock_in_time: Optional[time_type] = Field(None, description="上班时间")
    clock_out_time: Optional[time_type] = Field(None, description="下班时间")
    status: Optional[RecordStatus] = Field(None, description="状态")


class WeeklyStats(BaseModel):
    """周统计模型"""
    week_start: date = Field(..., description="周开始日期")
    week_end: date = Field(..., description="周结束日期")
    total_work_hours: float = Field(default=0, ge=0, description="总工作小时数")
    total_overtime_hours: float = Field(default=0, ge=0, description="总加班小时数")
    work_days: int = Field(default=0, ge=0, description="工作天数")
    avg_daily_hours: float = Field(default=0, ge=0, description="平均每日工作小时数")
    daily_records: List[DailyStats] = Field(default=[], description="每日记录")


class MonthlyStats(BaseModel):
    """月统计模型"""
    year: int = Field(..., description="年份")
    month: int = Field(..., ge=1, le=12, description="月份")
    work_days_in_month: int = Field(..., description="月工作日数")
    actual_work_days: int = Field(..., description="实际工作天数")
    attendance_rate: float = Field(..., ge=0, le=1, description="出勤率")
    total_work_hours: float = Field(..., description="总工作小时数")
    total_overtime_hours: float = Field(..., description="总加班小时数")
    avg_daily_hours: float = Field(..., description="平均每日工作小时数")
    expected_hours: float = Field(..., description="预期工作小时数")
    hours_variance: float = Field(..., description="工时差异")


class WorkSessionInfo(BaseModel):
    """工作会话信息"""
    active: bool = Field(..., description="是否活跃")
    session_start: Optional[datetime] = Field(None, description="会话开始时间")
    last_activity: Optional[datetime] = Field(None, description="最后活动时间")
    current_time: Optional[datetime] = Field(None, description="当前时间")
    session_duration_minutes: int = Field(default=0, description="会话时长(分钟)")
    work_duration_minutes: int = Field(default=0, description="工作时长(分钟)")
    break_duration_minutes: int = Field(default=0, description="休息时长(分钟)")
    work_hours: float = Field(default=0, description="工作小时数")
    is_on_break: bool = Field(default=False, description="是否正在休息")
    current_break: Optional[dict] = Field(None, description="当前休息信息")
    work_mode: str = Field(default="standard", description="工作模式")
    break_count: int = Field(default=0, description="休息次数")
