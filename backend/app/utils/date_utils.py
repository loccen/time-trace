"""
日期时间工具函数
"""
from datetime import datetime, date, time, timedelta
from typing import List, Tuple, Optional
import calendar


def get_week_range(target_date: date) -> Tuple[date, date]:
    """获取指定日期所在周的开始和结束日期（周一到周日）"""
    # 计算周一的日期
    days_since_monday = target_date.weekday()
    week_start = target_date - timedelta(days=days_since_monday)
    week_end = week_start + timedelta(days=6)
    
    return week_start, week_end


def get_month_range(year: int, month: int) -> Tuple[date, date]:
    """获取指定年月的开始和结束日期"""
    month_start = date(year, month, 1)
    
    # 获取月份的最后一天
    _, last_day = calendar.monthrange(year, month)
    month_end = date(year, month, last_day)
    
    return month_start, month_end


def get_quarter_range(year: int, quarter: int) -> Tuple[date, date]:
    """获取指定年季度的开始和结束日期"""
    if quarter not in [1, 2, 3, 4]:
        raise ValueError("季度必须是1-4之间的整数")
    
    start_month = (quarter - 1) * 3 + 1
    end_month = quarter * 3
    
    quarter_start = date(year, start_month, 1)
    _, last_day = calendar.monthrange(year, end_month)
    quarter_end = date(year, end_month, last_day)
    
    return quarter_start, quarter_end


def get_year_range(year: int) -> Tuple[date, date]:
    """获取指定年份的开始和结束日期"""
    year_start = date(year, 1, 1)
    year_end = date(year, 12, 31)
    
    return year_start, year_end


def get_workdays_in_range(start_date: date, end_date: date) -> List[date]:
    """获取日期范围内的工作日（周一到周五）"""
    workdays = []
    current_date = start_date
    
    while current_date <= end_date:
        # 0-6 对应周一到周日，0-4是工作日
        if current_date.weekday() < 5:
            workdays.append(current_date)
        current_date += timedelta(days=1)
    
    return workdays


def count_workdays_in_month(year: int, month: int) -> int:
    """计算指定月份的工作日数量"""
    start_date, end_date = get_month_range(year, month)
    workdays = get_workdays_in_range(start_date, end_date)
    return len(workdays)


def get_weeks_in_range(start_date: date, end_date: date) -> List[Tuple[date, date]]:
    """获取日期范围内的所有周"""
    weeks = []
    current_date = start_date
    
    while current_date <= end_date:
        week_start, week_end = get_week_range(current_date)
        
        # 调整周范围以适应指定的日期范围
        actual_start = max(week_start, start_date)
        actual_end = min(week_end, end_date)
        
        if actual_start <= actual_end:
            weeks.append((actual_start, actual_end))
        
        # 移动到下一周
        current_date = week_end + timedelta(days=1)
    
    return weeks


def format_duration(minutes: int) -> str:
    """格式化时长为可读字符串"""
    if minutes < 0:
        return "0分钟"
    
    hours = minutes // 60
    remaining_minutes = minutes % 60
    
    if hours == 0:
        return f"{remaining_minutes}分钟"
    elif remaining_minutes == 0:
        return f"{hours}小时"
    else:
        return f"{hours}小时{remaining_minutes}分钟"


def format_time_range(start_time: Optional[datetime], end_time: Optional[datetime]) -> str:
    """格式化时间范围为可读字符串"""
    if not start_time:
        return "未开始"
    
    start_str = start_time.strftime("%H:%M")
    
    if not end_time:
        return f"{start_str} - 进行中"
    
    end_str = end_time.strftime("%H:%M")
    return f"{start_str} - {end_str}"


def is_same_day(dt1: datetime, dt2: datetime) -> bool:
    """检查两个日期时间是否在同一天"""
    return dt1.date() == dt2.date()


def get_time_of_day_category(dt: datetime) -> str:
    """获取时间段分类"""
    hour = dt.hour
    
    if 6 <= hour < 12:
        return "上午"
    elif 12 <= hour < 18:
        return "下午"
    elif 18 <= hour < 22:
        return "晚上"
    else:
        return "深夜"


def calculate_age_in_days(start_date: date, end_date: date = None) -> int:
    """计算两个日期之间的天数"""
    if end_date is None:
        end_date = date.today()
    
    return (end_date - start_date).days


def get_relative_date_string(target_date: date) -> str:
    """获取相对日期字符串"""
    today = date.today()
    diff = (target_date - today).days
    
    if diff == 0:
        return "今天"
    elif diff == 1:
        return "明天"
    elif diff == -1:
        return "昨天"
    elif diff > 1 and diff <= 7:
        return f"{diff}天后"
    elif diff < -1 and diff >= -7:
        return f"{abs(diff)}天前"
    elif diff > 7:
        weeks = diff // 7
        return f"{weeks}周后"
    else:
        weeks = abs(diff) // 7
        return f"{weeks}周前"


def parse_time_string(time_str: str) -> Optional[time]:
    """解析时间字符串为time对象"""
    try:
        # 支持多种格式
        formats = ["%H:%M", "%H:%M:%S", "%I:%M %p", "%I:%M:%S %p"]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(time_str, fmt)
                return dt.time()
            except ValueError:
                continue
        
        return None
    except Exception:
        return None


def combine_date_time(target_date: date, target_time: time) -> datetime:
    """组合日期和时间为datetime对象"""
    return datetime.combine(target_date, target_time)


def get_business_hours_duration(start_time: datetime, end_time: datetime,
                               business_start: time = time(9, 0),
                               business_end: time = time(18, 0)) -> int:
    """计算营业时间内的工作时长（分钟）"""
    if start_time.date() != end_time.date():
        # 跨天的情况，只计算第一天的营业时间
        end_time = datetime.combine(start_time.date(), business_end)
    
    # 调整到营业时间范围内
    business_start_dt = datetime.combine(start_time.date(), business_start)
    business_end_dt = datetime.combine(start_time.date(), business_end)
    
    actual_start = max(start_time, business_start_dt)
    actual_end = min(end_time, business_end_dt)
    
    if actual_start >= actual_end:
        return 0
    
    return int((actual_end - actual_start).total_seconds() / 60)


def get_next_workday(target_date: date) -> date:
    """获取下一个工作日"""
    next_day = target_date + timedelta(days=1)
    
    while next_day.weekday() >= 5:  # 周六和周日
        next_day += timedelta(days=1)
    
    return next_day


def get_previous_workday(target_date: date) -> date:
    """获取上一个工作日"""
    prev_day = target_date - timedelta(days=1)
    
    while prev_day.weekday() >= 5:  # 周六和周日
        prev_day -= timedelta(days=1)
    
    return prev_day
