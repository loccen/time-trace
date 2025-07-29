"""
系统事件监听器
跨平台的系统事件监听架构
"""
import platform
import threading
import queue
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Callable, Optional, Any
from datetime import datetime
from enum import Enum

from models import EventType, EventSource, SystemEventCreate
from dao import system_event_dao
from logger import get_logger

logger = get_logger("EventListener")


class SystemEventData:
    """系统事件数据结构"""

    def __init__(self, event_type: EventType, event_time: datetime = None,
                 source: EventSource = EventSource.SYSTEM, details: str = None,
                 platform_info: str = None, raw_data: Any = None):
        self.event_type = event_type
        self.event_time = event_time or datetime.now()
        self.source = source
        self.details = details
        self.platform_info = platform_info or platform.system()
        self.raw_data = raw_data

    def to_create_model(self) -> SystemEventCreate:
        """转换为数据库创建模型"""
        return SystemEventCreate(
            event_type=self.event_type,
            event_time=self.event_time,
            event_source=self.source,
            details=self.details
        )

    def __str__(self):
        return f"SystemEvent({self.event_type}, {self.event_time}, {self.details})"


class EventListener(ABC):
    """事件监听器抽象基类"""

    def __init__(self, name: str):
        self.name = name
        self.is_running = False
        self.callbacks: List[Callable[[SystemEventData], None]] = []
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def add_callback(self, callback: Callable[[SystemEventData], None]):
        """添加事件回调函数"""
        self.callbacks.append(callback)

    def remove_callback(self, callback: Callable[[SystemEventData], None]):
        """移除事件回调函数"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)

    def _notify_callbacks(self, event_data: SystemEventData):
        """通知所有回调函数"""
        for callback in self.callbacks:
            try:
                callback(event_data)
            except Exception as e:
                logger.error(f"事件回调执行失败: {e}")

    def start(self):
        """启动监听器"""
        if self.is_running:
            logger.warning(f"监听器 {self.name} 已经在运行")
            return

        self.is_running = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.info(f"监听器 {self.name} 已启动")

    def stop(self):
        """停止监听器"""
        if not self.is_running:
            return

        self.is_running = False
        self._stop_event.set()

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)

        logger.info(f"监听器 {self.name} 已停止")

    @abstractmethod
    def _run(self):
        """监听器主循环，子类需要实现"""
        pass

    @abstractmethod
    def get_supported_events(self) -> List[EventType]:
        """获取支持的事件类型"""
        pass


class EventQueue:
    """事件队列管理器"""

    def __init__(self, max_size: int = 1000):
        self._queue = queue.Queue(maxsize=max_size)
        self._processing = False
        self._processor_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def put(self, event_data: SystemEventData):
        """添加事件到队列"""
        try:
            self._queue.put_nowait(event_data)
            logger.debug(f"事件已加入队列: {event_data}")
        except queue.Full:
            logger.warning("事件队列已满，丢弃事件")

    def start_processing(self, processor: Callable[[SystemEventData], None]):
        """启动事件处理"""
        if self._processing:
            return

        self._processing = True
        self._stop_event.clear()
        self._processor_thread = threading.Thread(
            target=self._process_events,
            args=(processor,),
            daemon=True
        )
        self._processor_thread.start()
        logger.info("事件队列处理器已启动")

    def stop_processing(self):
        """停止事件处理"""
        if not self._processing:
            return

        self._processing = False
        self._stop_event.set()

        if self._processor_thread and self._processor_thread.is_alive():
            self._processor_thread.join(timeout=5.0)

        logger.info("事件队列处理器已停止")

    def _process_events(self, processor: Callable[[SystemEventData], None]):
        """处理事件队列"""
        while self._processing and not self._stop_event.is_set():
            try:
                # 批量处理事件
                events = []

                # 收集一批事件
                try:
                    # 等待第一个事件
                    event = self._queue.get(timeout=1.0)
                    events.append(event)

                    # 收集更多事件（非阻塞）
                    while len(events) < 10:  # 批量大小限制
                        try:
                            event = self._queue.get_nowait()
                            events.append(event)
                        except queue.Empty:
                            break

                except queue.Empty:
                    continue

                # 处理事件批次
                for event in events:
                    try:
                        processor(event)
                        self._queue.task_done()
                    except Exception as e:
                        logger.error(f"事件处理失败: {e}")
                        self._queue.task_done()

            except Exception as e:
                logger.error(f"事件队列处理异常: {e}")

    def size(self) -> int:
        """获取队列大小"""
        return self._queue.qsize()


class EventManager:
    """事件管理器"""

    def __init__(self):
        self.listeners: Dict[str, EventListener] = {}
        self.event_queue = EventQueue()
        self.is_running = False

        # 启动事件处理
        self.event_queue.start_processing(self._handle_event)

    def register_listener(self, listener: EventListener):
        """注册事件监听器"""
        self.listeners[listener.name] = listener
        listener.add_callback(self._on_event_received)
        logger.info(f"注册事件监听器: {listener.name}")

    def unregister_listener(self, name: str):
        """注销事件监听器"""
        if name in self.listeners:
            listener = self.listeners[name]
            listener.remove_callback(self._on_event_received)
            listener.stop()
            del self.listeners[name]
            logger.info(f"注销事件监听器: {name}")

    def start_all(self):
        """启动所有监听器"""
        if self.is_running:
            return

        self.is_running = True
        for listener in self.listeners.values():
            listener.start()

        logger.info("所有事件监听器已启动")

    def stop_all(self):
        """停止所有监听器"""
        if not self.is_running:
            return

        self.is_running = False
        for listener in self.listeners.values():
            listener.stop()

        self.event_queue.stop_processing()
        logger.info("所有事件监听器已停止")

    def _on_event_received(self, event_data: SystemEventData):
        """接收到事件时的回调"""
        self.event_queue.put(event_data)

    def _handle_event(self, event_data: SystemEventData):
        """处理单个事件"""
        try:
            # 记录到数据库
            create_model = event_data.to_create_model()
            event_id = system_event_dao.create(create_model)

            logger.info(f"系统事件已记录: {event_data} (ID: {event_id})")

        except Exception as e:
            logger.error(f"处理系统事件失败: {e}")

    def get_status(self) -> Dict[str, Any]:
        """获取管理器状态"""
        return {
            "is_running": self.is_running,
            "listeners": {
                name: listener.is_running
                for name, listener in self.listeners.items()
            },
            "queue_size": self.event_queue.size()
        }


# 全局事件管理器实例
event_manager = EventManager()
