"""
FastAPI主应用程序
时迹工时追踪系统的API入口
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time
import traceback
from typing import Dict, Any
from datetime import datetime

from app.config.settings import get_config
from app.core.logger import get_logger
from app.schemas.response import ApiResponse, HealthResponse, ErrorResponse

logger = get_logger("API")

# 创建FastAPI应用实例
app = FastAPI(
    title="时迹 - 工时追踪系统",
    description="一个智能的工时追踪和管理系统，支持自动时间记录、统计分析和报告生成",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


def setup_middleware():
    """配置中间件"""
    
    # CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_config("api.cors_origins", ["http://localhost:3000", "http://127.0.0.1:3000"]),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 受信任主机中间件
    trusted_hosts = get_config("api.trusted_hosts", ["localhost", "127.0.0.1"])
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=trusted_hosts
    )


# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录请求日志"""
    start_time = time.time()
    
    # 记录请求信息
    logger.info(f"请求开始: {request.method} {request.url}")
    
    try:
        response = await call_next(request)
        
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 记录响应信息
        logger.info(f"请求完成: {request.method} {request.url} - "
                   f"状态码: {response.status_code} - "
                   f"处理时间: {process_time:.3f}s")
        
        # 添加处理时间到响应头
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"请求异常: {request.method} {request.url} - "
                    f"错误: {str(e)} - "
                    f"处理时间: {process_time:.3f}s")
        raise


# 全局异常处理器
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP异常处理器"""
    logger.warning(f"HTTP异常: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            message=exc.detail,
            error_code=f"HTTP_{exc.status_code}",
            error_details={"path": str(request.url)}
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理器"""
    error_id = f"ERR_{int(time.time())}"
    
    logger.error(f"未处理异常 [{error_id}]: {str(exc)}\n{traceback.format_exc()}")
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            message="服务器内部错误",
            error_code="INTERNAL_ERROR",
            error_details={"error_id": error_id, "path": str(request.url)}
        ).model_dump()
    )


def create_api_response(success: bool = True, message: str = "操作成功", 
                       data: Any = None) -> Dict[str, Any]:
    """创建标准API响应"""
    return ApiResponse(
        success=success,
        message=message,
        data=data
    ).model_dump()


# 健康检查端点
@app.get("/health", response_model=ApiResponse[HealthResponse], tags=["系统"])
async def health_check():
    """健康检查"""
    try:
        # 检查数据库连接
        from app.core.database import db_manager
        db_manager.execute_query("SELECT 1")
        
        # 检查事件服务
        from app.listeners import event_manager
        service_status = event_manager.get_status()
        
        health_data = HealthResponse(
            status="healthy",
            database="connected",
            event_service="running" if service_status["is_running"] else "stopped",
            uptime=0.0,  # TODO: 实现运行时间计算
            version="1.0.0"
        )
        
        return create_api_response(
            message="系统运行正常",
            data=health_data.model_dump()
        )
        
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return create_api_response(
            success=False,
            message="系统异常",
            data={"error": str(e)}
        )


@app.get("/", tags=["系统"])
async def root():
    """根路径"""
    return create_api_response(
        message="时迹工时追踪系统API",
        data={
            "version": "1.0.0",
            "docs_url": "/docs",
            "health_url": "/health"
        }
    )


# 系统信息端点
@app.get("/system/info", tags=["系统"])
async def system_info():
    """获取系统信息"""
    try:
        import platform
        import psutil
        
        # 获取系统信息
        system_info = {
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor()
            },
            "python": {
                "version": platform.python_version(),
                "implementation": platform.python_implementation()
            },
            "hardware": {
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available,
                "disk_usage": psutil.disk_usage('/').percent if platform.system() != "Windows" else psutil.disk_usage('C:').percent
            },
            "application": {
                "name": "时迹工时追踪系统",
                "version": "1.0.0",
                "start_time": datetime.now().isoformat()
            }
        }
        
        return create_api_response(
            message="系统信息获取成功",
            data=system_info
        )
        
    except Exception as e:
        logger.error(f"获取系统信息失败: {e}")
        raise HTTPException(status_code=500, detail="获取系统信息失败")


# 配置端点
@app.get("/system/config", tags=["系统"])
async def get_system_config():
    """获取系统配置"""
    try:
        # 只返回安全的配置信息
        safe_config = {
            "work": {
                "standard_hours": get_config("work.standard_hours", 8.0),
                "start_time": get_config("work.start_time", "09:00"),
                "end_time": get_config("work.end_time", "18:00"),
                "lunch_start": get_config("work.lunch_start", "12:00"),
                "lunch_end": get_config("work.lunch_end", "13:00")
            },
            "event": {
                "enabled_types": get_config("event.enabled_types", []),
                "min_intervals": get_config("event.min_intervals", {})
            },
            "api": {
                "cors_origins": get_config("api.cors_origins", []),
                "trusted_hosts": get_config("api.trusted_hosts", [])
            }
        }
        
        return create_api_response(
            message="配置获取成功",
            data=safe_config
        )
        
    except Exception as e:
        logger.error(f"获取系统配置失败: {e}")
        raise HTTPException(status_code=500, detail="获取系统配置失败")


# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("时迹API服务启动")
    
    # 设置中间件
    setup_middleware()
    
    # 初始化数据库
    try:
        from scripts.init_db import init_database
        init_database()
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
    
    # 启动事件服务
    try:
        from app.listeners import event_manager, create_platform_listener
        
        # 创建并注册平台监听器
        platform_listener = create_platform_listener()
        event_manager.register_listener(platform_listener)
        
        # 启动事件管理器
        event_manager.start_all()
        logger.info("事件服务启动完成")
    except Exception as e:
        logger.error(f"事件服务启动失败: {e}")


# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("时迹API服务关闭")
    
    # 停止事件服务
    try:
        from app.listeners import event_manager
        event_manager.stop_all()
        logger.info("事件服务已停止")
    except Exception as e:
        logger.error(f"停止事件服务失败: {e}")


# 自定义OpenAPI文档
def custom_openapi():
    """自定义OpenAPI文档"""
    if app.openapi_schema:
        return app.openapi_schema
    
    from fastapi.openapi.utils import get_openapi
    
    openapi_schema = get_openapi(
        title="时迹工时追踪系统API",
        version="1.0.0",
        description="智能工时追踪和管理系统的RESTful API接口文档",
        routes=app.routes,
    )
    
    # 添加自定义信息
    openapi_schema["info"]["contact"] = {
        "name": "时迹开发团队",
        "email": "support@timetracker.com"
    }
    
    openapi_schema["info"]["license"] = {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
