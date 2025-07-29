"""
API依赖注入
"""
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, Request
from datetime import datetime

from app.core.logger import get_logger, log_access
from app.dao import time_record_dao, system_event_dao

logger = get_logger("APIDeps")


async def get_current_user(request: Request) -> Dict[str, Any]:
    """获取当前用户（占位符，后续可扩展认证）"""
    # TODO: 实现真实的用户认证
    user_info = {
        "user_id": "system",
        "username": "system",
        "ip_address": request.client.host if request.client else "unknown"
    }
    
    # 记录访问日志
    log_access(
        user=user_info["username"],
        resource=str(request.url.path),
        action=request.method,
        ip=user_info["ip_address"]
    )
    
    return user_info


def get_time_record_dao():
    """获取工时记录DAO"""
    return time_record_dao


def get_system_event_dao():
    """获取系统事件DAO"""
    return system_event_dao


class PaginationParams:
    """分页参数"""
    
    def __init__(self, page: int = 1, size: int = 20):
        if page < 1:
            raise HTTPException(status_code=400, detail="页码必须大于0")
        if size < 1 or size > 100:
            raise HTTPException(status_code=400, detail="每页大小必须在1-100之间")
        
        self.page = page
        self.size = size
        self.offset = (page - 1) * size


def get_pagination_params(page: int = 1, size: int = 20) -> PaginationParams:
    """获取分页参数"""
    return PaginationParams(page, size)


class DateRangeParams:
    """日期范围参数"""
    
    def __init__(self, start_date: Optional[str] = None, end_date: Optional[str] = None):
        from datetime import date
        
        self.start_date = None
        self.end_date = None
        
        if start_date:
            try:
                self.start_date = date.fromisoformat(start_date)
            except ValueError:
                raise HTTPException(status_code=400, detail="开始日期格式错误，应为YYYY-MM-DD")
        
        if end_date:
            try:
                self.end_date = date.fromisoformat(end_date)
            except ValueError:
                raise HTTPException(status_code=400, detail="结束日期格式错误，应为YYYY-MM-DD")
        
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise HTTPException(status_code=400, detail="开始日期不能晚于结束日期")


def get_date_range_params(start_date: Optional[str] = None, end_date: Optional[str] = None) -> DateRangeParams:
    """获取日期范围参数"""
    return DateRangeParams(start_date, end_date)


def validate_record_id(record_id: int) -> int:
    """验证记录ID"""
    if record_id <= 0:
        raise HTTPException(status_code=400, detail="记录ID必须大于0")
    return record_id


def validate_date_string(date_str: str) -> str:
    """验证日期字符串格式"""
    try:
        from datetime import date
        date.fromisoformat(date_str)
        return date_str
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式错误，应为YYYY-MM-DD")


async def log_operation(
    operation: str,
    user: Dict[str, Any] = Depends(get_current_user),
    target_type: str = "",
    target_id: Optional[int] = None,
    details: str = ""
):
    """记录操作日志"""
    try:
        from app.dao.operation_log import operation_log_dao
        from app.models.operation_log import OperationLogCreate
        
        log_data = OperationLogCreate(
            operation=operation,
            operator=user["username"],
            target_type=target_type,
            target_id=target_id,
            details=details,
            ip_address=user.get("ip_address")
        )
        
        operation_log_dao.create(log_data)
        
    except Exception as e:
        logger.error(f"记录操作日志失败: {e}")
        # 不抛出异常，避免影响主要业务逻辑
