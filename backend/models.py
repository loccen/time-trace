"""
数据模型定义
"""
from datetime import datetime, date, time
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


# 工时记录模型
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


class TimeRecord(TimeRecordBase):
    """工时记录完整模型"""
    id: int = Field(..., description="记录ID")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# 系统事件模型
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


class SystemEvent(SystemEventBase):
    """系统事件完整模型"""
    id: int = Field(..., description="事件ID")
    created_at: Optional[datetime] = None


# 系统配置模型
class SystemConfigBase(BaseModel):
    """系统配置基础模型"""
    key: str = Field(..., max_length=50, description="配置键")
    value: Optional[str] = Field(None, description="配置值")
    description: Optional[str] = Field(None, description="配置描述")
    data_type: str = Field(default="string", description="数据类型")
    category: str = Field(default="general", description="配置分类")


class SystemConfigCreate(SystemConfigBase):
    """创建系统配置模型"""
    pass


class SystemConfigUpdate(BaseModel):
    """更新系统配置模型"""
    value: Optional[str] = None
    description: Optional[str] = None
    data_type: Optional[str] = None
    category: Optional[str] = None


class SystemConfig(SystemConfigBase):
    """系统配置完整模型"""
    updated_at: Optional[datetime] = None


# 操作日志模型
class OperationLogBase(BaseModel):
    """操作日志基础模型"""
    operation: str = Field(..., max_length=50, description="操作类型")
    operator: str = Field(default="system", max_length=50, description="操作者")
    target_type: Optional[str] = Field(None, description="目标类型")
    target_id: Optional[int] = Field(None, description="目标ID")
    old_value: Optional[str] = Field(None, description="旧值(JSON格式)")
    new_value: Optional[str] = Field(None, description="新值(JSON格式)")
    details: Optional[str] = Field(None, description="操作详情")
    ip_address: Optional[str] = Field(None, max_length=45, description="IP地址")
    user_agent: Optional[str] = Field(None, description="用户代理")


class OperationLogCreate(OperationLogBase):
    """创建操作日志模型"""
    pass


class OperationLog(OperationLogBase):
    """操作日志完整模型"""
    id: int = Field(..., description="日志ID")
    timestamp: datetime = Field(..., description="操作时间")


# 响应模型
class ApiResponse(BaseModel):
    """API响应基础模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[dict] = Field(None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")


# 统计模型
class DailyStats(BaseModel):
    """日统计模型"""
    date: date = Field(..., description="日期")
    work_hours: float = Field(default=0, ge=0, description="工作小时数")
    overtime_hours: float = Field(default=0, ge=0, description="加班小时数")
    break_hours: float = Field(default=0, ge=0, description="休息小时数")
    clock_in_time: Optional[time] = Field(None, description="上班时间")
    clock_out_time: Optional[time] = Field(None, description="下班时间")
    status: Optional[RecordStatus] = Field(None, description="状态")


# 查询参数模型
class TimeRecordQuery(BaseModel):
    """工时记录查询参数"""
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")
    status: Optional[RecordStatus] = Field(None, description="状态筛选")
    page: int = Field(default=1, ge=1, description="页码")
    size: int = Field(default=20, ge=1, le=100, description="每页大小")
    order_by: str = Field(default="date", description="排序字段")
    order_desc: bool = Field(default=True, description="是否降序")


class SystemEventQuery(BaseModel):
    """系统事件查询参数"""
    event_type: Optional[EventType] = Field(None, description="事件类型")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    processed: Optional[bool] = Field(None, description="是否已处理")
    page: int = Field(default=1, ge=1, description="页码")
    size: int = Field(default=50, ge=1, le=200, description="每页大小")


# 导出模型
class ExportRequest(BaseModel):
    """数据导出请求模型"""
    export_type: str = Field(..., description="导出类型: csv/excel/json")
    start_date: date = Field(..., description="开始日期")
    end_date: date = Field(..., description="结束日期")
    include_fields: list = Field(default=[], description="包含字段")
    exclude_fields: list = Field(default=[], description="排除字段")
    filters: dict = Field(default={}, description="筛选条件")


class ExportResult(BaseModel):
    """数据导出结果模型"""
    file_path: str = Field(..., description="导出文件路径")
    file_size: int = Field(..., ge=0, description="文件大小(字节)")
    record_count: int = Field(..., ge=0, description="导出记录数")
    export_time: datetime = Field(..., description="导出时间")
    download_url: Optional[str] = Field(None, description="下载链接")
