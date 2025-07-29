"""
工时记录API路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import date

from app.models import (
    TimeRecord, TimeRecordCreate, TimeRecordUpdate, TimeRecordQuery,
    DailyStats
)
from app.schemas.response import ApiResponse, PaginatedResponse
from app.dao import TimeRecordDAO
from app.api.deps import (
    get_current_user, get_time_record_dao, get_pagination_params,
    get_date_range_params, validate_record_id, validate_date_string,
    PaginationParams, DateRangeParams
)
from app.core.logger import get_logger

logger = get_logger("TimeRecordsAPI")
router = APIRouter()


@router.post("/", response_model=ApiResponse[TimeRecord], summary="创建工时记录")
async def create_time_record(
    record_data: TimeRecordCreate,
    dao: TimeRecordDAO = Depends(get_time_record_dao),
    user: dict = Depends(get_current_user)
):
    """创建新的工时记录"""
    try:
        # 检查日期是否已存在记录
        existing = dao.get_by_date(record_data.date)
        if existing:
            raise HTTPException(
                status_code=400, 
                detail=f"日期 {record_data.date} 已存在工时记录"
            )
        
        # 创建记录
        record_id = dao.create(record_data)
        
        # 获取创建的记录
        created_record = dao.get_by_id(record_id)
        
        return {
            "success": True,
            "message": "工时记录创建成功",
            "data": created_record
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建工时记录失败: {e}")
        raise HTTPException(status_code=500, detail="创建工时记录失败")


@router.get("/{record_id}", response_model=ApiResponse[TimeRecord], summary="获取工时记录")
async def get_time_record(
    record_id: int = Depends(validate_record_id),
    dao: TimeRecordDAO = Depends(get_time_record_dao),
    user: dict = Depends(get_current_user)
):
    """根据ID获取工时记录"""
    try:
        record = dao.get_by_id(record_id)
        if not record:
            raise HTTPException(status_code=404, detail="工时记录不存在")
        
        return {
            "success": True,
            "message": "获取工时记录成功",
            "data": record
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取工时记录失败: {e}")
        raise HTTPException(status_code=500, detail="获取工时记录失败")


@router.get("/date/{date_str}", response_model=ApiResponse[TimeRecord], summary="按日期获取工时记录")
async def get_time_record_by_date(
    date_str: str = Depends(validate_date_string),
    dao: TimeRecordDAO = Depends(get_time_record_dao),
    user: dict = Depends(get_current_user)
):
    """根据日期获取工时记录"""
    try:
        target_date = date.fromisoformat(date_str)
        record = dao.get_by_date(target_date)
        
        if not record:
            raise HTTPException(status_code=404, detail=f"日期 {date_str} 没有工时记录")
        
        return {
            "success": True,
            "message": "获取工时记录成功",
            "data": record
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"按日期获取工时记录失败: {e}")
        raise HTTPException(status_code=500, detail="获取工时记录失败")


@router.put("/{record_id}", response_model=ApiResponse[TimeRecord], summary="更新工时记录")
async def update_time_record(
    update_data: TimeRecordUpdate,
    record_id: int = Depends(validate_record_id),
    dao: TimeRecordDAO = Depends(get_time_record_dao),
    user: dict = Depends(get_current_user)
):
    """更新工时记录"""
    try:
        # 检查记录是否存在
        existing = dao.get_by_id(record_id)
        if not existing:
            raise HTTPException(status_code=404, detail="工时记录不存在")
        
        # 更新记录
        success = dao.update(record_id, update_data)
        if not success:
            raise HTTPException(status_code=500, detail="更新工时记录失败")
        
        # 获取更新后的记录
        updated_record = dao.get_by_id(record_id)
        
        return {
            "success": True,
            "message": "工时记录更新成功",
            "data": updated_record
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新工时记录失败: {e}")
        raise HTTPException(status_code=500, detail="更新工时记录失败")


@router.delete("/{record_id}", response_model=ApiResponse[None], summary="删除工时记录")
async def delete_time_record(
    record_id: int = Depends(validate_record_id),
    dao: TimeRecordDAO = Depends(get_time_record_dao),
    user: dict = Depends(get_current_user)
):
    """删除工时记录"""
    try:
        # 检查记录是否存在
        existing = dao.get_by_id(record_id)
        if not existing:
            raise HTTPException(status_code=404, detail="工时记录不存在")
        
        # 删除记录
        success = dao.delete(record_id)
        if not success:
            raise HTTPException(status_code=500, detail="删除工时记录失败")
        
        return {
            "success": True,
            "message": "工时记录删除成功",
            "data": None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除工时记录失败: {e}")
        raise HTTPException(status_code=500, detail="删除工时记录失败")


@router.get("/", response_model=ApiResponse[PaginatedResponse[TimeRecord]], summary="查询工时记录列表")
async def list_time_records(
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    status: Optional[str] = Query(None, description="状态筛选"),
    order_by: str = Query("date", description="排序字段"),
    order_desc: bool = Query(True, description="是否降序"),
    pagination: PaginationParams = Depends(get_pagination_params),
    date_range: DateRangeParams = Depends(get_date_range_params),
    dao: TimeRecordDAO = Depends(get_time_record_dao),
    user: dict = Depends(get_current_user)
):
    """查询工时记录列表"""
    try:
        # 构建查询参数
        from app.models import RecordStatus
        
        query_params = TimeRecordQuery(
            start_date=date_range.start_date,
            end_date=date_range.end_date,
            status=RecordStatus(status) if status else None,
            page=pagination.page,
            size=pagination.size,
            order_by=order_by,
            order_desc=order_desc
        )
        
        # 查询记录
        records = dao.list_records(query_params)
        total_count = dao.count_records(query_params)
        
        # 计算分页信息
        total_pages = (total_count + pagination.size - 1) // pagination.size
        
        paginated_data = PaginatedResponse(
            items=records,
            total=total_count,
            page=pagination.page,
            size=pagination.size,
            pages=total_pages,
            has_next=pagination.page < total_pages,
            has_prev=pagination.page > 1
        )
        
        return {
            "success": True,
            "message": f"查询到 {len(records)} 条工时记录",
            "data": paginated_data
        }
        
    except Exception as e:
        logger.error(f"查询工时记录列表失败: {e}")
        raise HTTPException(status_code=500, detail="查询工时记录列表失败")


@router.get("/range/summary", response_model=ApiResponse[dict], summary="获取日期范围统计摘要")
async def get_range_summary(
    date_range: DateRangeParams = Depends(get_date_range_params),
    dao: TimeRecordDAO = Depends(get_time_record_dao),
    user: dict = Depends(get_current_user)
):
    """获取指定日期范围的统计摘要"""
    try:
        if not date_range.start_date or not date_range.end_date:
            raise HTTPException(status_code=400, detail="必须提供开始日期和结束日期")
        
        summary = dao.get_statistics_summary(date_range.start_date, date_range.end_date)
        
        return {
            "success": True,
            "message": "统计摘要获取成功",
            "data": summary
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取统计摘要失败: {e}")
        raise HTTPException(status_code=500, detail="获取统计摘要失败")
