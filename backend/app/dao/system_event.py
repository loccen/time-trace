"""
系统事件数据访问对象
"""
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.models import SystemEvent, SystemEventCreate, SystemEventQuery
from app.core.logger import get_logger
from .base import BaseDAO, TimestampMixin

logger = get_logger("SystemEventDAO")


class SystemEventDAO(BaseDAO[SystemEvent], TimestampMixin):
    """系统事件数据访问对象"""
    
    def __init__(self):
        super().__init__("system_events")
    
    def create(self, event: SystemEventCreate) -> int:
        """创建系统事件"""
        try:
            # 准备数据
            data = {
                "event_type": event.event_type.value,
                "event_time": event.event_time.isoformat(),
                "event_source": event.event_source.value,
                "details": event.details,
                "processed": event.processed
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
            
            event_id = self.db.execute_insert(query, tuple(data.values()))
            logger.info(f"创建系统事件成功，ID: {event_id}")
            return event_id
            
        except Exception as e:
            logger.error(f"创建系统事件失败: {e}")
            raise
    
    def mark_processed(self, event_id: int) -> bool:
        """标记事件为已处理"""
        try:
            update_data = {"processed": True}
            query, params = self.build_update_query(self.table_name, update_data, event_id)
            affected_rows = self.db.execute_update(query, params)
            
            success = affected_rows > 0
            if success:
                logger.info(f"标记系统事件已处理，ID: {event_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"标记系统事件处理状态失败，ID: {event_id}, 错误: {e}")
            raise
    
    def mark_batch_processed(self, event_ids: List[int]) -> int:
        """批量标记事件为已处理"""
        try:
            if not event_ids:
                return 0
            
            placeholders = ",".join(["?" for _ in event_ids])
            query = f"""
                UPDATE {self.table_name} 
                SET processed = ?, updated_at = ? 
                WHERE id IN ({placeholders})
            """
            
            params = [True, datetime.now().isoformat()] + event_ids
            affected_rows = self.db.execute_update(query, tuple(params))
            
            logger.info(f"批量标记系统事件已处理，数量: {affected_rows}")
            return affected_rows
            
        except Exception as e:
            logger.error(f"批量标记系统事件处理状态失败: {e}")
            raise
    
    def list_events(self, query_params: SystemEventQuery) -> List[SystemEvent]:
        """查询系统事件列表"""
        try:
            # 构建查询条件
            conditions = []
            params = []
            
            if query_params.event_type:
                conditions.append("event_type = ?")
                params.append(query_params.event_type.value)
            
            if query_params.start_time:
                conditions.append("event_time >= ?")
                params.append(query_params.start_time.isoformat())
            
            if query_params.end_time:
                conditions.append("event_time <= ?")
                params.append(query_params.end_time.isoformat())
            
            if query_params.processed is not None:
                conditions.append("processed = ?")
                params.append(query_params.processed)
            
            # 构建查询语句
            where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
            order_clause = " ORDER BY event_time DESC"
            limit_clause = f" LIMIT {query_params.size} OFFSET {(query_params.page - 1) * query_params.size}"
            
            query = f"SELECT * FROM {self.table_name}{where_clause}{order_clause}{limit_clause}"
            
            rows = self.db.execute_query(query, tuple(params))
            return [self._row_to_model(row) for row in rows]
            
        except Exception as e:
            logger.error(f"查询系统事件列表失败: {e}")
            raise
    
    def count_events(self, query_params: SystemEventQuery) -> int:
        """统计系统事件数量"""
        try:
            # 构建查询条件
            conditions = []
            params = []
            
            if query_params.event_type:
                conditions.append("event_type = ?")
                params.append(query_params.event_type.value)
            
            if query_params.start_time:
                conditions.append("event_time >= ?")
                params.append(query_params.start_time.isoformat())
            
            if query_params.end_time:
                conditions.append("event_time <= ?")
                params.append(query_params.end_time.isoformat())
            
            if query_params.processed is not None:
                conditions.append("processed = ?")
                params.append(query_params.processed)
            
            where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
            query = f"SELECT COUNT(*) as count FROM {self.table_name}{where_clause}"
            
            rows = self.db.execute_query(query, tuple(params))
            return rows[0]['count'] if rows else 0
            
        except Exception as e:
            logger.error(f"统计系统事件数量失败: {e}")
            raise
    
    def get_unprocessed_events(self, limit: int = 100) -> List[SystemEvent]:
        """获取未处理的事件"""
        try:
            query = f"""
                SELECT * FROM {self.table_name} 
                WHERE processed = ? 
                ORDER BY event_time ASC 
                LIMIT ?
            """
            rows = self.db.execute_query(query, (False, limit))
            return [self._row_to_model(row) for row in rows]
            
        except Exception as e:
            logger.error(f"获取未处理事件失败: {e}")
            raise
    
    def get_recent_events(self, limit: int = 50) -> List[SystemEvent]:
        """获取最近的事件"""
        try:
            query = f"""
                SELECT * FROM {self.table_name} 
                ORDER BY event_time DESC 
                LIMIT ?
            """
            rows = self.db.execute_query(query, (limit,))
            return [self._row_to_model(row) for row in rows]
            
        except Exception as e:
            logger.error(f"获取最近事件失败: {e}")
            raise
    
    def get_event_statistics(self, start_time: datetime = None, 
                           end_time: datetime = None) -> Dict[str, Any]:
        """获取事件统计"""
        try:
            conditions = []
            params = []
            
            if start_time:
                conditions.append("event_time >= ?")
                params.append(start_time.isoformat())
            
            if end_time:
                conditions.append("event_time <= ?")
                params.append(end_time.isoformat())
            
            where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
            
            # 总体统计
            total_query = f"SELECT COUNT(*) as total FROM {self.table_name}{where_clause}"
            total_rows = self.db.execute_query(total_query, tuple(params))
            total_events = total_rows[0]['total'] if total_rows else 0
            
            # 按类型统计
            type_query = f"""
                SELECT event_type, COUNT(*) as count 
                FROM {self.table_name}{where_clause}
                GROUP BY event_type
            """
            type_rows = self.db.execute_query(type_query, tuple(params))
            event_counts = {row['event_type']: row['count'] for row in type_rows}
            
            # 处理状态统计
            processed_query = f"""
                SELECT processed, COUNT(*) as count 
                FROM {self.table_name}{where_clause}
                GROUP BY processed
            """
            processed_rows = self.db.execute_query(processed_query, tuple(params))
            processed_stats = {bool(row['processed']): row['count'] for row in processed_rows}
            
            return {
                "total_events": total_events,
                "event_counts": event_counts,
                "processed_count": processed_stats.get(True, 0),
                "unprocessed_count": processed_stats.get(False, 0)
            }
            
        except Exception as e:
            logger.error(f"获取事件统计失败: {e}")
            raise
    
    def cleanup_old_events(self, days: int = 90) -> int:
        """清理旧事件"""
        try:
            from datetime import timedelta
            cutoff_time = datetime.now() - timedelta(days=days)
            
            query = f"DELETE FROM {self.table_name} WHERE event_time < ? AND processed = ?"
            affected_rows = self.db.execute_update(query, (cutoff_time.isoformat(), True))
            
            logger.info(f"清理了 {affected_rows} 条旧系统事件")
            return affected_rows
            
        except Exception as e:
            logger.error(f"清理旧系统事件失败: {e}")
            raise
    
    def _row_to_model(self, row: Dict[str, Any]) -> SystemEvent:
        """将数据库行转换为模型对象"""
        return SystemEvent(
            id=row['id'],
            event_type=row['event_type'],
            event_time=datetime.fromisoformat(row['event_time']),
            event_source=row['event_source'],
            details=row['details'],
            processed=bool(row['processed']),
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row.get('updated_at') else None
        )


# 全局实例
system_event_dao = SystemEventDAO()
