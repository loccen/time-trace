"""
系统事件API路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime

from app.models import SystemEvent, SystemEventCreate, SystemEventQuery, EventType
from app.schemas.response import ApiResponse, PaginatedResponse
from app.dao import SystemEventDAO
from app.api.deps import (
    get_current_user, get_system_event_dao, get_pagination_params,
    validate_record_id, PaginationParams
)
from app.core.logger import get_logger

logger = get_logger("SystemEventsAPI")
router = APIRouter()


@router.post("/", response_model=ApiResponse[SystemEvent], summary="创建系统事件")
async def create_system_event(
    event_data: SystemEventCreate,
    dao: SystemEventDAO = Depends(get_system_event_dao),
    user: dict = Depends(get_current_user)
):
    """手动创建系统事件"""
    try:
        # 创建事件
        event_id = dao.create(event_data)
        
        # 获取创建的事件
        created_event = dao.get_by_id(event_id)
        
        return {
            "success": True,
            "message": "系统事件创建成功",
            "data": created_event
        }
        
    except Exception as e:
        logger.error(f"创建系统事件失败: {e}")
        raise HTTPException(status_code=500, detail="创建系统事件失败")


@router.get("/{event_id}", response_model=ApiResponse[SystemEvent], summary="获取系统事件")
async def get_system_event(
    event_id: int = Depends(validate_record_id),
    dao: SystemEventDAO = Depends(get_system_event_dao),
    user: dict = Depends(get_current_user)
):
    """根据ID获取系统事件"""
    try:
        event = dao.get_by_id(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="系统事件不存在")
        
        return {
            "success": True,
            "message": "获取系统事件成功",
            "data": event
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取系统事件失败: {e}")
        raise HTTPException(status_code=500, detail="获取系统事件失败")


@router.get("/", response_model=ApiResponse[PaginatedResponse[SystemEvent]], summary="查询系统事件列表")
async def list_system_events(
    event_type: Optional[str] = Query(None, description="事件类型"),
    start_time: Optional[str] = Query(None, description="开始时间 (ISO格式)"),
    end_time: Optional[str] = Query(None, description="结束时间 (ISO格式)"),
    processed: Optional[bool] = Query(None, description="是否已处理"),
    pagination: PaginationParams = Depends(get_pagination_params),
    dao: SystemEventDAO = Depends(get_system_event_dao),
    user: dict = Depends(get_current_user)
):
    """查询系统事件列表"""
    try:
        # 解析时间参数
        start_datetime = None
        end_datetime = None
        
        if start_time:
            try:
                start_datetime = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="开始时间格式错误")
        
        if end_time:
            try:
                end_datetime = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="结束时间格式错误")
        
        # 验证事件类型
        event_type_enum = None
        if event_type:
            try:
                event_type_enum = EventType(event_type.lower())
            except ValueError:
                raise HTTPException(status_code=400, detail="无效的事件类型")
        
        # 构建查询参数
        query_params = SystemEventQuery(
            event_type=event_type_enum,
            start_time=start_datetime,
            end_time=end_datetime,
            processed=processed,
            page=pagination.page,
            size=pagination.size
        )
        
        # 查询事件
        events = dao.list_events(query_params)
        total_count = dao.count_events(query_params)
        
        # 计算分页信息
        total_pages = (total_count + pagination.size - 1) // pagination.size
        
        paginated_data = PaginatedResponse(
            items=events,
            total=total_count,
            page=pagination.page,
            size=pagination.size,
            pages=total_pages,
            has_next=pagination.page < total_pages,
            has_prev=pagination.page > 1
        )
        
        return {
            "success": True,
            "message": f"查询到 {len(events)} 条系统事件",
            "data": paginated_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询系统事件列表失败: {e}")
        raise HTTPException(status_code=500, detail="查询系统事件列表失败")


@router.put("/{event_id}/process", response_model=ApiResponse[SystemEvent], summary="标记事件为已处理")
async def mark_event_processed(
    event_id: int = Depends(validate_record_id),
    dao: SystemEventDAO = Depends(get_system_event_dao),
    user: dict = Depends(get_current_user)
):
    """标记系统事件为已处理"""
    try:
        # 检查事件是否存在
        existing = dao.get_by_id(event_id)
        if not existing:
            raise HTTPException(status_code=404, detail="系统事件不存在")
        
        # 标记为已处理
        success = dao.mark_processed(event_id)
        if not success:
            raise HTTPException(status_code=500, detail="标记事件处理状态失败")
        
        # 获取更新后的事件
        updated_event = dao.get_by_id(event_id)
        
        return {
            "success": True,
            "message": "事件已标记为已处理",
            "data": updated_event
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"标记事件处理状态失败: {e}")
        raise HTTPException(status_code=500, detail="标记事件处理状态失败")


@router.put("/batch/process", response_model=ApiResponse[dict], summary="批量标记事件为已处理")
async def mark_events_processed_batch(
    event_ids: List[int],
    dao: SystemEventDAO = Depends(get_system_event_dao),
    user: dict = Depends(get_current_user)
):
    """批量标记系统事件为已处理"""
    try:
        if not event_ids:
            raise HTTPException(status_code=400, detail="事件ID列表不能为空")
        
        if len(event_ids) > 100:
            raise HTTPException(status_code=400, detail="批量处理的事件数量不能超过100个")
        
        # 批量标记为已处理
        affected_count = dao.mark_batch_processed(event_ids)
        
        return {
            "success": True,
            "message": f"成功标记 {affected_count} 个事件为已处理",
            "data": {
                "requested_count": len(event_ids),
                "affected_count": affected_count
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量标记事件处理状态失败: {e}")
        raise HTTPException(status_code=500, detail="批量标记事件处理状态失败")


@router.get("/unprocessed/list", response_model=ApiResponse[List[SystemEvent]], summary="获取未处理事件")
async def get_unprocessed_events(
    limit: int = Query(50, ge=1, le=200, description="返回数量限制"),
    dao: SystemEventDAO = Depends(get_system_event_dao),
    user: dict = Depends(get_current_user)
):
    """获取未处理的系统事件"""
    try:
        events = dao.get_unprocessed_events(limit)
        
        return {
            "success": True,
            "message": f"获取到 {len(events)} 条未处理事件",
            "data": events
        }
        
    except Exception as e:
        logger.error(f"获取未处理事件失败: {e}")
        raise HTTPException(status_code=500, detail="获取未处理事件失败")


@router.get("/recent/list", response_model=ApiResponse[List[SystemEvent]], summary="获取最近事件")
async def get_recent_events(
    limit: int = Query(20, ge=1, le=100, description="返回数量限制"),
    dao: SystemEventDAO = Depends(get_system_event_dao),
    user: dict = Depends(get_current_user)
):
    """获取最近的系统事件"""
    try:
        events = dao.get_recent_events(limit)
        
        return {
            "success": True,
            "message": f"获取到 {len(events)} 条最近事件",
            "data": events
        }
        
    except Exception as e:
        logger.error(f"获取最近事件失败: {e}")
        raise HTTPException(status_code=500, detail="获取最近事件失败")


@router.get("/statistics/summary", response_model=ApiResponse[dict], summary="获取事件统计")
async def get_event_statistics(
    start_time: Optional[str] = Query(None, description="开始时间 (ISO格式)"),
    end_time: Optional[str] = Query(None, description="结束时间 (ISO格式)"),
    dao: SystemEventDAO = Depends(get_system_event_dao),
    user: dict = Depends(get_current_user)
):
    """获取系统事件统计信息"""
    try:
        # 解析时间参数
        start_datetime = None
        end_datetime = None
        
        if start_time:
            try:
                start_datetime = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="开始时间格式错误")
        
        if end_time:
            try:
                end_datetime = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="结束时间格式错误")
        
        # 获取统计信息
        statistics = dao.get_event_statistics(start_datetime, end_datetime)
        
        return {
            "success": True,
            "message": "事件统计获取成功",
            "data": statistics
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取事件统计失败: {e}")
        raise HTTPException(status_code=500, detail="获取事件统计失败")
