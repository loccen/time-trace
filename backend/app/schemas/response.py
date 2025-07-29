"""
API响应模式
"""
from typing import Any, Optional, Generic, TypeVar, List
from datetime import datetime
from pydantic import BaseModel, Field

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """通用API响应模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应模型"""
    items: List[T] = Field(..., description="数据项列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页大小")
    pages: int = Field(..., description="总页数")
    has_next: bool = Field(..., description="是否有下一页")
    has_prev: bool = Field(..., description="是否有上一页")


class ErrorResponse(BaseModel):
    """错误响应模型"""
    success: bool = Field(default=False, description="是否成功")
    message: str = Field(..., description="错误消息")
    error_code: Optional[str] = Field(None, description="错误代码")
    error_details: Optional[dict] = Field(None, description="错误详情")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")


class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str = Field(..., description="服务状态")
    database: str = Field(..., description="数据库状态")
    event_service: str = Field(..., description="事件服务状态")
    uptime: float = Field(..., description="运行时间(分钟)")
    version: str = Field(..., description="版本号")


class SystemInfoResponse(BaseModel):
    """系统信息响应模型"""
    platform: dict = Field(..., description="平台信息")
    python: dict = Field(..., description="Python信息")
    hardware: dict = Field(..., description="硬件信息")
    application: dict = Field(..., description="应用信息")
