"""
API v1版本路由
"""
from fastapi import APIRouter

from .time_records import router as time_records_router
from .system_events import router as system_events_router
from .statistics import router as statistics_router
from .config import router as config_router

# 创建v1版本的主路由
api_v1_router = APIRouter(prefix="/api/v1")

# 注册子路由
api_v1_router.include_router(
    time_records_router,
    prefix="/time-records",
    tags=["工时记录"]
)

api_v1_router.include_router(
    system_events_router,
    prefix="/system-events",
    tags=["系统事件"]
)

api_v1_router.include_router(
    statistics_router,
    prefix="/statistics",
    tags=["统计分析"]
)

api_v1_router.include_router(
    config_router,
    prefix="/config",
    tags=["系统配置"]
)