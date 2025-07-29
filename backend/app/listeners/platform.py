"""
跨平台事件监听器
根据当前平台自动选择合适的事件监听器
"""
import platform
import time
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.listeners.base import EventListener, SystemEventData
from app.models import EventType, EventSource
from app.core.logger import get_logger

logger = get_logger("PlatformListener")


class GenericEventListener(EventListener):
    """通用事件监听器（用于不支持的平台）"""
    
    def __init__(self):
        super().__init__("GenericEventListener")
        self.check_interval = 30  # 检查间隔（秒）
        self.last_check_time = None
    
    def get_supported_events(self) -> List[EventType]:
        """获取支持的事件类型"""
        return [EventType.STARTUP]  # 只支持启动事件
    
    def _run(self):
        """监听器主循环"""
        logger.info("使用通用事件监听器（功能有限）")
        
        # 发送启动事件
        self._notify_startup_event()
        
        # 定期检查（保持监听器活跃）
        while self.is_running and not self._stop_event.is_set():
            try:
                time.sleep(self.check_interval)
                
                # 可以在这里添加一些通用的检查逻辑
                # 比如检查系统负载、网络状态等
                
            except Exception as e:
                logger.error(f"通用事件监听器异常: {e}")
    
    def _notify_startup_event(self):
        """通知启动事件"""
        event_data = SystemEventData(
            event_type=EventType.STARTUP,
            event_time=datetime.now(),
            source=EventSource.SYSTEM,
            details="应用程序启动",
            platform_info=platform.system()
        )
        self._notify_callbacks(event_data)


class MacOSEventListener(EventListener):
    """macOS事件监听器（占位符）"""
    
    def __init__(self):
        super().__init__("MacOSEventListener")
    
    def get_supported_events(self) -> List[EventType]:
        """获取支持的事件类型"""
        return [
            EventType.LOCK,
            EventType.UNLOCK,
            EventType.SUSPEND,
            EventType.RESUME,
            EventType.STARTUP,
            EventType.SHUTDOWN
        ]
    
    def _run(self):
        """监听器主循环"""
        logger.info("macOS事件监听器启动（待实现）")
        
        # TODO: 实现macOS特定的事件监听
        # 可以使用PyObjC和NSWorkspace notifications
        
        # 发送启动事件
        event_data = SystemEventData(
            event_type=EventType.STARTUP,
            event_time=datetime.now(),
            source=EventSource.SYSTEM,
            details="macOS应用程序启动",
            platform_info="macOS"
        )
        self._notify_callbacks(event_data)
        
        # 保持监听器运行
        while self.is_running and not self._stop_event.is_set():
            time.sleep(1)


class LinuxEventListener(EventListener):
    """Linux事件监听器（占位符）"""
    
    def __init__(self):
        super().__init__("LinuxEventListener")
    
    def get_supported_events(self) -> List[EventType]:
        """获取支持的事件类型"""
        return [
            EventType.LOCK,
            EventType.UNLOCK,
            EventType.SUSPEND,
            EventType.RESUME,
            EventType.STARTUP,
            EventType.SHUTDOWN
        ]
    
    def _run(self):
        """监听器主循环"""
        logger.info("Linux事件监听器启动（待实现）")
        
        # TODO: 实现Linux特定的事件监听
        # 可以使用D-Bus监听systemd或桌面环境事件
        
        # 发送启动事件
        event_data = SystemEventData(
            event_type=EventType.STARTUP,
            event_time=datetime.now(),
            source=EventSource.SYSTEM,
            details="Linux应用程序启动",
            platform_info="Linux"
        )
        self._notify_callbacks(event_data)
        
        # 保持监听器运行
        while self.is_running and not self._stop_event.is_set():
            time.sleep(1)


class PlatformEventListenerFactory:
    """平台事件监听器工厂"""
    
    @staticmethod
    def create_listener() -> EventListener:
        """根据当前平台创建合适的事件监听器"""
        system = platform.system()
        
        try:
            if system == "Windows":
                from app.listeners.windows import create_windows_listener
                listener = create_windows_listener()
                logger.info("创建Windows事件监听器")
                return listener
            
            elif system == "Darwin":  # macOS
                listener = MacOSEventListener()
                logger.info("创建macOS事件监听器")
                return listener
            
            elif system == "Linux":
                listener = LinuxEventListener()
                logger.info("创建Linux事件监听器")
                return listener
            
            else:
                logger.warning(f"不支持的平台: {system}，使用通用监听器")
                return GenericEventListener()
                
        except ImportError as e:
            logger.warning(f"无法导入平台特定监听器: {e}，使用通用监听器")
            return GenericEventListener()
        except Exception as e:
            logger.error(f"创建平台监听器失败: {e}，使用通用监听器")
            return GenericEventListener()
    
    @staticmethod
    def get_platform_info() -> Dict[str, Any]:
        """获取平台信息"""
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version()
        }


class MultiPlatformEventListener(EventListener):
    """多平台事件监听器包装器"""
    
    def __init__(self):
        super().__init__("MultiPlatformEventListener")
        self.platform_listener: Optional[EventListener] = None
        self.platform_info = PlatformEventListenerFactory.get_platform_info()
    
    def get_supported_events(self) -> List[EventType]:
        """获取支持的事件类型"""
        if self.platform_listener:
            return self.platform_listener.get_supported_events()
        return []
    
    def start(self):
        """启动监听器"""
        if self.is_running:
            return
        
        # 创建平台特定的监听器
        self.platform_listener = PlatformEventListenerFactory.create_listener()
        
        # 转发回调
        for callback in self.callbacks:
            self.platform_listener.add_callback(callback)
        
        # 启动平台监听器
        self.platform_listener.start()
        self.is_running = True
        
        logger.info(f"多平台事件监听器已启动 - {self.platform_info['system']}")
    
    def stop(self):
        """停止监听器"""
        if not self.is_running:
            return
        
        if self.platform_listener:
            self.platform_listener.stop()
            self.platform_listener = None
        
        self.is_running = False
        logger.info("多平台事件监听器已停止")
    
    def add_callback(self, callback):
        """添加回调函数"""
        super().add_callback(callback)
        if self.platform_listener:
            self.platform_listener.add_callback(callback)
    
    def remove_callback(self, callback):
        """移除回调函数"""
        super().remove_callback(callback)
        if self.platform_listener:
            self.platform_listener.remove_callback(callback)
    
    def _run(self):
        """监听器主循环（由平台监听器处理）"""
        pass
    
    def get_platform_info(self) -> Dict[str, Any]:
        """获取平台信息"""
        return self.platform_info.copy()


# 创建多平台事件监听器的便捷函数
def create_platform_listener() -> MultiPlatformEventListener:
    """创建多平台事件监听器"""
    return MultiPlatformEventListener()
