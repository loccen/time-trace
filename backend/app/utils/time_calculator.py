"""
工时计算工具
"""
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, date, time, timedelta
from enum import Enum

from app.models import WorkMode, BreakType, RecordStatus
from app.dao import time_record_dao
from app.config.settings import get_config
from app.core.logger import get_logger

logger = get_logger("TimeCalculator")


class WorkTimeRule:
    """工时计算规则"""
    
    def __init__(self):
        self.standard_hours = 8.0  # 标准工作时长（小时）
        self.max_daily_hours = 12.0  # 每日最大工作时长
        self.overtime_threshold = 8.0  # 加班时长阈值
        self.min_work_duration = 0.5  # 最小工作时长（小时）
        self.max_break_duration = 2.0  # 最大休息时长（小时）
        self.auto_break_threshold = 30  # 自动休息阈值（分钟）
        
        # 工作时间段
        self.work_start_time = time(9, 0)  # 标准上班时间
        self.work_end_time = time(18, 0)   # 标准下班时间
        self.lunch_start_time = time(12, 0)  # 午休开始时间
        self.lunch_end_time = time(13, 0)    # 午休结束时间
        
        # 加载配置
        self._load_config()
    
    def _load_config(self):
        """加载配置"""
        try:
            self.standard_hours = get_config("work.standard_hours", 8.0)
            self.max_daily_hours = get_config("work.max_daily_hours", 12.0)
            self.overtime_threshold = get_config("work.overtime_threshold", 8.0)
            self.min_work_duration = get_config("work.min_work_duration", 0.5)
            self.max_break_duration = get_config("work.max_break_duration", 2.0)
            self.auto_break_threshold = get_config("work.auto_break_threshold", 30)
            
            # 时间配置
            work_start = get_config("work.start_time", "09:00")
            work_end = get_config("work.end_time", "18:00")
            lunch_start = get_config("work.lunch_start", "12:00")
            lunch_end = get_config("work.lunch_end", "13:00")
            
            self.work_start_time = datetime.strptime(work_start, "%H:%M").time()
            self.work_end_time = datetime.strptime(work_end, "%H:%M").time()
            self.lunch_start_time = datetime.strptime(lunch_start, "%H:%M").time()
            self.lunch_end_time = datetime.strptime(lunch_end, "%H:%M").time()
            
        except Exception as e:
            logger.warning(f"加载工时规则配置失败，使用默认值: {e}")


class BreakPeriod:
    """休息时段"""
    
    def __init__(self, start_time: datetime, end_time: datetime = None, 
                 break_type: BreakType = BreakType.SHORT, description: str = ""):
        self.start_time = start_time
        self.end_time = end_time
        self.break_type = break_type
        self.description = description
    
    @property
    def duration_minutes(self) -> int:
        """休息时长（分钟）"""
        if not self.end_time:
            return 0
        return int((self.end_time - self.start_time).total_seconds() / 60)
    
    @property
    def is_active(self) -> bool:
        """是否正在休息"""
        return self.end_time is None
    
    def end_break(self, end_time: datetime):
        """结束休息"""
        self.end_time = end_time


class WorkTimeCalculator:
    """工时计算器"""
    
    def __init__(self, work_mode: WorkMode = WorkMode.STANDARD):
        self.work_mode = work_mode
        self.rules = WorkTimeRule()
        
        # 当前会话状态
        self.session_start: Optional[datetime] = None
        self.session_end: Optional[datetime] = None
        self.last_activity: Optional[datetime] = None
        
        # 休息时段记录
        self.break_periods: List[BreakPeriod] = []
        self.current_break: Optional[BreakPeriod] = None
        
        # 统计数据
        self.total_work_duration = 0  # 总工作时长（分钟）
        self.total_break_duration = 0  # 总休息时长（分钟）
        self.overtime_duration = 0    # 加班时长（分钟）
    
    def start_work_session(self, start_time: datetime, mode: WorkMode = None):
        """开始工作会话"""
        if mode:
            self.work_mode = mode
        
        self.session_start = start_time
        self.last_activity = start_time
        self.session_end = None
        
        # 重置统计
        self.break_periods.clear()
        self.current_break = None
        self.total_work_duration = 0
        self.total_break_duration = 0
        self.overtime_duration = 0
        
        logger.info(f"开始工作会话: {start_time}, 模式: {self.work_mode}")
    
    def end_work_session(self, end_time: datetime) -> Dict[str, Any]:
        """结束工作会话"""
        if not self.session_start:
            logger.warning("尝试结束未开始的工作会话")
            return {}
        
        self.session_end = end_time
        
        # 如果有未结束的休息，自动结束
        if self.current_break and self.current_break.is_active:
            self.end_break(end_time)
        
        # 计算工时
        result = self._calculate_work_time()
        
        # 保存到数据库
        self._save_to_database(result)
        
        logger.info(f"结束工作会话: {end_time}, 工作时长: {result['work_hours']:.2f}小时")
        return result
    
    def start_break(self, start_time: datetime, break_type: BreakType = BreakType.SHORT, 
                   description: str = ""):
        """开始休息"""
        if self.current_break and self.current_break.is_active:
            logger.warning("已有活跃的休息时段，自动结束前一个")
            self.end_break(start_time)
        
        self.current_break = BreakPeriod(start_time, None, break_type, description)
        self.break_periods.append(self.current_break)
        
        logger.debug(f"开始休息: {start_time}, 类型: {break_type}")
    
    def end_break(self, end_time: datetime):
        """结束休息"""
        if not self.current_break or not self.current_break.is_active:
            logger.warning("没有活跃的休息时段")
            return
        
        self.current_break.end_break(end_time)
        self.last_activity = end_time
        
        logger.debug(f"结束休息: {end_time}, 时长: {self.current_break.duration_minutes}分钟")
        self.current_break = None
    
    def _calculate_work_time(self) -> Dict[str, Any]:
        """计算工作时间"""
        if not self.session_start or not self.session_end:
            return {}
        
        # 总会话时长
        total_session_minutes = (self.session_end - self.session_start).total_seconds() / 60
        
        # 计算总休息时长
        total_break_minutes = sum(bp.duration_minutes for bp in self.break_periods)
        
        # 实际工作时长
        actual_work_minutes = max(0, total_session_minutes - total_break_minutes)
        
        # 应用工作模式规则
        work_minutes = self._apply_work_mode_rules(actual_work_minutes)
        
        # 计算加班时长
        standard_minutes = self.rules.standard_hours * 60
        overtime_minutes = max(0, work_minutes - standard_minutes)
        
        # 分类休息时长
        break_by_type = {}
        for break_type in BreakType:
            break_by_type[break_type.value] = sum(
                bp.duration_minutes for bp in self.break_periods 
                if bp.break_type == break_type
            )
        
        return {
            "session_start": self.session_start,
            "session_end": self.session_end,
            "total_session_minutes": int(total_session_minutes),
            "total_break_minutes": int(total_break_minutes),
            "work_minutes": int(work_minutes),
            "work_hours": work_minutes / 60,
            "overtime_minutes": int(overtime_minutes),
            "overtime_hours": overtime_minutes / 60,
            "break_by_type": break_by_type,
            "break_periods": [
                {
                    "start": bp.start_time,
                    "end": bp.end_time,
                    "duration_minutes": bp.duration_minutes,
                    "type": bp.break_type.value,
                    "description": bp.description
                }
                for bp in self.break_periods
            ],
            "work_mode": self.work_mode.value,
            "efficiency": self._calculate_efficiency(work_minutes, total_session_minutes)
        }
    
    def _apply_work_mode_rules(self, work_minutes: float) -> float:
        """应用工作模式规则"""
        if self.work_mode == WorkMode.FLEXIBLE:
            # 弹性工作模式：允许更灵活的时间安排
            return work_minutes
        
        elif self.work_mode == WorkMode.SHIFT:
            # 轮班模式：可能有不同的标准时长
            return work_minutes
        
        elif self.work_mode == WorkMode.REMOTE:
            # 远程工作模式：可能需要不同的计算方式
            return work_minutes
        
        else:  # STANDARD
            # 标准模式：应用标准规则
            max_minutes = self.rules.max_daily_hours * 60
            return min(work_minutes, max_minutes)
    
    def _calculate_efficiency(self, work_minutes: float, total_minutes: float) -> float:
        """计算工作效率"""
        if total_minutes <= 0:
            return 0.0
        return min(1.0, work_minutes / total_minutes)
    
    def _save_to_database(self, calculation_result: Dict[str, Any]):
        """保存计算结果到数据库"""
        try:
            from app.models import TimeRecordCreate
            
            work_date = self.session_start.date()
            
            # 检查是否已有记录
            existing_record = time_record_dao.get_by_date(work_date)
            
            # 准备备注信息
            notes = f"工作模式: {self.work_mode.value}, 效率: {calculation_result['efficiency']:.1%}"
            if calculation_result['break_periods']:
                notes += f", 休息次数: {len(calculation_result['break_periods'])}"
            
            if existing_record:
                # 更新现有记录
                from app.models import TimeRecordUpdate
                update_data = TimeRecordUpdate(
                    clock_out=self.session_end,
                    break_duration=calculation_result['total_break_minutes'],
                    notes=notes
                )
                time_record_dao.update(existing_record.id, update_data)
                logger.info(f"更新工时记录: {work_date}")
            else:
                # 创建新记录
                record_data = TimeRecordCreate(
                    date=work_date,
                    clock_in=self.session_start,
                    clock_out=self.session_end,
                    duration=calculation_result['work_minutes'],
                    break_duration=calculation_result['total_break_minutes'],
                    overtime_duration=calculation_result['overtime_minutes'],
                    status=RecordStatus.NORMAL,
                    notes=notes
                )
                time_record_dao.create(record_data)
                logger.info(f"创建工时记录: {work_date}")
                
        except Exception as e:
            logger.error(f"保存工时记录失败: {e}")
    
    def get_current_status(self) -> Dict[str, Any]:
        """获取当前状态"""
        if not self.session_start:
            return {"active": False}
        
        now = datetime.now()
        
        # 计算当前工作时长
        current_session_minutes = (now - self.session_start).total_seconds() / 60
        current_break_minutes = sum(bp.duration_minutes for bp in self.break_periods)
        
        # 如果正在休息，加上当前休息时长
        if self.current_break and self.current_break.is_active:
            current_break_minutes += (now - self.current_break.start_time).total_seconds() / 60
        
        current_work_minutes = max(0, current_session_minutes - current_break_minutes)
        
        return {
            "active": True,
            "session_start": self.session_start,
            "last_activity": self.last_activity,
            "current_time": now,
            "session_duration_minutes": int(current_session_minutes),
            "work_duration_minutes": int(current_work_minutes),
            "break_duration_minutes": int(current_break_minutes),
            "work_hours": current_work_minutes / 60,
            "is_on_break": self.current_break is not None and self.current_break.is_active,
            "current_break": {
                "start_time": self.current_break.start_time,
                "type": self.current_break.break_type.value,
                "duration_minutes": int((now - self.current_break.start_time).total_seconds() / 60)
            } if self.current_break and self.current_break.is_active else None,
            "work_mode": self.work_mode.value,
            "break_count": len(self.break_periods)
        }


# 全局工时计算器实例
work_time_calculator = WorkTimeCalculator()
