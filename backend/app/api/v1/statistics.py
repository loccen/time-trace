"""
统计分析API路由
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import date, datetime, timedelta

from app.models import DailyStats, WeeklyStats, MonthlyStats
from app.schemas.response import ApiResponse
from app.dao import TimeRecordDAO
from app.api.deps import get_current_user, get_time_record_dao
from app.utils.date_utils import (
    get_week_range, get_month_range, get_quarter_range, get_year_range,
    get_workdays_in_range, count_workdays_in_month, format_duration
)
from app.core.logger import get_logger

logger = get_logger("StatisticsAPI")
router = APIRouter()


@router.get("/daily/{date_str}", response_model=ApiResponse[DailyStats], summary="获取日统计")
async def get_daily_statistics(
    date_str: str,
    dao: TimeRecordDAO = Depends(get_time_record_dao),
    user: dict = Depends(get_current_user)
):
    """获取指定日期的统计信息"""
    try:
        target_date = date.fromisoformat(date_str)
        
        # 获取当日记录
        record = dao.get_by_date(target_date)
        
        if record:
            daily_stats = DailyStats(
                date=record.date,
                work_hours=record.duration / 60.0,
                overtime_hours=record.overtime_duration / 60.0,
                break_hours=record.break_duration / 60.0,
                clock_in_time=record.clock_in.time() if record.clock_in else None,
                clock_out_time=record.clock_out.time() if record.clock_out else None,
                status=record.status
            )
        else:
            daily_stats = DailyStats(
                date=target_date,
                work_hours=0.0,
                overtime_hours=0.0,
                break_hours=0.0
            )
        
        return {
            "success": True,
            "message": "日统计获取成功",
            "data": daily_stats
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式错误")
    except Exception as e:
        logger.error(f"获取日统计失败: {e}")
        raise HTTPException(status_code=500, detail="获取日统计失败")


@router.get("/weekly/{date_str}", response_model=ApiResponse[WeeklyStats], summary="获取周统计")
async def get_weekly_statistics(
    date_str: str,
    dao: TimeRecordDAO = Depends(get_time_record_dao),
    user: dict = Depends(get_current_user)
):
    """获取指定日期所在周的统计信息"""
    try:
        target_date = date.fromisoformat(date_str)
        week_start, week_end = get_week_range(target_date)
        
        # 获取周内记录
        records = dao.get_date_range_records(week_start, week_end)
        
        # 计算统计数据
        total_work_hours = sum(record.duration for record in records) / 60.0
        total_overtime_hours = sum(record.overtime_duration for record in records) / 60.0
        work_days = len(records)
        avg_daily_hours = total_work_hours / work_days if work_days > 0 else 0.0
        
        # 构建每日记录
        daily_records = []
        current_date = week_start
        while current_date <= week_end:
            record = next((r for r in records if r.date == current_date), None)
            
            if record:
                daily_stats = DailyStats(
                    date=record.date,
                    work_hours=record.duration / 60.0,
                    overtime_hours=record.overtime_duration / 60.0,
                    break_hours=record.break_duration / 60.0,
                    clock_in_time=record.clock_in.time() if record.clock_in else None,
                    clock_out_time=record.clock_out.time() if record.clock_out else None,
                    status=record.status
                )
            else:
                daily_stats = DailyStats(
                    date=current_date,
                    work_hours=0.0,
                    overtime_hours=0.0,
                    break_hours=0.0
                )
            
            daily_records.append(daily_stats)
            current_date += timedelta(days=1)
        
        weekly_stats = WeeklyStats(
            week_start=week_start,
            week_end=week_end,
            total_work_hours=total_work_hours,
            total_overtime_hours=total_overtime_hours,
            work_days=work_days,
            avg_daily_hours=avg_daily_hours,
            daily_records=daily_records
        )
        
        return {
            "success": True,
            "message": "周统计获取成功",
            "data": weekly_stats
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式错误")
    except Exception as e:
        logger.error(f"获取周统计失败: {e}")
        raise HTTPException(status_code=500, detail="获取周统计失败")


@router.get("/monthly/{year}/{month}", response_model=ApiResponse[MonthlyStats], summary="获取月统计")
async def get_monthly_statistics(
    year: int,
    month: int,
    dao: TimeRecordDAO = Depends(get_time_record_dao),
    user: dict = Depends(get_current_user)
):
    """获取指定年月的统计信息"""
    try:
        if month < 1 or month > 12:
            raise HTTPException(status_code=400, detail="月份必须在1-12之间")
        
        # 获取月度记录
        records = dao.get_monthly_records(year, month)
        
        # 计算工作日数
        work_days_in_month = count_workdays_in_month(year, month)
        actual_work_days = len(records)
        
        # 计算统计数据
        total_work_hours = sum(record.duration for record in records) / 60.0
        total_overtime_hours = sum(record.overtime_duration for record in records) / 60.0
        avg_daily_hours = total_work_hours / actual_work_days if actual_work_days > 0 else 0.0
        
        # 计算出勤率
        attendance_rate = actual_work_days / work_days_in_month if work_days_in_month > 0 else 0.0
        
        # 计算预期工作小时数（假设每天8小时）
        expected_hours = work_days_in_month * 8.0
        hours_variance = total_work_hours - expected_hours
        
        monthly_stats = MonthlyStats(
            year=year,
            month=month,
            work_days_in_month=work_days_in_month,
            actual_work_days=actual_work_days,
            attendance_rate=attendance_rate,
            total_work_hours=total_work_hours,
            total_overtime_hours=total_overtime_hours,
            avg_daily_hours=avg_daily_hours,
            expected_hours=expected_hours,
            hours_variance=hours_variance
        )
        
        return {
            "success": True,
            "message": "月统计获取成功",
            "data": monthly_stats
        }
        
    except Exception as e:
        logger.error(f"获取月统计失败: {e}")
        raise HTTPException(status_code=500, detail="获取月统计失败")


@router.get("/range/summary", response_model=ApiResponse[Dict[str, Any]], summary="获取范围统计摘要")
async def get_range_summary(
    start_date: str = Query(..., description="开始日期 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="结束日期 (YYYY-MM-DD)"),
    dao: TimeRecordDAO = Depends(get_time_record_dao),
    user: dict = Depends(get_current_user)
):
    """获取指定日期范围的统计摘要"""
    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
        
        if start > end:
            raise HTTPException(status_code=400, detail="开始日期不能晚于结束日期")
        
        # 获取统计摘要
        summary = dao.get_statistics_summary(start, end)
        
        # 添加额外的计算字段
        workdays = get_workdays_in_range(start, end)
        summary["workdays_in_range"] = len(workdays)
        summary["attendance_rate"] = summary["total_days"] / len(workdays) if workdays else 0.0
        summary["avg_hours_per_workday"] = summary["total_hours"] / len(workdays) if workdays else 0.0
        
        # 格式化时长
        summary["total_hours_formatted"] = format_duration(int(summary["total_hours"] * 60))
        summary["total_overtime_hours_formatted"] = format_duration(int(summary["total_overtime_hours"] * 60))
        summary["avg_hours_formatted"] = format_duration(int(summary["avg_hours"] * 60))
        
        return {
            "success": True,
            "message": "范围统计摘要获取成功",
            "data": summary
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式错误")
    except Exception as e:
        logger.error(f"获取范围统计摘要失败: {e}")
        raise HTTPException(status_code=500, detail="获取范围统计摘要失败")


@router.get("/trends/weekly", response_model=ApiResponse[List[Dict[str, Any]]], summary="获取周趋势数据")
async def get_weekly_trends(
    weeks: int = Query(12, ge=1, le=52, description="获取最近几周的数据"),
    dao: TimeRecordDAO = Depends(get_time_record_dao),
    user: dict = Depends(get_current_user)
):
    """获取最近几周的工时趋势数据"""
    try:
        trends = []
        today = date.today()
        
        for i in range(weeks):
            # 计算周的开始日期
            week_offset = timedelta(weeks=i)
            week_date = today - week_offset
            week_start, week_end = get_week_range(week_date)
            
            # 获取该周的记录
            records = dao.get_date_range_records(week_start, week_end)
            
            # 计算统计数据
            total_hours = sum(record.duration for record in records) / 60.0
            overtime_hours = sum(record.overtime_duration for record in records) / 60.0
            work_days = len(records)
            
            trends.append({
                "week_start": week_start.isoformat(),
                "week_end": week_end.isoformat(),
                "total_hours": total_hours,
                "overtime_hours": overtime_hours,
                "work_days": work_days,
                "avg_daily_hours": total_hours / work_days if work_days > 0 else 0.0
            })
        
        # 按时间正序排列
        trends.reverse()
        
        return {
            "success": True,
            "message": f"获取最近 {weeks} 周趋势数据成功",
            "data": trends
        }
        
    except Exception as e:
        logger.error(f"获取周趋势数据失败: {e}")
        raise HTTPException(status_code=500, detail="获取周趋势数据失败")


@router.get("/overview/dashboard", response_model=ApiResponse[Dict[str, Any]], summary="获取仪表板概览")
async def get_dashboard_overview(
    dao: TimeRecordDAO = Depends(get_time_record_dao),
    user: dict = Depends(get_current_user)
):
    """获取仪表板概览数据"""
    try:
        today = date.today()
        
        # 今日统计
        today_record = dao.get_by_date(today)
        today_hours = today_record.duration / 60.0 if today_record else 0.0
        
        # 本周统计
        week_start, week_end = get_week_range(today)
        week_records = dao.get_date_range_records(week_start, week_end)
        week_hours = sum(record.duration for record in week_records) / 60.0
        
        # 本月统计
        month_records = dao.get_monthly_records(today.year, today.month)
        month_hours = sum(record.duration for record in month_records) / 60.0
        month_workdays = count_workdays_in_month(today.year, today.month)
        
        # 最近7天趋势
        recent_days = []
        for i in range(7):
            day = today - timedelta(days=i)
            record = dao.get_by_date(day)
            recent_days.append({
                "date": day.isoformat(),
                "hours": record.duration / 60.0 if record else 0.0
            })
        recent_days.reverse()
        
        overview = {
            "today": {
                "date": today.isoformat(),
                "hours": today_hours,
                "status": today_record.status.value if today_record else "no_record"
            },
            "this_week": {
                "start_date": week_start.isoformat(),
                "end_date": week_end.isoformat(),
                "total_hours": week_hours,
                "work_days": len(week_records),
                "avg_daily_hours": week_hours / len(week_records) if week_records else 0.0
            },
            "this_month": {
                "year": today.year,
                "month": today.month,
                "total_hours": month_hours,
                "work_days": len(month_records),
                "expected_workdays": month_workdays,
                "attendance_rate": len(month_records) / month_workdays if month_workdays > 0 else 0.0
            },
            "recent_trend": recent_days
        }
        
        return {
            "success": True,
            "message": "仪表板概览获取成功",
            "data": overview
        }
        
    except Exception as e:
        logger.error(f"获取仪表板概览失败: {e}")
        raise HTTPException(status_code=500, detail="获取仪表板概览失败")
