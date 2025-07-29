"""
系统配置API路由
"""
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.schemas.response import ApiResponse
from app.api.deps import get_current_user
from app.config.settings import settings, get_config, set_config
from app.core.logger import get_logger

logger = get_logger("ConfigAPI")
router = APIRouter()


class ConfigItem(BaseModel):
    """配置项模型"""
    key: str
    value: Any
    description: str = ""
    data_type: str = "string"
    category: str = "general"


class ConfigUpdate(BaseModel):
    """配置更新模型"""
    value: Any


@router.get("/", response_model=ApiResponse[Dict[str, Any]], summary="获取所有配置")
async def get_all_config(
    user: dict = Depends(get_current_user)
):
    """获取所有系统配置"""
    try:
        all_config = settings.get_all()
        
        return {
            "success": True,
            "message": "配置获取成功",
            "data": all_config
        }
        
    except Exception as e:
        logger.error(f"获取配置失败: {e}")
        raise HTTPException(status_code=500, detail="获取配置失败")


@router.get("/category/{category}", response_model=ApiResponse[Dict[str, Any]], summary="按分类获取配置")
async def get_config_by_category(
    category: str,
    user: dict = Depends(get_current_user)
):
    """按分类获取配置"""
    try:
        all_config = settings.get_all()
        
        # 筛选指定分类的配置
        category_config = {}
        for key, value in all_config.items():
            if key.startswith(f"{category}."):
                category_config[key] = value
        
        return {
            "success": True,
            "message": f"分类 {category} 配置获取成功",
            "data": category_config
        }
        
    except Exception as e:
        logger.error(f"获取分类配置失败: {e}")
        raise HTTPException(status_code=500, detail="获取分类配置失败")


@router.get("/key/{config_key:path}", response_model=ApiResponse[Any], summary="获取单个配置")
async def get_config_item(
    config_key: str,
    user: dict = Depends(get_current_user)
):
    """获取单个配置项"""
    try:
        value = get_config(config_key)
        
        if value is None:
            raise HTTPException(status_code=404, detail="配置项不存在")
        
        return {
            "success": True,
            "message": "配置项获取成功",
            "data": {
                "key": config_key,
                "value": value
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取配置项失败: {e}")
        raise HTTPException(status_code=500, detail="获取配置项失败")


@router.put("/key/{config_key:path}", response_model=ApiResponse[Any], summary="更新单个配置")
async def update_config_item(
    config_key: str,
    update_data: ConfigUpdate,
    user: dict = Depends(get_current_user)
):
    """更新单个配置项"""
    try:
        # 验证配置键是否存在
        current_value = get_config(config_key)
        if current_value is None:
            raise HTTPException(status_code=404, detail="配置项不存在")
        
        # 更新配置
        set_config(config_key, update_data.value)
        
        # 获取更新后的值
        new_value = get_config(config_key)
        
        return {
            "success": True,
            "message": "配置项更新成功",
            "data": {
                "key": config_key,
                "old_value": current_value,
                "new_value": new_value
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新配置项失败: {e}")
        raise HTTPException(status_code=500, detail="更新配置项失败")


@router.put("/batch", response_model=ApiResponse[Dict[str, Any]], summary="批量更新配置")
async def update_config_batch(
    config_updates: Dict[str, Any],
    user: dict = Depends(get_current_user)
):
    """批量更新配置"""
    try:
        if not config_updates:
            raise HTTPException(status_code=400, detail="配置更新数据不能为空")
        
        updated_items = {}
        failed_items = {}
        
        for key, value in config_updates.items():
            try:
                # 验证配置键是否存在
                current_value = get_config(key)
                if current_value is None:
                    failed_items[key] = "配置项不存在"
                    continue
                
                # 更新配置
                set_config(key, value)
                updated_items[key] = {
                    "old_value": current_value,
                    "new_value": value
                }
                
            except Exception as e:
                failed_items[key] = str(e)
        
        return {
            "success": len(failed_items) == 0,
            "message": f"批量更新完成，成功: {len(updated_items)}, 失败: {len(failed_items)}",
            "data": {
                "updated": updated_items,
                "failed": failed_items
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量更新配置失败: {e}")
        raise HTTPException(status_code=500, detail="批量更新配置失败")


@router.post("/reload", response_model=ApiResponse[None], summary="重新加载配置")
async def reload_config(
    user: dict = Depends(get_current_user)
):
    """重新加载配置文件"""
    try:
        settings.reload()
        
        return {
            "success": True,
            "message": "配置重新加载成功",
            "data": None
        }
        
    except Exception as e:
        logger.error(f"重新加载配置失败: {e}")
        raise HTTPException(status_code=500, detail="重新加载配置失败")


@router.get("/work/settings", response_model=ApiResponse[Dict[str, Any]], summary="获取工作配置")
async def get_work_settings(
    user: dict = Depends(get_current_user)
):
    """获取工作相关配置"""
    try:
        work_config = {
            "standard_hours": get_config("work.standard_hours", 8.0),
            "max_daily_hours": get_config("work.max_daily_hours", 12.0),
            "overtime_threshold": get_config("work.overtime_threshold", 8.0),
            "min_work_duration": get_config("work.min_work_duration", 0.5),
            "max_break_duration": get_config("work.max_break_duration", 2.0),
            "auto_break_threshold": get_config("work.auto_break_threshold", 30),
            "start_time": get_config("work.start_time", "09:00"),
            "end_time": get_config("work.end_time", "18:00"),
            "lunch_start": get_config("work.lunch_start", "12:00"),
            "lunch_end": get_config("work.lunch_end", "13:00")
        }
        
        return {
            "success": True,
            "message": "工作配置获取成功",
            "data": work_config
        }
        
    except Exception as e:
        logger.error(f"获取工作配置失败: {e}")
        raise HTTPException(status_code=500, detail="获取工作配置失败")


@router.put("/work/settings", response_model=ApiResponse[Dict[str, Any]], summary="更新工作配置")
async def update_work_settings(
    work_config: Dict[str, Any],
    user: dict = Depends(get_current_user)
):
    """更新工作相关配置"""
    try:
        # 验证配置项
        valid_keys = {
            "standard_hours", "max_daily_hours", "overtime_threshold",
            "min_work_duration", "max_break_duration", "auto_break_threshold",
            "start_time", "end_time", "lunch_start", "lunch_end"
        }
        
        updated_config = {}
        for key, value in work_config.items():
            if key in valid_keys:
                config_key = f"work.{key}"
                set_config(config_key, value)
                updated_config[key] = value
        
        return {
            "success": True,
            "message": "工作配置更新成功",
            "data": updated_config
        }
        
    except Exception as e:
        logger.error(f"更新工作配置失败: {e}")
        raise HTTPException(status_code=500, detail="更新工作配置失败")


@router.get("/event/settings", response_model=ApiResponse[Dict[str, Any]], summary="获取事件配置")
async def get_event_settings(
    user: dict = Depends(get_current_user)
):
    """获取事件相关配置"""
    try:
        event_config = {
            "enabled_types": get_config("event.enabled_types", []),
            "min_intervals": get_config("event.min_intervals", {})
        }
        
        return {
            "success": True,
            "message": "事件配置获取成功",
            "data": event_config
        }
        
    except Exception as e:
        logger.error(f"获取事件配置失败: {e}")
        raise HTTPException(status_code=500, detail="获取事件配置失败")


@router.put("/event/settings", response_model=ApiResponse[Dict[str, Any]], summary="更新事件配置")
async def update_event_settings(
    event_config: Dict[str, Any],
    user: dict = Depends(get_current_user)
):
    """更新事件相关配置"""
    try:
        updated_config = {}
        
        if "enabled_types" in event_config:
            set_config("event.enabled_types", event_config["enabled_types"])
            updated_config["enabled_types"] = event_config["enabled_types"]
        
        if "min_intervals" in event_config:
            set_config("event.min_intervals", event_config["min_intervals"])
            updated_config["min_intervals"] = event_config["min_intervals"]
        
        return {
            "success": True,
            "message": "事件配置更新成功",
            "data": updated_config
        }
        
    except Exception as e:
        logger.error(f"更新事件配置失败: {e}")
        raise HTTPException(status_code=500, detail="更新事件配置失败")
