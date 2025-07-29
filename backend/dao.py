"""
数据访问层 (Data Access Object)
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import json

from db_manager import db_manager
from models import (
    TimeRecord, TimeRecordCreate, TimeRecordUpdate,
    SystemEvent, SystemEventCreate,
    SystemConfig, SystemConfigCreate, SystemConfigUpdate,
    OperationLog, OperationLogCreate,
    TimeRecordQuery, SystemEventQuery
)
from logger import get_logger

logger = get_logger("DAO")


class TimeRecordDAO:
    """工时记录数据访问对象"""
    
    def create(self, record: TimeRecordCreate) -> int:
        """创建工时记录"""
        try:
            # 计算工作时长
            record.calculate_duration()
            
            query = """
                INSERT INTO time_records 
                (date, clock_in, clock_out, duration, break_duration, overtime_duration, status, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                record.date.isoformat(),
                record.clock_in.isoformat() if record.clock_in else None,
                record.clock_out.isoformat() if record.clock_out else None,
                record.duration,
                record.break_duration,
                record.overtime_duration,
                record.status.value,
                record.notes
            )
            
            record_id = db_manager.execute_insert(query, params)
            logger.info(f"创建工时记录成功，ID: {record_id}")
            return record_id
            
        except Exception as e:
            logger.error(f"创建工时记录失败: {e}")
            raise
    
    def get_by_id(self, record_id: int) -> Optional[TimeRecord]:
        """根据ID获取工时记录"""
        try:
            query = "SELECT * FROM time_records WHERE id = ?"
            rows = db_manager.execute_query(query, (record_id,))
            
            if rows:
                return self._row_to_model(rows[0])
            return None
            
        except Exception as e:
            logger.error(f"获取工时记录失败，ID: {record_id}, 错误: {e}")
            raise
    
    def get_by_date(self, target_date: date) -> Optional[TimeRecord]:
        """根据日期获取工时记录"""
        try:
            query = "SELECT * FROM time_records WHERE date = ?"
            rows = db_manager.execute_query(query, (target_date.isoformat(),))
            
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
            fields = []
            params = []
            
            update_dict = update_data.model_dump(exclude_unset=True)
            
            for field, value in update_dict.items():
                if field == 'status' and value:
                    fields.append(f"{field} = ?")
                    params.append(value.value)
                elif field in ['clock_in', 'clock_out'] and value:
                    fields.append(f"{field} = ?")
                    params.append(value.isoformat())
                else:
                    fields.append(f"{field} = ?")
                    params.append(value)
            
            if not fields:
                return True  # 没有需要更新的字段
            
            # 添加更新时间
            fields.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            
            # 添加WHERE条件
            params.append(record_id)
            
            query = f"UPDATE time_records SET {', '.join(fields)} WHERE id = ?"
            affected_rows = db_manager.execute_update(query, tuple(params))
            
            success = affected_rows > 0
            if success:
                logger.info(f"更新工时记录成功，ID: {record_id}")
            else:
                logger.warning(f"更新工时记录失败，记录不存在，ID: {record_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"更新工时记录失败，ID: {record_id}, 错误: {e}")
            raise
    
    def delete(self, record_id: int) -> bool:
        """删除工时记录"""
        try:
            query = "DELETE FROM time_records WHERE id = ?"
            affected_rows = db_manager.execute_update(query, (record_id,))
            
            success = affected_rows > 0
            if success:
                logger.info(f"删除工时记录成功，ID: {record_id}")
            else:
                logger.warning(f"删除工时记录失败，记录不存在，ID: {record_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"删除工时记录失败，ID: {record_id}, 错误: {e}")
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
            
            query = f"SELECT * FROM time_records{where_clause}{order_clause}{limit_clause}"
            
            rows = db_manager.execute_query(query, tuple(params))
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
            query = f"SELECT COUNT(*) as count FROM time_records{where_clause}"
            
            rows = db_manager.execute_query(query, tuple(params))
            return rows[0]['count'] if rows else 0
            
        except Exception as e:
            logger.error(f"统计工时记录数量失败: {e}")
            raise
    
    def _row_to_model(self, row) -> TimeRecord:
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


class SystemEventDAO:
    """系统事件数据访问对象"""

    def create(self, event: SystemEventCreate) -> int:
        """创建系统事件"""
        try:
            query = """
                INSERT INTO system_events
                (event_type, event_time, event_source, details, processed)
                VALUES (?, ?, ?, ?, ?)
            """
            params = (
                event.event_type.value,
                event.event_time.isoformat(),
                event.event_source.value,
                event.details,
                event.processed
            )

            event_id = db_manager.execute_insert(query, params)
            logger.info(f"创建系统事件成功，ID: {event_id}")
            return event_id

        except Exception as e:
            logger.error(f"创建系统事件失败: {e}")
            raise

    def get_by_id(self, event_id: int) -> Optional[SystemEvent]:
        """根据ID获取系统事件"""
        try:
            query = "SELECT * FROM system_events WHERE id = ?"
            rows = db_manager.execute_query(query, (event_id,))

            if rows:
                return self._row_to_model(rows[0])
            return None

        except Exception as e:
            logger.error(f"获取系统事件失败，ID: {event_id}, 错误: {e}")
            raise

    def mark_processed(self, event_id: int) -> bool:
        """标记事件为已处理"""
        try:
            query = "UPDATE system_events SET processed = ? WHERE id = ?"
            affected_rows = db_manager.execute_update(query, (True, event_id))

            success = affected_rows > 0
            if success:
                logger.info(f"标记系统事件已处理，ID: {event_id}")

            return success

        except Exception as e:
            logger.error(f"标记系统事件处理状态失败，ID: {event_id}, 错误: {e}")
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

            query = f"SELECT * FROM system_events{where_clause}{order_clause}{limit_clause}"

            rows = db_manager.execute_query(query, tuple(params))
            return [self._row_to_model(row) for row in rows]

        except Exception as e:
            logger.error(f"查询系统事件列表失败: {e}")
            raise

    def get_unprocessed_events(self) -> List[SystemEvent]:
        """获取未处理的事件"""
        try:
            query = "SELECT * FROM system_events WHERE processed = ? ORDER BY event_time ASC"
            rows = db_manager.execute_query(query, (False,))
            return [self._row_to_model(row) for row in rows]

        except Exception as e:
            logger.error(f"获取未处理事件失败: {e}")
            raise

    def _row_to_model(self, row) -> SystemEvent:
        """将数据库行转换为模型对象"""
        return SystemEvent(
            id=row['id'],
            event_type=row['event_type'],
            event_time=datetime.fromisoformat(row['event_time']),
            event_source=row['event_source'],
            details=row['details'],
            processed=bool(row['processed']),
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
        )


class SystemConfigDAO:
    """系统配置数据访问对象"""

    def create(self, config: SystemConfigCreate) -> bool:
        """创建系统配置"""
        try:
            query = """
                INSERT OR REPLACE INTO system_config
                (key, value, description, data_type, category)
                VALUES (?, ?, ?, ?, ?)
            """
            params = (
                config.key,
                config.value,
                config.description,
                config.data_type,
                config.category
            )

            db_manager.execute_insert(query, params)
            logger.info(f"创建系统配置成功，键: {config.key}")
            return True

        except Exception as e:
            logger.error(f"创建系统配置失败: {e}")
            raise

    def get_by_key(self, key: str) -> Optional[SystemConfig]:
        """根据键获取系统配置"""
        try:
            query = "SELECT * FROM system_config WHERE key = ?"
            rows = db_manager.execute_query(query, (key,))

            if rows:
                return self._row_to_model(rows[0])
            return None

        except Exception as e:
            logger.error(f"获取系统配置失败，键: {key}, 错误: {e}")
            raise

    def update(self, key: str, update_data: SystemConfigUpdate) -> bool:
        """更新系统配置"""
        try:
            # 构建更新字段
            fields = []
            params = []

            update_dict = update_data.model_dump(exclude_unset=True)

            for field, value in update_dict.items():
                fields.append(f"{field} = ?")
                params.append(value)

            if not fields:
                return True  # 没有需要更新的字段

            # 添加更新时间
            fields.append("updated_at = ?")
            params.append(datetime.now().isoformat())

            # 添加WHERE条件
            params.append(key)

            query = f"UPDATE system_config SET {', '.join(fields)} WHERE key = ?"
            affected_rows = db_manager.execute_update(query, tuple(params))

            success = affected_rows > 0
            if success:
                logger.info(f"更新系统配置成功，键: {key}")

            return success

        except Exception as e:
            logger.error(f"更新系统配置失败，键: {key}, 错误: {e}")
            raise

    def delete(self, key: str) -> bool:
        """删除系统配置"""
        try:
            query = "DELETE FROM system_config WHERE key = ?"
            affected_rows = db_manager.execute_update(query, (key,))

            success = affected_rows > 0
            if success:
                logger.info(f"删除系统配置成功，键: {key}")

            return success

        except Exception as e:
            logger.error(f"删除系统配置失败，键: {key}, 错误: {e}")
            raise

    def list_by_category(self, category: str = None) -> List[SystemConfig]:
        """按分类查询系统配置"""
        try:
            if category:
                query = "SELECT * FROM system_config WHERE category = ? ORDER BY key"
                rows = db_manager.execute_query(query, (category,))
            else:
                query = "SELECT * FROM system_config ORDER BY category, key"
                rows = db_manager.execute_query(query)

            return [self._row_to_model(row) for row in rows]

        except Exception as e:
            logger.error(f"查询系统配置失败，分类: {category}, 错误: {e}")
            raise

    def _row_to_model(self, row) -> SystemConfig:
        """将数据库行转换为模型对象"""
        return SystemConfig(
            key=row['key'],
            value=row['value'],
            description=row['description'],
            data_type=row['data_type'],
            category=row['category'],
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
        )


class OperationLogDAO:
    """操作日志数据访问对象"""

    def create(self, log: OperationLogCreate) -> int:
        """创建操作日志"""
        try:
            query = """
                INSERT INTO operation_logs
                (operation, operator, target_type, target_id, old_value, new_value,
                 details, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                log.operation,
                log.operator,
                log.target_type,
                log.target_id,
                log.old_value,
                log.new_value,
                log.details,
                log.ip_address,
                log.user_agent
            )

            log_id = db_manager.execute_insert(query, params)
            logger.debug(f"创建操作日志成功，ID: {log_id}")
            return log_id

        except Exception as e:
            logger.error(f"创建操作日志失败: {e}")
            raise

    def get_by_id(self, log_id: int) -> Optional[OperationLog]:
        """根据ID获取操作日志"""
        try:
            query = "SELECT * FROM operation_logs WHERE id = ?"
            rows = db_manager.execute_query(query, (log_id,))

            if rows:
                return self._row_to_model(rows[0])
            return None

        except Exception as e:
            logger.error(f"获取操作日志失败，ID: {log_id}, 错误: {e}")
            raise

    def list_logs(self, operation: str = None, operator: str = None,
                  target_type: str = None, limit: int = 100) -> List[OperationLog]:
        """查询操作日志列表"""
        try:
            # 构建查询条件
            conditions = []
            params = []

            if operation:
                conditions.append("operation = ?")
                params.append(operation)

            if operator:
                conditions.append("operator = ?")
                params.append(operator)

            if target_type:
                conditions.append("target_type = ?")
                params.append(target_type)

            where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
            limit_clause = f" LIMIT {limit}"

            query = f"SELECT * FROM operation_logs{where_clause} ORDER BY timestamp DESC{limit_clause}"

            rows = db_manager.execute_query(query, tuple(params))
            return [self._row_to_model(row) for row in rows]

        except Exception as e:
            logger.error(f"查询操作日志列表失败: {e}")
            raise

    def cleanup_old_logs(self, days: int = 90) -> int:
        """清理旧的操作日志"""
        try:
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days)

            query = "DELETE FROM operation_logs WHERE timestamp < ?"
            affected_rows = db_manager.execute_update(query, (cutoff_date.isoformat(),))

            logger.info(f"清理了 {affected_rows} 条旧操作日志")
            return affected_rows

        except Exception as e:
            logger.error(f"清理旧操作日志失败: {e}")
            raise

    def _row_to_model(self, row) -> OperationLog:
        """将数据库行转换为模型对象"""
        return OperationLog(
            id=row['id'],
            operation=row['operation'],
            operator=row['operator'],
            target_type=row['target_type'],
            target_id=row['target_id'],
            old_value=row['old_value'],
            new_value=row['new_value'],
            details=row['details'],
            ip_address=row['ip_address'],
            user_agent=row['user_agent'],
            timestamp=datetime.fromisoformat(row['timestamp'])
        )


# 全局DAO实例
time_record_dao = TimeRecordDAO()
system_event_dao = SystemEventDAO()
system_config_dao = SystemConfigDAO()
operation_log_dao = OperationLogDAO()
