"""
事件处理器
增强的事件处理和业务逻辑
"""
import asyncio
import threading
import time
from typing import List, Dict, Any, Callable, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque

from event_listener import SystemEventData
from models import EventType, EventSource, SystemEventCreate
from dao import system_event_dao, time_record_dao
from logger import get_logger

logger = get_logger("EventProcessor")


class EventFilter:
    """事件过滤器"""
    
    def __init__(self):
        self.enabled_events: set = set(EventType)
        self.min_interval: Dict[EventType, float] = {}  # 最小间隔（秒）
        self.last_event_time: Dict[EventType, datetime] = {}
    
    def set_enabled_events(self, events: List[EventType]):
        """设置启用的事件类型"""
        self.enabled_events = set(events)
    
    def set_min_interval(self, event_type: EventType, interval: float):
        """设置事件最小间隔"""
        self.min_interval[event_type] = interval
    
    def should_process(self, event_data: SystemEventData) -> bool:
        """判断是否应该处理事件"""
        # 检查事件类型是否启用
        if event_data.event_type not in self.enabled_events:
            return False
        
        # 检查时间间隔
        if event_data.event_type in self.min_interval:
            min_interval = self.min_interval[event_data.event_type]
            last_time = self.last_event_time.get(event_data.event_type)
            
            if last_time:
                time_diff = (event_data.event_time - last_time).total_seconds()
                if time_diff < min_interval:
                    logger.debug(f"事件 {event_data.event_type} 间隔过短，跳过处理")
                    return False
        
        # 更新最后事件时间
        self.last_event_time[event_data.event_type] = event_data.event_time
        return True


class EventStatistics:
    """事件统计"""
    
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.event_counts: Dict[EventType, int] = defaultdict(int)
        self.event_history: deque = deque(maxlen=window_size)
        self.start_time = datetime.now()
    
    def record_event(self, event_data: SystemEventData):
        """记录事件"""
        self.event_counts[event_data.event_type] += 1
        self.event_history.append({
            "type": event_data.event_type,
            "time": event_data.event_time,
            "details": event_data.details
        })
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        total_events = sum(self.event_counts.values())
        uptime = datetime.now() - self.start_time
        
        return {
            "total_events": total_events,
            "event_counts": dict(self.event_counts),
            "uptime_seconds": uptime.total_seconds(),
            "events_per_hour": total_events / max(uptime.total_seconds() / 3600, 0.001),
            "recent_events": list(self.event_history)[-10:]  # 最近10个事件
        }


class WorkTimeCalculator:
    """工时计算器"""
    
    def __init__(self):
        self.session_start: Optional[datetime] = None
        self.last_activity: Optional[datetime] = None
        self.lock_time: Optional[datetime] = None
        self.total_lock_duration = 0  # 总锁屏时长（秒）
    
    def handle_event(self, event_data: SystemEventData):
        """处理事件并计算工时"""
        event_type = event_data.event_type
        event_time = event_data.event_time
        
        if event_type == EventType.STARTUP:
            self._handle_startup(event_time)
        elif event_type == EventType.UNLOCK:
            self._handle_unlock(event_time)
        elif event_type == EventType.LOCK:
            self._handle_lock(event_time)
        elif event_type == EventType.SHUTDOWN:
            self._handle_shutdown(event_time)
        
        # 更新最后活动时间
        if event_type in [EventType.STARTUP, EventType.UNLOCK]:
            self.last_activity = event_time
    
    def _handle_startup(self, event_time: datetime):
        """处理启动事件"""
        self.session_start = event_time
        self.last_activity = event_time
        self.lock_time = None
        logger.info(f"工作会话开始: {event_time}")
    
    def _handle_unlock(self, event_time: datetime):
        """处理解锁事件"""
        if self.lock_time:
            lock_duration = (event_time - self.lock_time).total_seconds()
            self.total_lock_duration += lock_duration
            logger.debug(f"解锁，锁屏时长: {lock_duration:.1f}秒")
        
        self.lock_time = None
        self.last_activity = event_time
    
    def _handle_lock(self, event_time: datetime):
        """处理锁屏事件"""
        self.lock_time = event_time
        logger.debug(f"锁屏时间: {event_time}")
    
    def _handle_shutdown(self, event_time: datetime):
        """处理关机事件"""
        if self.session_start:
            self._save_work_session(event_time)
        
        self._reset_session()
        logger.info(f"工作会话结束: {event_time}")
    
    def _save_work_session(self, end_time: datetime):
        """保存工作会话"""
        if not self.session_start:
            return
        
        try:
            # 计算工作时长
            total_duration = (end_time - self.session_start).total_seconds()
            work_duration = max(0, total_duration - self.total_lock_duration)
            
            # 检查是否已有当天记录
            work_date = self.session_start.date()
            existing_record = time_record_dao.get_by_date(work_date)
            
            if existing_record:
                # 更新现有记录
                from models import TimeRecordUpdate
                update_data = TimeRecordUpdate(
                    clock_out=end_time,
                    notes=f"系统自动记录 - 锁屏时长: {self.total_lock_duration/60:.1f}分钟"
                )
                time_record_dao.update(existing_record.id, update_data)
                logger.info(f"更新工时记录: {work_date}")
            else:
                # 创建新记录
                from models import TimeRecordCreate, RecordStatus
                record_data = TimeRecordCreate(
                    date=work_date,
                    clock_in=self.session_start,
                    clock_out=end_time,
                    duration=int(work_duration / 60),  # 转换为分钟
                    break_duration=int(self.total_lock_duration / 60),
                    status=RecordStatus.NORMAL,
                    notes="系统自动记录"
                )
                time_record_dao.create(record_data)
                logger.info(f"创建工时记录: {work_date}")
                
        except Exception as e:
            logger.error(f"保存工作会话失败: {e}")
    
    def _reset_session(self):
        """重置会话"""
        self.session_start = None
        self.last_activity = None
        self.lock_time = None
        self.total_lock_duration = 0
    
    def get_current_session_info(self) -> Dict[str, Any]:
        """获取当前会话信息"""
        if not self.session_start:
            return {"active": False}
        
        now = datetime.now()
        total_duration = (now - self.session_start).total_seconds()
        
        # 如果当前锁屏，计算锁屏时长
        current_lock_duration = 0
        if self.lock_time:
            current_lock_duration = (now - self.lock_time).total_seconds()
        
        work_duration = max(0, total_duration - self.total_lock_duration - current_lock_duration)
        
        return {
            "active": True,
            "session_start": self.session_start,
            "last_activity": self.last_activity,
            "is_locked": self.lock_time is not None,
            "lock_time": self.lock_time,
            "total_duration_minutes": total_duration / 60,
            "work_duration_minutes": work_duration / 60,
            "lock_duration_minutes": (self.total_lock_duration + current_lock_duration) / 60
        }


class EnhancedEventProcessor:
    """增强的事件处理器"""
    
    def __init__(self):
        self.filter = EventFilter()
        self.statistics = EventStatistics()
        self.work_calculator = WorkTimeCalculator()
        self.custom_handlers: List[Callable[[SystemEventData], None]] = []
        
        # 设置默认过滤规则
        self._setup_default_filters()
    
    def _setup_default_filters(self):
        """设置默认过滤规则"""
        # 设置最小间隔，避免重复事件
        self.filter.set_min_interval(EventType.LOCK, 5.0)  # 锁屏事件最小间隔5秒
        self.filter.set_min_interval(EventType.UNLOCK, 5.0)  # 解锁事件最小间隔5秒
        self.filter.set_min_interval(EventType.SUSPEND, 10.0)  # 挂起事件最小间隔10秒
        self.filter.set_min_interval(EventType.RESUME, 10.0)  # 恢复事件最小间隔10秒
    
    def add_custom_handler(self, handler: Callable[[SystemEventData], None]):
        """添加自定义事件处理器"""
        self.custom_handlers.append(handler)
    
    def process_event(self, event_data: SystemEventData):
        """处理事件"""
        try:
            # 过滤事件
            if not self.filter.should_process(event_data):
                return
            
            # 记录统计
            self.statistics.record_event(event_data)
            
            # 保存到数据库
            self._save_to_database(event_data)
            
            # 工时计算
            self.work_calculator.handle_event(event_data)
            
            # 执行自定义处理器
            for handler in self.custom_handlers:
                try:
                    handler(event_data)
                except Exception as e:
                    logger.error(f"自定义事件处理器执行失败: {e}")
            
            logger.info(f"事件处理完成: {event_data}")
            
        except Exception as e:
            logger.error(f"事件处理失败: {e}")
    
    def _save_to_database(self, event_data: SystemEventData):
        """保存事件到数据库"""
        try:
            create_model = event_data.to_create_model()
            event_id = system_event_dao.create(create_model)
            logger.debug(f"事件已保存到数据库: ID={event_id}")
        except Exception as e:
            logger.error(f"保存事件到数据库失败: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """获取处理器状态"""
        return {
            "statistics": self.statistics.get_statistics(),
            "work_session": self.work_calculator.get_current_session_info(),
            "filter_settings": {
                "enabled_events": list(self.filter.enabled_events),
                "min_intervals": self.filter.min_interval
            }
        }


# 全局事件处理器实例
enhanced_event_processor = EnhancedEventProcessor()
