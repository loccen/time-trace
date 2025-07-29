"""
增强的工时计算模块
支持自动计算、手动调整、加班统计等功能
"""
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, date, time, timedelta
from enum import Enum
import json

from models import (
    TimeRecord, TimeRecordCreate, TimeRecordUpdate, 
    RecordStatus, EventType
)
from dao import time_record_dao
from config import config_manager
from logger import get_logger

logger = get_logger("WorkTimeCalculator")


class WorkMode(str, Enum):
    """工作模式枚举"""
    STANDARD = "standard"  # 标准工作模式
    FLEXIBLE = "flexible"  # 弹性工作模式
    SHIFT = "shift"        # 轮班工作模式
    REMOTE = "remote"      # 远程工作模式


class BreakType(str, Enum):
    """休息类型枚举"""
    LUNCH = "lunch"        # 午休
    SHORT = "short"        # 短暂休息
    LONG = "long"          # 长时间休息
    MEETING = "meeting"    # 会议间隙
    SYSTEM = "system"      # 系统锁屏


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
            self.standard_hours = config_manager.get("work.standard_hours", 8.0)
            self.max_daily_hours = config_manager.get("work.max_daily_hours", 12.0)
            self.overtime_threshold = config_manager.get("work.overtime_threshold", 8.0)
            self.min_work_duration = config_manager.get("work.min_work_duration", 0.5)
            self.max_break_duration = config_manager.get("work.max_break_duration", 2.0)
            self.auto_break_threshold = config_manager.get("work.auto_break_threshold", 30)
            
            # 时间配置
            work_start = config_manager.get("work.start_time", "09:00")
            work_end = config_manager.get("work.end_time", "18:00")
            lunch_start = config_manager.get("work.lunch_start", "12:00")
            lunch_end = config_manager.get("work.lunch_end", "13:00")
            
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


class EnhancedWorkTimeCalculator:
    """增强的工时计算器"""
    
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
    
    def handle_system_event(self, event_type: EventType, event_time: datetime):
        """处理系统事件"""
        if event_type == EventType.STARTUP:
            self.start_work_session(event_time)
        
        elif event_type == EventType.SHUTDOWN:
            if self.session_start:
                self.end_work_session(event_time)
        
        elif event_type == EventType.LOCK:
            # 自动开始系统休息
            self.start_break(event_time, BreakType.SYSTEM, "系统锁屏")
        
        elif event_type == EventType.UNLOCK:
            # 结束系统休息
            if self.current_break and self.current_break.break_type == BreakType.SYSTEM:
                self.end_break(event_time)
            self.last_activity = event_time
    
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
            work_date = self.session_start.date()
            
            # 检查是否已有记录
            existing_record = time_record_dao.get_by_date(work_date)
            
            # 准备备注信息
            notes = f"工作模式: {self.work_mode.value}, 效率: {calculation_result['efficiency']:.1%}"
            if calculation_result['break_periods']:
                notes += f", 休息次数: {len(calculation_result['break_periods'])}"
            
            if existing_record:
                # 更新现有记录
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


class WorkTimeAnalyzer:
    """工时分析器"""

    def __init__(self):
        self.rules = WorkTimeRule()

    def analyze_daily_records(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """分析日工时记录"""
        from dao import time_record_dao
        from models import TimeRecordQuery

        query = TimeRecordQuery(
            start_date=start_date,
            end_date=end_date,
            page=1,
            size=1000  # 假设不会超过1000条记录
        )

        records = time_record_dao.list_records(query)

        if not records:
            return {"total_days": 0, "records": []}

        daily_stats = []
        total_work_hours = 0
        total_overtime_hours = 0
        total_break_hours = 0

        for record in records:
            work_hours = record.duration / 60 if record.duration else 0
            overtime_hours = record.overtime_duration / 60 if record.overtime_duration else 0
            break_hours = record.break_duration / 60 if record.break_duration else 0

            total_work_hours += work_hours
            total_overtime_hours += overtime_hours
            total_break_hours += break_hours

            daily_stats.append({
                "date": record.date,
                "clock_in": record.clock_in,
                "clock_out": record.clock_out,
                "work_hours": work_hours,
                "overtime_hours": overtime_hours,
                "break_hours": break_hours,
                "status": record.status,
                "notes": record.notes
            })

        # 计算平均值
        total_days = len(records)
        avg_work_hours = total_work_hours / total_days if total_days > 0 else 0
        avg_overtime_hours = total_overtime_hours / total_days if total_days > 0 else 0

        return {
            "period": {"start_date": start_date, "end_date": end_date},
            "total_days": total_days,
            "total_work_hours": total_work_hours,
            "total_overtime_hours": total_overtime_hours,
            "total_break_hours": total_break_hours,
            "avg_work_hours": avg_work_hours,
            "avg_overtime_hours": avg_overtime_hours,
            "records": daily_stats,
            "summary": {
                "standard_days": sum(1 for r in records if abs((r.duration or 0) / 60 - self.rules.standard_hours) <= 0.5),
                "overtime_days": sum(1 for r in records if (r.overtime_duration or 0) > 0),
                "undertime_days": sum(1 for r in records if (r.duration or 0) / 60 < self.rules.standard_hours - 0.5)
            }
        }

    def analyze_weekly_summary(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """分析周工时汇总"""
        daily_analysis = self.analyze_daily_records(start_date, end_date)

        if not daily_analysis["records"]:
            return {"weeks": []}

        # 按周分组
        weeks = {}
        for record in daily_analysis["records"]:
            record_date = record["date"]
            # 计算周的开始日期（周一）
            week_start = record_date - timedelta(days=record_date.weekday())
            week_key = week_start.isoformat()

            if week_key not in weeks:
                weeks[week_key] = {
                    "week_start": week_start,
                    "week_end": week_start + timedelta(days=6),
                    "days": [],
                    "total_work_hours": 0,
                    "total_overtime_hours": 0,
                    "work_days": 0
                }

            weeks[week_key]["days"].append(record)
            weeks[week_key]["total_work_hours"] += record["work_hours"]
            weeks[week_key]["total_overtime_hours"] += record["overtime_hours"]
            weeks[week_key]["work_days"] += 1

        # 转换为列表并排序
        weekly_summary = []
        for week_data in sorted(weeks.values(), key=lambda x: x["week_start"]):
            weekly_summary.append({
                **week_data,
                "avg_daily_hours": week_data["total_work_hours"] / week_data["work_days"] if week_data["work_days"] > 0 else 0,
                "standard_week_hours": self.rules.standard_hours * 5,  # 假设一周5个工作日
                "overtime_ratio": week_data["total_overtime_hours"] / week_data["total_work_hours"] if week_data["total_work_hours"] > 0 else 0
            })

        return {
            "period": {"start_date": start_date, "end_date": end_date},
            "weeks": weekly_summary,
            "total_weeks": len(weekly_summary)
        }

    def analyze_monthly_summary(self, year: int, month: int) -> Dict[str, Any]:
        """分析月工时汇总"""
        from calendar import monthrange

        start_date = date(year, month, 1)
        _, last_day = monthrange(year, month)
        end_date = date(year, month, last_day)

        daily_analysis = self.analyze_daily_records(start_date, end_date)
        weekly_analysis = self.analyze_weekly_summary(start_date, end_date)

        # 计算工作日数（排除周末）
        work_days_in_month = 0
        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() < 5:  # 周一到周五
                work_days_in_month += 1
            current_date += timedelta(days=1)

        actual_work_days = daily_analysis["total_days"]
        attendance_rate = actual_work_days / work_days_in_month if work_days_in_month > 0 else 0

        return {
            "year": year,
            "month": month,
            "period": {"start_date": start_date, "end_date": end_date},
            "work_days_in_month": work_days_in_month,
            "actual_work_days": actual_work_days,
            "attendance_rate": attendance_rate,
            "total_work_hours": daily_analysis["total_work_hours"],
            "total_overtime_hours": daily_analysis["total_overtime_hours"],
            "avg_daily_hours": daily_analysis["avg_work_hours"],
            "expected_hours": work_days_in_month * self.rules.standard_hours,
            "hours_variance": daily_analysis["total_work_hours"] - (work_days_in_month * self.rules.standard_hours),
            "weekly_breakdown": weekly_analysis["weeks"],
            "daily_records": daily_analysis["records"]
        }


# 全局实例
enhanced_calculator = EnhancedWorkTimeCalculator()
work_time_analyzer = WorkTimeAnalyzer()
