"""
事件服务
集成事件监听、处理和数据存储的完整服务
"""
import threading
import time
from typing import Dict, Any, Optional
from datetime import datetime

from event_listener import event_manager
from platform_listener import create_platform_listener
from event_processor import enhanced_event_processor
from config import config_manager
from logger import get_logger

logger = get_logger("EventService")


class EventService:
    """事件服务主类"""
    
    def __init__(self):
        self.is_running = False
        self.platform_listener = None
        self.start_time: Optional[datetime] = None
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        # 加载配置
        self._load_config()
    
    def _load_config(self):
        """加载配置"""
        try:
            # 事件过滤配置
            enabled_events = config_manager.get("event.enabled_types", [
                "LOCK", "UNLOCK", "STARTUP", "SHUTDOWN", "SUSPEND", "RESUME"
            ])
            
            # 转换为EventType枚举
            from models import EventType
            event_types = []
            for event_name in enabled_events:
                try:
                    event_types.append(EventType(event_name.lower()))
                except ValueError:
                    logger.warning(f"未知的事件类型: {event_name}")
            
            enhanced_event_processor.filter.set_enabled_events(event_types)
            
            # 事件间隔配置
            intervals = config_manager.get("event.min_intervals", {
                "LOCK": 5.0,
                "UNLOCK": 5.0,
                "SUSPEND": 10.0,
                "RESUME": 10.0
            })
            
            for event_name, interval in intervals.items():
                try:
                    event_type = EventType(event_name.lower())
                    enhanced_event_processor.filter.set_min_interval(event_type, interval)
                except ValueError:
                    logger.warning(f"未知的事件类型: {event_name}")
            
            logger.info("事件服务配置加载完成")
            
        except Exception as e:
            logger.error(f"加载事件服务配置失败: {e}")
    
    def start(self):
        """启动事件服务"""
        if self.is_running:
            logger.warning("事件服务已经在运行")
            return
        
        try:
            logger.info("启动事件服务...")
            
            # 创建平台监听器
            self.platform_listener = create_platform_listener()
            
            # 注册到事件管理器
            event_manager.register_listener(self.platform_listener)
            
            # 替换默认的事件处理器
            event_manager._handle_event = enhanced_event_processor.process_event
            
            # 启动事件管理器
            event_manager.start_all()
            
            # 启动监控线程
            self._start_monitor()
            
            self.is_running = True
            self.start_time = datetime.now()
            
            logger.info("事件服务启动成功")
            
        except Exception as e:
            logger.error(f"启动事件服务失败: {e}")
            self.stop()
            raise
    
    def stop(self):
        """停止事件服务"""
        if not self.is_running:
            return
        
        try:
            logger.info("停止事件服务...")
            
            self.is_running = False
            self._stop_event.set()
            
            # 停止监控线程
            if self._monitor_thread and self._monitor_thread.is_alive():
                self._monitor_thread.join(timeout=5.0)
            
            # 停止事件管理器
            event_manager.stop_all()
            
            # 注销监听器
            if self.platform_listener:
                event_manager.unregister_listener(self.platform_listener.name)
                self.platform_listener = None
            
            logger.info("事件服务已停止")
            
        except Exception as e:
            logger.error(f"停止事件服务失败: {e}")
    
    def _start_monitor(self):
        """启动监控线程"""
        self._stop_event.clear()
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        logger.debug("事件服务监控线程已启动")
    
    def _monitor_loop(self):
        """监控循环"""
        last_status_log = time.time()
        status_interval = 300  # 5分钟记录一次状态
        
        while self.is_running and not self._stop_event.is_set():
            try:
                current_time = time.time()
                
                # 定期记录状态
                if current_time - last_status_log >= status_interval:
                    self._log_status()
                    last_status_log = current_time
                
                # 检查事件管理器状态
                manager_status = event_manager.get_status()
                if not manager_status["is_running"]:
                    logger.warning("事件管理器已停止，尝试重启")
                    event_manager.start_all()
                
                # 检查队列大小
                queue_size = manager_status.get("queue_size", 0)
                if queue_size > 100:
                    logger.warning(f"事件队列积压: {queue_size} 个事件")
                
                time.sleep(30)  # 30秒检查一次
                
            except Exception as e:
                logger.error(f"监控循环异常: {e}")
                time.sleep(60)  # 出错时等待更长时间
    
    def _log_status(self):
        """记录状态信息"""
        try:
            status = self.get_status()
            logger.info(f"事件服务状态: 运行时间={status['uptime_minutes']:.1f}分钟, "
                       f"处理事件={status['processor_status']['statistics']['total_events']}个, "
                       f"队列大小={status['manager_status']['queue_size']}")
        except Exception as e:
            logger.error(f"记录状态失败: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        uptime = 0
        if self.start_time:
            uptime = (datetime.now() - self.start_time).total_seconds() / 60
        
        return {
            "is_running": self.is_running,
            "start_time": self.start_time,
            "uptime_minutes": uptime,
            "platform_listener": {
                "name": self.platform_listener.name if self.platform_listener else None,
                "is_running": self.platform_listener.is_running if self.platform_listener else False,
                "supported_events": (
                    [e.value for e in self.platform_listener.get_supported_events()] 
                    if self.platform_listener else []
                )
            },
            "manager_status": event_manager.get_status(),
            "processor_status": enhanced_event_processor.get_status()
        }
    
    def restart(self):
        """重启事件服务"""
        logger.info("重启事件服务...")
        self.stop()
        time.sleep(2)  # 等待完全停止
        self.start()
    
    def reload_config(self):
        """重新加载配置"""
        logger.info("重新加载事件服务配置...")
        try:
            config_manager.reload()
            self._load_config()
            logger.info("配置重新加载完成")
        except Exception as e:
            logger.error(f"重新加载配置失败: {e}")


class EventServiceManager:
    """事件服务管理器（单例）"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.service = EventService()
        self._initialized = True
    
    def start(self):
        """启动事件服务"""
        return self.service.start()
    
    def stop(self):
        """停止事件服务"""
        return self.service.stop()
    
    def restart(self):
        """重启事件服务"""
        return self.service.restart()
    
    def get_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        return self.service.get_status()
    
    def reload_config(self):
        """重新加载配置"""
        return self.service.reload_config()
    
    def is_running(self) -> bool:
        """检查服务是否运行"""
        return self.service.is_running


# 全局事件服务管理器实例
event_service_manager = EventServiceManager()


# 便捷函数
def start_event_service():
    """启动事件服务"""
    return event_service_manager.start()


def stop_event_service():
    """停止事件服务"""
    return event_service_manager.stop()


def get_event_service_status():
    """获取事件服务状态"""
    return event_service_manager.get_status()


def is_event_service_running():
    """检查事件服务是否运行"""
    return event_service_manager.is_running()
