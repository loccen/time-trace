"""
API路由模块
定义所有API路由和路由组织结构
"""
from fastapi import APIRouter
from api_main import app

# 创建路由器
api_router = APIRouter(prefix="/api/v1")

# 导入各个模块的路由（稍后实现）
# from api.time_records import router as time_records_router
# from api.system_events import router as system_events_router
# from api.statistics import router as statistics_router
# from api.config import router as config_router

# 注册路由
# api_router.include_router(time_records_router, prefix="/time-records", tags=["工时记录"])
# api_router.include_router(system_events_router, prefix="/system-events", tags=["系统事件"])
# api_router.include_router(statistics_router, prefix="/statistics", tags=["统计分析"])
# api_router.include_router(config_router, prefix="/config", tags=["系统配置"])

# 将API路由注册到主应用
app.include_router(api_router)


def setup_routes():
    """设置所有路由"""
    # 这个函数将在后续实现具体路由时使用
    pass
