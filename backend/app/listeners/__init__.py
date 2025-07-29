"""
事件监听器包
"""
from .base import EventListener, SystemEventData, EventQueue, EventManager, event_manager
from .platform import (
    MultiPlatformEventListener, PlatformEventListenerFactory,
    create_platform_listener
)

# 条件导入平台特定监听器
try:
    from .windows import WindowsEventListener, create_windows_listener
    __all_windows__ = ["WindowsEventListener", "create_windows_listener"]
except ImportError:
    __all_windows__ = []

__all__ = [
    # 基础组件
    "EventListener", "SystemEventData", "EventQueue", "EventManager", "event_manager",

    # 跨平台组件
    "MultiPlatformEventListener", "PlatformEventListenerFactory", "create_platform_listener"
] + __all_windows__