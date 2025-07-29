"""
工时记录数据访问对象
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date

from app.models import TimeRecord, TimeRecordCreate, TimeRecordUpdate, TimeRecordQuery
from app.core.logger import get_logger
from .base import BaseDAO, TimestampMixin

logger = get_logger("TimeRecordDAO")


class TimeRecordDAO(BaseDAO[TimeRecord], TimestampMixin):
    """工时记录数据访问对象"""
    
    def __init__(self):
        super().__init__("time_records")
    
    def create(self, record: TimeRecordCreate) -> int:
        """创建工时记录"""
        try:
            # 计算工作时长
            record.calculate_duration()
            
            # 准备数据
            data = {
                "date": record.date.isoformat(),
                "clock_in": record.clock_in.isoformat() if record.clock_in else None,
                "clock_out": record.clock_out.isoformat() if record.clock_out else None,
                "duration": record.duration,
                "break_duration": record.break_duration,
                "overtime_duration": record.overtime_duration,
                "status": record.status.value,
                "notes": record.notes
            }
            
            # 添加时间戳
            data = self.add_timestamps(data)
            
            # 构建查询
            fields = list(data.keys())
            placeholders = ["?" for _ in fields]
            query = f"""
                INSERT INTO {self.table_name} 
                ({', '.join(fields)})
                VALUES ({', '.join(placeholders)})
            """
            
            record_id = self.db.execute_insert(query, tuple(data.values()))
            logger.info(f"创建工时记录成功，ID: {record_id}")
            return record_id
            
        except Exception as e:
            logger.error(f"创建工时记录失败: {e}")
            raise
    
    def get_by_date(self, target_date: date) -> Optional[TimeRecord]:
        """根据日期获取工时记录"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE date = ?"
            rows = self.db.execute_query(query, (target_date.isoformat(),))
            
            if rows:
                return self._row_to_model(rows[0])
            return None
            
        except Exception as e:
            logger.error(f"获取工时记录失败，日期: {target_date}, 错误: {e}")
            raise
    
    def update(self, record_id: int, update_data: TimeRecordUpdate) -> bool:
        """更新工时记录"""
        try:
            # 构建更新字段
            update_dict = {}
            
            for field, value in update_data.model_dump(exclude_unset=True).items():
                if field == 'status' and value:
                    update_dict[field] = value.value
                elif field in ['clock_in', 'clock_out'] and value:
                    update_dict[field] = value.isoformat()
                else:
                    update_dict[field] = value
            
            if not update_dict:
                return True  # 没有需要更新的字段
            
            # 构建查询
            query, params = self.build_update_query(self.table_name, update_dict, record_id)
            affected_rows = self.db.execute_update(query, params)
            
            success = affected_rows > 0
            if success:
                logger.info(f"更新工时记录成功，ID: {record_id}")
            else:
                logger.warning(f"更新工时记录失败，记录不存在，ID: {record_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"更新工时记录失败，ID: {record_id}, 错误: {e}")
            raise
    
    def list_records(self, query_params: TimeRecordQuery) -> List[TimeRecord]:
        """查询工时记录列表"""
        try:
            # 构建查询条件
            conditions = []
            params = []
            
            if query_params.start_date:
                conditions.append("date >= ?")
                params.append(query_params.start_date.isoformat())
            
            if query_params.end_date:
                conditions.append("date <= ?")
                params.append(query_params.end_date.isoformat())
            
            if query_params.status:
                conditions.append("status = ?")
                params.append(query_params.status.value)
            
            # 构建查询语句
            where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
            order_clause = f" ORDER BY {query_params.order_by}"
            if query_params.order_desc:
                order_clause += " DESC"
            
            # 分页
            limit_clause = f" LIMIT {query_params.size} OFFSET {(query_params.page - 1) * query_params.size}"
            
            query = f"SELECT * FROM {self.table_name}{where_clause}{order_clause}{limit_clause}"
            
            rows = self.db.execute_query(query, tuple(params))
            return [self._row_to_model(row) for row in rows]
            
        except Exception as e:
            logger.error(f"查询工时记录列表失败: {e}")
            raise
    
    def count_records(self, query_params: TimeRecordQuery) -> int:
        """统计工时记录数量"""
        try:
            # 构建查询条件
            conditions = []
            params = []
            
            if query_params.start_date:
                conditions.append("date >= ?")
                params.append(query_params.start_date.isoformat())
            
            if query_params.end_date:
                conditions.append("date <= ?")
                params.append(query_params.end_date.isoformat())
            
            if query_params.status:
                conditions.append("status = ?")
                params.append(query_params.status.value)
            
            where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
            query = f"SELECT COUNT(*) as count FROM {self.table_name}{where_clause}"
            
            rows = self.db.execute_query(query, tuple(params))
            return rows[0]['count'] if rows else 0
            
        except Exception as e:
            logger.error(f"统计工时记录数量失败: {e}")
            raise
    
    def get_date_range_records(self, start_date: date, end_date: date) -> List[TimeRecord]:
        """获取日期范围内的记录"""
        try:
            query = f"""
                SELECT * FROM {self.table_name} 
                WHERE date >= ? AND date <= ? 
                ORDER BY date ASC
            """
            rows = self.db.execute_query(query, (start_date.isoformat(), end_date.isoformat()))
            return [self._row_to_model(row) for row in rows]
        except Exception as e:
            logger.error(f"获取日期范围记录失败: {start_date} - {end_date}, 错误: {e}")
            raise
    
    def get_monthly_records(self, year: int, month: int) -> List[TimeRecord]:
        """获取月度记录"""
        try:
            start_date = date(year, month, 1)
            if month == 12:
                end_date = date(year + 1, 1, 1)
            else:
                end_date = date(year, month + 1, 1)
            
            query = f"""
                SELECT * FROM {self.table_name} 
                WHERE date >= ? AND date < ? 
                ORDER BY date ASC
            """
            rows = self.db.execute_query(query, (start_date.isoformat(), end_date.isoformat()))
            return [self._row_to_model(row) for row in rows]
        except Exception as e:
            logger.error(f"获取月度记录失败: {year}-{month}, 错误: {e}")
            raise
    
    def get_statistics_summary(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """获取统计摘要"""
        try:
            query = f"""
                SELECT 
                    COUNT(*) as total_days,
                    SUM(duration) as total_minutes,
                    SUM(overtime_duration) as total_overtime_minutes,
                    SUM(break_duration) as total_break_minutes,
                    AVG(duration) as avg_minutes,
                    MIN(date) as first_date,
                    MAX(date) as last_date
                FROM {self.table_name}
                WHERE date >= ? AND date <= ?
            """
            rows = self.db.execute_query(query, (start_date.isoformat(), end_date.isoformat()))
            
            if rows and rows[0]['total_days']:
                row = rows[0]
                return {
                    "total_days": row['total_days'],
                    "total_hours": (row['total_minutes'] or 0) / 60,
                    "total_overtime_hours": (row['total_overtime_minutes'] or 0) / 60,
                    "total_break_hours": (row['total_break_minutes'] or 0) / 60,
                    "avg_hours": (row['avg_minutes'] or 0) / 60,
                    "first_date": row['first_date'],
                    "last_date": row['last_date']
                }
            else:
                return {
                    "total_days": 0,
                    "total_hours": 0,
                    "total_overtime_hours": 0,
                    "total_break_hours": 0,
                    "avg_hours": 0,
                    "first_date": None,
                    "last_date": None
                }
        except Exception as e:
            logger.error(f"获取统计摘要失败: {e}")
            raise
    
    def _row_to_model(self, row: Dict[str, Any]) -> TimeRecord:
        """将数据库行转换为模型对象"""
        return TimeRecord(
            id=row['id'],
            date=date.fromisoformat(row['date']),
            clock_in=datetime.fromisoformat(row['clock_in']) if row['clock_in'] else None,
            clock_out=datetime.fromisoformat(row['clock_out']) if row['clock_out'] else None,
            duration=row['duration'],
            break_duration=row['break_duration'],
            overtime_duration=row['overtime_duration'],
            status=row['status'],
            notes=row['notes'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
        )


# 全局实例
time_record_dao = TimeRecordDAO()
